import asyncio
import os
import random as rnd
import traceback
from pathlib import Path
from typing import *

import typer
from rich import traceback
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from telethon import *

from . import helpers
from .loader import Loader
from .modules import Modules
from .prestart import on_startup
from .settings import *

__docs__ = "Simple Telegram-Botnet with modules system"
__version__ = "3.0.1"

c = Console()
app = typer.Typer()
traceback.install()


def q() -> str:
    return c.input("[green]> [/]")


async def _main():  # sourcery no-metrics
    """
    It loads accounts from the `sessions` folder and runs the modules.
    """
    c.clear()
    c.print(f"DegenerateNet v{__version__}", style="green")
    _root = Path(os.path.dirname(__file__)).parent
    work_mode = None
    on_startup(_root)
    accs_list: List[str] = [
        os.path.join(_root, "sessions", i)
        for i in os.listdir(os.path.join(_root, "sessions"))
    ]
    rnd.shuffle(accs_list)
    c.print(
        f"How many account do you want to load? [Enter - {len(accs_list)}]",
        style="green",
    )
    while True:
        accs_count = q()
        try:
            accs_count = int(accs_count)
        except ValueError:
            break
        if accs_count > len(accs_list):
            c.print("Too many accounts!", style="red")
        elif accs_count == 0:
            work_mode = "utils"
            accs_list = []
            break
        elif accs_count < 0:
            c.print("Must be >= 0!", style="red")
        else:
            accs_list = accs_list[:accs_count]
            if len(accs_list) == 0:
                work_mode = "utils"
                accs_list = []
            break
    accs = []
    with c.status(f"[red]Loading {accs_count or len(accs_list)} accounts!"):
        for l in helpers.chunks(accs_list, 250):
            accs.extend(
                list(
                    filter(
                        lambda x: x is not None,
                        await asyncio.gather(*[Loader.load_acc(c, i) for i in l]),
                    )
                )
            )
    rnd.shuffle(accs)
    c.bell()
    c.print(f"[green]Loaded accounts: {len(accs)}[/]")
    if not work_mode:
        work_mode = Prompt.ask(
            "[b green]Choose mode[/]", choices=["modules", "utils"], default="modules"
        )
    while True:
        try:
            c.print(Markdown("-----"))
            mdls = Modules(os.path.join(_root, work_mode))
            mdls.load_modules()
            c.print(f"[b white]Accounts[/] > {len(accs)}")
            for i, v in enumerate(mdls.modules, 1):
                c.print(f"[white bold][{str(i).zfill(2)}][/] > [green]{v.name}[/]")
            choice = q().lower()
            if choice == "clear":
                c.clear()
                continue
            if not choice or not choice.isdigit():
                continue
            if choice == "0":
                work_mode = "modules" if work_mode == "utils" else "utils"
                c.print(f"[b green]>>> Switched to {work_mode}[/]")
                continue
            if int(choice) not in list(map(lambda x: x[0], enumerate(mdls.modules, 1))):
                c.print("[red bold][Error][/] [gray]Invalid module[/]")
                continue
            mod = mdls.modules[int(choice) - 1]
            c.print(f"[yellow]Running `{mod.name}` module[/]")
            try:
                await asyncio.gather(*[s.connect() for s in accs])
                await mod.instance().execute(accs)
                await asyncio.gather(*[s.disconnect() for s in accs])
            except KeyboardInterrupt:
                c.print(f"\n[red bold]Module `{mod.name}` is forcibly terminated![/]")
            except Exception as e:
                c.print(f"{type(e)} | {e}")
            else:
                c.print(f"[yellow]Module `{mod.name}` completed![/]")
            c.bell()
        except KeyboardInterrupt:
            c.print("[red bold]Exiting...[/]")
            exit(0)


@app.command()
def cli():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_main())
    loop.close()


@app.command()
def ui():
    from PySide6.QtWidgets import QApplication

    from .UI import activation

    app = QApplication()
    window = activation.win()
    window.show()
    app.exec()


if __name__ == "__main__":
    app()
