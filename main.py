import logging
import os
import time
from collections.abc import Iterable
from typing import Final

import discord
from discord.ext import tasks
import requests

POLL_FREQUENCY_SECONDS: Final = 60

log = logging.getLogger(__name__)


class SOClient(discord.Client):
    def __init__(
            self,
            *,
            intents: discord.Intents,
            channel: int,
            tags: Iterable[str],
            start_epoch: int,
    ):
        super().__init__(intents=intents)

        self._tags: str = ";".join(tags)
        self._last_question_poll = start_epoch
        self._channel = channel

    async def setup_hook(self) -> None:
        self.poll_and_send.start()

    async def on_ready(self) -> None:
        log.info(f"Logged in as {self.user}")

    @tasks.loop(seconds=POLL_FREQUENCY_SECONDS)
    async def poll_and_send(self) -> None:
        channel = self.get_channel(self._channel)

        last_question_poll = self._last_question_poll
        self._last_question_poll = int(time.time())

        if channel is None:
            log.info(f"No channel found with ID {self._channel}, waiting for next poll")
            return

        log.info(f"Found channel at ID {self._channel}, fetching SO posts")

        response = requests.get(
            "https://api.stackexchange.com/2.3/questions",
            params={
                "site": "stackoverflow",
                "sort": "creation",
                "order": "asc",
                "tagged": self._tags,
                "min": str(last_question_poll),  # `str` to make mypy happy
            }
        )

        for question in response.json()["items"]:
            url = question["link"]
            log.info(f"Found SO post at URL: {url}")
            await channel.send(  # type: ignore  # since we're copying the example
                f"""{question["title"]}\n{question["link"]}"""
            )

    @poll_and_send.before_loop
    async def before_task(self) -> None:
        await self.wait_until_ready()


discord_token = os.getenv("DISCORD_TOKEN")

if discord_token is None:
    raise RuntimeError("Env var DISCORD_TOKEN expected but not found.")

channel_str = os.getenv("CHANNEL")

if channel_str is None:
    raise RuntimeError("Env var CHANNEL expected but not found.")
else:
    try:
        channel = int(channel_str)
    except ValueError:
        raise ValueError(f"Failed to convert env var CHANNEL to integer.")

tags = os.getenv("TAGS")

if tags is None:
    raise RuntimeError(
        "Comma-separated Stack Overflow tags expected in env var TAGS, but not found."
    )

log.info(f"Polling every {POLL_FREQUENCY_SECONDS}s on channel {channel}")

SOClient(
    intents=discord.Intents.default(),
    channel=channel,
    tags=tags.split(','),
    start_epoch=int(time.time()),
).run(discord_token)
