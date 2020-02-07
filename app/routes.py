import folium
import jinja2
from flask import render_template, request, jsonify
from flask_cors import cross_origin

from app import app
from app.maps import create_risk_map, create_capitals
from dal.sparql_queries import get_countries_with_risk_score
from util.pd_utils import get_as_df


@app.route('/home')
def home():
    m, geojson = create_risk_map()
    m = create_capitals(m)
    folium.LayerControl().add_to(m)

    # TODO add extra html, css, javascript to map here
    el = folium.MacroElement().add_to(m)
    map_name = m.get_name()
    el._template = jinja2.Template("""
        {%% macro script(this, kwargs) %%}
        // write JS here
        console.log('hello world')
        
        // folium variables
        map = %s;
        geojson = %s;
        
        const sendPost = async (c) => {
            const url = 'http://localhost:5000/countryInfo'; // the URL to send the HTTP request to
            const body = JSON.stringify({'country': c}); // whatever you want to send in the body of the HTTP request
            const headers = {'Content-Type': 'application/json', 'Access-Control-Allow-Origin':'*'}; // if you're sending JSON to the server
            const method = 'POST';
            const response = await fetch(url, { method, body, headers });
            const data = await response.json(); // or response.json() if your server returns JSON
            console.log(data);
        }
        
        // click event in country layer
        map.on('click', function(e) {
            console.log(geojson._tooltip._source.feature.properties.name);
            sendPost(geojson._tooltip._source.feature.properties.name);
        });
        {%% endmacro %%}
    """ % (map_name, geojson))
    return render_template('map.html', title='Home', foliummap=m._repr_html_())


@app.route('/countryInfo', methods=["POST"])
@cross_origin()
def country_info():
    if request.method == 'POST':
        country = request.json['country']
        print(country)
        return jsonify(data='got country %s' % country)


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
