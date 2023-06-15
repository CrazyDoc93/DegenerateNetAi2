import asyncio
from typing import *

from rich.prompt import Prompt
from telethon import TelegramClient, functions, types
from telethon.sync import TelegramClient

from DegenerateNet.__base__ import BaseFunc


class ReportFunc(BaseFunc):
    """Report"""

    def __init__(self):
        """
        The function creates a tuple of tuples. Each tuple contains a string and an InputReportReason
        object
        """
        super().__init__()

        self.reasons = (
            ("Child abuse", types.InputReportReasonChildAbuse()),
            ("Copyright", types.InputReportReasonCopyright()),
            ("Fake channel/account", types.InputReportReasonFake()),
            ("Pornography", types.InputReportReasonPornography()),
            ("Spam", types.InputReportReasonSpam()),
            ("Violence", types.InputReportReasonViolence()),
            ("Other", types.InputReportReasonOther()),
        )

    async def runner(
        self,
        s: TelegramClient,
        tip: str,
        link: str,
        reason_type,
        posts: list = None,
        comment: str = None,
    ):
        """
        This function is used to report a user or a channel

        :param s: The TelegramClient object
        :type s: TelegramClient
        :param tip: c or u
        :type tip: str
        :param link: The link of the channel or group you want to report
        :type link: str
        :param reason_type: The reason for reporting the user
        :param posts: List of post messages to report
        :type posts: list
        :param comment: The comment to be sent along with the report
        :type comment: str
        """
        if posts is None:
            posts = []
        me = await s.get_me()
        try:
            if tip == "c":
                await s(
                    functions.messages.ReportRequest(
                        peer=link, id=posts, reason=reason_type, message=comment
                    )
                )
            else:
                await s(
                    functions.account.ReportPeerRequest(
                        peer=link, reason=reason_type, message=comment
                    )
                )
        except Exception as err:
            self.c.print(
                "[{name}] [b red]Error > [/] {error}".format(
                    name=me.first_name, error=err
                )
            )

    async def execute(self, accs: List[TelegramClient]):
        """
        It runs the report function for each account in the list.

        :param accs: List[TelegramClient]
        :type accs: List[TelegramClient]
        """
        tip = Prompt.ask("Channel(Post|Message) / User ", choices=["c", "u"]).lower()
        link = Prompt.ask("[b red]Link > [/]")
        posts = None
        if tip == "c":
            posts = Prompt.ask(
                "[b red]Enter the message/post ids comma separated > [/]"
            )
            posts = [int(i) for i in posts.split(",")]

        while True:
            for index, reasons in enumerate(self.reasons):
                reason, _ = reasons

                self.c.print(f"[b white][{index + 1}] {reason}[/]")
            choice = self.c.input("[b red]>> [/]")
            if (
                not choice
                or not choice.isdigit()
                or int(choice) <= 0
                or int(choice) > len(self.reasons)
            ):
                continue
            break
        reason_type = self.reasons[int(choice) - 1][1]
        comment = self.c.input("[b red]Comment > [/]")

        with self.c.status("[b red] Reporting...[/]"):
            await asyncio.gather(
                *[self.runner(s, tip, link, reason_type, posts, comment) for s in accs]
            )
