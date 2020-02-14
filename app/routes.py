import os

import folium
import jinja2
from flask import render_template, request, jsonify, send_from_directory
from flask_cors import cross_origin

from app import app
from app.maps import create_risk_map, create_capitals, create_empty_map, create_ski_resorts, create_town_markers
from dal.sparql_queries import get_countries_with_risk_score, get_country_info, get_resources, get_related_countries, \
    get_top10_vacc_coverage, get_safe_countries_asia, get_measles_threats
from util.folium_macros import add_event_macro
from util.pd_utils import get_as_df
import numpy as np

country_info_view = None
country_info_map = None
empty_map_view = None


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
@app.route('/home')
def home():
    global country_info_view
    if country_info_view is None:
        m, geojson = create_risk_map()
        m = create_capitals(m)
        m = create_ski_resorts(m)
        folium.LayerControl().add_to(m)

        # TODO add extra html, css, javascript to map here
        # ugly, but it works
        el = folium.MacroElement().add_to(m)
        map_name = m.get_name()
        el._template = jinja2.Template("""
            {%% macro script(this, kwargs) %%}        
            // folium variables
            map = %s;
            geojson = %s;
            
            // console.log(geojson._tooltip._source)
            
            
            // click event in country layer
            map.on('click', function(e) {
                $.ajax({
                    url:"http://localhost:5000/countryInfo",
                    type: "post",
                    data: JSON.stringify({'country': geojson._tooltip._source.feature.properties.name, 'id': geojson._tooltip._source.feature.id}),
                    crossDomain: true,
                    dataType: 'html',
                    contentType: 'application/json; charset=utf-8',
                    success: function(response) {
                        window.parent.postMessage(response, "*");
                    }, 
                    error: function(err) {
                        console.log('something went wrong')
                        console.error(err)
                    }
                });
            });
            {%% endmacro %%}
        """ % (map_name, geojson))
        country_info_view = m._repr_html_()
    return render_template('map.html', title='Home', foliummap=country_info_view)


@app.route('/countryInfo', methods=["POST"])
@cross_origin()
def country_info():
    if request.method == 'POST':
        info = get_country_info(request.json['id'])
        r = ''
        curr = ''
        cont = ''
        if len(info) > 0:
            r = info[0][1]
            curr = info[0][3]
            cont = info[0][2]
        ret = render_template('country_info.html', name=request.json['country'], risk=r, currency=curr,
                              continent=cont, iso=request.json['id'])

        return ret


@app.route('/towns', methods=["POST"])
@cross_origin()
def towns():
    global country_info_map
    if request.method == 'POST':
        iso = request.json['iso']
        month = request.json['month']
        m, geojson = create_risk_map()
        m = create_capitals(m)
        m = create_ski_resorts(m)
        m = create_town_markers(m, iso, int(month))
        folium.LayerControl().add_to(m)

        el = folium.MacroElement().add_to(m)
        map_name = m.get_name()
        el._template = jinja2.Template("""
                    {%% macro script(this, kwargs) %%}        
                    // folium variables
                    map = %s;
                    geojson = %s;

                    // console.log(geojson._tooltip._source)


                    // click event in country layer
                    map.on('click', function(e) {
                        $.ajax({
                            url:"http://localhost:5000/countryInfo",
                            type: "post",
                            data: JSON.stringify({'country': geojson._tooltip._source.feature.properties.name, 'id': geojson._tooltip._source.feature.id}),
                            crossDomain: true,
                            dataType: 'html',
                            contentType: 'application/json; charset=utf-8',
                            success: function(response) {
                                window.parent.postMessage(response, "*");
                            }, 
                            error: function(err) {
                                console.log('something went wrong')
                                console.error(err)
                            }
                        });
                    });
                    {%% endmacro %%}
                """ % (map_name, geojson))

        return m._repr_html_()


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


@app.route('/events')
def events():
    global empty_map_view
    if empty_map_view is None:
        map, geojson = create_empty_map()
        add_event_macro(map, geojson)
        empty_map_view = map._repr_html_()
    return render_template('events.html', title='Events', foliummap=empty_map_view)


@app.route('/sendPreset', methods=["POST"])
@cross_origin()
def sendPreset():
    print("sendpreset called")
    if request.method == 'POST':
        query = request.json['value']
        views = {'top10_vacc': get_top10_vacc_coverage(), 'safe_asia': get_safe_countries_asia(),
                 'measles': get_measles_threats()}
        map = folium.Map(max_bounds=True, height=str(80) + '%', location=[0, 0], zoom_start=1.5, min_zoom=1,
                         min_lat=-90,
                         max_lat=90,
                         min_lon=-180,
                         max_lon=180)

        qryResult = views[query]
        df_results = get_as_df(qryResult, ['country'])
        df_results['vals'] = np.ones(df_results.shape[0])

        layer = folium.Choropleth(geo_data='world_countries.json',
                                  name=query,
                                  data=df_results,
                                  columns=['country', 'vals'],
                                  key_on='feature.properties.name',
                                  fill_color='YlGn',
                                  fill_opacity=0.7,
                                  line_opacity=0.2,
                                  nan_fill_opacity=0
                                  ).add_to(map)
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
        geojson.add_to(layer)


        return map._repr_html_()


@app.route('/presets')
def presets():
    map = folium.Map(max_bounds=True, height=str(80) + '%', location=[0, 0], zoom_start=1.5, min_zoom=1,
                     min_lat=-90,
                     max_lat=90,
                     min_lon=-180,
                     max_lon=180)

    qryResult = get_top10_vacc_coverage()
    df_results = get_as_df(qryResult, ['country'])
    df_results['vals'] = np.ones(df_results.shape[0])
    layer = folium.Choropleth(geo_data='world_countries.json',
                              name='Top-10 Vaccination Coverage',
                              data=df_results,
                              columns=['country', 'vals'],
                              key_on='feature.properties.name',
                              fill_color='YlGn',
                              fill_opacity=0.7,
                              line_opacity=0.2,
                              nan_fill_opacity=0
                              ).add_to(map)
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
    geojson.add_to(layer)

    return render_template('presets.html', title='Presets', foliummap=map._repr_html_())


@app.route('/resources')
@cross_origin(supports_credentials=True)
def resources():
    matched_res = get_resources(request.args['q'])
    res_dict = {'results': [{'value': x} for x in matched_res]}
    return jsonify(res_dict)


@app.route('/resourceCountries', methods=["POST"])
@cross_origin()
def resource_countries():
    matched_countries = get_related_countries(request.json['resource'])
    res_dict = {'results': matched_countries}
    print(matched_countries)
    return jsonify(res_dict)
