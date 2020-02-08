import folium
import jinja2
from flask import render_template, request, jsonify
from flask_cors import cross_origin

from app import app
from app.maps import create_risk_map, create_capitals, create_empty_map
from dal.sparql_queries import get_countries_with_risk_score, get_country_info, get_resources
from util.pd_utils import get_as_df


@app.route('/home')
def home():
    m, geojson = create_risk_map()
    m = create_capitals(m)
    folium.LayerControl().add_to(m)

    # TODO add extra html, css, javascript to map here
    # ugly, but it works
    el = folium.MacroElement().add_to(m)
    map_name = m.get_name()
    el._template = jinja2.Template("""
        {%% macro script(this, kwargs) %%}
        // write JS here
        console.log('hello world')
        
        // folium variables
        map = %s;
        geojson = %s;
        
        // console.log(geojson._tooltip._source)
        
        
        // click event in country layer
        map.on('click', function(e) {
            console.log(geojson._tooltip._source.feature.properties.name);
            $.ajax({
                url:"http://localhost:5000/countryInfo",
                type: "post",
                data: JSON.stringify({'country': geojson._tooltip._source.feature.properties.name, 'id': geojson._tooltip._source.feature.id}),
                crossDomain: true,
                dataType: 'html',
                contentType: 'application/json; charset=utf-8',
                success: function(response) {
                    console.log(response)
                    $('body').append(response) // find better solution
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
        print(request.json)
        info = get_country_info(request.json['id'])
        ret = render_template('country_info.html', infos=info)
        print(ret)
        return ret


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


@app.route('/events')
def events():
    # TODO: mark countries which match resource
    map = create_empty_map()
    return render_template('events.html', title='Events', foliummap=map._repr_html_())


@app.route('/resources')
@cross_origin(supports_credentials=True)
def resources():
    matched_res = get_resources(request.args['q'])
    res_dict = {'results': [{'value': x} for x in matched_res]}
    return jsonify(res_dict)