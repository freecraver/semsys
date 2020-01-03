TURTLE_PATH = "ttl/"
import glob
from rdflib import Graph

if __name__=='__main__':
    total_graph = Graph()
    for file in glob.glob(TURTLE_PATH + "*.ttl"):
        print(f"Loading file {file}")
        cur_graph = Graph()
        cur_graph.parse(file, format='turtle')
        total_graph += cur_graph

    total_graph.serialize(TURTLE_PATH + "complete.ttl", format="turtle")
