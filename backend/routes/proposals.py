from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.proposal_service import get_proposals, create_proposal, update_proposal_status
from services.admin_service import decode_token

router = APIRouter(prefix="/api/v1/proposals", tags=["propuestas"])


def require_admin(authorization: str | None = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return payload


@router.get("")
async def list_proposals(status: str = "approved", db: AsyncSession = Depends(get_db)):
    proposals = await get_proposals(db, status=status)
    return [{"id": p.id, "titulo": p.titulo, "descripcion": p.descripcion,
             "costo": p.costo, "area": p.area, "municipio": p.municipio, "status": p.status}
            for p in proposals]


@router.get("/pending")
async def list_pending_proposals(
    db: AsyncSession = Depends(get_db),
    authorization: str | None = None
):
    require_admin(authorization)
    proposals = await get_proposals(db, status="pending")
    return [{"id": p.id, "titulo": p.titulo, "descripcion": p.descripcion,
             "costo": p.costo, "area": p.area, "municipio": p.municipio, "status": p.status}
            for p in proposals]


@router.post("")
async def submit_proposal(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("titulo") or not data.get("descripcion"):
        raise HTTPException(status_code=400, detail="Título y descripción son obligatorios")
    proposal = await create_proposal(db, data)
    return {"id": proposal.id, "status": "pending"}


@router.patch("/{proposal_id}")
async def patch_proposal(
    proposal_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = None
):
    require_admin(authorization)
    status_val = data.get("status")
    if status_val not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status debe ser 'approved' o 'rejected'")
    updated = await update_proposal_status(db, proposal_id, status_val)
    if not updated:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return {"id": updated.id, "status": updated.status}
