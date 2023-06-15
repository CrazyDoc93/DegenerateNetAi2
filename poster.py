import asyncio
from dataclasses import dataclass
from typing import *

from telethon import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class PosterFunc(BaseFunc):
    "Poster"

    @dataclass
    class UserCSV:
        user_id: int
        first_name: str
        last_name: str or None
        username: str or None

    def to_user(self, user: list):
        return self.UserCSV(
            user_id=int(user[0]),
            first_name=user[1],
            last_name=user[2] or None,
            username=user[3] or None,
        )

    async def runner(
        self,
        s: TelegramClient,
        to: UserCSV,
    ):
        me = await s.get_me()
        try:
            send_to = to.username or to.user_id
            if self.link and self.text:
                await s.send_file(send_to, self.link, caption=self.text)
            elif self.link:
                await s.send_file(send_to, self.link)
            elif self.text:
                await s.send_message(send_to, self.text)
            self.c.print(f"[b green][{me.id}] Успешно отправлено {send_to}[/]")
        except Exception as e:
            self.c.print(f"[b red][ERR][/] {e}")

    async def execute(self, accs: List[TelegramClient], file: str = None):
        users_list = list(
            map(
                self.to_user,
                [
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
                ][1:],
            )
        )

        while True:
            choice = self.c.input(f"[b red]Count [{len(users_list)}] > [/]") or len(
                users_list
            )
            if (
                not choice
                or not choice.isdigit()
                or int(choice) <= 0
                or int(choice) > len(users_list)
            ):
                continue
            break
        users_list = users_list[: int(choice)]
        self.text = self.c.input("[b red]Text > [/]")
        self.link = self.c.input("[b red]Link > [/]")

        self.c.print(f"[b green]{len(users_list)} users[/]")
        await asyncio.gather(
            *[
                self.runner(acc, t)
                for t, acc in zip(
                    users_list, (accs * len(users_list))[: len(users_list)]
                )
            ]
        )
