import os
import sys

import asyncio
from datetime import datetime

import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

from discord.ext import commands

from sqlalchemy import create_engine, func, MetaData, Table, Column, BigInteger, String, TIMESTAMP

if not os.path.isfile('config.py'):
    sys.exit("'config.py' not found.")
else:
    import config

class Prices(commands.Cog, name='prices'):
    # Initializes background collection of crypto data from CMC
    def __init__(self, bot):
        self.bot = bot
        self.prices = {}
        # Establishes connection with database
        self.engine = create_engine('sqlite:///db/coinsDB.db', echo = True)
        self.conn = self.engine.connect()
        # Adds class functions to loop background tasks
        self.bg_task1 = self.bot.loop.create_task(self.check_prices())
        self.bg_task2 = self.bot.loop.create_task(self.send_prices())
        
    async def check_prices(self):
        # REST query, parse, and stores data about crypto coins all in one go
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # API request to CMC
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
            parameters = {
                'start': '1',
                'limit': '5000',
                'convert': 'USD'
            }
            
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': '1bc59ff0-44db-417a-818d-9f93408f36fc'
            }
            
            try:
                response = requests.get(url, params=parameters, headers=headers)
                response.raise_for_status()
                data = json.loads(response.text)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                data = json.loads(response.text)
                code = data['status']['error_code']
                message = data['status']['error_message']
                print(f'{code}: {message}')
                print(e)
            
            # Parse info from request
            for i in data['data']:
                coin = i['symbol']
                # Creates table for coin if it doesn't exist in database
                if not self.engine.dialect.has_table(self.engine, coin):
                    meta = MetaData(self.engine)
                    # Create table with columns
                    Table(coin, meta,
                        Column('timestamp', TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()),
                        Column('supply', BigInteger),
                        Column('price', String),
                        Column('volume_24h', BigInteger),
                        Column('percent_1h', String),
                        Column('percent_24h', String)
                    )
                    meta.create_all()
                # Fill respective table with data
                meta = MetaData(bind=None)
                table = Table(coin, meta, autoload=True, autoload_with=self.engine)
                ins = table.insert().values(
                    supply=i['circulating_supply'],
                    price = '%.2f'%i['quote']['USD']['price'],
                    volume_24h = i['quote']['USD']['volume_24h'],
                    percent_1h = '%.2f'%i['quote']['USD']['percent_change_1h'],
                    percent_24h = '%.2f'%i['quote']['USD']['percent_change_24h']
                )
                self.conn.execute(ins)
                
                # Save coin, price, and 1h percent to dict
                price = i['quote']['USD']['price']
                price = '%.2f'%price
                percent_1h = i['quote']['USD']['percent_change_1h']
                percent_1h = '%.2f'%percent_1h
                self.prices[coin] = {
                    'price': price,
                    'percent_1h': percent_1h
                }
                
            await asyncio.sleep(60*10)
            
    async def send_prices(self):
        # Spits message to Discord channel
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(config.CHANNELS[0])
        while not self.bot.is_closed():
            now = datetime.now().strftime("%H:%M")
            if (now in ['06:00', '12:00', '18:00']):
                message = 'Current prices:\n'
                for k, v in self.prices.items():
                    if k in ['BTC', 'ETH', 'LINK', 'AAVE', 'DOGE']:
                        message += f'{k} -- ${v["price"]} ({v["percent_1h"]}%)\n'
                await channel.send(message)
                await asyncio.sleep(60)
            await asyncio.sleep(1)
            
    @commands.command(name='getprice')
    async def get_price(self, ctx, coin='ALL'):
        coin = coin.upper()
        if coin == 'ALL':
            message = 'Last updated prices:\n'
            for k, v in self.prices.items():
                if k in ['BTC', 'ETH', 'LINK', 'AAVE', 'DOGE']:
                    message += f'{k} -- ${v["price"]} ({v["percent_1h"]}%)\n'
            await ctx.send(message)
        else:
            if coin in self.prices.keys():
                await ctx.send(f'Last updated price of {coin}: ${self.prices[coin]["price"]} ({self.prices[coin]["percent_1h"]}%)')
            else:
                await ctx.send('That coin doesn\'t exist, and neither should you.')
    
def setup(bot):
    bot.add_cog(Prices(bot))
