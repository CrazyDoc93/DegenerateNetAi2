import os
from pathlib import Path
import shutil

from rich.prompt import Confirm


def on_startup(root: Path) -> None:
    """
    Create the directories for the project

    :param root: Path
    :type root: Path
    """
    for p in ["sessions", "loaded_sessions", "invalid_sessions", "assets"]:
        if not (root / p).is_dir():
            (root / p).mkdir()

    if len(os.listdir(root / "loaded_sessions")) > 0 and Confirm.ask(
        "[b red]Are you want to use loaded_accounts?[/]", default=True
    ):
        for f in os.listdir(root / "loaded_sessions"):
            shutil.move(root / "loaded_sessions" / f, root / "sessions" / f)
