import asyncio
import random
from typing import *

from telethon import TelegramClient
from telethon import functions
from DegenerateNet.__base__ import BaseFunc
from rich.progress import track


class ReactionsFunc(BaseFunc):
    "Reactions"

    async def execute(self, accs: List[TelegramClient]):
        fast = bool(self.c.input("Fast reactions? (y/n - enter) "))
        chat = self.c.input("[green]Chat > [/]")
        msg_id = int(self.c.input("[green]Message ID > [/]"))
        reactions = "👍 👎 ❤️ 🔥 🎉 🤩 😱 😁 😢 💩 🤮 🥰 🤯 🤔 🤬 👏".split()
        while True:
            for r in enumerate(reactions, 1):
                i, r = r
                self.c.print(f"[b white][{str(i).zfill(2)}][/] - {r}")
            choice = self.c.input("[b red]Reaction > [/]") or len(reactions)
            if (
                not choice
                or not choice.isdigit()
                or int(choice) <= 0
                or int(choice) > len(reactions)
            ):
                continue
            break
        reaction = reactions[int(choice) - 1]

        if fast:
            with self.c.status("Reacting..."):
                await asyncio.gather(
                    *[
                        acc(
                            functions.messages.SendReactionRequest(
                                chat, msg_id, reaction=reaction
                            )
                        )
                        for acc in accs
                    ]
                )
        else:
            for acc in track(accs):
                await acc(
                    functions.messages.SendReactionRequest(
                        chat, msg_id, reaction=reaction
                    )
                )
