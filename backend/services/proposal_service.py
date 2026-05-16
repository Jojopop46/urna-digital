from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ProposalModel


async def get_proposals(session: AsyncSession, status: str = "approved"):
    result = await session.execute(
        select(ProposalModel).where(ProposalModel.status == status).order_by(ProposalModel.id)
    )
    return result.scalars().all()


async def get_proposal_by_id(session: AsyncSession, proposal_id: int):
    result = await session.execute(
        select(ProposalModel).where(ProposalModel.id == proposal_id)
    )
    return result.scalar_one_or_none()


async def create_proposal(session: AsyncSession, data: dict) -> ProposalModel:
    proposal = ProposalModel(
        titulo=data.get("titulo", ""),
        descripcion=data.get("descripcion", ""),
        costo=data.get("costo", ""),
        area=data.get("area", ""),
        municipio=data.get("municipio", ""),
        status="pending"
    )
    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)
    return proposal


async def update_proposal_status(session: AsyncSession, proposal_id: int, status: str):
    proposal = await get_proposal_by_id(session, proposal_id)
    if not proposal:
        return None
    proposal.status = status
    await session.commit()
    await session.refresh(proposal)
    return proposal
