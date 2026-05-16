import os
import json
import hashlib
import hmac
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, ConfigDict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

import database
from config import settings
from models import VoteReceiptModel, BlockModel, ProposalModel
from cache import set_nullifier, has_nullifier, set_merkle_cache, get_merkle_cache, ping as redis_ping
from blockchain import Blockchain
from crypto.zk_commitment import generate_commitment, verify_commitment
from crypto.merkle_tree import MerkleTree
from crypto.block_signer import AUDITOR_PUBLIC_KEY, verify_block_payload
from routes import proposals, admin
from services.admin_service import decode_token, seed_default_admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando base de datos...")
    await database.init_db()
    async with database.async_session() as session:
        await seed_default_admin(session)
    await urna_chain.load_from_db()
    logger.info(f"Blockchain cargada: {len(urna_chain.chain)} bloques")
    yield
    logger.info("Apagando aplicación...")

# --- App ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Voz ciudadana API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [settings.frontend_url]
if settings.dev_mode == "1":
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

app.include_router(proposals.router)
app.include_router(admin.router)

urna_chain = Blockchain()

# --- Connection Managers ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket, role: str):
        await ws.accept()
        if role == "admin":
            self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast_audit(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as exc:
                logger.warning("Error enviando audit: %s", exc)

manager = ConnectionManager()

class ResultsConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, process_id: str):
        await ws.accept()
        self.connections.setdefault(process_id, []).append(ws)

    def disconnect(self, ws: WebSocket, process_id: str):
        conns = self.connections.get(process_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast(self, process_id: str, message: dict):
        for conn in self.connections.get(process_id, []):
            try:
                await conn.send_json(message)
            except Exception as exc:
                logger.warning("Error enviando resultados: %s", exc)

results_manager = ResultsConnectionManager()

# --- Models ---
class LoginRequest(BaseModel):
    ine: str = Field(..., min_length=18, max_length=18, pattern=r"^[A-Z0-9]+$")

class BulkVerifyRequest(BaseModel):
    hashes: list[str] = Field(..., max_length=500)

class CommitRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    process_id: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    vote_index: int = Field(..., ge=0)
    num_options: int = Field(..., gt=0)

    @validator("vote_index")
    def vote_index_valid(cls, v, values):
        if "num_options" in values.data and v >= values.data["num_options"]:
            raise ValueError("vote_index debe ser menor que num_options")
        return v

class CommitResponse(BaseModel):
    commitment_x: str
    commitment_y: str
    nullifier: str
    receipt_token: str
    block_hash: str

# --- Helpers ---
def hash_ine(ine: str, proceso_id: str) -> str:
    return hashlib.sha256(f"{settings.process_salt}:{ine}:{proceso_id}".encode()).hexdigest()

def generate_receipt_jwt(nullifier: str) -> str:
    import jwt as _jwt
    return _jwt.encode({"nullifier": nullifier, "typ": "receipt"}, settings.jwt_secret, algorithm="HS256")

async def _update_merkle_tree(process_id: str):
    async with database.async_session() as session:
        result = await session.execute(select(BlockModel.hash).where(BlockModel.index > 0).order_by(BlockModel.index))
        leaf_hashes = [row[0] for row in result.all()]
    if not leaf_hashes:
        return
    tree = MerkleTree(leaf_hashes)
    await set_merkle_cache(process_id, {"root": tree.root, "tree": tree.tree, "leaves": tree.leaves})

async def _broadcast_results(process_id: str):
    counts: dict[str, int] = {}
    for block in urna_chain.chain:
        if block.index == 0:
            continue
        opt = block.data.get("opcion_id", "unknown")
        counts[opt] = counts.get(opt, 0) + 1
    payload = [{"option": k, "count": v} for k, v in counts.items()]
    await results_manager.broadcast(process_id, payload)

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Voz ciudadana API Blockchain is running", "chain_valid": urna_chain.is_chain_valid()}

@app.get("/health")
async def health_check():
    db_ok = False
    redis_ok = False
    try:
        async with database.async_session() as session:
            await session.execute(select(1))
            db_ok = True
    except Exception as exc:
        logger.warning("Health DB fail: %s", exc)
    try:
        redis_ok = await redis_ping()
    except Exception as exc:
        logger.warning("Health Redis fail: %s", exc)

    if not db_ok or not redis_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "postgres": "connected" if db_ok else "disconnected", "redis": "connected" if redis_ok else "disconnected"}
        )
    return {
        "status": "ok",
        "postgres": "connected",
        "redis": "connected",
        "blockchain_height": len(urna_chain.chain),
        "last_block_ts": urna_chain.get_latest_block().timestamp
    }

@app.post("/api/v1/vote/commit", response_model=CommitResponse)
@limiter.limit("5/minute")
async def commit_vote(request: Request, body: CommitRequest):
    zk = generate_commitment(body.vote_index, body.num_options)
    existing = await has_nullifier(zk["nullifier"])
    if existing:
        raise HTTPException(status_code=409, detail="Voto ya emitido para este proceso.", headers={"X-Error-Code": "VOTE_ALREADY_CAST"})

    await set_nullifier(zk["nullifier"], ttl=3600 * 24)

    # Datos que se almacenan en la cadena: NUNCA incluyen identidad.
    # El nullifier ZK evita doble voto sin revelar quién votó.
    vote_data = {
        "opcion_id": f"opt{body.vote_index + 1}",
        "commitment": zk["commitment"],
        "nullifier": zk["nullifier"],
        "process_id": body.process_id,
    }
    nuevo_bloque = await urna_chain.add_block(vote_data)

    await _update_merkle_tree(body.process_id)

    await manager.broadcast_audit({
        "event": "vote_cast",
        "timestamp": nuevo_bloque.timestamp,
        "hash": nuevo_bloque.hash,
        "nullifier": zk["nullifier"],
        "ip_ofuscada": request.client.host if request.client else "unknown"
    })

    await _broadcast_results(body.process_id)

    return CommitResponse(
        commitment_x=zk["commitment"][0],
        commitment_y=zk["commitment"][1],
        nullifier=zk["nullifier"],
        receipt_token=generate_receipt_jwt(zk["nullifier"]),
        block_hash=nuevo_bloque.hash
    )

@app.get("/transparencia/chain")
async def get_chain():
    return {
        "length": len(urna_chain.chain),
        "chain": [b.to_dict() for b in urna_chain.chain],
        "auditor_pubkey": AUDITOR_PUBLIC_KEY,
        "signatures_valid": urna_chain.is_chain_signatures_valid()
    }

@app.get("/transparencia/export")
async def export_chain(format: str = "json"):
    chain_data = await get_chain()
    secret = settings.hmac_secret.encode()
    payload = json.dumps(chain_data).encode()
    signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return {"data": chain_data, "signature": signature, "format": format}

@app.get("/transparencia/verificar/{hash_recibo}")
async def verificar_voto(hash_recibo: str, process_id: str = "proceso_2025"):
    bloque = urna_chain.find_vote_by_hash(hash_recibo)
    if not bloque:
        for block in urna_chain.chain:
            if block.index == 0:
                continue
            if block.data.get("nullifier") == hash_recibo:
                bloque = block
                break
    if not bloque:
        return {"status": "error", "encontrado": False, "message": "Voto no encontrado en la cadena"}

    # Verificar firma del bloque antes de devolverlo
    sig_valid = verify_block_payload(bloque.payload_for_signing(), bloque.signature, bloque.auditor_pubkey)

    merkle_data = await get_merkle_cache(process_id)
    proof = []
    is_valid = False
    if merkle_data:
        tree = MerkleTree.__new__(MerkleTree)
        tree.tree = merkle_data["tree"]
        tree.leaves = tree.tree[0]
        try:
            leaf_index = tree.leaves.index(hash_recibo)
            proof = tree.get_proof(leaf_index)
            is_valid = MerkleTree.verify_proof(hash_recibo, proof, merkle_data["root"])
        except ValueError:
            pass

    return {
        "status": "success",
        "encontrado": True,
        "block_hash": bloque.hash,
        "block_index": bloque.index,
        "block_timestamp": bloque.timestamp,
        "signature_valid": sig_valid,
        "auditor_pubkey": bloque.auditor_pubkey,
        "merkle_root": merkle_data["root"] if merkle_data else None,
        "proof": proof,
        "verified": is_valid,
        "message": "Voto verificado en el escrutinio oficial." if is_valid else "Hash encontrado pero sin prueba Merkle disponible."
    }

@app.post("/transparencia/verificar/bulk")
@limiter.limit("1/minute")
async def verificar_bulk(request: Request, req: BulkVerifyRequest):
    resultados = []
    for h in req.hashes:
        bloque = urna_chain.find_vote_by_hash(h)
        resultados.append({"hash": h, "valido": bloque is not None})
    return {"resultados": resultados}

@app.websocket("/ws/audit")
async def audit_ws(ws: WebSocket, token: str = ""):
    payload = decode_token(token)
    if not payload or payload.get("type") != "admin":
        await ws.close(code=1008)
        return
    await manager.connect(ws, role="admin")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.websocket("/ws/results/{process_id}")
async def results_stream(ws: WebSocket, process_id: str):
    await results_manager.connect(ws, process_id)
    try:
        import asyncio
        while True:
            counts: dict[str, int] = {}
            for block in urna_chain.chain:
                if block.index == 0:
                    continue
                opt = block.data.get("opcion_id", "unknown")
                counts[opt] = counts.get(opt, 0) + 1
            payload = [{"option": k, "count": v} for k, v in counts.items()]
            await ws.send_json(payload)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        results_manager.disconnect(ws, process_id)
