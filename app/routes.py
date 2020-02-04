from flask import render_template, request, jsonify, make_response
from app import app
import folium

from app.maps import create_risk_map, create_capitals
from dal.sparql_queries import get_countries_with_risk_score
from util.pd_utils import get_as_df


@app.route('/home')
def home():
    m = create_risk_map()
    m = create_capitals(m)
    folium.LayerControl().add_to(m)
    return render_template('map.html', title='Home', foliummap=m._repr_html_())


@app.route('/')
@app.route('/index')
def index():
    folium_map = folium.Map(location=[100, 0], zoom_start=1.5)
    country_info = get_countries_with_risk_score()
    df_country = get_as_df(country_info, ['country', 'risk_level'])
    df_country.risk_level = df_country.risk_level.astype(int)

    folium_map.choropleth(geo_data='world_countries.json', data=df_country,
                          columns=['country', 'risk_level'],
                          key_on='feature.properties.name',
                          fill_color='OrRd', fill_opacity=0.7,
                          line_opacity=0.2, nan_fill_opacity=0)
    return folium_map._repr_html_()
