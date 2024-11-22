import os
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from craig.graphs import coin_scatter_plot
from craig.handlers import (
    get_coin_history,
    get_listing_by_coin,
    get_select_listings,
)


TURSO_DATABASE_URL = os.environ.get("DB_URL")
TURSO_AUTH_TOKEN_DISCORD_CLIENT = os.environ.get(
    "TURSO_AUTH_TOKEN_DISCORD_CLIENT", "MISSING_TURSO_AUTH_TOKEN"
)

db_url = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN_DISCORD_CLIENT}&secure=true"

engine = create_engine(db_url)
CraigSession = sessionmaker(bind=engine)


class Craig(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix="!",
            decription="Craig the cryptocurrency bot!",
            intents=kwargs.pop("intents"),
        )

    @property
    def session(self):
        return CraigSession()


intents = discord.Intents.default()
intents.message_content = True
bot = Craig(intents=intents)


@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print(f"We have logged in as {bot.user}")


@bot.command()
async def getprice(ctx, coin: str):
    coin = coin.upper()

    result = get_listing_by_coin(bot.session, coin)
    if not result:
        await ctx.reply(f"Could not find a price for {coin}.", mention_author=True)
        return

    price = f"${result.price:,.2f}"
    await ctx.reply(f"Price for {coin}: {price}", mention_author=True)


@getprice.error
async def getprice_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Usage: `!getprice <coin_symbol>`", mention_author=True)
    else:
        raise error


@bot.command(name="all")
async def getprice_all(ctx):
    listings = get_select_listings(bot.session)
    msg = "Current prices:\n"
    for listing in listings:
        msg += f"{listing[0].coin}: ${listing[0].price:,.2f}\n"

    await ctx.reply(f"```{msg}```", mention_author=True)


@bot.command()
async def history(ctx, coin: str, date_range: str = "7d"):
    coin = coin.upper()
    rng = _range(date_range)

    listings = get_coin_history(bot.session, coin.upper(), rng)
    time = [listing[0].updated_at for listing in listings]
    prices = [listing[0].price for listing in listings]
    img = coin_scatter_plot(coin=coin, time=time, prices=prices)

    await ctx.reply(file=discord.File(img, filename="plot.png"), mention_author=True)


@history.error
async def history_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Usage: `!history <coin_symbol> [range]`", mention_author=True)


async def status_task():
    while True:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="CoinMarketCap"
            )
        )


def _range(rng: str) -> datetime:
    now = _sanitize_date(datetime.now(timezone.utc)) - timedelta(hours=1)
    match rng:
        case "7d":
            return _sanitize_date(now) - timedelta(days=7)
        case "30d" | "1m":
            return _sanitize_date(now) - timedelta(days=30)
        case "3m":
            return _sanitize_date(now) - timedelta(days=90)
        case "6m":
            return _sanitize_date(now) - timedelta(days=180)
        case "1y":
            return _sanitize_date(now) - timedelta(days=365)
        case _:
            return _sanitize_time(now) - timedelta(hours=1)


def _sanitize_time(date: datetime) -> datetime:
    return date.replace(minute=0, second=0, microsecond=0)


def _sanitize_date(date: datetime) -> datetime:
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def run():
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "MISSING_DISCORD_TOKEN")
    print(f"using token: {DISCORD_TOKEN[:4]}...{DISCORD_TOKEN[-4:]}")
    bot.run(DISCORD_TOKEN)
