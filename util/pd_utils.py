from enum import Enum

import pandas as pd


def get_as_df(arr, col_names):
    df_country = pd.DataFrame(arr, columns=col_names)
    if 'country' in df_country.columns:
        df_country.country = df_country.country.transform(
            lambda c: c.split('/')[-1].replace('_', ' ').replace('-', ' '))
    return df_country


class Month(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


class EarlyMidLate(Enum):
    early = 5
    mid = 15
    late = 25
