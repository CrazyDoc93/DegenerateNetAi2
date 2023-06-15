from typing import *

from telethon import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class SkeletonFunc(BaseFunc):
    "Skeleton of module"

    async def execute(self, accs: List[TelegramClient]):
        """
        It prints some information about the current module.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        self.c.print("Simple module")
        self.c.print("Available dirs:")
        self.c.print(f"self.root: {self.root}")
        self.c.print(f"self.assets: {self.assets}")
        self.c.print(f"self.modules: {self.modules}")
