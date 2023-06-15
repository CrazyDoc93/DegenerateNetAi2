import random
from typing import *

from rich.progress import track
from telethon import TelegramClient, functions

from DegenerateNet.__base__ import BaseFunc

# Change the name of all accounts in the list


class ChangeNameFunc(BaseFunc):
    "Change name"

    async def execute(self, accs: List[TelegramClient]):
        """
        This function will change the name of the account that is being used in the loop

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        nfile = self.c.input("[bold red]From file? (y/n) > ").lower()
        if nfile == "y":
            with (self.assets / "names.txt").open("r") as file:
                names = file.read().strip().splitlines()
        else:
            name = self.c.input("[bold red]Name > [/]").split()
        for c in track(accs):
            if nfile == "y":
                name = random.choice(names).split()
            elif not name:
                name = ["⁠"]
            first_name = name[0]
            last_name = name[1] if len(name) == 2 else ""
            try:
                await c(
                    functions.account.UpdateProfileRequest(
                        first_name=first_name, last_name=last_name
                    )
                )
            except:
                pass
