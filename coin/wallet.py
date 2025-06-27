from ecdsa import SigningKey, SECP256k1
import hashlib

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = self.generate_address()

    def generate_address(self):
        pubkey_bytes = self.public_key.to_string()
        return hashlib.sha256(pubkey_bytes).hexdigest()

    def sign(self, message):
        return self.private_key.sign(message.encode()).hex()

    @staticmethod
    def verify_signature(public_key_hex, message, signature_hex):
        from ecdsa import VerifyingKey
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
            return vk.verify(bytes.fromhex(signature_hex), message.encode())
        except Exception:
            return False 