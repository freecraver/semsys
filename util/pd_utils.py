import pandas as pd

def get_as_df(arr, col_names):
    df_country = pd.DataFrame(arr, columns=col_names)
    if 'country' in df_country.columns:
        df_country.country = df_country.country.transform(lambda c: c.split('/')[-1].replace('_',' ').replace('-',' '))
    return df_country