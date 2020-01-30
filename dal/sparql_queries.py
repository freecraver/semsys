from SPARQLWrapper import SPARQLWrapper, JSON

SPARQL_ENDPOINT = "http://localhost:7200/repositories/semsys" # make sure youre repository in graph db matches the name 'semsys'
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