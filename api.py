# # Licenced under the CC BY-NC-SA 4.0 licence: by modifying any code you agree to be bound by the terms of the licence: https://creativecommons.org/licenses/by-nc-sa/4.0/

import aiohttp
import asyncio
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)


####################
# Getter Functions #
####################

# Given a URL, this will return the text of that page
async def getData(session, url):
    async with session.get(url) as response:
        return await response.text()


# Returns country list
async def getAllCountries():
    cf = open('countries.json', 'r')
    countryList = json.loads(cf.read())
    cf.close()
    countryNames = []
    for country in countryList:
        if not country["iso2"]:
            continue
        countryNames.append(country)
    return countryNames


# Returns stats for a country, given any of the 3 types of codes (country name, ISO2 code, or ISO3 code)
async def getCurrentStats(countryName):
    if countryName == "world":
        cf = open("world.json", "r")
        cfd = json.loads(cf.read())
        cf.close()
    else:
        cList = await getAllCountries()
        code = getISO2Code(countryName, cList)
        if code is None:
            return None
        try:
            cf = open("{0}.json".format(code), "r")
        except FileNotFoundError:
            return None
        cfd = json.loads(cf.read())
        cf.close()
    return cfd


# Updates global stats
async def updateStats():
    logging.info('Opening new AIOHttp session...')
    async with aiohttp.ClientSession() as session:
        logging.info("Getting new data...")
        data = json.loads(await getData(session, "https://disease.sh/v2/countries"))
        logging.info("Parsing data and writing it")
        isoCodes = []
        for country in data:
            if country['countryInfo']['iso2'] is not None:
                cf = open(f"{country['countryInfo']['iso2']}.json", "w")
                cf.write(json.dumps(country))
                cf.close()
                isoCode = dict(country=country["country"], iso2=country["countryInfo"]["iso2"],
                               iso3=country["countryInfo"]["iso3"])
                isoCodes.append(isoCode)
        cf = open("countries.json", "w")
        cf.write(json.dumps(isoCodes))
        cf.close()
        logging.info("Getting more stats...")
        worldData = json.loads(await getData(session, "https://disease.sh/v2/all"))  # Global stats
        gf = open("world.json", "w")
        gf.write(json.dumps(worldData))
        gf.close()
    logging.info("Done!")
    return 0


async def getAllCountryData():
    async with aiohttp.ClientSession() as session:
        cdl = json.loads(await getData(session, "https://disease.sh/v2/countries"))
    return cdl


# Returns data used in the /top command
async def getList(_type):
    cList = await getAllCountryData()
    _type = str(_type).lower()
    if _type == "cases":
        sortedCList = sorted(cList, key=lambda k: k['cases'])
        sortedCList.reverse()
    elif _type == "recovered":
        sortedCList = sorted(cList, key=lambda k: k['recovered'])
        sortedCList.reverse()
    elif _type == "deaths":
        sortedCList = sorted(cList, key=lambda k: k['deaths'])
        sortedCList.reverse()
    elif _type == "critical":
        sortedCList = sorted(cList, key=lambda k: k['critical'])
        sortedCList.reverse()
    elif _type == "tests":
        sortedCList = sorted(cList, key=lambda k: k['tests'])
        sortedCList.reverse()
    elif _type == "population":
        sortedCList = sorted(cList, key=lambda k: k['population'])
        sortedCList.reverse()
    else:
        return None
    return sortedCList


####################
# Helper Functions #
####################

# Returns a slug that allows getting country data, given any of the 3 types of codes
def getISO2Code(_input, _list):
    _input = str(_input).lower()
    iso2Code = None
    try:
        for country in _list:
            if str(country['country']).lower() == _input:
                iso2Code = country['iso2']
                break
            elif str(country['iso2']).lower() == _input:
                iso2Code = country['iso2']
                break
            elif str(country["iso3"]).lower() == _input:
                iso2Code = country["iso2"]
                break
    except IndexError:
        return None
    return iso2Code


# Same as getISO2Code(), returns a ISO3 code
def getISO3Code(_input, _list):
    _input = getISO2Code(_input, _list)
    if not _input:
        return -1
    name = None
    try:
        for country in _list:
            if _input == str(country["iso2"]).lower():
                name = country["iso3"]
                break
    except IndexError:
        return -2
    return name


# Same as getISO2Code(), only returns a country name
def getCountryName(_input, _list):
    _input = getISO2Code(_input, _list)
    if not _input:
        return -1
    name = None
    try:
        for country in _list:
            if _input == str(country["iso2"]).lower():
                name = country["country"]
                break
    except IndexError:
        return -2
    return name


if __name__ == '__main__':
    status = asyncio.get_event_loop().run_until_complete(updateStats())
    print(status)
