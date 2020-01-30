from flask import Flask

import folium
from dal.sparql_queries import get_countries_with_risk_score
from util.pd_utils import get_as_df

app = Flask(__name__)

@app.route('/')
def index():
    folium_map = folium.Map(location=[100, 0], zoom_start=1.5)
    country_info = get_countries_with_risk_score()
    df_country = get_as_df(country_info, ['id', 'risk_level'])
    df_country.risk_level = df_country.risk_level.astype(int)

    folium_map.choropleth(geo_data='world_countries.json', data=df_country,
                   columns=['id', 'risk_level'],
                   key_on='feature.id',
                   fill_color='OrRd', fill_opacity=0.7,
                    line_opacity=0.2, nan_fill_opacity=0)
    return folium_map._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)