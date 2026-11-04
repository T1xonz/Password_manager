import base64
import json
import secrets

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from expectetions import AuthenticationError


class CryptoService:
    SALT_SIZE = 16
    ITERATIONS = 480000

    @staticmethod
    def generate_salt() -> bytes:
        return secrets.token_bytes(CryptoService.SALT_SIZE)

    @staticmethod
    def _derive_key(master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=CryptoService.ITERATIONS,
        )
        key = kdf.derive(master_password.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    @staticmethod
    def encrypt(data: dict, master_password: str, salt: bytes) -> bytes:
        key = CryptoService._derive_key(master_password, salt)
        text = json.dumps(data, ensure_ascii=False)
        return Fernet(key).encrypt(text.encode("utf-8"))

    @staticmethod
    def decrypt(token: bytes, master_password: str, salt: bytes) -> dict:
        key = CryptoService._derive_key(master_password, salt)
        try:
            decrypted = Fernet(key).decrypt(token)
        except InvalidToken:
            raise AuthenticationError("Неверный мастер-пароль.")
        return json.loads(decrypted.decode("utf-8"))