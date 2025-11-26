from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings
import base64
import os

class EncryptionService:
    def __init__(self):
        # Ensure key is 32 bytes for AES-256
        # In production, this should be handled more robustly
        key_str = settings.APP_MASTER_KEY
        # Pad or truncate to 32 bytes if necessary for this demo
        # A real key should be exactly 32 bytes random
        if len(key_str) < 32:
            key_str = key_str.ljust(32, '0')
        elif len(key_str) > 32:
            key_str = key_str[:32]
        
        self.key = key_str.encode('utf-8')
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: bytes) -> bytes:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        nonce = ciphertext[:12]
        data = ciphertext[12:]
        return self.aesgcm.decrypt(nonce, data, None)

encryption_service = EncryptionService()
