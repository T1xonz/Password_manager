import pytest

from expectetions import AuthenticationError, EntryExistsError, EntryNotFoundError
from Generate_paasword import PasswordGenerator
from vault import Vault


@pytest.mark.parametrize(
    ("requested_length", "expected_length"), [(None, 16), (2, 8), (24, 24)]
)
def test_generate_password(requested_length, expected_length):
    password = (
        PasswordGenerator.generate()
        if requested_length is None
        else PasswordGenerator.generate(requested_length)
    )

    assert len(password) == expected_length
    assert set(password) <= set(PasswordGenerator.ALPHABET)
    assert any(char.islower() for char in password)
    assert any(char.isupper() for char in password)
    assert any(char.isdigit() for char in password)
    assert any(char in PasswordGenerator.SPECIAL for char in password)


def test_vault_persists_changes(tmp_path):
    path = tmp_path / "vault.dat"
    vault = Vault(path)
    assert not vault.exists()
    vault.create("мастер-пароль")
    assert vault.exists()
    vault.add_entry("почта", "пользователь", "пароль-сервиса")
    assert "пароль-сервиса".encode() not in path.read_bytes()

    with pytest.raises(EntryExistsError):
        vault.add_entry("почта", "другой логин", "другой пароль")

    vault.update_entry("почта", login="новый логин")
    reopened = Vault(path)
    reopened.unlock("мастер-пароль")
    entry = reopened.get_entry("почта")
    assert entry.login == "новый логин"
    assert entry.password == "пароль-сервиса"
    assert entry.masked_password == "********"

    reopened.delete_entry("почта")
    vault.unlock("мастер-пароль")
    assert vault.entries == {}
    with pytest.raises(EntryNotFoundError):
        vault.get_entry("почта")


def test_change_master_password(tmp_path):
    path = tmp_path / "vault.dat"
    vault = Vault(path)
    vault.create("старый пароль")
    vault.add_entry("почта", "логин", "пароль-сервиса")
    original_bytes = path.read_bytes()

    with pytest.raises(AuthenticationError):
        vault.change_master_password("неверный пароль", "новый пароль")
    assert path.read_bytes() == original_bytes

    vault.change_master_password("старый пароль", "новый пароль")
    reopened = Vault(path)
    with pytest.raises(AuthenticationError):
        reopened.unlock("старый пароль")

    reopened.unlock("новый пароль")
    assert reopened.get_entry("почта").password == "пароль-сервиса"
