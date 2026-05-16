from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.admin_service import authenticate, create_admin, create_access_token, seed_default_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/login")
async def login(data: dict, db: AsyncSession = Depends(get_db)):
    user = await authenticate(db, data.get("username", ""), data.get("password", ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/users")
async def create_user(data: dict, db: AsyncSession = Depends(get_db)):
    # Seed default admin si no existe
    await seed_default_admin(db)

    username = data.get("username", "")
    password = data.get("password", "")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Contraseña mínimo 4 caracteres")

    user = await create_admin(db, username, password)
    if not user:
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    return {"username": user.username, "message": "Usuario creado exitosamente"}
