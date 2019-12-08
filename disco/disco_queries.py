from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

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
        res_dict = set([e["disambiguation"]["dbpedia_resource"]
                         for e in enriched_text["entities"]
                         if e["relevance"] > 0.5 and e.get("disambiguation") and e.get("disambiguation").get(
                "dbpedia_resource")])

    if enriched_text.get("concepts"):
        res_dict |= set(c["dbpedia_resource"] for c in enriched_text["concepts"] if c["relevance"] > 0.5)

    return list(res_dict)


def extract_info(news_result):
    return {
        "publication_date": news_result.get('publication_date'),
        "url": news_result.get('url'),
        "host": news_result.get('host'),
        "title": news_result.get('title'),
        "sentiment": news_result.get('enriched_text').get('sentiment').get('score') if news_result.get('enriched_text') else None,
        "related_res": extract_resources(news_result)
    }


def load_disaster_news(country_name):
    res = discovery.query('system', 'news-en',
                          query=f'enriched_text.entities:(type:Location,'
                                f'disambiguation:(subtype:Country, name:"{country_name}"),relevance>0.5),'
                                f'enriched_text.categories:(label:"/science/weather/meteorological disaster/", score>0.75)')
    news_results = [extract_info(r) for r in res.result.get('results')]
    return news_results
