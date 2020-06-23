# Licenced under the CC BY-NC-SA 4.0 licence: by modifying any code you agree to be bound by the terms of the licence: https://creativecommons.org/licenses/by-nc-sa/4.0/

import asyncio
import json
import time
# noinspection PyUnresolvedReferences
import discord

from discord.ext import tasks, commands

import api as covid19api
import embeds

fileLock = asyncio.Lock()


@commands.group()
@commands.has_permissions(manage_messages=True)
async def autoupdate(ctx, delay: int) -> int:
    '''
    /autoupdate <delay> updates stats for World every <delay> minutes
    '''
    if ctx.guild is None:
        await ctx.send(
            "We're in a private channel! Go to a server where you have the MANAGE MESSAGES permission and try again!")
        return -1

    currentTime = time.time()

    iso2Code = "OT"  # OT stands for "global"
    channel = ctx.channel.id
    autoUpdateData = {
        "ChannelID": channel,
        "UpdateTime": delay * 60,
        "Country": iso2Code,
        "LastUpdateTime": currentTime}

    async with fileLock:
        adf = open("autoupdates.json", "r")
        updatedAutoUpdaterList = json.loads(adf.read())
        adf.close()
        updatedAutoUpdaterList.append(autoUpdateData)
        adf = open("autoupdates.json", "w")
        adf.write(json.dumps(updatedAutoUpdaterList))
        adf.close()
    await ctx.send("Posting stats for World in this channel every {0} minutes".format(delay))
    return 0


@commands.command()
@commands.has_permissions(manage_messages=True)
async def autoupdateCountry(ctx, updateTime: int, country: str) -> int:
    '''
    /autoupdateCountry <delay> <country> updates stats for <country> every <delay> minutes
    <country> must be one of the 3 types available in /list
    '''
    if ctx.guild is None:
        await ctx.send(
            "We're in a private channel! Go to a server where you have the MANAGE MESSAGES permission and try again!")
        return -1

    currentTime = time.time()

    iso2Code = covid19api.getISO2Code(country, await covid19api.getAllCountries())
    if not iso2Code:
        await ctx.send(
            'Failed to get a ISO2 code for the country! `/list` will show you a list of countries and their IDs.')
        return -2
    channelID = ctx.channel.id
    guildID = ctx.guild.id
    autoUpdateData = {
        "ChannelID": channelID,
        "GuildID": guildID,
        "UpdateTime": updateTime * 60,
        "Country": iso2Code,
        "LastUpdateTime": currentTime
    }

    async with fileLock:
        adf = open("autoupdates.json", "r")
        updatedAutoUpdaterList = json.loads(adf.read())
        adf.close()
        updatedAutoUpdaterList.append(autoUpdateData)
        adf = open("autoupdates.json", "w")
        adf.write(json.dumps(updatedAutoUpdaterList))
        adf.close()
    await ctx.send("Posting stats for {0} in this channel every {1} minutes".format(iso2Code, updateTime))
    return 0


@tasks.loop(minutes=1.0)
async def pushAutoUpdates():
    async with fileLock:
        uf = open("autoupdates.json", "r")
        ud = json.loads(uf.read())
        uf.close()

        i = 0
        for updater in ud:
            currentTime = time.time()
            guild = bot.get_guild(updater["GuildID"])
            if not guild:
                ud.pop(i)
                i = i + 1
                continue
            channel = guild.get_channel(updater["ChannelID"])
            if not channel:
                ud.pop(i)
                i = i + 1
                continue
            sinceLastUpdate = currentTime - updater["LastUpdateTime"]
            if not sinceLastUpdate >= updater["UpdateTime"]:
                i = i + 1
                continue
            try:
                if updater["Country"] == "OT":
                    embed = await embeds.statsEmbed("global")
                    await channel.send(embed=embed)
                else:
                    country = updater["Country"]
                    country = country.lower()
                    embed = await embeds.statsEmbed(country)
                    await channel.send(embed=embed)
            except discord.errors.Forbidden:
                pass
            i = i + 1
        uf = open("autoupdates.json", "w")
        uf.write(json.dumps(ud))
        uf.close()


@commands.command()
async def disableUpdates(ctx):
    '''
    /disableupdates removes all autoupdates for the channel it is run in
    '''
    adf = open("autoupdates.json", "r")
    autoUpdaterList = json.loads(adf.read())
    adf.close()

    i = 0
    toRemove = []
    for updater in autoUpdaterList:
        if updater["ChannelID"] == ctx.channel.id:
            toRemove.append(i)
        i = i + 1

    if len(toRemove) == 0:
        await ctx.send("There aren't any autoupdaters set in this channel!")
        return
    toRemove.pop(len(toRemove)-1)
    async with fileLock:
        adf = open("autoupdates.json", "r")
        updatedAutoUpdaterList = json.loads(adf.read())
        adf.close()
        for remove in toRemove:
            updatedAutoUpdaterList.pop(remove)
        adf = open("autoupdates.json", "w")
        adf.write(json.dumps(updatedAutoUpdaterList))
        adf.close()
    await ctx.send("Removed all autoupdaters for this channel!")


def setup(mainBot):
    mainBot.add_command(autoupdate)
    mainBot.add_command(autoupdateCountry)
    mainBot.add_command(disableUpdates)
    pushAutoUpdates.start()
    # noinspection PyGlobalUndefined
    global bot
    bot = mainBot
