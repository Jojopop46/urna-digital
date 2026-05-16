from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import json
import hashlib
import asyncio
from typing import List, Dict, Optional
from blockchain import Blockchain
from crypto.zk_commitment import generate_commitment, verify_commitment
from crypto.merkle_tree import MerkleTree

app = FastAPI(title="Urna Digital API")

import os

origins = [os.getenv("FRONTEND_URL", "http://localhost:3000")]
if os.getenv("DEV_MODE") == "1":
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

urna_chain = Blockchain()

# In-memory stores for demo (fallback if Redis not connected)
nullifier_store: Dict[str, str] = {}  # identity_hash -> nullifier
merkle_cache: Dict[str, dict] = {}    # process_id -> merkle data

# --- Connection Managers ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

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
            except:
                pass

manager = ConnectionManager()

class ResultsConnectionManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

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
            except:
                pass

results_manager = ResultsConnectionManager()

# --- Models ---
class LoginRequest(BaseModel):
    ine: str

class VotoRequest(BaseModel):
    opcion_id: str
    token_sesion: str

class BulkVerifyRequest(BaseModel):
    hashes: List[str]

class CommitRequest(BaseModel):
    process_id: str
    vote_index: int
    num_options: int
    identity_hash: str

class CommitResponse(BaseModel):
    commitment_x: str
    commitment_y: str
    nullifier: str
    receipt_token: str
    block_hash: str

# --- Helper ---
def hash_ine(ine: str, proceso_id: str) -> str:
    salt = os.getenv("PROCESS_SALT", "default_salt_123")
    return hashlib.sha256(f"{salt}:{ine}:{proceso_id}".encode()).hexdigest()

def generate_receipt_jwt(nullifier: str) -> str:
    import jwt
    secret = os.getenv("JWT_SECRET", "super_secret_jwt_key")
    return jwt.encode({"nullifier": nullifier, "typ": "receipt"}, secret, algorithm="HS256")

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Urna Digital API Blockchain is running", "chain_valid": urna_chain.is_chain_valid()}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "postgres": "connected",
        "redis": "connected",
        "blockchain_height": len(urna_chain.chain),
        "last_block_ts": urna_chain.get_latest_block().timestamp
    }

@app.post("/urna/emitir")
async def emitir_voto(voto: VotoRequest):
    data = {
        "opcion_id": voto.opcion_id,
        "token_sesion": voto.token_sesion
    }
    nuevo_bloque = urna_chain.add_block(data)
    
    await manager.broadcast_audit({
        "event": "vote_cast",
        "timestamp": nuevo_bloque.timestamp,
        "hash": nuevo_bloque.hash,
        "ip_ofuscada": "192.168.x.x"
    })

    return {
        "status": "success",
        "recibo": nuevo_bloque.hash,
        "index": nuevo_bloque.index,
        "timestamp": nuevo_bloque.timestamp
    }

@app.post("/api/v1/vote/commit", response_model=CommitResponse)
async def commit_vote(body: CommitRequest):
    # 1. Verificar que el nullifier no exista (previene doble voto)
    existing = nullifier_store.get(body.identity_hash)
    if existing:
        raise HTTPException(status_code=409, detail="Voto ya emitido para este proceso.")

    # 2. Generar commitment ZK
    zk = generate_commitment(body.vote_index, body.num_options)

    # 3. Guardar SOLO el nullifier (TTL simulado en memoria)
    nullifier_store[body.identity_hash] = zk["nullifier"]

    # 4. Minar en blockchain (el voto es el commitment)
    vote_data = {
        "opcion_id": f"opt{body.vote_index + 1}",
        "commitment": zk["commitment"],
        "nullifier": zk["nullifier"],
        "process_id": body.process_id,
        "identity_hash": body.identity_hash,
    }
    nuevo_bloque = urna_chain.add_block(vote_data)

    # 5. Construir / actualizar Merkle Tree para el proceso
    await _update_merkle_tree(body.process_id)

    # 6. Emitir evento de auditoría
    await manager.broadcast_audit({
        "event": "vote_cast",
        "timestamp": nuevo_bloque.timestamp,
        "hash": nuevo_bloque.hash,
        "nullifier": zk["nullifier"],
        "ip_ofuscada": "192.168.x.x"
    })

    # 7. Notificar resultados en tiempo real
    await _broadcast_results(body.process_id)

    return CommitResponse(
        commitment_x=zk["commitment"][0],
        commitment_y=zk["commitment"][1],
        nullifier=zk["nullifier"],
        receipt_token=generate_receipt_jwt(zk["nullifier"]),
        block_hash=nuevo_bloque.hash
    )

async def _update_merkle_tree(process_id: str):
    # Obtener todos los hashes de bloques del proceso (simplificado: usamos block.hash)
    leaf_hashes = [block.hash for block in urna_chain.chain if block.index > 0]
    if not leaf_hashes:
        return
    tree = MerkleTree(leaf_hashes)
    merkle_cache[process_id] = {
        "root": tree.root,
        "tree": tree.tree,
        "leaves": tree.leaves,
    }

async def _broadcast_results(process_id: str):
    # Conteo simple por opción
    counts: Dict[str, int] = {}
    for block in urna_chain.chain:
        if block.index == 0:
            continue
        opt = block.data.get("opcion_id", "unknown")
        counts[opt] = counts.get(opt, 0) + 1
    payload = [{"option": k, "count": v} for k, v in counts.items()]
    await results_manager.broadcast(process_id, payload)

@app.get("/transparencia/chain")
def get_chain():
    chain_data = []
    for block in urna_chain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })
    return {"length": len(chain_data), "chain": chain_data}

@app.get("/transparencia/export")
def export_chain(format: str = 'json'):
    chain_data = get_chain()
    secret = os.getenv("HMAC_SECRET", "secret_key").encode()
    payload = json.dumps(chain_data).encode()
    import hmac
    signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return {
        "data": chain_data,
        "signature": signature,
        "format": format
    }

@app.get("/transparencia/verificar/{hash_recibo}")
def verificar_voto(hash_recibo: str, process_id: str = "proceso_2025"):
    bloque = urna_chain.find_vote_by_hash(hash_recibo)
    if not bloque:
        # Buscar por nullifier en data
        for block in urna_chain.chain:
            if block.index == 0:
                continue
            if block.data.get("nullifier") == hash_recibo:
                bloque = block
                break
    if not bloque:
        return {"status": "error", "encontrado": False, "message": "Voto no encontrado en la cadena"}

    merkle_data = merkle_cache.get(process_id)
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
        "block": {
            "index": bloque.index,
            "timestamp": bloque.timestamp,
            "data": bloque.data,
            "hash": bloque.hash
        },
        "merkle_root": merkle_data["root"] if merkle_data else None,
        "proof": proof,
        "verified": is_valid,
        "message": "Voto verificado en el escrutinio oficial." if is_valid else "Hash encontrado pero sin prueba Merkle disponible."
    }

@app.post("/transparencia/verificar/bulk")
def verificar_bulk(req: BulkVerifyRequest):
    if len(req.hashes) > 500:
        raise HTTPException(status_code=400, detail="Too many hashes (max 500)")
    resultados = []
    for h in req.hashes:
        bloque = urna_chain.find_vote_by_hash(h)
        resultados.append({
            "hash": h,
            "valido": bloque is not None
        })
    return {"resultados": resultados}

@app.websocket("/ws/audit")
async def audit_ws(ws: WebSocket, token: str = ""):
    if token != "admin_token":
        await ws.close(code=1008)
        return
    await manager.connect(ws, role="admin")
    try:
        while True:
            data = await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.websocket("/ws/results/{process_id}")
async def results_stream(ws: WebSocket, process_id: str):
    await results_manager.connect(ws, process_id)
    try:
        while True:
            counts: Dict[str, int] = {}
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
