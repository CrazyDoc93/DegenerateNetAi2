import re
import shutil
from pathlib import Path
from typing import *

from rich.console import Console
from telethon import *
from telethon.sessions.string import StringSession

from DegenerateNet.settings import (
    api_hash,
    api_id,
    app_version,
    device_model,
    lang_code,
    system_lang_code,
    system_version,
)


class Loader:
    "Loads accounts from the `accounts` folder and stores them in the `loaded_sessions` folder."

    @staticmethod
    async def load_acc(c: Console, acc_path: str) -> str or None:
        s = re.sub(r"(\n|\r|\t)", "", open(acc_path, "r").read())
        s = TelegramClient(
            StringSession(s),
            api_id,
            api_hash,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
        )
        s.parse_mode = "html"
        try:
            await s.connect()
        except Exception:
            c.print("Account is dead!", style="red")
            p = Path(acc_path)
            shutil.move(p, p.parent.parent / "invalid_sessions" / p.name)
            return
        if await s.is_user_authorized():
            try:
                await s.get_me()
                await s.disconnect()
                p = Path(acc_path)
                shutil.move(p, p.parent.parent / "loaded_sessions" / p.name)
                return s
            except:
                c.print("Account is dead!", style="red")
                p = Path(acc_path)
                shutil.move(p, p.parent.parent / "invalid_sessions" / p.name)
                return
        else:
            p = Path(acc_path)
            shutil.move(p, p.parent.parent / "invalid_sessions" / p.name)
            c.print("Account is dead!", style="red")
            await s.disconnect()
