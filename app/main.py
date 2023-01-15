import logging
import os
import time

import discord

from app.client import SOClient, POLL_FREQUENCY_SECONDS

log = logging.getLogger(__name__)

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
        raise ValueError("Failed to convert env var CHANNEL to integer.")

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
