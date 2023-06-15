import asyncio
import os
from asyncio import sleep
from typing import *

import yaml
from telethon import TelegramClient, events as tl_events
from telethon.tl import types
from telethon.tl.functions.messages import SetTypingRequest

from DegenerateNet.__base__ import BaseFunc

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

auto_answer_config: dict
event_time: int
messages: List[Any]
events: List[Any]

number = {}

actions = {
    "type": types.SendMessageTypingAction,
    "audio": types.SendMessageRecordAudioAction,
    "document": types.SendMessageUploadDocumentAction,
    "photo": types.SendMessageUploadPhotoAction,
    "video": types.SendMessageUploadVideoAction,
    "round": types.SendMessageRecordRoundAction,
    "geo": types.SendMessageGeoLocationAction,
}


async def handler(event):
    peer = await event.get_sender()
    if event.chat_id not in number:
        action = actions[events[0]]
        try:
            await event.client(SetTypingRequest(
                peer=peer,
                action=action()
            ))
        except Exception as e:
            print(e)
        await sleep(event_time)
        try:
            await event.client(SetTypingRequest(
                peer=peer,
                action=types.SendMessageCancelAction()
            ))
        except Exception as e:
            print(e)
        await event.client.send_message(peer, messages[0])
        number[event.chat_id] = 1
    else:
        action = actions[events[number[event.chat_id]]]
        try:
            await event.client(SetTypingRequest(
                peer=peer,
                action=action()
            ))
        except Exception as e:
            print(e)
        await sleep(event_time)
        try:
            await event.client(SetTypingRequest(
                peer=peer,
                action=types.SendMessageCancelAction()
            ))
        except Exception as e:
            print(e)
        await event.client.send_message(peer, messages[number[event.chat_id]])
        number[event.chat_id] += 1
        if number[event.chat_id] == len(messages):
            return


class NewFunc(BaseFunc):
    "Auto-answer & Groups"

    async def groups(self, group: str, accs: List[TelegramClient], groups_config: Dict[str, Any]):
        timeout = groups_config["timeout"]
        for acc in accs:
            try:
                messages = await acc.get_messages(groups_config["channel"], reverse=True, min_id=1, limit=None)
                break
            except Exception as e:
                self.c.print(f"[b red][-] {e}[/]")
        for acc in accs:
            group = group.strip()
            for i in range(len(messages)):
                try:
                    await acc.send_message(group, messages[i])
                    messages.pop(i)
                    await asyncio.sleep(timeout)
                except Exception as e:
                    self.c.print(f"[b red][-] {e}[/]")

    async def auto_answer(self, s: TelegramClient, config: Dict[str, Any]):
        s.add_event_handler(handler, tl_events.NewMessage(func=lambda e: e.is_private, incoming=True))
        await s.run_until_disconnected()

    async def execute(self, accs: List[TelegramClient]):
        global auto_answer_config, event_time, messages, events

        with open(os.path.join("assets", "new", "config.yaml")) as file:
            config = yaml.load(file.read(), Loader=Loader)
            auto_answer_config = config["auto-answer"]
            event_time = auto_answer_config["event_time"]
            groups_config = config["groups"]

        if groups_config['working']:
            file_name = self.c.input("[b red]File name in assets folder> ")
            with open(os.path.join("assets", file_name)) as file:
                groups = file.readlines()

        with self.c.status("[red b] Working..."):
            if auto_answer_config['working']:
                for acc in accs:
                    try:
                        messages = await acc.get_messages(groups_config["channel"], reverse=True, min_id=1, limit=None)
                        break
                    except Exception as e:
                        self.c.print(f"[b red][-] {e}[/]")
                events = auto_answer_config["events"]
                await asyncio.gather(
                    *[
                        self.auto_answer(acc, auto_answer_config)
                        for acc in accs
                    ]
                )
            if groups_config['working']:
                await asyncio.gather(
                    *[
                        self.groups(group, accs, groups_config)
                        for group in groups
                    ]
                )
