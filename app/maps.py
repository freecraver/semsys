import folium
import numpy as np

from dal.sparql_queries import get_countries_with_risk_score, get_capitals, get_ski_resorts
from util.pd_utils import get_as_df, Month


def create_risk_map():
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
    df_country = get_as_df(country_info, ['country', 'risk_level'])
    df_country.risk_level = df_country.risk_level.astype(int)

    countries = folium.Choropleth(geo_data='world_countries.json',
                                  name='Risk Levels',
                                  data=df_country,
                                  columns=['country', 'risk_level'],
                                  key_on='feature.properties.name',
                                  fill_color='OrRd',
                                  fill_opacity=0.7,
                                  line_opacity=0.2,
                                  nan_fill_opacity=0
                                  ).add_to(m)
    tooltip = folium.GeoJsonTooltip(fields=['name'],
                                    labels=False)
    geojson = folium.GeoJson(
        'world_countries.json',
        tooltip=tooltip,
        style_function=lambda feature: {
            'color': 'black',
            'fillOpacity': 0,
            'weight': 0
        }
    )
    geojson.add_to(countries)

    return m, geojson.get_name()


def create_empty_map():
    lon = 15
    lat = 35
    min_lon, max_lon = -180, 180
    min_lat, max_lat = -90, 90

    country_info = get_countries_with_risk_score()
    df_country = get_as_df(country_info, ['country', 'risk_level'])
    df_country.risk_level = np.nan

    m = folium.Map(max_bounds=True,
                   height=str(80) + '%',
                   location=[lat, lon],
                   zoom_start=1.5,
                   min_zoom=1,
                   min_lat=min_lat,
                   max_lat=max_lat,
                   min_lon=min_lon,
                   max_lon=max_lon)

    cp = folium.Choropleth(geo_data='world_countries.json',
                           name='Risk Levels',
                           data=df_country,
                           columns=['country', 'risk_level'],
                           key_on='feature.properties.name',
                           fill_color='OrRd',
                           fill_opacity=0.7,
                           line_opacity=0.2,
                           nan_fill_opacity=0
                           ).add_to(m)

    tooltip = folium.GeoJsonTooltip(fields=['name'],
                                    labels=False)
    geojson = folium.GeoJson(
        'world_countries.json',
        tooltip=tooltip,
        style_function=lambda feature: {
            'color': 'black',
            'fillOpacity': 0,
            'weight': 0
        })
    geojson.add_to(cp)

    return m, geojson


def create_capitals(m):
    feature_group = folium.FeatureGroup(name='low risk summer Capitals').add_to(m)

    capitals = get_capitals()
    df_capitals = get_as_df(capitals, ['name', 'lat', 'lon', 'low', 'high', 'mf', 'mt'])

    for i in range(0, len(df_capitals)):
        mf = int(df_capitals.iloc[i]['mf'].split('/')[-1].replace('_', ' '))
        mt = int(df_capitals.iloc[i]['mt'].split('/')[-1].replace('_', ' '))
        test = folium.Html(''
                           '<div>'
                           '<h4>' + df_capitals.iloc[i]['name'].split('/')[-1].replace('_', ' ') + '</h4>'
                                                                                                   '<span>Temperatures typically between ' +
                           df_capitals.iloc[i]['low'].split('/')[-1].replace('_', ' ') + ' and '
                           + df_capitals.iloc[i]['high'].split('/')[-1].replace('_', ' ') + '° Celsius</span>'
                                                                                            '<hr><span></p>Visit between ' +
                           Month(mf).name + ' and ' + Month(mt).name
                           + '</span>'
                             '</div>'
                           , script=True)

        popup = folium.Popup(test, max_width=2650)
        # ,
        # iframe = folium.element.IFrame(html=html, width=500, height=300)
        # popup = folium.Popup(iframe, max_width=2650)
        feature_group.add_child(folium.Marker([df_capitals.iloc[i]['lat'], df_capitals.iloc[i]['lon']],
                                              icon=folium.Icon(color='cadetblue', icon='certificate',
                                                               icon_color='#FACC2E'),
                                              popup=popup).add_to(m))

    return m


def create_ski_resorts(m):
    feature_group = folium.FeatureGroup(name='Ski Resorts', show=False).add_to(m)

    ski = get_ski_resorts()
    df_skis = get_as_df(ski, ['country', 's', 'lat', 'lon'])
    df_skis = df_skis[-df_skis['s'].duplicated()]
    # df_skis = df.sort_values('s').reset_index(drop=True)

    for i in range(0, len(df_skis)):
        feature_group.add_child(folium.Marker([df_skis.iloc[i]['lat'], df_skis.iloc[i]['lon']],
                                              icon=folium.Icon(color='white', icon='hand-lizard-o',
                                                               icon_color='#000000', prefix='fa'),
                                              popup=df_skis.iloc[i]['s']).add_to(m))

    return m
