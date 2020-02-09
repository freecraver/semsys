$(function () {

    // Instantiate the Bloodhound suggestion engine
    var newsResources = new Bloodhound({
        datumTokenizer: function (datum) {
            return Bloodhound.tokenizers.whitespace(datum.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            wildcard: '%QUERY',
            url: 'http://localhost:5000/resources?q=%QUERY',
            prepare: function(query, settings) {
                  settings.beforeSend = function(jqXHR, settings) {
                    settings.xhrFields = { withCredentials: true };
                  };
                  settings.url = settings.url.replace('%QUERY', query);
                  return settings;
            },
            transform: function (response) {
                return response.results;
            }
        }
    });

    // Instantiate the Typeahead UI
    $('#typeahead').typeahead(null, {
        display: 'value',
        source: newsResources
    });

    // select listener
    $('#typeahead').on('typeahead:selected', function(evt, item) {
        $.ajax({
                url:"http://localhost:5000/resourceCountries",
                type: "post",
                data: JSON.stringify({'resource': item.value}),
                crossDomain: true,
                dataType: 'html',
                contentType: 'application/json; charset=utf-8',
                success: function(response) {
                    $("iframe").get(0).contentWindow.postMessage(response, "*");
                },
                error: function(err) {
                    console.error(err)
                }
            });
    })


});