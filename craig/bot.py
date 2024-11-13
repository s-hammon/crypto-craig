import discord
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from models.repositories import Listing


class CraigBot(discord.Client):
    def __init__(self, engine: Engine, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine

    async def status_task(self):
        while True:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name="CoinMarketCap"
                )
            )

    async def on_ready(self):
        self.loop.create_task(self.status_task())
        print(f'We have logged in as {self.user}')

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        
        if message.content.startswith("!getprice"):
            split = message.content.split(" ")
            if len(split) != 2:
                await message.reply("Usage: `!getprice <coin>`", mention_author=True)
                return

            coin = split[1].upper()

            result = get_listing_by_coin(self.engine, coin)
            if not result:
                await message.reply(f"Could not find a price for {coin}.", mention_author=True)
                return

            price = f"${result.price:,.2f}"
            await message.reply(f"Price for {coin}: {price}", mention_author=True)

        if message.content.startswith("!all"):
            listings = get_select_listings(self.engine)
            msg = "Current prices:\n"
            for listing in listings:
                price = f"${listing.price:,.2f}"
                msg += f"{listing.coin}: {price}\n"

            await message.reply(msg, mention_author=True)

def get_listing_by_coin(engine: Engine, coin: str) -> Listing | None:
    # TODO: cache
    if not coin:
        raise ValueError("Coin is empty")
    
    with Session(engine) as session:
        stmt = select(Listing).where(Listing.coin.is_(coin)).order_by(Listing.updated_at.desc()).limit(1)
        result = session.scalar(stmt)

    return result


def get_select_listings(engine: Engine) -> list[Listing]:
    # TODO: cache
    coins = ["BTC", "ETH", "LINK", "AAVE", "DOGE"]
    listings = []
    for coin in coins:
        listing = get_listing_by_coin(engine, coin)
        if listing:
            listings.append(listing)

    return listings