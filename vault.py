import os
import secrets
from typing import Dict, Optional

from crypto_service import CryptoService
from expectetions import (
    AuthenticationError,
    Entry,
    EntryExistsError,
    EntryNotFoundError,
)


class Vault:
    def __init__(self, path: str = "vault.dat") -> None:
        self._path = path
        self._master_password: Optional[str] = None
        self._salt: Optional[bytes] = None
        self._entries: Dict[str, Entry] = {}

    def exists(self) -> bool:
        return os.path.exists(self._path)

    @property
    def entries(self) -> Dict[str, Entry]:
        return dict(self._entries)

    def create(self, master_password: str) -> None:
        self._master_password = master_password
        self._salt = CryptoService.generate_salt()
        self._entries = {}
        self._save()

    def unlock(self, master_password: str) -> None:
        with open(self._path, "rb") as file:
            raw = file.read()
        salt = raw[: CryptoService.SALT_SIZE]
        token = raw[CryptoService.SALT_SIZE :]
        data = CryptoService.decrypt(token, master_password, salt)
        self._entries = {name: Entry.from_dict(item) for name, item in data.items()}
        self._master_password = master_password
        self._salt = salt

    def _save(self) -> None:
        payload = {name: entry.to_dict() for name, entry in self._entries.items()}
        token = CryptoService.encrypt(payload, self._master_password, self._salt)
        with open(self._path, "wb") as file:
            file.write(self._salt + token)

    def add_entry(self, service: str, login: str, password: str) -> None:
        if service in self._entries:
            raise EntryExistsError(service)
        self._entries[service] = Entry(login, password)
        self._save()

    def get_entry(self, service: str) -> Entry:
        if service not in self._entries:
            raise EntryNotFoundError(service)
        return self._entries[service]

    def update_entry(self, service: str, login: str = "", password: str = "") -> None:
        entry = self.get_entry(service)
        if login:
            entry.login = login
        if password:
            entry.password = password
        self._save()

    def delete_entry(self, service: str) -> None:
        self.get_entry(service)
        del self._entries[service]
        self._save()

    def change_master_password(self, current: str, new: str) -> None:
        same = secrets.compare_digest(
            current.encode("utf-8"), self._master_password.encode("utf-8")
        )
        if not same:
            raise AuthenticationError("Неверный текущий мастер-пароль.")
        self._master_password = new
        self._salt = CryptoService.generate_salt()
        self._save()
