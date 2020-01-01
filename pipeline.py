from util.load_countries import load_countries
from disco.disco_queries import load_disaster_news
from rdf.rdf_map import write_to_turtle

if __name__ == '__main__':
    print('Initially loading country information...')
    country_names = load_countries()
    for country in country_names:
        print(f'Fetching news for {country}...')
        news_res = load_disaster_news(country)
        print(f'Found {len(news_res)} news entries')
        if len(news_res) > 0:
            print(f'Converting to Turtle file {country.replace(" ", "_")}.ttl')
            write_to_turtle(news_res, country)