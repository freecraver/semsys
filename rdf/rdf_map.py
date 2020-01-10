from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import Namespace, NamespaceManager, RDF, XSD
import hashlib


def write_to_turtle(news_results, country_str):
    g = Graph()
    namespace_manager = NamespaceManager(Graph())
    n_dbpedia_res = Namespace("http://dbpedia.org/resource/")
    n_custom_ontology = Namespace("http://www.semanticweb.org/sws/group4/ontology/")
    n_custom_resources = Namespace("http://www.semanticweb.org/sws/group4/resources/")

    namespace_manager.bind('dbp', n_dbpedia_res, override=False)
    namespace_manager.bind('swo', n_custom_ontology, override=False)
    namespace_manager.bind('sws', n_custom_resources, override=False)
    g.namespace_manager = namespace_manager

    country = n_dbpedia_res[country_str.replace(" ", "_")]

    for news_entity in news_results:
        # article = BNode()
        news_title = news_entity['title']
        # generate 15 digit hash for name
        news_id = int(hashlib.sha256(news_title.encode('utf-8')).hexdigest(), 16) % 10**15
        article = URIRef(n_custom_resources['Article-' + str(news_id)])

        g.add((article, RDF.type, n_custom_ontology['NewsArticle']))

        # data properties
        g.add((article,n_custom_ontology['origin'], Literal(news_entity['host'])))
        g.add((article, n_custom_ontology['sourceUrl'], Literal(news_entity['url'])))
        g.add((article, n_custom_ontology['publicationDate'], Literal(news_entity['publication_date'], datatype=XSD.dateTime)))
        g.add((article, n_custom_ontology['title'], Literal(news_entity['title'])))
        if news_entity['sentiment']:
            g.add((article, n_custom_ontology['sentiment'], Literal(news_entity['sentiment'])))

        # object properties
        g.add((article, n_custom_ontology['mentionsCountry'], country))

        # blank node for related resources
        for related_res in news_entity['related_res']:
            # rel = BNode()
            # generate 15 digit hash for news article mention
            s = str(related_res[1]) + str(related_res[0]) + str(news_id)
            mention_id = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10 ** 15

            rel = URIRef(n_custom_resources['ArticleMention-' + str(mention_id)])

            g.add((rel, RDF.type, n_custom_ontology['ArticleMention']))
            g.add((rel, n_custom_ontology['relevance'], Literal(related_res[1])))
            g.add((rel, n_custom_ontology['mentionsResource'], URIRef(related_res[0])))

            g.add((article, n_custom_ontology['hasMention'], rel))


    # write to output file
    g.serialize(destination=f'ttl/{country_str.replace(" ","_")}.ttl', format='turtle')


def write_countries_to_turtle(countries):
    g = Graph()
    namespace_manager = NamespaceManager(Graph())
    n_dbpedia_res = Namespace("http://dbpedia.org/resource/")
    n_dbo_res = Namespace("http://dbpedia.org/ontology/")
    n_custom_ontology = Namespace("http://www.semanticweb.org/sws/group4/ontology/")
    n_custom_resources = Namespace("http://www.semanticweb.org/sws/group4/resources/")

    namespace_manager.bind('swo', n_custom_ontology, override=False)
    namespace_manager.bind('sws', n_custom_resources, override=False)
    namespace_manager.bind('dbp', n_dbpedia_res, override=False)
    namespace_manager.bind('dbo', n_dbo_res, override=False)
    g.namespace_manager = namespace_manager

    # country = n_dbpedia_res[country_str.replace(" ", "_")]
    for country, risk in countries:
        c = URIRef(n_dbpedia_res[country.replace(" ", "_")])

        # add the country as a named individual
        g.add((c, RDF.type, n_dbo_res.Country))

        # add risk level
        g.add((c, n_custom_ontology['Risk_Level'], Literal(risk)))

    # write to output file
    g.serialize(destination=f'ttl/countries.ttl', format='turtle')
