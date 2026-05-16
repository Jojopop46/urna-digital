"""
Firma criptográfica de bloques con Ed25519.

Objetivo: garantizar que cada bloque fue emitido por la autoridad auditora
y que cualquier tercero puede verificarlo sin confiar en el servidor.

La clave privada (AUDITOR_SECRET_KEY) debe ser generada fuera del servidor
y almacenada de forma segura (idealmente en un HSM o variable de entorno
con acceso restringido). La clave pública se publica para verificación.
"""
import os
import base64
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError


def _load_signing_key() -> SigningKey:
    """Carga la clave de firma desde env; si no existe, genera una nueva
    y loguea un WARNING (solo para desarrollo)."""
    raw = os.environ.get("AUDITOR_SECRET_KEY", "")
    if raw:
        # Soporta hex o base64
        try:
            seed = bytes.fromhex(raw)
        except ValueError:
            seed = base64.b64decode(raw)
        return SigningKey(seed)
    # Fallback: generar nueva (solo dev)
    sk = SigningKey.generate()
    os.environ["AUDITOR_SECRET_KEY"] = base64.b64encode(bytes(sk)).decode()
    return sk


_signing_key: SigningKey = _load_signing_key()

# Clave pública que debe distribuirse a verificadores
AUDITOR_PUBLIC_KEY: str = base64.b64encode(bytes(_signing_key.verify_key)).decode()


def sign_block_payload(payload_json: str) -> str:
    """Firma un string JSON (con sort_keys) y retorna signature base64."""
    signature = _signing_key.sign(payload_json.encode())
    # sign retorna message + signature; nos quedamos solo con la firma (últimos 64 bytes Ed25519)
    sig_bytes = signature.signature
    return base64.b64encode(sig_bytes).decode()


def verify_block_payload(payload_json: str, signature_b64: str, public_key_b64: str | None = None) -> bool:
    """Verifica que la firma corresponda al payload y a la clave pública del auditor."""
    try:
        pk_bytes = base64.b64decode(public_key_b64 or AUDITOR_PUBLIC_KEY)
        vk = VerifyKey(pk_bytes)
        sig = base64.b64decode(signature_b64)
        vk.verify(payload_json.encode(), sig)
        return True
    except (BadSignatureError, ValueError, TypeError):
        return False
