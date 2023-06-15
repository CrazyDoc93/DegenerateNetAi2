import asyncio
from time import perf_counter
from typing import *

from rich.progress import track
from rich.prompt import Confirm, Prompt
from telethon import TelegramClient, events, types
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from DegenerateNet.__base__ import BaseFunc

# It joins a Telegram account to a channel or chat


class JoinerFunc(BaseFunc):
    "Joiner"

    async def join(self, session, link, index, mode):
        """
        It joins a channel or group.

        :param session: The client session
        :param link: The invite link or the chat ID
        :param index: The index of the account in the list
        :param mode: 1 = Join a channel, 2 = Join a supergroup
        :return: Nothing.
        """
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
                self.c.print(f"[-] [acc {index + 1}] {error}")
            else:
                return True

        elif mode == "2":
            try:
                channel = await session(GetFullChannelRequest(link))
                chat = channel.chats[1]
                await session(JoinChannelRequest(chat))
            except Exception as error:
                self.c.print(f"[-] [acc {index + 1}] {error}")
            else:
                return True

    async def solve_captcha(self, session: TelegramClient):
        """
        It adds a handler to the client that will be called whenever a new message is received.

        :param session: The TelegramClient instance that will be used to send messages and wait for the
        response
        :type session: TelegramClient
        """
        session.add_event_handler(self.on_message, events.NewMessage)

        await session.run_until_disconnected()

    async def on_message(self, msg: types.Message):
        """
        If the message is mentioned and it has a reply markup, then click the first button in the reply
        markup

        :param msg: The message object that was sent by the user
        :type msg: types.Message
        """
        if msg.mentioned and msg.reply_markup:
            captcha = msg.reply_markup.rows[0].buttons[0].data.decode("utf-8")

            await msg.click(data=captcha)

    async def execute(self, accs: List[TelegramClient]):
        """
        It joins a group or channel.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        self.c.print(
            "[1] Chat / Channel",
            "[2] Linked to channel chat",
            sep="\n",
            style="bold white",
        )

        print()

        mode = self.c.input("[b red]Mode > [/]")
        link = self.c.input("[b red]Link > [/]")

        speed = Prompt.ask("[bold red]Speed > [/]", choices=["normal", "fast"])

        joined = 0

        if speed == "normal":
            delay = Prompt.ask("[b red]Delay [0] > [/]", default="0")
            captcha = Confirm.ask("[b red]Captcha [false] > [/]")

            start = perf_counter()

            for index, session in track(
                enumerate(accs), "[yellow b]Joining... [/]", total=len(accs)
            ):

                if captcha:
                    asyncio.create_task(self.solve_captcha(session))

                is_joined = await self.join(session, link, index, mode)

                if is_joined:
                    joined += 1

                await asyncio.sleep(int(delay))

        if speed == "fast":
            with self.c.status("[red b]Joining...[/]"):
                start = perf_counter()

                tasks = await asyncio.gather(
                    *[
                        self.join(session, link, index, mode)
                        for index, session in enumerate(accs)
                    ]
                )

            for result in tasks:
                if result:
                    joined += 1

        joined_time = round(perf_counter() - start, 2)
        self.c.print(f"[+] {joined} bots joined in [yellow]{joined_time}[/]s")
