import os
from typing import Sequence, Tuple

import discord
from discord.ext import commands
from sqlalchemy import Engine, Row, create_engine, func, select
from sqlalchemy.orm import Session

from models.repositories import Listing


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
    if not coin:
        await ctx.reply("Usage: `!getprice <coin_symbol>`", mention_author=True)
        return

    result = get_listing_by_coin(bot.engine, coin.upper())
    if not result:
        await ctx.reply(f"Could not find a price for {coin}.", mention_author=True)
        return

    price = f"${result.price:,.2f}"
    await ctx.reply(f"Price for {coin}: {price}", mention_author=True)


@bot.command(name="all")
async def getprice_all(ctx):
    listings = get_select_listings(bot.engine)
    msg = "Current prices:\n"
    for listing in listings:
        msg += f"{listing[0].coin}: ${listing[0].price:,.2f}\n"

    await ctx.reply(f"```{msg}```", mention_author=True)


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