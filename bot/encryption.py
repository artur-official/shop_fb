import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """AES-256-GCM encryption for sensitive data"""
    
    def __init__(self, key: str):
        if len(key) != 32:
            raise ValueError(f"Key must be 32 characters, got {len(key)}")
        
        self.key = key.encode('utf-8')
        self.aesgcm = AESGCM(self.key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypts string, returns base64"""
        if not plaintext:
            return ""
        
        try:
            nonce = os.urandom(12)
            ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            encrypted = base64.b64encode(nonce + ciphertext).decode('utf-8')
            return encrypted
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypts base64 string"""
        if not encrypted:
            return ""
        
        try:
            data = base64.b64decode(encrypted.encode('utf-8'))
            nonce = data[:12]
            ciphertext = data[12:]
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: dict) -> dict:
        """Encrypts login, password, cookies, two_fa fields"""
        encrypted = data.copy()
        sensitive_fields = ['login', 'password', 'cookies', 'two_fa']
        
        for field in sensitive_fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encrypt(str(encrypted[field]))
        
        return encrypted
    
    def decrypt_dict(self, data: dict) -> dict:
        """Decrypts login, password, cookies, two_fa fields"""
        decrypted = data.copy()
        sensitive_fields = ['login', 'password', 'cookies', 'two_fa']
        
        for field in sensitive_fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = self.decrypt(decrypted[field])
                except Exception:
                    pass
        
        return decrypted