import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import AdminUserModel
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {"sub": username, "exp": expire, "type": "admin"}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


async def authenticate(session: AsyncSession, username: str, password: str):
    result = await session.execute(
        select(AdminUserModel).where(AdminUserModel.username == username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def create_admin(session: AsyncSession, username: str, password: str):
    result = await session.execute(
        select(AdminUserModel).where(AdminUserModel.username == username)
    )
    if result.scalar_one_or_none():
        return None
    user = AdminUserModel(username=username, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def seed_default_admin(session: AsyncSession):
    result = await session.execute(select(AdminUserModel))
    if result.scalars().first() is None:
        user = AdminUserModel(username="IEE1", password_hash=hash_password("1234"))
        session.add(user)
        await session.commit()
