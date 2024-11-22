import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Sequence, Tuple

import discord
from discord.ext import commands
from sqlalchemy import Engine, Row, create_engine, func, select
from sqlalchemy.orm import Session

from models.repositories import Listing
from craig.graphs import coin_scatter_plot


TURSO_DATABASE_URL = os.environ.get("DB_URL")
TURSO_AUTH_TOKEN_DISCORD_CLIENT = os.environ.get(
    "TURSO_AUTH_TOKEN_DISCORD_CLIENT", "MISSING_TURSO_AUTH_TOKEN"
)

db_url = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN_DISCORD_CLIENT}&secure=true"

engine = create_engine(db_url)

class Craig(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix="!",
            decription="Craig the cryptocurrency bot!",
            intents=kwargs.pop("intents"),
        )
        self.engine = kwargs.pop("engine")


intents = discord.Intents.default()
intents.message_content = True
bot = Craig(engine=engine, intents=intents)

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print(f"We have logged in as {bot.user}")

@bot.command()
async def getprice(ctx, coin: str):
    coin = coin.upper()

    result = get_listing_by_coin(bot.engine, coin)
    if not result:
        await ctx.reply(f"Could not find a price for {coin}.", mention_author=True)
        return

    price = f"${result.price:,.2f}"
    await ctx.reply(f"Price for {coin}: {price}", mention_author=True)

@getprice.error
async def getprice_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Usage: `!getprice <coin_symbol>`", mention_author=True)

@bot.command(name="all")
async def getprice_all(ctx):
    listings = get_select_listings(bot.engine)
    msg = "Current prices:\n"
    for listing in listings:
        msg += f"{listing[0].coin}: ${listing[0].price:,.2f}\n"

    await ctx.reply(f"```{msg}```", mention_author=True)

@bot.command()
async def history(ctx, coin: str, date_range: str="7d"):
    coin = coin.upper()
    rng = _range(date_range)

    listings = get_coin_history(coin.upper(), rng)
    time = [listing[0].updated_at for listing in listings]
    prices = [listing[0].price for listing in listings]
    img = coin_scatter_plot(coin=coin, time=time, prices=prices)
    
    await ctx.reply(file=discord.File(img, filename="plot.png"), mention_author=True)

@history.error
async def history_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Usage: `!history <coin_symbol> [range]`", mention_author=True)

@lru_cache(maxsize=128)
def get_coin_history(coin: str, rng: datetime) -> Sequence[Row[Tuple[Listing]]]:
    if not coin:
        raise ValueError("Coin is empty")

    with Session(engine) as session:
        stmt = (
            select(Listing)
            .where(Listing.coin.is_(coin))
            .where(Listing.updated_at > rng)
        )
        result = session.execute(stmt).all() 

    return result

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
    # remove minutes, seconds, and microseconds
    return date.replace(minute=0, second=0, microsecond=0)
    
def _sanitize_date(date: datetime) -> datetime:
    # also remove hours
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

@lru_cache(maxsize=128)
def get_listing_by_coin(engine: Engine, coin: str) -> Listing | None:
    # TODO: cache
    if not coin:
        raise ValueError("Coin is empty")

    with Session(engine) as session:
        stmt = (
            select(Listing)
            .where(Listing.coin.is_(coin))
            .order_by(Listing.updated_at.desc())
            .limit(1)
        )
        result = session.scalar(stmt)

    return result


@lru_cache(maxsize=128)
def get_select_listings(engine: Engine) -> Sequence[Row[Tuple[Listing]]]:
    # TODO: cache
    coins = ["BTC", "ETH", "LINK", "AAVE", "DOGE"]
    with Session(engine) as session:
        # use the orm to get the latest listing for each coin
        subq = (
            select(Listing.coin, func.max(Listing.updated_at).label("max_updated_at"))
            .where(Listing.coin.in_(coins))
            .group_by(Listing.coin)
            .subquery()
        )

        stmt = (
            select(Listing)
            .join(
                subq,
                (Listing.coin == subq.c.coin) & (Listing.updated_at == subq.c.max_updated_at)
            )
        )

        result = session.execute(stmt).all()

    return result

async def status_task():
    while True:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="CoinMarketCap"
            )
        )

def run():
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "MISSING_DISCORD_TOKEN")
    print(f"using token: {DISCORD_TOKEN[:4]}...{DISCORD_TOKEN[-4:]}")
    bot.run(DISCORD_TOKEN)