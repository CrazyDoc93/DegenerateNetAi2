import contextlib
import random
from typing import *

from rich.prompt import Confirm
from rich.table import Table
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
from modules.inviter import InviterFunc as inviter


class ParserFunc(BaseFunc):
    "Parser"

    async def execute(self, accs: List[TelegramClient]):
        """
        It joins a channel, gets all the users in that channel, and then leaves the channel

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        :return: Nothing.
        """
        session = random.choice(accs)
        chat = None
        self.c.print(
            "[1] Chat / Channel",
            "[2] Linked to channel chat",
            sep="\n",
            style="bold white",
        )

        print()

        mode = self.c.input("[b red]Mode > [/]")
        promote = Confirm.ask("[b red]Print username to promote to admin?[/]")
        link = self.c.input("[b red]Link > [/]")
        aggressive = Confirm.ask("[b red]Aggressive?[/]")
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
                chat = await session.get_entity(
                    (await session(CheckChatInviteRequest(invite))).chat
                )
            elif "+" in link:
                invite = link.split("+")[1]
                chat = await session.get_entity(
                    (await session(CheckChatInviteRequest(invite))).chat
                )
            else:
                chat = await session.get_entity(link)
        elif mode == "2":
            try:
                channel = await session(GetFullChannelRequest(link))
                chat = channel.chats[1]
                await session(JoinChannelRequest(chat))
            except Exception as error:
                return self.c.print(f"[b red][-] {error}[/]")
        data = ["id;first_name;last_name;username;phone"]
        me = await session.get_me()
        if promote:
            self.c.print(
                f"{me.username} | {me.id} | Promote it to admin and press `Enter`"
            )
            self.c.input()
        try:
            allusers = await session.get_participants(chat, aggressive=aggressive)
            deleted, bots = 0, 0
            t = Table()
            t.add_column("ID")
            t.add_column("First name")
            t.add_column("Last name")
            t.add_column("Username")
            t.add_column("Phone")
            for user in allusers:
                if user.deleted:
                    deleted += 1
                if user.bot:
                    bots += 1
                if not user.bot and not user.deleted and user.id != me.id:
                    if len(allusers) < 51:
                        t.add_row(str(user.id), str(user.first_name))
                    data.append(
                        f'{user.id};{user.first_name or ""};{user.last_name or ""};{user.username or ""};{user.phone or ""}'
                    )
            if len(allusers) < 51:
                self.c.print(t)
            self.c.print(f"[b green]Total users parsed:[/] {len(data)}")
            self.c.print(f"[b green]Total bots (not parsed):[/] {bots}")
            self.c.print(f"[b green]Total deleted accounts (not parsed):[/] {deleted}")
        except Exception as e:
            return self.c.print(f"[b red][-] {e}[/]")
        with contextlib.suppress(Exception):
            await session(LeaveChannelRequest(chat))
        path = self.c.input("[b red]Save to > [/]")
        path = self.assets / (path if path.endswith(".csv") else f"{path}.csv")
        path.open("w", encoding="utf8").write("\n".join(data))

        if Confirm.ask("[b red]Run Inviter?[/]"):
            i = inviter()
            await i.execute(accs, path)
