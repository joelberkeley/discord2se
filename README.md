# Stack Overflow Discord bot

This small bot posts new Stack Overflow questions at a given set of tags to a specific channel on a Discord server.

## How to use

### Set up a Discord Bot account

Instructions are [here](https://discordpy.readthedocs.io/en/stable/discord.html). You'll need to generate an invitation URL for the bot, and get someone with "Manage Server" permissions on the Discord server to follow that link to add the bot.

### Run the bot

Install the Python dependenices with
```bash
$ pip install .
```
Then populate the following environment variables:
* `DISCORD_TOKEN` with the bot token
* `CHANNEL` with the ID of the Discord server channel you want SO posts submitted to. The ID is the last number in the channel URL (right click on a channel name in the list of channels in the Discord app and "Copy Link").
* `TAGS` with the comma-separated Stack Overflow tags to monitor. The bot will search for all questions with any of the tags

and run
```bash
$ python3 main.py
```
