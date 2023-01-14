import os
import time
from typing import Sequence, Final

import discord
from discord.ext import tasks
import requests

POLL_FREQUENCY_SECONDS: Final = 60


class SOClient(discord.Client):
    def __init__(
            self,
            *,
            intents: discord.Intents,
            channel: int,
            tags: Sequence[str],
            start_epoch: int,
    ):
        super().__init__(intents=intents)

        self._tags: str = ";".join(tags)
        self._last_question_poll = start_epoch
        self._channel = channel

    async def setup_hook(self) -> None:
        self.poll_and_send.start()

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")

    @tasks.loop(seconds=POLL_FREQUENCY_SECONDS)
    async def poll_and_send(self) -> None:
        last_question_poll = int(time.time())
        response = requests.get(
            "https://api.stackexchange.com/2.3/questions",
            params={
                "site": "stackoverflow",
                "sort": "creation",
                "order": "asc",
                "tagged": self._tags,
                "min": str(self._last_question_poll),  # `str` to make mypy happy
            }
        )
        self._last_question_poll = last_question_poll

        channel = self.get_channel(self._channel)

        if channel is None:
            raise RuntimeError(f"Discord channel with ID {self._channel} not found.")

        for question in response.json()["items"]:
            print(question["title"])
            print(question["link"])

            await channel.send(  # type: ignore  # since we're copying the example
                f"""{question["title"]}\n{question["link"]}"""
            )

    @poll_and_send.before_loop
    async def before_task(self) -> None:
        await self.wait_until_ready()


discord_token: Final = os.getenv("DISCORD_TOKEN")

if discord_token is None:
    raise RuntimeError("Discord token required but not found.")


SOClient(
    intents=discord.Intents.default(),
    channel=0,
    tags=["idris"],
    start_epoch=int(time.time()),
).run(discord_token)
