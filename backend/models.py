from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, JSON, DateTime, func, Integer, Float


class Base(DeclarativeBase):
    pass


class BlockModel(Base):
    __tablename__ = "blocks"

    index: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    nonce: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)


class ProposalModel(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    costo: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    area: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    municipio: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)


class VoteReceiptModel(Base):
    __tablename__ = "vote_receipts"

    nullifier: Mapped[str] = mapped_column(String(64), primary_key=True)
    block_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    process_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AdminUserModel(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
