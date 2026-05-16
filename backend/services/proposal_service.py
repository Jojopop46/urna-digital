from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ProposalModel


async def get_proposals(session: AsyncSession, status: str = "approved"):
    query = select(ProposalModel).order_by(ProposalModel.id)
    if status != "all":
        query = query.where(ProposalModel.status == status)
    result = await session.execute(query)
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


_DEFAULT_PROPOSALS = [
    {
        "titulo": "Mejoramiento de alumbrado público en zonas rurales",
        "descripcion": "Instalación de luminarias LED solares en caminos rurales de difícil acceso para mejorar la seguridad nocturna y reducir accidentes.",
        "costo": "$2,400,000 MXN",
        "area": "Infraestructura",
        "municipio": "Chihuahua",
    },
    {
        "titulo": "Centro de salud digital para comunidades indígenas",
        "descripcion": "Telemedicina y consulta médica remota en comunidades rarámuri y tepehuana con conectividad satelital y personal capacitado.",
        "costo": "$1,800,000 MXN",
        "area": "Salud",
        "municipio": "Guachochi",
    },
    {
        "titulo": "Recolección de agua pluvial en escuelas primarias",
        "descripcion": "Sistemas de captación de agua de lluvia en 15 escuelas primarias rurales para garantizar abasto durante temporada de sequía.",
        "costo": "$950,000 MXN",
        "area": "Educación",
        "municipio": "Cuauhtémoc",
    },
]


async def seed_default_proposals(session: AsyncSession):
    result = await session.execute(select(ProposalModel))
    if result.scalars().first() is None:
        for data in _DEFAULT_PROPOSALS:
            proposal = ProposalModel(
                titulo=data["titulo"],
                descripcion=data["descripcion"],
                costo=data["costo"],
                area=data["area"],
                municipio=data["municipio"],
                status="approved",
            )
            session.add(proposal)
        await session.commit()
