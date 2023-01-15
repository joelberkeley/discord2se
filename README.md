# Stack Overflow Discord bot

This small bot posts new Stack Overflow questions at a given set of tags to specific channel on a Discord server.

## How to use

I'll assume you know how to set up a Python environment.

Set up a Discord Bot account, instructions are [here](https://discordpy.readthedocs.io/en/stable/discord.html). Generate an invitation URL for the bot, and get someone with "Manage Server" permissions on the Discord server to add the bot.

Now you need to run the bot. Populate the following environment variables:
* `DISCORD_TOKEN` with the bot token
* `CHANNEL` with the discord channel you want SO posts submitted to
* `TAGS` with the comma-separated Stack Overflow tags to monitor. Note that the bot only fetches posts that match _all_ tags. 
Then run the bot with
```bash
$ python3 main.py
```
