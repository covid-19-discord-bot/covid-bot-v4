# # Licenced under the CC BY-NC-SA 4.0 licence: by modifying any code you agree to be bound by the terms of the licence: https://creativecommons.org/licenses/by-nc-sa/4.0/

import api as covid19api
import discord
# noinspection PyUnresolvedReferences
import asyncio
import datetime


def addZeroSpace(embed, count):
    for i in range(1, count):
        embed.add_field(name="\u200b", value="\u200b")


def errorEmbed(bot, reason=None):
    _errorEmbed = discord.Embed(title="Error!", color=discord.Color.red())
    zeroslashzero = bot.get_user(661660243033456652)
    _errorEmbed.add_field(name="An error happened!",
                          value="Report this to {0} on the official Discord server, available via `/invite`".format(
                              zeroslashzero.mention))
    if reason:
        _errorEmbed.add_field(name="Add this when you're reporting this message", value=reason)
    _errorEmbed.set_thumbnail(url="https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
    return _errorEmbed


async def statsEmbed(countryName):
    try:
        if countryName != "world":
            cList = await covid19api.getAllCountries()
            _id = covid19api.getISO2Code(countryName, cList)
            name = covid19api.getCountryName(_id, cList)
            if not _id:
                return None
            cData = await covid19api.getCurrentStats(_id)
            updatedTime = datetime.datetime.fromtimestamp(cData["updated"] / 1000)
            embed = discord.Embed(title="COVID-19 Stats for {0}".format(name), color=discord.Color.dark_red(),
                                  timestamp=updatedTime)
            embed.set_footer(text="Stats last updated at")
            embed.set_thumbnail(url=cData["countryInfo"]["flag"])
        else:
            cData = await covid19api.getCurrentStats("world")
            embed = discord.Embed(title="COVID-19 Stats for World", color=discord.Color.dark_red())
        embed.add_field(name="Active Cases", value=format(int(cData["active"]), ","))
        embed.add_field(name="Active Case Change",
                        value=format(int(cData["todayCases"] - (cData["todayDeaths"] + cData["todayRecovered"])), ","))
        addZeroSpace(embed, 2)
        # Discord has a limit of 4 values per row in a embed on the desktop variant: the above line causes
        # that limit to be reached, forcing the rest of the fields to go onto a newline
        # Thanks to that random person on the d.py server for showing me that trick
        embed.add_field(name="Total Deaths", value=format(int(cData["deaths"]), ","))
        embed.add_field(name="New Deaths", value=format(int(cData["todayDeaths"]), ","))
        addZeroSpace(embed, 2)
        embed.add_field(name="Total Recoveries", value=format(int(cData["recovered"]), ","))
        embed.add_field(name="New Recoveries", value=format(int(cData["todayRecovered"]), ","))
        addZeroSpace(embed, 2)
        embed.add_field(name="Critical Cases", value=format(int(cData["critical"]), ","))
        embed.add_field(name="Tests", value=format(int(cData["tests"]), ","))
        addZeroSpace(embed, 2)
        embed.add_field(name="Cases per 1m People", value=format(int(cData["casesPerOneMillion"]), ","))
        embed.add_field(name="Tests per 1m People", value=format(int(cData["testsPerOneMillion"]), ","))
        addZeroSpace(embed, 2)
        embed.add_field(name="Deaths per 1m People", value=format(int(cData["deathsPerOneMillion"]), ","))
        embed.add_field(name="Recovered per 1m People", value=format(int(cData["recoveredPerOneMillion"]), ","))
        addZeroSpace(embed, 2)
        return embed
    except Exception as e:
        eEmbed = errorEmbed(bot, reason=e)
        return eEmbed


async def listEmbed(bot, letter):
    try:
        _list = await covid19api.getAllCountries()
        embed = discord.Embed(color=discord.Color.blue(), title="Country List",
                              description="Use either the country name, or the ISO2 code when getting stats with "
                                          "`/covid country <name>`!")
        countries = []
        letter = str(letter).lower()
        for field in _list:
            countryName = field["Country"].lower()
            if countryName.startswith(letter):
                countries.append(field)
        if len(countries) != 0:
            for country in countries:
                embed.add_field(name="Country Name", value=country["country"])
                embed.add_field(name="Country ISO2 ID", value=country["iso2"])
                embed.add_field(name="Country ISO3 ID", value=country["iso3"])
                addZeroSpace(embed, 1)
            return embed
        else:
            return None
    except Exception as e:
        eEmbed = errorEmbed(bot, reason=e)
        return eEmbed


# Old global embed
'''
nowDT = datetime.datetime.now()
        data = covid19api.getCurrentStats("world")
        if type(data) == type(69) and (data <= -1 or data >= -3):
            await ctx.send(embed=errorEmbed("Failed to pull data: code: {0}".format(data)))
            return
        flag = "http://siftswift.com/s/img/earthicon.png"
        statsEmbed = discord.Embed(title="COVID-19 Stats For World", color=discord.Color.dark_red(), timestamp=nowDT)
        statsEmbed.set_footer(text="Stats retrieved at")
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
        statsEmbed.add_field(name="Active Cases", value=active)
        statsEmbed.add_field(name="Active Case Change", value=activeChange)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Deaths", value=deaths)
        statsEmbed.add_field(name="New Deaths", value=newDeaths)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Recoveries", value=recovered)
        statsEmbed.add_field(name="New Recoveries", value=newRecovered)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Cases", value=confirmed)
        statsEmbed.add_field(name="New Cases", value=newConfirmed)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.set_thumbnail(url=flag)
        await ctx.send(embed=statsEmbed)
'''

# Old country embed
'''
list = covid19api.getAllCountries()
        slug = covid19api.getISO2Code(country, list)
        if not slug:
            await ctx.send(
                f"Could not find a country named {country}! Run `/list` for a list of all countries and their IDs!")
            return
        data = await covid19api.getCurrentStats(slug)
        if type(data) == type(69) and (data <= -1 or data >= -3):
            await ctx.send(embed=errorEmbed(f"Failed to pull data: code: {data}"))
            return

        flag = "https://www.countryflags.io/{0}/shiny/64.png".format(covid19api.getISO2Code(slug, list))

        try:
            updatedDateTime = str(data["Date"])
        except TypeError:
            zeroslashzero = bot.get_user(661660243033456652)
            noCasesEmbed = discord.Embed(title="No Cases",
                                         description="{0} doesn't seem to have any reported cases!\nIf this is "
                                                     "incorrect, report it to {1} on the official Discord server (get "
                                                     "the invite via `/invite`)".format(
                                             covid19api.getCountryName(slug), zeroslashzero.mention))
            await ctx.send(embed=noCasesEmbed)
        dt = datetime.datetime.strptime(updatedDateTime, "%Y-%m-%dT%H:%M:%SZ")
        niceName = str(data["Country"])
        statsEmbed = discord.Embed(title="COVID-19 Stats For {0}".format(niceName), timestamp=dt,
                                   color=discord.Color.dark_red())
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

        statsEmbed.add_field(name="Active Cases", value=active)
        statsEmbed.add_field(name="Active Case Change", value=activeChange)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Deaths", value=deaths)
        statsEmbed.add_field(name="New Deaths", value=newDeaths)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Recoveries", value=recovered)
        statsEmbed.add_field(name="New Recoveries", value=newRecovered)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Cases", value=confirmed)
        statsEmbed.add_field(name="New Cases", value=newConfirmed)
        addZeroSpace(statsEmbed, 2)
'''

# Another old global embed
'''
nowDT = datetime.datetime.now()
        data = covid19api.getCurrentStats("world")
        if type(data) == type(69) and (data <= -1 or data >= -3):
            await ctx.send(embed=errorEmbed("Failed to pull data: code: {0}".format(data)))
            return
        flag = "http://siftswift.com/s/img/earthicon.png"
        statsEmbed = discord.Embed(title="COVID-19 Stats For World", color=discord.Color.dark_red(), timestamp=nowDT)
        statsEmbed.set_footer(text="Stats retrieved at")
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
        statsEmbed.add_field(name="Active Cases", value=active)
        statsEmbed.add_field(name="Active Case Change", value=activeChange)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Deaths", value=deaths)
        statsEmbed.add_field(name="New Deaths", value=newDeaths)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Recoveries", value=recovered)
        statsEmbed.add_field(name="New Recoveries", value=newRecovered)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.add_field(name="Total Cases", value=confirmed)
        statsEmbed.add_field(name="New Cases", value=newConfirmed)
        addZeroSpace(statsEmbed, 2)
        statsEmbed.set_thumbnail(url=flag)
'''

# Another old country embed
'''
list = covid19api.getAllCountries()
                slug = covid19api.getSlug(country, list)
                if not slug:
                    await channel.send(
                        "Could not find a country named {0}! Run `/list` for a list of all countries and their IDs!".format(
                            country))
                    return
                data = covid19api.getCurrentStats(slug)
                if type(data) == type(69) and (data <= -1 or data >= -3):
                    await channel.send(embed=errorEmbed("Failed to pull data: code: {0}".format(data)))
                    return
                flag = "https://www.countryflags.io/{0}/shiny/64.png".format(covid19api.getISO2Code(slug, list))
                try:
                    updatedDateTime = str(data["Date"])
                except TypeError:
                    zeroslashzero = bot.get_user(661660243033456652)
                    noCasesEmbed = discord.Embed(title="No Cases",
                                                 description="{0} doesn't seem to have any reported cases!\nIf this is "
                                                             "incorrect, report it to {1} on the official Discord server "
                                                             "(get the invite via `/invite`)".format(
                                                     covid19api.getCountryName(slug), zeroslashzero.mention))
                    await channel.send(embed=noCasesEmbed)
                dt = datetime.datetime.strptime(updatedDateTime, "%Y-%m-%dT%H:%M:%SZ")
                niceName = str(data["Country"])
                statsEmbed = discord.Embed(title="COVID-19 Stats For {0}".format(niceName), timestamp=dt,
                                           color=discord.Color.dark_red())
                statsEmbed.set_footer(text="Stats supplied by country at")
                newConfirmed = format(int(data["NewConfirmed"]), ",")
                confirmed = format(int(data["TotalConfirmed"]), ",")
                newDeaths = format(int(data["NewDeaths"]), ",")
                deaths = format(int(data["TotalDeaths"]), ",")
                newRecovered = format(int(data["NewRecovered"]), ",")
                recovered = format(int(data["TotalRecovered"]), ",")
                active = format(int(data["TotalConfirmed"]) - (int(data["TotalRecovered"]) + int(data["TotalDeaths"])),
                                ",")
                activeChange = int(data["NewConfirmed"]) - (int(data["NewRecovered"]) + int(data["NewDeaths"]))
                positiveChange = 0 < activeChange
                if positiveChange:
                    activeChange = "+{0}".format(format(activeChange, ","))
                else:
                    activeChange = "-{0}".format(format(abs(activeChange), ","))
                statsEmbed.add_field(name="Active Cases", value=active)
                statsEmbed.add_field(name="Active Case Change", value=activeChange)
                addZeroSpace(statsEmbed, 2)
                statsEmbed.add_field(name="Total Deaths", value=deaths)
                statsEmbed.add_field(name="New Deaths", value=newDeaths)
                addZeroSpace(statsEmbed, 2)
                statsEmbed.add_field(name="Total Recoveries", value=recovered)
                statsEmbed.add_field(name="New Recoveries", value=newRecovered)
                addZeroSpace(statsEmbed, 2)
                statsEmbed.add_field(name="Total Cases", value=confirmed)
                statsEmbed.add_field(name="New Cases", value=newConfirmed)
                addZeroSpace(statsEmbed, 2)
                statsEmbed.set_thumbnail(url=flag)
                await channel.send(embed=statsEmbed)
'''
