from flask import render_template
from app import app
import folium
from dal.sparql_queries import get_countries_with_risk_score
from util.pd_utils import get_as_df


@app.route('/home')
def home():
    lon = 15
    lat = 35
    min_lon, max_lon = -180, 180
    min_lat, max_lat = -90, 90
    m = folium.Map(max_bounds=True,
                   height=str(80) + '%',
                   location=[lat, lon],
                   zoom_start=1.5,
                   min_zoom=1,
                   min_lat=min_lat,
                   max_lat=max_lat,
                   min_lon=min_lon,
                   max_lon=max_lon)
    country_info = get_countries_with_risk_score()
    df_country = get_as_df(country_info, ['id', 'risk_level'])
    df_country.risk_level = df_country.risk_level.astype(int)

    countries = folium.Choropleth(geo_data='world_countries.json',
                                  name='choropleth',
                                  data=df_country,
                                  columns=['id', 'risk_level'],
                                  key_on='feature.id',
                                  fill_color='OrRd',
                                  fill_opacity=0.7,
                                  line_opacity=0.2,
                                  nan_fill_opacity=0
                                  ).add_to(m)

    folium.GeoJson(
        'world_countries.json',
        tooltip=folium.GeoJsonTooltip(fields=['name'],
                                      labels=False),
        style_function=lambda feature: {
            'color': 'black',
            'fillOpacity': 0,
            'weight': 0
        }
    ).add_to(countries)

    folium.LayerControl().add_to(m)

    return render_template('index.html', title='Home', foliummap=m._repr_html_())


@app.route('/')
@app.route('/index')
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
