# noinspection PyInterpreter
import os
from pathlib import Path
from typing import *

from DegenerateNet.settings import (
    api_id,
    api_hash,
    device_model,
    system_version,
    app_version,
    lang_code,
    system_lang_code,
)
from rich.console import Console
from telethon import TelegramClient

# The BaseFunc class is a class that is used to define the base functions that are used by the other
# modules


class BaseFunc:
    def __init__(self):
        """
        Initializes the variables that will be used in the program
        """
        self.root: Path = Path(os.path.dirname(__file__)).parent
        self.modules: Path = self.root / "modules"
        self.assets: Path = self.root / "assets"
        self.sessions: Path = self.root / "sessions"
        self.api_id = api_id
        self.api_hash = api_hash
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version
        self.lang_code = lang_code
        self.system_lang_code = system_lang_code
        self.c: Console = Console()

    async def execute(self, accs: List[TelegramClient]):
        """
        It prints a message to the console.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        self.c.print("[b green]:hello: Hello from base![/]")
