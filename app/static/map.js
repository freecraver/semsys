$(function () {
    window.addEventListener("message", receiveMessage, false);

    function receiveMessage(event) {
        $('#country_info').append(event.data);
        // ...
    }
});