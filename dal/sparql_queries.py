from SPARQLWrapper import SPARQLWrapper, JSON

SPARQL_ENDPOINT = "http://localhost:7200/repositories/semsys"  # make sure youre repository in graph db matches the name 'semsys'
sparql = SPARQLWrapper(SPARQL_ENDPOINT)


def get_countries_by_risk_score(risk_score):
    # dummy for parameter passing usage
    if type(risk_score) != int:
        raise ValueError("Number required")

    sparql.setQuery("""
        PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
        select ?c
        where { ?c ns1:Risk_Level %d}
    """ % risk_score)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return [x['c']['value'] for x in results["results"]["bindings"]]


def get_countries_with_risk_score():
    sparql.setQuery("""
            PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
            select ?c ?rl
            where { 
            ?c1 ns1:Risk_Level ?rl;
            ns1:ISO3_Code ?c.
            }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return [(x['c']['value'], x['rl']['value']) for x in results["results"]["bindings"]]


def get_capitals():
    sparql.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        select ?capital ?lat ?lon where { 
            ?capital ns1:isCapitalOf ?o .
            ?capital ns1:latitude ?lat .
            ?capital ns1:longitude ?lon .
            ?capital ns1:monthFrom ?mf . FILTER(?mf <= 9)
            ?capital ns1:monthTo ?mt . FILTER(?mt >= 7 || (?mf<7 && ?mt>9))
            ?o a dbo:Country;
               ns1:Risk_Level 1.
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(x['capital']['value'], x['lat']['value'], x['lon']['value']) for x in results["results"]["bindings"]]
