from util.load_countries import load_countries, load_countries_with_risk_level
from disco.disco_queries import load_disaster_news
from rdf.rdf_map import write_to_turtle, write_countries_to_turtle

first_country_to_load = "Sudan"
fetch = False

if __name__ == '__main__':
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
