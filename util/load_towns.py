import json
from util.load_countries import get_geonames_country_name

RES_FILE_PATH = "res/cities.json"
d={}

def putD(iso, countryName):
    d[iso]=get_geonames_country_name(countryName)
    return d.get(iso)
    
def load_towns():
    with open(RES_FILE_PATH, encoding='utf8') as f:
        data = json.load(f)        
        towns = [(x.get('iso'), x.get('city'), x.get('latitude'), x.get('longitude'), x.get('temp_typical_low'), x.get('temp_typical_high'), x.get('day_from'), x.get('day_to'), x.get('month_from'), x.get('month_to')) for x in data]        
        countryTowns = [(d.get(x.get('iso')) if x.get('iso') in d else putD(x.get('iso'), x.get('country')), x.get('city')) for x in data]
        return towns, countryTowns
