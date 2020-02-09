import folium
import jinja2


def add_event_macro(map, geojson):
    el = folium.MacroElement().add_to(map)
    map_name = map.get_name()
    geojson_name = geojson.get_name()
    el._template = jinja2.Template("""
            {%% macro script(this, kwargs) %%}        
            // folium variables
            map = %s;
            geojson = %s;
            
            window.addEventListener("message", receiveMessage, false);

            function receiveMessage(event) {
                results = JSON.parse(event.data).results;
                geojson.eachLayer(function (layer) {  
                    if (results.includes(layer.feature.properties.name)) {
                        // matched country
                        layer.setStyle({fillColor :'rgb(179, 0, 0)', opacity: 1, fillOpacity: 1});
                    } else {
                        layer.setStyle({fillColor :'white', opacity: 0, fillOpacity: 0});
                    }
                    //debugger;
                });
            }
            {%% endmacro %%}
        """ % (map_name, geojson_name))