import secrets
import string


class PasswordGenerator:
    SPECIAL = "!@#$%^&*()-_=+"
    ALPHABET = string.ascii_letters + string.digits + SPECIAL
    MIN_LENGTH = 8

    @classmethod
    def generate(cls, length: int = 16) -> str:
        length = max(length, cls.MIN_LENGTH)
        while True:
            password = "".join(secrets.choice(cls.ALPHABET) for _ in range(length))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in cls.SPECIAL for c in password)
            ):
                return password
