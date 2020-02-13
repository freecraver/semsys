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

// function get_capitals(e) {
//     console.log("get capitals");
//     console.log(e.checked);
//     if (e.checked) {
//         let params = {
//             value: 'all'
//         };
//
//         fetch(`${window.origin}/getcapitals`, {
//             method: "GET",
//             // credentials: "include",
//             // body: JSON.stringify(params),
//             // cache: "no-cache",
//             // headers: new Headers({
//             //     "content-type": "application/json"
//             // })
//         })
//             .then(function (response) {
//                 if (response.status !== 200) {
//                     console.log(`Looks like there was a problem. Status code: ${response.status}`);
//                     return;
//                 }
//                 response.json().then(function (response) {
//                     const map_div = document.getElementById('map_div');
//                     while (map_div.firstChild) {
//                         map_div.removeChild(map_div.firstChild);
//                     }
//
//
//                     console.log(response.data);
//
//                     map_div.innerHTML=response.data;
//                 });
//             })
//             .catch(function (error) {
//                 console.log("Fetch error: " + error);
//             });
//     }
// }