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
            select ?c1 ?rl
            where { 
            ?c1 ns1:Risk_Level ?rl
            }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    res_list = [(x['c1']['value'], x['rl']['value']) for x in results["results"]["bindings"]]

    # add data which was not mapable by geocoder-api (i.e. where not dbpedia resource was found)
    res_list.append(('Democratic Republic of the Congo', 5))
    res_list.append(('North Korea', 4))
    res_list.append(('South Korea', 1))

    return res_list


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


def get_ski_resorts():
    sparql.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        select distinct ?country ?s ?lat ?lon where { 
            
            SERVICE <http://dbpedia.org/sparql> {
                ?ski a dbo:SkiArea .
                ?ski rdfs:label ?s .
                ?ski geo:lat ?lat .
                ?ski geo:long ?lon .
                ?ski dbo:location+ ?country.
            }
            ?country a dbo:Country .  
            ?t a dbo:Town .
            ?t ns1:tempTypicalLow ?low . FILTER (?low < -5) .
            ?country ns1:hasTown ?t .
        }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(x['country']['value'], x['s']['value'], x['lat']['value'], x['lon']['value']) for x in
            results['results']['bindings']]


def get_currency():
    sparql.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        select ?country ?currency where {
            SERVICE <http://dbpedia.org/sparql> {
                ?country dbo:currency ?currency .
            }
            ?country a dbo:Country .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(x['country']['value'], x['currency']['value']) for x in results['results']['bindings']]


def get_country_info(country_iso3):
    sparql.setQuery("""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX wd: <http://www.wikidata.org/entity/>
            select ?p ?o where { 
                ?country a dbo:Country;
                         ns1:ISO3_Code "%s".
                ?country ?p ?o.
            }
        """ % country_iso3)

    sparql.setQuery("""PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?country ?risk ?continent 
            where { 
                ?country a dbo:Country ;
                         ns1:ISO3_Code "%s".
                ?country ns1:Risk_Level ?risk .
                ?country ns1:Country_Located_In ?cont .
                SERVICE <http://dbpedia.org/sparql> {
                    ?cont a dbo:Continent .
                    ?cont rdfs:label ?continent .
                }
            } LIMIT 1
        """ % country_iso3)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(x['country']['value'], x['risk']['value'], x['continent']['value']) for x in results["results"]["bindings"]]


def get_resources(q_string):
    query_term = q_string.replace(" ", "_").lower()
    sparql.setQuery("""
                PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>
                select distinct ?res
                where {
                    ?m ns1:mentionsResource ?res.
                    FILTER(strStarts( lcase(str(?res)), "http://dbpedia.org/resource/%s" ))
                }
                group by ?res
            """ % query_term)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return [x['res']['value'].split('/')[-1].replace('_', ' ').replace('-', ' ') for x
            in results["results"]["bindings"] if 'res' in x]


def get_related_countries(resource_name):
    res_uri = "<http://dbpedia.org/resource/" + resource_name.replace(" ", "_") + ">"
    sparql.setQuery("""
                PREFIX ns1: <http://www.semanticweb.org/sws/group4/ontology/>                
                select DISTINCT ?c
                where {
                    ?m ns1:mentionsResource %s .
                    ?a ns1:hasMention ?m;
                       ns1:mentionsCountry ?c.
                }
            """ % res_uri)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return [x['c']['value'].split('/')[-1].replace('_', ' ').replace('-', ' ') for x
            in results["results"]["bindings"] if 'c' in x]
