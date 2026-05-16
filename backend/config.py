import sys
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret: str
    hmac_secret: str
    process_salt: str
    frontend_url: str = "http://localhost:3000"
    dev_mode: str = "0"
    rate_limit: str = "10/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Validaciones críticas en startup: abortar si los secretos son débiles o defaults
_errors = []
if len(settings.jwt_secret) < 32:
    _errors.append("JWT_SECRET debe tener al menos 32 caracteres")
if len(settings.hmac_secret) < 32:
    _errors.append("HMAC_SECRET debe tener al menos 32 caracteres")
if len(settings.process_salt) < 16:
    _errors.append("PROCESS_SALT debe tener al menos 16 caracteres")
if "default_salt" in settings.process_salt.lower() or "secret" in settings.jwt_secret.lower():
    _errors.append("Los secretos no pueden contener palabras por defecto como 'default_salt' o 'secret'")

if _errors:
    print("[FATAL] Configuración insegura detectada:", file=sys.stderr)
    for err in _errors:
        print(f"  - {err}", file=sys.stderr)
    sys.exit(1)
