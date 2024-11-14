import logging
import os
from pathlib import Path

import discord
from sqlalchemy import Engine, create_engine


TURSO_DATABASE_URL = os.environ.get("DB_URL")
TURSO_AUTH_TOKEN_DISCORD_CLIENT = os.environ.get(
    "TURSO_AUTH_TOKEN_DISCORD_CLIENT", "MISSING_TURSO_AUTH_TOKEN"
)

base_db_url = f"sqlite+{TURSO_DATABASE_URL}/"


def new_engine(token: str) -> Engine:
    url = base_db_url + f"?authToken={token}&secure=true"
    return create_engine(url)


def run(debug: bool = False):
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

    engine = new_engine(TURSO_AUTH_TOKEN_DISCORD_CLIENT)
    bot = CraigBot(engine, intents=intents)
    bot.run(DISCORD_TOKEN, log_handler=handler)
