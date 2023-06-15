import asyncio
import contextlib
import os
import random
from typing import *

import yaml
from telethon import TelegramClient

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from DegenerateNet.__base__ import BaseFunc


# It's a class that lets you create your own scenario
class ScenarioFunc(BaseFunc):
    "Свой сценарий"

    # Команды:
    # send - Отправить текст
    #   Аргумент - текст
    # sendfile - Отправить файл(caption supported)
    #   Аргумент - [ссылка на файл, подпись(не обязан)]
    # click - Нажать на кнопку в сообщении в буфере
    #   Аргумент - номер кнопки с 0
    # delay - Нажать на кнопку
    #   Аргумент - секунды (float)
    # wait_msg - Ожидать сообщение и поместить его в буфер
    #   Аргумент - None (да, это аргумент, а не нихуя)
    # wait_read - Ожидать прочтения ласт сообщения
    #   Аргумент - None (да, это аргумент, а не нихуя)

    start_actions = []
    actions = []
    end_actions = []
    repeats = 1

    async def cmd_exec(self, conv, cmd: str, args: list = None, m=None):
        """
        It takes a command and a list of arguments, and executes the command with the arguments

        :param conv: the conversation object
        :param cmd: The command to be executed
        :type cmd: str
        :param args: list = None, m = None
        :type args: list
        :param m: The message object that was sent
        :return: Nothing.
        """
        if cmd == "click":
            await m.click(args)
        elif cmd == "delay":
            await asyncio.sleep(args)
        elif cmd == "send":
            await conv.send_message(random.choice(args) if type(args) == list else args)
        elif cmd == "sendfile":
            await conv.send_file(
                args[0],
                caption=(
                    (random.choice(args[1]) if type(args[1]) == list else args[1])
                    if len(args) == 2
                    else None
                ),
            )
        elif cmd == "wait_msg":
            return await conv.get_response(timeout=300)
        elif cmd == "wait_read":
            await conv.wait_read(timeout=300)

    async def executor(self, s: TelegramClient, target: str):
        """
        The function is a loop that runs the number of times specified in the `repeats` variable.

        The loop will run the `start_actions` list first, then the `actions` list, and finally the
        `end_actions` list.

        The `actions` list is a list of tuples that contain the command and the arguments to be passed
        to the command.

        The `start_actions` and `end_actions` lists are the same, except the `start_actions` list is run
        before the loop and the `end_actions` list is run after the loop.

        The `cmd_exec` function is used to execute the commands.

        :param s: TelegramClient
        :type s: TelegramClient
        :param target: The target to send messages to
        :type target: str
        """
        m = None
        with contextlib.suppress(Exception):
            async with s.conversation(target) as conv:
                for cmd, args in self.start_actions:
                    with contextlib.suppress(Exception):
                        tmp = await self.cmd_exec(conv, cmd, args, m)
                        if tmp:
                            m = tmp
                for _ in range(self.repeats or int(10e100)):
                    try:
                        for cmd, args in self.actions:
                            tmp = await self.cmd_exec(conv, cmd, args, m)
                        if tmp:
                            m = tmp
                    except Exception as e:
                        self.c.print("[red b]new suicide bro..[/]")
                        self.c.print(e)
                for cmd, args in self.end_actions:
                    with contextlib.suppress(Exception):
                        tmp = await self.cmd_exec(conv, cmd, args, m)
                        if tmp:
                            m = tmp

    async def execute(self, accs: List[TelegramClient]):
        """
        It takes a list of Telegram clients, and a list of targets, and runs the scenario on each client
        for each target

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        targets = []
        scenarios = []
        while True:
            scenarios.clear()
            for i, scn in enumerate(
                (
                    self.assets / "scenario" / i
                    for i in os.listdir((self.assets / "scenario"))
                    if not i.startswith("__") and i.endswith(".yaml")
                ),
                1,
            ):
                s = yaml.load(scn.read_text("utf-8"), Loader=Loader)["scenario"]
                scenarios.append(s)
                self.c.print(f"[{i}] {s['name']}")
            choice = self.c.input("[b red]> [/]")
            if (
                not choice
                or not choice.isdigit()
                or int(choice) <= 0
                or int(choice) > len(scenarios)
            ):
                continue
            break
        scn = scenarios[int(choice) - 1]
        self.actions = scn["actions"]
        if "start_actions" in scn:
            self.start_actions = scn["start_actions"]
        if "end_actions" in scn:
            self.end_actions = scn["end_actions"]
        while True:
            if target := self.c.input("[red b]Chat/User [Enter - skip] > [/]"):
                targets.append(target)
            elif not targets:
                self.c.print("[red b]Enter minimum one shitty target[/]")
            else:
                break
        if "repeats" in scn:
            self.repeats = scn["repeats"]
        else:
            self.repeats = int(self.c.input("[red b]Repeats [1] > [/]") or 1)
        with self.c.status("[red]Running scenario...[/]"):
            while True:
                await asyncio.gather(
                    *[
                        self.executor(acc, t)
                        for acc, t in zip(accs, (targets * len(accs))[: len(accs)])
                    ]
                )
                if self.repeats != 0:
                    break
