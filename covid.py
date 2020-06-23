# Licenced under the CC BY-NC-SA 4.0 licence: by modifying any code you agree to be bound by the terms of the licence: https://creativecommons.org/licenses/by-nc-sa/4.0/

import discord

from discord.ext import commands

import api as covid19api
import embeds


@commands.group()
async def covid(ctx, *args):
    try:
        # noinspection PyUnusedLocal
        exist = args[0]
    except IndexError:
        statsEmbed = await embeds.statsEmbed("world")
        if statsEmbed is None:
            errorEmbed = embeds.errorEmbed(bot, reason="Severe error: no world file found!")
            await ctx.send(embed=errorEmbed)
        await ctx.send(embed=statsEmbed)
    else:
        country = str(args[0]).lower()
        statsEmbed = await embeds.statsEmbed(country)
        if statsEmbed is None:
            await ctx.send("Couldn't find a country with that ID (`/list` for a list of IDs) or the country has no "
                           "cases!")
        await ctx.send(embed=statsEmbed)


'''
@covid.command()
async def country(ctx, *, country: str):
    country = country.lower()
    list = api.getAllCountries()
    slug = api.getSlug(country, list)
    if not slug:
        await ctx.send("Could not find a country named {0}! Run `/list` for a list of all countries and their IDs!".format(country))
        return
    data = api.getCurrentStats(slug)
    if type(data) == type(69):
        if data <= -1 or data >= -3:
            await ctx.send(embed=errorEmbed("Failed to pull data: code: {0}".format(data)))
            return

    flag = "https://www.countryflags.io/{0}/shiny/64.png".format(api.getISO2Code(slug, list))

    try:
        updatedDateTime = str(data["Date"])
    except TypeError:
        zeroslashzero = bot.get_user(661660243033456652)
        noCasesEmbed = discord.Embed(title="No Cases",description="{0} doesn't seem to have any reported cases!\nIf this is incorrect, report it to {1} on the official Discord server (get the invite via `/invite`)".format(api.getCountryName(slug), zeroslashzero.mention))
        await ctx.send(embed=noCasesEmbed)
    dt = datetime.datetime.strptime(updatedDateTime, "%Y-%m-%dT%H:%M:%SZ")
    niceName = str(data["Country"])
    statsEmbed = discord.Embed(title="COVID-19 Stats For {0}".format(niceName),timestamp=dt,color=discord.Color.dark_red())
    statsEmbed.set_footer(text="Stats supplied by country at")

    newConfirmed = format(int(data["NewConfirmed"]), ",")
    confirmed = format(int(data["TotalConfirmed"]), ",")
    newDeaths = format(int(data["NewDeaths"]), ",")
    deaths = format(int(data["TotalDeaths"]), ",")
    newRecovered = format(int(data["NewRecovered"]), ",")
    recovered = format(int(data["TotalRecovered"]), ",")
    active = format(int(data["TotalConfirmed"]) - (int(data["TotalRecovered"]) + int(data["TotalDeaths"])), ",")
    activeChange = int(data["NewConfirmed"]) - (int(data["NewRecovered"]) + int(data["NewDeaths"]))
    positiveChange = 0 < activeChange

    if positiveChange:
        activeChange = "+{0}".format(format(activeChange, ","))
    else:
        activeChange = "-{0}".format(format(abs(activeChange), ","))

    statsEmbed.add_field(name="Active Cases",value=active)
    statsEmbed.add_field(name="Active Case Change",value=activeChange)
    addZeroSpace(statsEmbed,2)
    statsEmbed.add_field(name="Total Deaths",value=deaths)
    statsEmbed.add_field(name="New Deaths",value=newDeaths)
    addZeroSpace(statsEmbed,2)
    statsEmbed.add_field(name="Total Recoveries",value=recovered)
    statsEmbed.add_field(name="New Recoveries",value=newRecovered)
    addZeroSpace(statsEmbed,2)
    statsEmbed.add_field(name="Total Cases",value=confirmed)
    statsEmbed.add_field(name="New Cases",value=newConfirmed)
    addZeroSpace(statsEmbed,2)

    statsEmbed.set_thumbnail(url=flag)

    await ctx.send(embed=statsEmbed)
'''


# noinspection PyShadowingBuiltins
@commands.command()
async def list(ctx, *firstLetter):
    if len(firstLetter) == 0:
        await ctx.send(
            "I can't send the entire country list: it's over Discord's 6,000 character limit! Try `/list <letter>` to "
            "get only countries starting with `<letter>`.")
    embed = await embeds.listEmbed(bot, firstLetter)
    if embed is not None:
        await ctx.author.send(embed=embed)
        if ctx.message.guild is not None:
            await ctx.send("DMed a list to you!")
    else:
        await ctx.send("Couldn't find any countries starting with those letters!")


@commands.command()
async def top(ctx, *_type):
    '''
    /top <type>

    where <type> is one of "cases", "recovered", "deaths", "critical", "tests"
    '''
    try:
        _list = await covid19api.getList(_type[0])
    except IndexError:
        notCorrectTypeEmbed = discord.Embed(title="Incorrect Top List Type",
                                            description="Try sorting with one of the following:")
        for _type in ["cases", "recovered", "deaths", "critical", "tests"]:
            notCorrectTypeEmbed.add_field(name="\u200b", value=_type)
        await ctx.send(embed=notCorrectTypeEmbed)
        return
    if _list is None:
        notCorrectTypeEmbed = discord.Embed(title="Incorrect Top List Type",
                                            description="Try sorting with one of the following:")
        for _type in ["cases", "recovered", "deaths", "critical", "tests"]:
            notCorrectTypeEmbed.add_field(name="\u200b", value=_type)
        await ctx.send(embed=notCorrectTypeEmbed)
        return
    topEmbed = discord.Embed(title="Top List", description="Run `/help list` for a list of all possible sorts")
    for country in _list:
        topEmbed.add_field(name=country["country"], value=country[_type[0]])
        embeds.addZeroSpace(topEmbed, 3)
    await ctx.send(embed=topEmbed)


def setup(mainBot):
    mainBot.add_command(covid)
    mainBot.add_command(list)
    mainBot.add_command(top)
    # noinspection PyGlobalUndefined
    global bot
    bot = mainBot
