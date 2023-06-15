import contextlib
from typing import *

from rich.markup import escape
from rich.progress import track
from telethon import TelegramClient, functions

from DegenerateNet.__base__ import BaseFunc

# Vote poll


class VotePollFunc(BaseFunc):
    "Vote poll"

    async def execute(self, accs: List[TelegramClient]):
        """
        It sends a vote to a chat

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        chat = self.c.input("[green]Chat: [/]")
        with contextlib.suppress(Exception):
            chat = int(chat)
        mid = int(self.c.input("[green]Message id: [/]"))
        ans = [self.c.input("[green]Answer: [/]").encode("utf-8")]
        for acc in track(accs, "[b red]Voting...[/]"):
            try:
                await acc(
                    functions.messages.SendVoteRequest(
                        peer=chat, msg_id=mid, options=ans
                    )
                )
            except Exception as e:
                self.c.print(f"[red]Error[/]: [grey]{escape(str(e))}[/]")
