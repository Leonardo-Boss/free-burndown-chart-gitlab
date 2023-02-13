import json
import os

import discord
from discord.ext import commands

from chart import GitLab, create_burndown_chart

description = '''bot for generating burndown chart'''
CONFIG_FOLDER = 'config'
CONFIG = f'{CONFIG_FOLDER}/config.json'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', description=description, intents=intents)
client = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def devclean(ctx):
    async with ctx.typing():
        with open(CONFIG) as f:
            config = json.load(f)
        command = config['devclean']
        ssh = f'ssh -i "{CONFIG_FOLDER}/key.pem" {config["serverlink"]} "{command}"'
        os.system(ssh)


@bot.command()
async def chart(ctx):
    async with ctx.typing():
        gitlab = GitLab(CONFIG)
        issues = gitlab.get_issues_from_open_milestones()
        weights = gitlab.calculate_weights(issues)
        path = create_burndown_chart(*weights)
        with open(path, 'rb') as f:
            file = discord.File(f, 'chart.png')
        await ctx.send(file=file)

with open(CONFIG, 'r') as f:
    token = json.load(f)['discord_token']

bot.run(token)
