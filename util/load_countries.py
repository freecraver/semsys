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