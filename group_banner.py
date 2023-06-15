import asyncio
import math
import random
import string
from typing import *

from DegenerateNet.__base__ import BaseFunc
from rich.prompt import Prompt
from telethon import TelegramClient, errors, events, functions, types
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    JoinChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.messages import (
    CheckChatInviteRequest,
    ImportChatInviteRequest,
)


class GroupBannerFunc(BaseFunc):
    "GroupBanner"

    def chunker(self, lst, c_num):
        """
        Given a list and a number, return a list of lists where each sublist is of length n

        :param lst: the list to be split
        :param c_num: The number of chunks you want to split the data into
        """
        n = math.ceil(len(lst) / c_num)

        for x in range(0, len(lst), n):
            yield lst[x : n + x]

    async def joinTo(self, session, link: str, mode: str) -> Any:
        """
        The joinTo function is used to join a channel or a group using a link. It takes in a session,
        a link and a mode. The mode is used to specify if the link is a channel or a group. The function
        returns the chat object of the channel or group that was joined.

        :param session: The client session
        :param link: The link to join the chat
        :type link: str
        :param mode: 1 = Join a channel, 2 = Join a supergroup
        :type mode: str
        :return: The chat object.
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
            except errors.UserAlreadyParticipantError:
                pass
            except Exception as error:
                self.c.print(f"[b red][-] {error}[/]")
                raise Exception from error
            if "joinchat" in link:
                invite = link.split("/")[-1]
                chat = await session.get_entity(
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
                return chat
            except errors.UserAlreadyParticipantError:
                pass
            except Exception as error:
                self.c.print(f"[b red][-] {error}[/]")
                raise Exception from error

    async def getSetUsernameAndSettings(self, acc: TelegramClient) -> str:
        me = await acc.get_me()
        await acc(
            functions.account.SetPrivacyRequest(
                key=types.InputPrivacyKeyChatInvite(),
                rules=[types.InputPrivacyValueAllowAll()],
            )
        )
        if not (username := me.username):
            username = "".join([random.choice(string.ascii_letters) for _ in range(32)])
            await acc(functions.account.UpdateUsernameRequest(username))
        return username

    async def reportOnInvite(self, event) -> None:
        if event.user_added:
            client = event.client
            try:
                await client(
                    functions.account.ReportPeerRequest(
                        event.chat, types.InputReportReasonSpam(), ""
                    )
                )
                self.c.print("[b green][OK][/] Reported chat")
            except Exception as e:
                self.c.print(f"[b red][ERR][/] {e}")
            try:
                await client(LeaveChannelRequest(event.chat))
                self.c.print("[b green][OK][/] Leaved")
            except Exception as e:
                self.c.print(f"[b red][ERR][/] {e}")
            raise events.StopPropagation

    async def hyperInvite(self, session: TelegramClient, chat, user):
        try:
            if type(chat) == types.Channel:
                await session(
                    functions.channels.InviteToChannelRequest(
                        channel=chat, users=[await session.get_entity(user)]
                    )
                )
            else:
                await session(
                    functions.messages.AddChatUserRequest(
                        chat_id=chat.id,
                        user_id=await session.get_entity(user),
                        fwd_limit=50,
                    )
                )
            self.c.print(f"[b green][OK][/] @{user}")
            await asyncio.sleep(0.5)
        except errors.UserPrivacyRestrictedError:
            self.c.print(f"[b yellow][WARN][/] @{user} | Privacy-restricted")
        except errors.UserAlreadyParticipantError:
            self.c.print(f"[b yellow][WARN][/] @{user} | Already in chat")
        except errors.UserNotMutualContactError:
            self.c.print(f"[b yellow][WARN][/] @{user} | Not mutual contact")
        except errors.UserKickedError:
            self.c.print(f"[b yellow][WARN][/] @{user} | User was kicked")
        except errors.UserChannelsTooMuchError:
            self.c.print(
                f"[b yellow][WARN][/] @{user} | Already in too many channels/supergroups"
            )
        except Exception as e:
            self.c.print(f"[b red][ERR][/] @{user} | {e}")
        try:
            await session(LeaveChannelRequest(chat))
        except Exception as e:
            self.c.print(f"[b red][ERR][/] Inviter can't leave chat | {e}")

    async def wrapper(self, i, link, mode, username):
        await self.hyperInvite(i, await self.joinTo(i, link, mode), username)

    async def execute(self, accs: List[TelegramClient]):
        inviters, reporters = self.chunker(accs, 2)
        self.c.print(f"[red b]Inviters:[/] {len(inviters)}")
        self.c.print(f"[red b]Reporters:[/] {len(reporters)}")
        usernames_of_reporters = await asyncio.gather(
            *[self.getSetUsernameAndSettings(i) for i in reporters]
        )
        # Add handler to report on invite
        [
            client.add_event_handler(self.reportOnInvite, events.ChatAction)
            for client in reporters
        ]
        for client in reporters:
            asyncio.create_task(client.run_until_disconnected())
        self.c.print(usernames_of_reporters)

        self.c.print("[b red] Select mode[/]")
        self.c.print(
            "[1] Chat / Channel",
            "[2] Linked to channel chat",
            sep="\n",
            style="bold white",
        )

        print()

        mode = Prompt.ask("[b red]Mode > [/]", choices=["1", "2"], default="1")
        link = self.c.input("[b red]Link > [/]")

        joined_chats_of_inviters = await asyncio.gather(
            *[self.joinTo(i, link, mode) for i in inviters]
        )
        await asyncio.gather(
            *[
                self.hyperInvite(i[0], i[1], i[2])
                for i in zip(inviters, joined_chats_of_inviters, usernames_of_reporters)
            ]
        )
