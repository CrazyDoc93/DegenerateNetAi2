from typing import *

from rich.progress import track
from telethon import TelegramClient, functions

from DegenerateNet.__base__ import BaseFunc


class ChangeBioFunc(BaseFunc):
    "Change bio"

    async def execute(self, accs: List[TelegramClient]):
        """
        It updates the bio of the account.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        bio = self.c.input("[bold red]Bio > [/]")
        for s in track(accs):
            await s(functions.account.UpdateProfileRequest(about=bio))
