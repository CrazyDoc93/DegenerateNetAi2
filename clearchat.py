import asyncio
from typing import *

from rich.prompt import Confirm
from telethon import TelegramClient, functions, types

from DegenerateNet.__base__ import BaseFunc


# Clear all dialogs in all accounts
class ClearDialogsFunc(BaseFunc):
    """Clear dialogs"""

    async def clear(self, s: TelegramClient):
        """
        Clear all dialogs and leave all channels

        :param s: TelegramClient: The client to use for the request
        :type s: TelegramClient
        """
        async for dialog in s.iter_dialogs():
            try:
                if not isinstance(dialog.entity, types.Channel):
                    await s(
                        functions.messages.DeleteHistoryRequest(
                            peer=dialog.entity, max_id=0, just_clear=True, revoke=True
                        )
                    )
                else:
                    await s(functions.channels.LeaveChannelRequest(dialog.id))
            except:
                pass

    async def execute(self, accs: List[TelegramClient]):
        """
        It deletes all the chats in the account.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        if Confirm.ask("[b red]Are you sure? [/]"):
            with self.c.status("[red]Deleting chats...[/]"):
                await asyncio.gather(*[self.clear(session) for session in accs])
