$(function () {
    window.addEventListener("message", receiveMessage, false);

    function receiveMessage(event) {
        // $('#country_info').append(event.data);
        const map_div = document.getElementById('country_info');
        while (map_div.firstChild) {
            map_div.removeChild(map_div.firstChild);
        }

        map_div.innerHTML = event.data;
    }
});