import asyncio
import contextlib
from typing import *

from telethon import TelegramClient
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    JoinChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.messages import (
    CheckChatInviteRequest,
    ImportChatInviteRequest,
)
from DegenerateNet.__base__ import BaseFunc


class FloodFunc(BaseFunc):
    "Flood"

    async def join(self, session: TelegramClient, mode: str, link: str):
        if mode == "1":
            try:
                if "joinchat" in link:
                    invite = link.split("/")[-1]
                    await session(ImportChatInviteRequest(invite))
                elif "+" in link:
                    invite = link.split("+")[1]
                    await session(ImportChatInviteRequest(invite))
                else:
                    await session(JoinChannelRequest(link))
            except Exception as error:
                return self.c.print(f"[b red][-] {error}[/]")
            if "joinchat" in link:
                invite = link.split("/")[-1]
                return await session.get_entity(
                    (await session(CheckChatInviteRequest(invite))).chat
                )

            elif "+" in link:
                invite = link.split("+")[1]
                return await session.get_entity(
                    (await session(CheckChatInviteRequest(invite))).chat
                )

            else:
                return await session.get_entity(link)
        elif mode == "2":
            try:
                channel = await session(GetFullChannelRequest(link))
                chat = channel.chats[1]
                await session(JoinChannelRequest(chat))
            except Exception as error:
                return self.c.print(f"[b red][-] {error}[/]")
            return chat

    async def runner(
        self,
        s: TelegramClient,
        mode: str,
        channel_link: str,
        repeats: int,
        text: str,
        link: str,
        delay: int,
    ):
        chat = await self.join(s, mode, channel_link)
        for _ in range(repeats):
            try:
                if link and text:
                    await s.send_file(chat, link, caption=text)
                elif link:
                    await s.send_file(chat, link)
                elif text:
                    await s.send_message(chat, text)
                if delay:
                    await asyncio.sleep(delay)
            except Exception as e:
                self.c.print(f"[b red][ERR][/] {e}")
        with contextlib.suppress(Exception):
            await s(LeaveChannelRequest(chat))

    async def execute(self, accs: List[TelegramClient]):

        self.c.print(
            "[1] Chat / Channel",
            "[2] Linked to channel chat",
            sep="\n",
            style="bold white",
        )

        print()

        mode = self.c.input("[b red]Mode > [/]")

        channel_link = self.c.input("[bold red]Channel > [/]")
        text = self.c.input("[bold red]Text > [/]")
        link = self.c.input("[bold red]Link to media > [/]")
        repeats = int(self.c.input("[bold red]Repeats [1] > [/]") or 1)
        delay = int(self.c.input("[bold red]Delay for each account [0] > [/]") or 0)

        with self.c.status("[red b] Flooding..."):
            await asyncio.gather(
                *[
                    self.runner(s, mode, channel_link, repeats, text, link, delay)
                    for s in accs
                ]
            )
