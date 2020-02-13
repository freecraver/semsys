import folium
import jinja2
from flask import render_template, request, jsonify
from flask_cors import cross_origin

from app import app
from app.maps import create_risk_map, create_capitals, create_empty_map, create_ski_resorts
from dal.sparql_queries import get_countries_with_risk_score, get_country_info, get_resources, get_related_countries, get_top10_vacc_coverage,get_safe_countries_asia,get_measles_threats
from util.folium_macros import add_event_macro
from util.pd_utils import get_as_df
import numpy as np


@app.route('/')
@app.route('/home')
def home():
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
    return render_template('map.html', title='Home', foliummap=m._repr_html_())


@app.route('/countryInfo', methods=["POST"])
@cross_origin()
def country_info():
    if request.method == 'POST':
        info = get_country_info(request.json['id'])
        ret = render_template('country_info.html', name=request.json['country'], risk=info[0][1], currency=info[0][3],
                              continent=info[0][2])

        return ret


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
    map, geojson = create_empty_map()
    add_event_macro(map, geojson)
    return render_template('events.html', title='Events', foliummap=map._repr_html_())


@app.route('/sendPreset', methods=["POST"])
@cross_origin()
def sendPreset():
    print("sendpreset called")
    if request.method == 'POST':
        query=request.json['value']
        views = {'top10_vacc': get_top10_vacc_coverage(), 'safe_asia': get_safe_countries_asia(),
                 'measles': get_measles_threats()}
        map = folium.Map(location=[0, 0], zoom_start=1.5)

        qryResult = views[query]
        df_results = get_as_df(qryResult, ['country'])
        df_results['vals'] = np.ones(df_results.shape[0])
        map.choropleth(geo_data='world_countries.json', data=df_results,
                       columns=['country', 'vals'],
                       key_on='feature.properties.name',
                       fill_color='OrRd', fill_opacity=0.7,
                       line_opacity=0.2, nan_fill_opacity=0)
        print("TEST")
        print(map._repr_html_())
        return map._repr_html_()



@app.route('/presets')
def presets():
    print("Routed to presets!")
    map = folium.Map(location=[0, 0], zoom_start=1.5)
    qryResult = get_top10_vacc_coverage()
    df_results = get_as_df(qryResult, ['country'])
    df_results['vals'] = np.ones(df_results.shape[0])
    map.choropleth(geo_data='world_countries.json', data=df_results,
                         columns=['country','vals'],
                          key_on='feature.properties.name',
                          fill_color='OrRd', fill_opacity=0.7,
                          line_opacity=0.2, nan_fill_opacity=0)


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
