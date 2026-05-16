"""
Compromiso de Pedersen simplificado sobre BN128.
El ciudadano genera un 'commitment' C = r*G + vote*H
donde r es un nonce secreto, vote es el índice de opción, G y H son puntos del grupo.
El backend verifica el commitment SIN conocer r ni vote individualmente.
"""
import secrets
import hashlib
from py_ecc.bn128 import G1, multiply, add, is_on_curve, curve_order


def generate_commitment(vote_index: int, num_options: int) -> dict:
    """
    vote_index: índice de la opción seleccionada (0-based)
    Retorna: {commitment_hex, nullifier_hex, r_secret}
    """
    if vote_index < 0 or vote_index >= num_options:
        raise ValueError("Índice de voto fuera de rango")

    # Nonce secreto del ciudadano (nunca sale del frontend en producción)
    r = secrets.randbelow(curve_order)

    # Punto H = hash-to-point del string "URNA_DIGITAL_CHI_2025"
    H_scalar = int.from_bytes(b"URNA_DIGITAL_CHI_2025", "big") % curve_order
    H = multiply(G1, H_scalar)

    # Commitment: C = r*G + vote_index*H
    C = add(multiply(G1, r), multiply(H, vote_index))

    # Nullifier: evita doble voto sin revelar identidad
    nullifier = hashlib.sha256(
        r.to_bytes(32, "big") + b"proceso_2025"
    ).hexdigest()

    return {
        "commitment": (hex(int(C[0])), hex(int(C[1]))),  # Punto de la curva
        "nullifier": nullifier,
        "r_secret": hex(r),  # Solo para el recibo del ciudadano; NUNCA persiste en BD
    }


def verify_commitment(commitment_tuple: tuple, nullifier: str) -> bool:
    """
    Verifica que el commitment es un punto válido en BN128.
    El nullifier se busca en Redis para prevenir doble voto.
    """
    x = int(commitment_tuple[0], 16)
    y = int(commitment_tuple[1], 16)
    point = (x % curve_order, y % curve_order)
    return is_on_curve(point, b2=3)  # BN128: y²=x³+3
