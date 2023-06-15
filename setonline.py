import asyncio
from typing import *

from telethon import TelegramClient, functions

from DegenerateNet.__base__ import BaseFunc


# Set online status
class SetOnlineFunc(BaseFunc):
    "Set online status"

    async def runner(self, s: TelegramClient, online: bool):
        """
        It changes the status of the bot.

        :param s: The TelegramClient instance
        :type s: TelegramClient
        :param online: Whether the account should be online or offline
        :type online: bool
        """
        await s(functions.account.UpdateStatusRequest(offline=not online))
        me = await s.get_me()
        self.c.print(
            f'[[{"green" if online else "red"}]{me.id}[/]] {"Online" if online else "Offline"}'
        )

    async def execute(self, accs: List[TelegramClient]):
        """
        It runs the main function for each account in the list.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        online = bool(self.c.input("[red b]Online[any str] / Offline[enter] > [/]"))
        await asyncio.gather(*[self.runner(c, online) for c in accs])
