import getpass
from typing import Dict

from expectetions import Entry


class ConsoleUI:
    MENU = (
        ("1", "Добавить запись"),
        ("2", "Показать список записей"),
        ("3", "Показать пароль записи"),
        ("4", "Изменить запись"),
        ("5", "Удалить запись"),
        ("6", "Сгенерировать пароль"),
        ("7", "Сменить мастер-пароль"),
        ("0", "Выход"),
    )

    def ask(self, prompt: str) -> str:
        return input(prompt).strip()

    def ask_secret(self, prompt: str) -> str:
        return getpass.getpass(prompt)

    def confirm(self, prompt: str) -> bool:
        return self.ask(prompt + " (д/н): ").lower() == "д"

    def say(self, message: str = "") -> None:
        print(message)

    def pause(self) -> None:
        input("\nНажмите Enter, чтобы продолжить...")

    def show_menu(self) -> None:
        self.say("=" * 35)
        self.say("      МЕНЕДЖЕР ПАРОЛЕЙ")
        self.say("=" * 35)
        for number, title in self.MENU:
            self.say(f"{number}. {title}")

    def show_table(self, entries: Dict[str, Entry]) -> None:
        self.say(f"\n{'Сервис':<20}{'Логин':<25}{'Пароль'}")
        self.say("-" * 55)
        for service, entry in entries.items():
            self.say(f"{service:<20}{entry.login:<25}{entry.masked_password}")
        self.say()