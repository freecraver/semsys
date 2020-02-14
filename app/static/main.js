function w3_toggle() {
    let element = document.getElementById("mySidebar");
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}

function collapse_sibling(e) {
    e.classList.toggle("active");
    let content = e.nextElementSibling;
    if (content.style.maxHeight) {
        content.style.maxHeight = null;
    } else {
        content.style.maxHeight = content.scrollHeight + "px";
    }
}

function get_towns(e) {
    console.log('get_towns');
    console.log(e);

    let iso = 'AUT';
    if (document.getElementById('selected_iso') !== null) {
        console.log('iso not null');
        iso = document.getElementById('selected_iso').innerHTML;
    }
    console.log('iso ' + iso);
    $.ajax({
        url: "http://localhost:5000/towns",
        type: "POST",
        data: JSON.stringify({'iso': iso, 'month': e}),
        crossDomain: true,
        dataType: 'html',
        contentType: 'application/json; charset=utf-8',
        success: function (response) {

            let map_div = document.getElementById('country_info_map_div');
            while (map_div.firstChild) {
                map_div.removeChild(map_div.firstChild);
            }
            map_div.innerHTML = response;
        },
        error: function (err) {
            console.log('something went wrong');
            console.error(err)
        }
    });

}