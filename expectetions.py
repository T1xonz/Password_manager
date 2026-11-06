from dataclasses import dataclass


class VaultError(Exception):
    pass


class AuthenticationError(VaultError):
    pass


class EntryNotFoundError(VaultError):
    pass


class EntryExistsError(VaultError):
    pass


@dataclass
class Entry:
    login: str
    password: str

    MASK = "*" * 8

    @property
    def masked_password(self) -> str:
        return self.MASK

    def to_dict(self) -> dict:
        return {"login": self.login, "password": self.password}

    @classmethod
    def from_dict(cls, data: dict) -> "Entry":
        return cls(login=data["login"], password=data["password"])
