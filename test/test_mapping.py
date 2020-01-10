import unittest

from rdf.rdf_map import write_to_turtle, write_countries_to_turtle


class TestRdfMapping(unittest.TestCase):

    def test_mapping(self):
        disco_res = [{
            "publication_date": '2019-11-18T16:28:00Z',
            "url": 'https://www.urdupoint.com/en/world/man-dies-in-landslide-as-austria-hit-by-heavy-765122.html',
            "host": 'urdupoint.com',
            "title": 'Man dies in landslide as Austria hit by heavy rain and snow',
            "sentiment": 0.1324,
            "related_res": [
                ('http://dbpedia.org/resource/Bad_Gastein', 0.518708),
                ('http://dbpedia.org/resource/Salzburg', 0.577873)
            ]
        }]
        write_to_turtle(disco_res, 'Austria')

        # add mapping of country
        countries = [
            ('Austria', 1),
            ('Afghanistan', 6),
            ('Germany', 1)
        ]
        write_countries_to_turtle(countries)
