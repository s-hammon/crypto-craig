import os
import platform
import sys

import discord
from discord.ext import commands

if not os.path.isfile('config.py'):
    sys.exit("'config.py' not found.")
else:
    import config

bot = commands.Bot(command_prefix=config.PREFIX)

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print(f'Logged in as {bot.user.name}')
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print('-------------------')
    
async def status_task():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="CoinMarketCap"))

if __name__ == '__main__':
    try:
        c = config.BOOT_COGS[0]
        bot.load_extension(c)
        c = c.replace('cogs.', '')
        print(f"Loaded extensions '{c}'")
    except Exception as e:
        exception = f'{type(e).__name__}: {e}'
        c = c.replace('cogs.', '')
        print(f'Failed to load extension {c}\n{exception}')
            
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    else:
        if message.author.id not in config.BLACKLIST:
            await bot.process_commands(message)
        else:
            context = await bot.get_context(message)
            embed = discord.Embed(
				title="You're blacklisted, you dumb fuck.",
				description="Tell it to the judge. Maybe stop beaing a little SHIT.",
				color=0x00FF00
			)
            await context.send(embed=embed)
            
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(' ')
    executedCommand = str(split[0])
    print(f'Executed {executedCommand} command in {ctx.guild.name} by {ctx.message.author} (ID: {ctx.message.author.id})')
    
@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title='Wait, asshole.',
            description='This command is on a %.2fs cooldown'%error.retry_after,
            color=0x00FF00
        )
        await context.send(embed=embed)
    raise error
    
bot.run(config.TOKEN)