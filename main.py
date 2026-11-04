import sys

from console import ConsoleUI
from expectetions import AuthenticationError, EntryExistsError, EntryNotFoundError
from Generate_paasword import PasswordGenerator
from vault import Vault


class PasswordManagerApp:
    MAX_ATTEMPTS = 3
    MIN_MASTER_LENGTH = 8

    def __init__(self, vault: Vault, ui: ConsoleUI) -> None:
        self._vault = vault
        self._ui = ui
        self._actions = {
            "1": self._add_entry,
            "2": self._list_entries,
            "3": self._show_entry,
            "4": self._update_entry,
            "5": self._delete_entry,
            "6": self._generate_password,
            "7": self._change_master_password,
        }

    def run(self) -> None:
        if self._vault.exists():
            self._login()
        else:
            self._first_run()

        while True:
            self._ui.show_menu()
            choice = self._ui.ask("Выберите пункт: ")
            if choice == "0":
                self._ui.say("До свидания!")
                break
            action = self._actions.get(choice)
            if action is None:
                self._ui.say("Неверный пункт меню.")
            else:
                try:
                    action()
                except EntryNotFoundError:
                    self._ui.say("Запись не найдена.")
                except EntryExistsError:
                    self._ui.say("Такая запись уже есть. Используйте пункт 'Изменить'.")
                except AuthenticationError as error:
                    self._ui.say(str(error))
            self._ui.pause()

    def _ask_new_master_password(self) -> str:
        while True:
            password = self._ui.ask_secret("Придумайте мастер-пароль: ")
            if len(password) < self.MIN_MASTER_LENGTH:
                self._ui.say(f"Пароль слишком короткий (минимум {self.MIN_MASTER_LENGTH} символов).")
                continue
            if password != self._ui.ask_secret("Повторите мастер-пароль: "):
                self._ui.say("Пароли не совпадают, попробуйте ещё раз.")
                continue
            return password

    def _first_run(self) -> None:
        self._ui.say("Хранилище не найдено. Создаём новое.")
        self._vault.create(self._ask_new_master_password())
        self._ui.say("Хранилище создано!\n")

    def _login(self) -> None:
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            password = self._ui.ask_secret("Введите мастер-пароль: ")
            try:
                self._vault.unlock(password)
                self._ui.say("Вход выполнен!\n")
                return
            except AuthenticationError:
                left = self.MAX_ATTEMPTS - attempt
                self._ui.say(f"Неверный пароль. Осталось попыток: {left}")
        self._ui.say("Превышено число попыток. Программа закрывается.")
        sys.exit(1)

    def _add_entry(self) -> None:
        service = self._ui.ask("Название сервиса (например, gmail): ")
        if not service:
            self._ui.say("Название не может быть пустым.")
            return
        login = self._ui.ask("Логин: ")
        if self._ui.confirm("Сгенерировать пароль автоматически?"):
            password = PasswordGenerator.generate()
            self._ui.say(f"Сгенерирован пароль: {password}")
        else:
            password = self._ui.ask_secret("Пароль (ввод скрыт): ")
        self._vault.add_entry(service, login, password)
        self._ui.say("Запись добавлена.")

    def _list_entries(self) -> None:
        entries = self._vault.entries
        if not entries:
            self._ui.say("Хранилище пусто.")
            return
        self._ui.show_table(entries)

    def _show_entry(self) -> None:
        service = self._ui.ask("Название сервиса: ")
        entry = self._vault.get_entry(service)
        self._ui.say(f"Логин: {entry.login}")
        self._ui.say(f"Пароль: {entry.password}")

    def _update_entry(self) -> None:
        service = self._ui.ask("Название сервиса для изменения: ")
        self._vault.get_entry(service)
        login = self._ui.ask("Новый логин (Enter - оставить прежний): ")
        password = self._ui.ask_secret("Новый пароль (Enter - оставить прежний): ")
        self._vault.update_entry(service, login, password)
        self._ui.say("Запись обновлена.")

    def _delete_entry(self) -> None:
        service = self._ui.ask("Название сервиса для удаления: ")
        self._vault.get_entry(service)
        if self._ui.confirm(f"Точно удалить '{service}'?"):
            self._vault.delete_entry(service)
            self._ui.say("Запись удалена.")
        else:
            self._ui.say("Удаление отменено.")

    def _generate_password(self) -> None:
        try:
            length = int(self._ui.ask("Длина пароля (по умолчанию 16): ") or 16)
        except ValueError:
            length = 16
        self._ui.say(f"Пароль: {PasswordGenerator.generate(length)}")

    def _change_master_password(self) -> None:
        current = self._ui.ask_secret("Введите текущий мастер-пароль: ")
        new = self._ask_new_master_password()
        self._vault.change_master_password(current, new)
        self._ui.say("Мастер-пароль изменён.")


def main() -> None:
    app = PasswordManagerApp(Vault(), ConsoleUI())
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")