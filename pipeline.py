from util.load_countries import load_countries, load_countries_with_risk_level
from util.load_towns import load_towns
from disco.disco_queries import load_disaster_news
from rdf.rdf_map import write_to_turtle, write_countries_to_turtle, write_vaccine_info_to_turtle, write_towns_to_turtle
import pandas as pd

first_country_to_load = "Afghanistan"
fetch = False

if __name__ == '__main__':
    """
    print('Initially loading country information...')

    country_names = load_countries()
    for country in country_names:
        # continue previous run
        if country == first_country_to_load:
            fetch = True
        if not fetch:
            print(f'Skipping already processed country {country}')
            continue
        print(f'Fetching news for {country}...')

        news_res = load_disaster_news(country)
        print(f'Found {len(news_res)} news entries')
        if len(news_res) > 0:
            print(f'Converting to Turtle file {country.replace(" ", "_")}.ttl')
            write_to_turtle(news_res, country)
    print('Loading countries from resource')

    countries = load_countries_with_risk_level()
    write_countries_to_turtle(countries)
    
    """
    print('Loading vaccine related information...')
    vaccine_df= pd.read_csv("res/vaccine_coverage.csv",delimiter=',',header=0)
    vaccine_names= pd.read_excel("res/vaccine_names.xlsx",header=0)
    write_vaccine_info_to_turtle(vaccine_df,vaccine_names)
    """
    print('Loading town and city related information...')
    towns, countryTowns = load_towns()
    write_towns_to_turtle(towns, countryTowns)
    """
