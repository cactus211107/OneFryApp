let restaurant_markers = [];

function display_restaurant_buttons_on_map(buttons) {
    buttons.forEach(button => {
        const marker = new google.maps.Marker({
            position: { lat: button.lat, lng: button.lon },
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: "white",
                fillOpacity: 1,
                scale: 8,
                strokeColor: "red",
                strokeWeight: 3,
            },
            title: button.name || "Button " + button.id,
            id: button.id
        });
        marker.addListener('click', async function () {
            await goToRestaurant(marker.id);
        });

        restaurant_markers.push(marker);
    });
}

function remove_all_restaurant_map_icons() {
    restaurant_markers.forEach(marker => marker.setMap(null));
    restaurant_markers = [];
}
async function performTextSearch(query,max=4) {
    // Import the Places library
    const { PlacesService } = await google.maps.importLibrary("places");
    const map = new google.maps.Map(document.createElement('div'));
    const service = new PlacesService(map);
    const request = {
        query: query,
        fields: ['place_id', 'name', 'formatted_address', 'geometry', 'photos'],
    };

    // Return a promise (so await works)
    return new Promise((resolve, reject) => {
        service.textSearch(request, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                const places = results.map((p) => ({
                    id: p.place_id,
                    name: p.name,
                    address: p.formatted_address,
                    location: p.geometry.location,
                    photo: p.photos?.[0]?.getUrl({ maxWidth: 400 }) || ''
                }));
                resolve(places.slice(0,max));
            } else {
                reject(`Places search failed with status: ${status}`);
            }
        });
    });
}

async function goToRestaurant(restaurant_id) {
    console.log("Travelling to restaurant with id: " + restaurant_id);
    let data = await getRestaurant(restaurant_id)
    _putRestaurant(data)
    moveBox('restaurant-page', 'right')
}