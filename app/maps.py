import folium

from dal.sparql_queries import get_countries_with_risk_score, get_capitals
from util.pd_utils import get_as_df


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


def create_capitals(m):
    feature_group = folium.FeatureGroup(name='lrs Capitals').add_to(m)

    capitals = get_capitals()
    df_capitals = get_as_df(capitals, ['name', 'lat', 'lon'])

    for i in range(0, len(df_capitals)):
        feature_group.add_child(folium.Marker([df_capitals.iloc[i]['lat'], df_capitals.iloc[i]['lon']],
                                              icon=folium.Icon(color='cadetblue', icon='certificate',
                                                               icon_color='#FACC2E'),
                                              popup=df_capitals.iloc[i]['name'].split('/')[-1].replace('_',
                                                                                                       ' ')).add_to(m))

    return m
