from typing import *

from rich.progress import track
from telethon import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class ChangeTwoStepPasswordFunc(BaseFunc):
    "Change 2FA"

    async def execute(self, accs: List[TelegramClient]):
        while True:
            password = self.c.input("[bold red]New 2FA Password > [/]")
            if password:
                break

        valid, inv = 0, 0
        for s in track(accs):
            try:
                await s(s.edit_2fa(new_password=password))
                valid += 1
            except Exception:
                inv += 1
        self.c.print(f"[red b] 2Fa set on {valid} accs! Errors with {inv} accs")
