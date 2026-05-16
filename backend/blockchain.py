import hashlib
import json
from time import time
import logging
from sqlalchemy import select
from database import async_session
from models import BlockModel
from crypto.block_signer import sign_block_payload, AUDITOR_PUBLIC_KEY


class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0, hash=None, signature="", auditor_pubkey=""):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()
        self.signature = signature
        self.auditor_pubkey = auditor_pubkey or AUDITOR_PUBLIC_KEY

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def payload_for_signing(self) -> str:
        """JSON canónico usado para la firma Ed25519."""
        return json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }, sort_keys=True)

    def sign(self):
        self.signature = sign_block_payload(self.payload_for_signing())
        self.auditor_pubkey = AUDITOR_PUBLIC_KEY

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "signature": self.signature,
            "auditor_pubkey": self.auditor_pubkey,
        }

    @classmethod
    def from_model(cls, model: BlockModel):
        return cls(
            index=model.index,
            timestamp=model.timestamp,
            data=model.data,
            previous_hash=model.previous_hash,
            nonce=model.nonce,
            hash=model.hash,
            signature=model.signature,
            auditor_pubkey=model.auditor_pubkey,
        )


class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self.difficulty = 2

    async def load_from_db(self):
        async with async_session() as session:
            result = await session.execute(select(BlockModel).order_by(BlockModel.index))
            blocks = result.scalars().all()
            if not blocks:
                genesis = self.create_genesis_block()
                session.add(BlockModel(**genesis.to_dict()))
                await session.commit()
                self.chain = [genesis]
            else:
                self.chain = [Block.from_model(b) for b in blocks]

    def create_genesis_block(self):
        genesis = Block(0, time(), "Bloque Genesis - Voz ciudadana", "0")
        genesis.sign()
        return genesis

    def get_latest_block(self):
        return self.chain[-1]

    async def add_block(self, data):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time(),
            data=data,
            previous_hash=previous_block.hash
        )
        self.mine_block(new_block)
        new_block.sign()
        async with async_session() as session:
            session.add(BlockModel(**new_block.to_dict()))
            await session.commit()
        self.chain.append(new_block)
        return new_block

    def mine_block(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        logging.info(f"Bloque minado: {block.hash}")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def is_chain_signatures_valid(self) -> bool:
        """Verifica que cada bloque tenga firma criptográfica válida del auditor."""
        from crypto.block_signer import verify_block_payload
        for block in self.chain:
            if not block.signature:
                return False
            if not verify_block_payload(block.payload_for_signing(), block.signature, block.auditor_pubkey):
                return False
        return True

    def find_vote_by_hash(self, tx_hash):
        for block in self.chain:
            if block.hash == tx_hash:
                return block
        return None
