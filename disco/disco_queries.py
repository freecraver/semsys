from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from settings import START_DATE, END_DATE

authenticator = IAMAuthenticator('o-V5I0eeHruCOX5uyc8dICpCNT4Uzbd-6Q8JEpuCM7_D')
discovery = DiscoveryV1(
    version='2019-11-30',
    authenticator=authenticator
)

discovery.set_service_url('https://gateway-lon.watsonplatform.net/discovery/api')


def extract_resources(news_result):
    if not news_result.get("enriched_text"):
        return []
    enriched_text = news_result["enriched_text"]
    res_dict = {}

    if enriched_text.get("entities"):
        for e in enriched_text["entities"]:
            if not e.get("disambiguation") or not e.get("disambiguation")\
                    .get("dbpedia_resource") or e["relevance"] < 0.5:
                continue

            val = e["disambiguation"]["dbpedia_resource"]
            if not res_dict.get(val) or res_dict[val] < e["relevance"]:
                res_dict[val] = e["relevance"]

    if enriched_text.get("concepts"):
        for c in enriched_text["concepts"]:
            if c["relevance"] < 0.5:
                continue

            val = c["dbpedia_resource"]
            if not res_dict.get(val) or res_dict[val] < c["relevance"]:
                res_dict[val] = c["relevance"]

    return list(res_dict.items())

def extract_sentiment(news_result):
    if not news_result.get('enriched_text'):
        return None
    elif not news_result.get('enriched_text').get('sentiment'):
        return None
    elif not news_result.get('enriched_text').get('sentiment').get('document'):
        return None
    return  news_result.get('enriched_text').get('sentiment').get('document').get('score')


def extract_info(news_result):
    return {
        "publication_date": news_result.get('publication_date'),
        "url": news_result.get('url'),
        "host": news_result.get('host'),
        "title": news_result.get('title'),
        "sentiment":extract_sentiment(news_result),
        "related_res": extract_resources(news_result)
    }


def load_disaster_news(country_name):
    res = discovery.query('system', 'news-en',
                          query=f'enriched_text.entities:(type:Location,'
                                f'disambiguation:(subtype:Country, name:"{country_name}"),relevance>0.5),'
                                f'enriched_text.categories:(label:"/science/weather/meteorological disaster/", score>0.75),'
                                f'publication_date>={START_DATE},'
                                f'publication_date<={END_DATE}',
                          count=50)
    news_results = [extract_info(r) for r in res.result.get('results')]
    return news_results
