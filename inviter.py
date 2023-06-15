import asyncio
import random
from pathlib import Path
from typing import *

from DegenerateNet.__base__ import BaseFunc
from rich.prompt import Prompt
from telethon import TelegramClient, errors, functions, types
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


class InviterFunc(BaseFunc):
    "Inviter"

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

    async def execute(self, accs: List[TelegramClient], file: Union[Path, str] = None):
        """
        It takes a list of Telegram clients, and a list of users, and adds them to a channel

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        :return: Nothing.
        """
        session = random.choice(accs)
        users_list = None
        while True:
            try:
                users_list = [
                    i.split(";")
                    for i in (
                        self.assets
                        / (
                            file
                            or self.c.input("[b red]Users list (file in assets) > [/]")
                        )
                    )
                    .open("r", encoding="utf8")
                    .read()
                    .split("\n")
                ][1:]
                break
            except KeyboardInterrupt as e:
                raise KeyboardInterrupt from e
            except:
                pass
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
        while True:
            session = random.choice(accs)
            chat = await self.joinTo(session, link, mode)
            err = False
            for user in [i for i in users_list if i[3]]:
                #  0           1          2         3      4
                # id; first_name; last_name; username; phone
                try:
                    if type(chat) == types.Channel:
                        await session(
                            functions.channels.InviteToChannelRequest(
                                channel=chat, users=[await session.get_entity(user[3])]
                            )
                        )
                    else:
                        await session(
                            functions.messages.AddChatUserRequest(
                                chat_id=chat.id,
                                user_id=await session.get_entity(user[3]),
                                fwd_limit=50,
                            )
                        )
                    self.c.print(f"[b green][OK][/] @{user[3]}")
                    users_list.remove(user)
                    await asyncio.sleep(0.5)
                except errors.UserPrivacyRestrictedError:
                    self.c.print(f"[b yellow][WARN][/] @{user[3]} | Privacy-restricted")
                except errors.UserAlreadyParticipantError:
                    self.c.print(f"[b yellow][WARN][/] @{user[3]} | Already in chat")
                except errors.UserNotMutualContactError:
                    self.c.print(f"[b yellow][WARN][/] @{user[3]} | Not mutual contact")
                except errors.UserKickedError:
                    self.c.print(f"[b yellow][WARN][/] @{user[3]} | User was kicked")
                except errors.UserChannelsTooMuchError:
                    self.c.print(
                        f"[b yellow][WARN][/] @{user[3]} | Already in too many channels/supergroups"
                    )
                except (
                    errors.FloodError,
                    errors.FloodWaitError,
                    errors.PeerFloodError,
                    errors.RightForbiddenError,
                    errors.ChannelPrivateError,
                    errors.ChatWriteForbiddenError,
                    errors.UserBannedInChannelError,
                    errors.UserBannedInChannelError,
                ) as e:
                    try:
                        await session(LeaveChannelRequest(chat))
                    except:
                        pass
                    err = True
                except Exception as e:
                    self.c.print(f"[b red][ERR][/] @{user[3]} | {e}")
            if err:
                continue
            try:
                await session(LeaveChannelRequest(chat))
            except:
                pass
            break
