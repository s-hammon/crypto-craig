import logging
import os
from pathlib import Path

import discord
from sqlalchemy import Engine


def run(engine: Engine, debug: bool = False):
    from craig.bot import CraigBot

    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "MISSING_DISCORD_TOKEN")

    LOG_DIR = os.environ.get("LOG_DIR", "logs")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    handler = logging.StreamHandler()
    if not debug:
        handler = logging.FileHandler(
            Path(LOG_DIR) / "discord.log", encoding="utf-8", mode="w"
        )

    intents = discord.Intents.default()
    intents.message_content = True

    bot = CraigBot(engine, intents=intents)
    bot.run(DISCORD_TOKEN, log_handler=handler)
