from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import Namespace, NamespaceManager, RDF, XSD


def write_to_turtle(news_results, country_str):
    g = Graph()
    namespace_manager = NamespaceManager(Graph())
    n_dbpedia_res = Namespace("http://dbpedia.org/resource/")
    n_custom = Namespace("http://www.semanticweb.org/sws/group4/")

    namespace_manager.bind('dbp', n_dbpedia_res, override=False)
    namespace_manager.bind('sws', n_custom, override=False)
    g.namespace_manager = namespace_manager

    country = n_dbpedia_res[country_str.replace(" ", "_")]

    for news_entity in news_results:
        article = BNode()

        g.add((article, RDF.type, n_custom['NewsArticle']))

        # data properties
        g.add((article, n_custom['origin'], Literal(news_entity['host'])))
        g.add((article, n_custom['sourceUrl'], Literal(news_entity['url'])))
        g.add((article, n_custom['publicationDate'], Literal(news_entity['publication_date'], datatype=XSD.dateTime)))
        g.add((article, n_custom['title'], Literal(news_entity['title'])))
        if news_entity['sentiment']:
            g.add((article, n_custom['sentiment'], Literal(news_entity['sentiment'])))

        # object properties
        g.add((article, n_custom['mentionsCountry'], country))

        # blank node for related resources
        for related_res in news_entity['related_res']:
            rel = BNode()

            g.add((rel, RDF.type, n_custom['ArticleMention']))
            g.add((rel, n_custom['relevance'], Literal(related_res[1])))
            g.add((rel, n_custom['mentionsResource'], URIRef(related_res[0])))

            g.add((article, n_custom['hasMention'], rel))


    # write to output file
    g.serialize(destination=f'ttl/{country_str.replace(" ","_")}.ttl', format='turtle')


def write_countries_to_turtle(countries):
    g = Graph()
    namespace_manager = NamespaceManager(Graph())
    n_dbpedia_res = Namespace("http://dbpedia.org/resource/")
    n_schema_res = Namespace("https://schema.org/")
    n_dbo_res = Namespace("http://dbpedia.org/ontology/")
    n_custom = Namespace("http://www.semanticweb.org/sws/group4/")

    namespace_manager.bind('dbp', n_dbpedia_res, override=False)
    namespace_manager.bind('schema', n_schema_res, override=False)
    namespace_manager.bind('sws', n_custom, override=False)
    namespace_manager.bind('dbo', n_dbo_res, override=False)
    g.namespace_manager = namespace_manager

    # country = n_dbpedia_res[country_str.replace(" ", "_")]
    for country, risk in countries:
        c = URIRef(n_dbpedia_res[country.replace(" ", "_")])

        # add the country as a named individual
        g.add((c, RDF.type, n_dbo_res.Country))

        # add risk level
        g.add((c, n_custom['Risk_Level'], Literal(risk)))

    # write to output file
    g.serialize(destination=f'ttl/countries.ttl', format='turtle')
