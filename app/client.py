import logging
import time
from collections.abc import Iterable
from typing import Final

import discord
from discord.ext import tasks
import requests

from stackoverflow import QuestionsResponse


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

        self._tags = tags
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

        found_question_ids = set[int]()

        for tag in self._tags:
            response: QuestionsResponse = requests.get(
                "https://api.stackexchange.com/2.3/questions",
                params={
                    "site": "stackoverflow",
                    "sort": "creation",
                    "order": "asc",
                    "tagged": tag,
                    "min": str(last_question_poll),  # `str` to make mypy happy
                }
            ).json()

            for question in response["items"]:
                question_id = question["question_id"]

                if question_id in found_question_ids:
                    continue

                found_question_ids.add(question_id)
                url = question["link"]
                log.info(f"Found SO post at URL: {url}")
                await channel.send(  # type: ignore  # since we're copying the example
                    f"""{question["title"]}\n{url}"""
                )

    @poll_and_send.before_loop
    async def before_task(self) -> None:
        await self.wait_until_ready()
