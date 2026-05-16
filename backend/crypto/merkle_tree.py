import hashlib
from typing import Optional


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class MerkleTree:
    def __init__(self, leaves: list[str]):
        """leaves: lista de hashes de votos individuales."""
        if not leaves:
            raise ValueError("El árbol no puede estar vacío")
        # Si número impar, duplicar el último (estándar Bitcoin)
        self.leaves = leaves if len(leaves) % 2 == 0 else leaves + [leaves[-1]]
        self.tree = self._build()

    def _build(self) -> list[list[str]]:
        tree = [self.leaves[:]]
        while len(tree[-1]) > 1:
            level = tree[-1]
            next_level = []
            for i in range(0, len(level), 2):
                combined = sha256(level[i] + level[i + 1])
                next_level.append(combined)
            if len(next_level) % 2 != 0 and len(next_level) > 1:
                next_level.append(next_level[-1])
            tree.append(next_level)
        return tree

    @property
    def root(self) -> str:
        return self.tree[-1][0]

    def get_proof(self, leaf_index: int) -> list[dict]:
        """Genera la prueba de inclusión para el voto en leaf_index."""
        proof = []
        idx = leaf_index
        for level in self.tree[:-1]:
            sibling_idx = idx + 1 if idx % 2 == 0 else idx - 1
            sibling_idx = min(sibling_idx, len(level) - 1)
            direction = "right" if idx % 2 == 0 else "left"
            proof.append({"hash": level[sibling_idx], "direction": direction})
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list[dict], root: str) -> bool:
        """Verifica que leaf_hash pertenece al árbol con la raíz dada."""
        current = leaf_hash
        for step in proof:
            if step["direction"] == "right":
                current = sha256(current + step["hash"])
            else:
                current = sha256(step["hash"] + current)
        return current == root
