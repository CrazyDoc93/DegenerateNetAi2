import asyncio
from typing import *

from telethon import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class FloodCommentsFunc(BaseFunc):
    "Flood Comments"

    async def runner(
        self,
        s: TelegramClient,
        channel: str,
        repeats: int,
        text: str,
        link: str,
        pid: int,
        delay: int,
    ):
        for _ in range(repeats):
            try:
                if link and text:
                    await s.send_file(channel, link, caption=text, comment_to=pid)
                elif link:
                    await s.send_file(channel, link, comment_to=pid)
                elif text:
                    await s.send_message(channel, text, comment_to=pid)
                if delay:
                    await asyncio.sleep(delay)
            except Exception as e:
                self.c.print(f"[b red][ERR][/] {e}")

    async def execute(self, accs: List[TelegramClient]):

        channel = self.c.input("[bold red]Channel > [/]")
        pid = int(self.c.input("[bold red]Post ID > [/]"))
        text = self.c.input("[bold red]Text > [/]")
        link = self.c.input("[bold red]Link to media > [/]")
        repeats = int(self.c.input("[bold red]Repeats [1] > [/]") or 1)
        delay = int(self.c.input("[bold red]Delay for each account [0] > [/]") or 0)
        with self.c.status("[red b] Flooding..."):
            await asyncio.gather(
                *[
                    self.runner(s, channel, repeats, text, link, pid, delay)
                    for s in accs
                ]
            )
