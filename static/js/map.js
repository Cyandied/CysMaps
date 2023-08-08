async function fetchFromJson(place) {
    const response = await fetch(`/${place}`)
    const data = await response.json()
    return data
}

async function doAll() {
    const map_name = document.querySelector("#map-name").value
    const max_zoom = document.querySelector("#max-zoom").value
    const min_zoom = document.querySelector("#min-zoom").value
    const path = document.querySelector("#path").value
    const recent_marker = document.querySelector("#recent-marker").value

    const default_pos = document.querySelector("#start_pos").value
    const default_zoom = document.querySelector("#start_zoom").value
    const bg_color = document.querySelector("#bg_color").value

    const current_map = document.querySelector("#map")

    let pos = eval(default_pos)
    let zoom = parseInt(default_zoom)
    if(recent_marker != "None"){
        pos = eval(recent_marker)
        zoom = parseInt(max_zoom)-1
    }

    var map = L.map("map").setView(pos, zoom)

    L.tileLayer(`/${path}/{z}/{x}/{y}.png`, {
        minZoom: parseInt(min_zoom),
        maxZoom: parseInt(max_zoom),
        noWrap: true
    }).addTo(map)

    current_map.style["background-color"] = bg_color

    const add_attribute = document.querySelectorAll(".add-attribute")
    const delete_attribute = document.querySelectorAll(".delete-attribute")
    const marker_display = document.querySelectorAll(".show-marker")

    add_attribute.forEach(button => {
        button.addEventListener("click", e => {
            const target = e.target.dataset.target
            let target_div = null
            const target_divs = document.querySelectorAll(`.attributes`)
            target_divs.forEach(thing => {
                if(thing.dataset.id == target){
                    target_div = thing
                }
            })
            const new_div = document.createElement("div")
            const input_key = document.createElement("input")
            const input_val = document.createElement("input")
            const delete_button = document.createElement("button")

            input_key.type = "text"
            input_key.name = `${target}.attribute.key`
            input_key.placeholder = "Name of attribute"

            input_val.type = "text"
            input_val.name = `${target}.attribute.val`
            input_val.placeholder = "Value of attribute"

            delete_button.type = "button"
            delete_button.classList.add("delete-attribute")
            delete_button.innerHTML = "&#10006"
            delete_button.addEventListener("click", e => {
                e.target.parentElement.remove()
            })

            new_div.appendChild(input_key)
            new_div.appendChild(input_val)
            new_div.appendChild(delete_button)

            target_div.appendChild(new_div)
        })
    })

    delete_attribute.forEach(button => {
        button.addEventListener("click", e => {
            e.target.parentElement.remove()
        })
    });

    const curr_lat = document.querySelector("#curr-lat")
    const curr_lang = document.querySelector("#curr-lang")

    const onclick_popup = L.popup()

    function onMapClick(e){
        curr_lat.value = e.latlng.lat
        curr_lang.value = e.latlng.lng
        onclick_popup
            .setLatLng(e.latlng)
            .setContent(`<button name="make-marker">Make marker here</button>`)
            .openOn(map)
    }

    map.on("click", onMapClick)

    function makeMarker(id, lat, lang, icontype) {
        const size = 30
        const iconImg = L.icon({
            iconUrl: `/images/icons/${icontype}`,
            iconSize: [size,size],
            iconAnchor: [size/2,size],
            popupAnchor: [0,-(size/2)]
        })

        const marker = L.marker([lat, lang],{icon:iconImg}).addTo(map)
        marker.id = id

        marker.addEventListener("click", e => {
            marker_display.forEach(marker => {
                marker.classList.add("hidden")
            })
            const display = document.querySelector(`#${id}`)
            display.classList.remove("hidden")
        })
    }

    const map_markers = await fetchFromJson(`map/${map_name}/map_markers`)
    for (const key in map_markers){
        makeMarker(map_markers[key].id, map_markers[key].pos[0], map_markers[key].pos[1], map_markers[key].icon)
    }

    const image_to_select = document.querySelectorAll(".image-to-select")
    const curr_icons = document.querySelectorAll(".curr-icon")

    image_to_select.forEach(image => {
        image.addEventListener("click", e => {
            const target = e.target.dataset.icon
            const id = e.target.dataset.id
            curr_icons.forEach(curr_icon => {
                if(curr_icon.dataset.id == id){
                    curr_icon.value = target
                }
            })
            const deselects = document.querySelectorAll(".selected")
            deselects.forEach(deselect => {
                if(deselect.dataset.id == id){
                    deselect.classList.remove("selected")
                }
            })

            const display_icons = document.querySelectorAll(`.display-image`)
            display_icons.forEach(display_icon => {
                if(display_icon.dataset.id == id){
                    display_icon.src = `/images/icons/${target}`
                }
            })

            e.target.classList.add("selected")

        })
    })

}

doAll()