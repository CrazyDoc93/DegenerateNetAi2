import contextlib
import random

from typing import *

from rich.progress import track
from telethon import TelegramClient, functions

from DegenerateNet.__base__ import BaseFunc


class ChangeUsernameFunc(BaseFunc):
    "Change username"

    async def execute(self, accs: List[TelegramClient]):
        nfile = self.c.input("[bold red]From file? (y/n) > ").lower()
        if nfile == "y":
            with (self.assets / "usernames.txt").open("r") as file:
                usernames = file.read().strip().splitlines()
        else:
            username = self.c.input("[bold red]Username > [/]").split()
        for c in track(accs):
            if nfile == "y":
                username = random.choice(usernames).split()
            elif not username:
                username = ["⁠"]
            username = username[0]
            with contextlib.suppress(Exception):
                await c(functions.account.UpdateUsernameRequest(username))
