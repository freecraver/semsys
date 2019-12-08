import unittest

from disco.disco_queries import load_disaster_news


class TestDisco(unittest.TestCase):

    def test_natural_disaster(self):
        x = load_disaster_news('Austria')
        self.assertTrue(len(x) > 0, 'Could not fetch natural disaster news')