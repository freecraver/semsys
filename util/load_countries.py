import geocoder
import json

RES_FILE_PATH = "res/aut_min_travel.json"


def get_geonames_country_name(country):
    res = geocoder.geonames(country, key='freecraver')
    if len(res):
        return res[0].country
    return None


def load_countries():
    with open(RES_FILE_PATH) as f:
        data = json.load(f)
        countries = [x.get("country") for x in data["countries"]]
        mapped_countries = [c for c in [get_geonames_country_name(x) for x in countries] if c is not None]
        return mapped_countries


def load_countries_with_risk_level():
    with open(RES_FILE_PATH) as f:
        data = json.load(f)
        countries = [(x.get("country"), x.get("riskLevel")) for x in data["countries"]]
        mapped_countries = [(c, d) for (c, d) in [(get_geonames_country_name(x), y) for (x, y) in countries] if c is not None]
        return mapped_countries
