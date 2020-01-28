import unittest

from dal.sparql_queries import get_countries_by_risk_score, get_countries_with_risk_score
from util.pd_utils import get_as_df


class TestSparql(unittest.TestCase):

    def test_get_countries(self):
        x = get_countries_by_risk_score(3)
        self.assertTrue(len(x) > 5, "There should be more countries with risk level 3")

    def test_get_risk_scores(self):
        x = get_countries_with_risk_score()
        y = get_as_df(x, ['country', 'risk_level'])
        self.assertIsNotNone(x, "No countries found")
