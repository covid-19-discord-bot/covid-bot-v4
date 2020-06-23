import asyncio
from math import floor

import traceback
import api
import datetime
import discord
import json
import logging
from discord.ext import tasks, commands

# api.getCurrentStats(countryName) returns a dictionary of data about a country

try:
    configFile = open("config.json", "r")
    configData = json.loads(configFile.read())
    configFile.close()
except FileNotFoundError:
    logging.fatal("No config file is created! Creating one...")
    configData = {
        BOT_TOKEN: "",
        LOG_CHANNEL: "",
        EXTENSIONS: [
            'utils',
            "covid",
            "autoupdate"
        ],
        VERSION: "v3.0.0beta"}
    configFile = open("config.json", "w")
    configFile.write(json.dumps(configData))
    configFile.close()
    exit(1)

logging.disable(logging.DEBUG)
bot = commands.AutoShardedBot(command_prefix='/', case_insensitive=True)
channelFileLock = asyncio.Lock()


####################
# Helper Functions #
####################


# Pushes a message to all subscribed channels when one is sent by either Symphonic or 0/0mainB
async def pushBotUpdate(message):
    embed = discord.Embed(title="Important Bot Message", description=message)
    embed.set_footer(text="Change where these messages are sent by running `/updatehere` in the channel you want them "
                          "sent to")
    async with channelFileLock:
        cf = open("channelFile.json", "r")
        df = json.loads(cf.read())
        cf.close()
    i = 0
    for guild in bot.guilds:
        sentMessage = False
        for details in df:
            if details["guildID"] == guild.id:
                guild = bot.get_guild(details["guildID"])
                if guild is None:
                    sentMessage = True
                    break
                channel = guild.get_channel(details["channelID"])
                if channel is None:
                    sentMessage = True
                    break
                await channel.send(embed=embed)
                sentMessage = True
        if not sentMessage:
            sysChannel = guild.system_channel
            if sysChannel is None:
                sysChannel = guild.text_channels[0].id
            else:
                sysChannel = sysChannel.id
            updates = {
                "guildID": guild.id,
                "channelID": sysChannel
            }
            async with channelFileLock:
                cf = open("channelFile.json", "r")
                cfd = json.loads(cf.read())
                cf.close()
                cfd.append(updates)
                cf = open("channelFile.json", "w")
                cf.write(json.dumps(cfd))
                cf.close()

            channel = bot.get_channel(updates["channelID"])
            channel.send(embed=embed)

            i = i + 1
        logging.info("Sent a message to {0} servers.".format(i))


###################
# Main Bot Events #
###################


@bot.event
async def on_shard_ready(_id):
    logging.info("Shard ID {0} is online!".format(str(_id)))


@bot.event
async def on_ready():
    logging.info("All {0} shards online!".format(len(bot.latencies)))
    logging.info("Logged in as {0}".format(bot.user))


@bot.event
async def on_message(ctx):
    await bot.process_commands(ctx)
    # Because... well... it's against ToS
    '''
    if ctx.channel.id == 681249487573745667:
        if ctx.author.id == 661660243033456652 or ctx.author.id == 263128260009787392:
            await pushBotUpdate(ctx.message.content)
    '''


@bot.event
async def on_guild_join(guild):
    sysChannel = guild.system_channel
    if sysChannel is None:
        sysChannel = guild.text_channels[0].id
    else:
        sysChannel = sysChannel.id
    updates = {
        "guildID": guild.id,
        "channelID": sysChannel
    }
    async with channelFileLock:
        cf = open("channelFile.json", "r")
        cfd = json.loads(cf.read())
        cf.close()
        cfd.append(updates)
        cf = open("channelFile.json", "w")
        cf.write(json.dumps(cfd))
        cf.close()


# noinspection PyUnusedLocal
@bot.event
async def on_guild_update(before, guild):
    sysChannel = guild.system_channel
    if sysChannel is None:
        sysChannel = guild.text_channels[0].id
    else:
        sysChannel = sysChannel.id
    updates = {
        "guildID": guild.id,
        "channelID": sysChannel
    }
    async with channelFileLock:
        cf = open("channelFile.json", "r")
        cfd = json.loads(cf.read())
        cf.close()
        cfd.append(updates)
        cf = open("channelFile.json", "w")
        cf.write(json.dumps(cfd))
        cf.close()


async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send("You're missing a required argument! `/help command` will show you what you need.")
        return
    elif isinstance(error, discord.Forbidden):
        return
    elif isinstance(error, discord.ext.commands.CommandNotFound):
        return
    elif isinstance(error, discord.ext.commands.CommandInvokeError):
        await ctx.send("A error happened while trying to run your request: report to @0/0 on the official Discord "
                       "server (`/invite`) or it'll never be fixed!\nAdd these lines while reporting your error:"
                       "```{0}```".format(error.original))
    else:
        await ctx.send("A error happened while trying to parse your command: report to @0/0 on the official Discord "
                       "server (`/invite`)\nAdd these next lines while reporting your error:\n```{0}```".format(
                        traceback.format_exc()))
        logging.critical("Fatal error on message: stack trace below (hopefully)", exc_info=True)


################
# Bot Commands #
################

@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Please use `/reload all` for the time being.")
    # await ctx.send("Rebooting bot... may take a little while.")


@bot.command()
@commands.is_owner()
async def reload(ctx, *, args):
    args = str(args)
    if args == "all":
        await ctx.send(
            "⚠ **Reloading all extensions!** ⚠\nIf the bot stops working after this, simply call `reload all` again.")
        for _extension in configData["EXTENSIONS"]:
            bot.reload_extension(_extension)
        await ctx.send("Reloaded all extensions.")
    else:
        if args in configData["EXTENSIONS"]:
            await ctx.send("Reloading extension {0}...".format(args))
            bot.reload_extension(args)
            await ctx.send("Reloaded extension {0}!".format(args))
        else:
            await ctx.send("Invalid extension name!")


@tasks.loop(minutes=15.0, reconnect=False)
async def update():
    await bot.wait_until_ready()
    logging.info("Updating COVID-19 stats...")
    status = await api.updateStats()
    if status == -1:
        logging.info("Shouldn't ever see this message!")
    updateChannel = bot.get_channel(configData["LOG_CHANNEL"])
    updateEmbed = discord.Embed(title="Successful update of stats!")
    updateEmbed.add_field(name="Finished updating data for all countries just now.",
                          value="The new updated data has been deployed successfully.")
    await updateChannel.send(embed=updateEmbed)
    logging.info("Updated COVID-19 stats!")


@tasks.loop(minutes=30.0, reconnect=False)
async def updateStats():
    await bot.wait_until_ready()
    logging.info("Updating stats...")
    stats = {}
    guildCount = 0
    memberCount = 0
    shardCount = 0
    # Calculates guild and member count
    for guild in bot.guilds:
        guildCount = guildCount + 1
        for _ in guild.members:
            memberCount = memberCount + 1
    # Calculates shard count
    for _ in bot.latencies:
        shardCount = shardCount + 1
    # Calculates days since bot was created
    createdDate = datetime.datetime(2020, 2, 7, 0, 0, 0)
    currentDate = datetime.datetime.now()
    td = currentDate - createdDate
    createdDays = floor(int(td.total_seconds()) / 86400)

    stats["userCount"] = memberCount
    stats["guildCount"] = guildCount
    stats["shards"] = shardCount
    stats["daysSinceCreation"] = createdDays
    statFile = open("stats.json", "w")
    statFile.write(json.dumps(stats))
    statFile.close()
    logging.info("Updated stats!")


for extension in configData["EXTENSIONS"]:
    bot.load_extension(name=extension)

updateStats.start()
update.start()
bot.add_listener(on_command_error, "on_command_error")

bot.run(configData['BOT_TOKEN'])
