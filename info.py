import asyncio
from typing import *

from rich.table import Table
from telethon import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class InfoFunc(BaseFunc):
    "Info table"

    async def runner(self, s: TelegramClient):
        """
        It gets the information of the user.

        :param s: The TelegramClient object
        :type s: TelegramClient
        :return: The user's ID, first name, last name, username, and phone number.
        """
        me = await s.get_me()
        return (
            str(me.id),
            me.first_name or "",
            me.last_name or "",
            me.username or "",
            me.phone or "",
        )

    async def execute(self, accs: List[TelegramClient]):
        """
        It creates a table with the information of the accounts.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        table = Table(title="Accounts info", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("FName")
        table.add_column("LName")
        table.add_column("Username")
        table.add_column("Phone")
        with self.c.status("[red b]Creating table...[/]"):
            for id, first_name, last_name, username, phone in await asyncio.gather(
                *[self.runner(c) for c in accs]
            ):
                table.add_row(
                    id, first_name or "", last_name or "", username or "", phone or ""
                )
        self.c.print(table)
