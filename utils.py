# Licenced under the CC BY-NC-SA 4.0 licence: by modifying any code you agree to be bound by the terms of the licence: https://creativecommons.org/licenses/by-nc-sa/4.0/

import discord
import json


from discord.ext import commands

configFile = open("config.json", "r")
configData = json.loads(configFile.read())
configFile.close()


@commands.command()
async def credits(ctx):
    """
    A simple credits screen
    """
    creditsEmbed = discord.Embed(color=discord.Color.dark_green(), title="Credits")
    symphonic = bot.get_user(263128260009787392)
    zeroslashzero = bot.get_user(661660243033456652)
    symphonicMention: str = symphonic.mention
    zeroslashzeroMention: str = zeroslashzero.mention
    creditsEmbed.set_footer(text="current bot version: {0}".format(configData["VERSION"]))
    creditsEmbed.add_field(name="v3+ Creator", value=zeroslashzeroMention)
    creditsEmbed.add_field(name="Original Creator", value=symphonicMention)
    creditsEmbed.add_field(name='API Providers', value="https://covid19api.com", inline=False)
    creditsEmbed.add_field(name="Creators of discord.py", value="https://discordpy.readthedocs.io", inline=False)
    await ctx.send(embed=creditsEmbed)
    return None


@commands.command()
async def invite(ctx):
    inviteEmbed = discord.Embed(color=discord.Color.purple(), title="Invite Links")
    oauthUrl = discord.utils.oauth_url(str(bot.user.id),
                                       permissions=discord.Permissions(read_messages=True, send_messages=True,
                                                                       embed_links=True),
                                       redirect_uri="https://discord.com/oauth2/authorized")
    inviteEmbed.add_field(name="Bot Invite Link", value=oauthUrl)
    inviteEmbed.add_field(name="Discord Server Invite Link", value="https://discord.gg/v8qDQDc")
    await ctx.send(embed=inviteEmbed)


@commands.command()
async def stats(ctx):
    sf = open("stats.json", "r")
    sd = json.loads(sf.read())
    sf.close()
    statsEmbed = discord.Embed(color=discord.Color.blue(), title="Bot Stats")
    statsEmbed.add_field(name="Number of servers the bot is in", value=sd["guildCount"])
    statsEmbed.add_field(name="Number of users the bot can see", value=sd["userCount"])
    try:
        statsEmbed.add_field(name="Number of shards the bot is running on", value=sd["shardCount"])
    except KeyError:
        pass
    statsEmbed.add_field(name="Total days since bot was created", value=sd["daysSinceCreation"])
    await ctx.send(embed=statsEmbed)


@commands.command()
@commands.has_guild_permissions(administrator=True)
async def claim(ctx):
    if ctx.message.guild is None:
        await ctx.send(
            'We\'re in a private DM channel: head to a server where you\'re a admin with this bot and try again!')
        return
    for member in ctx.message.guild.members:
        if member.id == 675390513020403731:
            await ctx.send('I\'ve detected the non-beta version of the bot in this server! Remove that bot to be able '
                           'to claim your beta tester role.')
            return
    botGuild = bot.get_guild(675390855716274216)
    betaRole = botGuild.get_role(723645816245452880)
    for member in botGuild.members:
        if member.id == ctx.author.id:
            member.add_roles(betaRole)
            await ctx.send("You are now a beta tester!")
            return
    await ctx.send("You don't seem to be part of the bot's support server. Try joining it and trying again: `/invite`")


def setup(mainBot):
    mainBot.add_command(credits)
    mainBot.add_command(invite)
    mainBot.add_command(stats)
    mainBot.add_command(claim)
    # noinspection PyGlobalUndefined
    global bot
    bot = mainBot
