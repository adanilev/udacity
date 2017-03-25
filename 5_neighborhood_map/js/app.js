/*
    Portions of the code relating to Google Maps were taken from the Udacity Google Maps course
    and modified. Also some structural inspiration from the todomvc knockout example.
 */


var map;
var restaurants = [];
var cuisines = [];
var markers = [];

// Knockout
function knockItOut() {

    // The Model
    // ???

    // The ViewModel
    var ViewModel = function () {

        this.sidePanelHeading = ko.observable('Restaurants');

        this.selectedCuisine = ko.observable('All');

        this.cuisineList = ko.observableArray(cuisines);

        this.restaurantList = ko.observableArray(restaurants);

        this.filteredRestaurantList = ko.computed(function () {
            var self = this;
            return this.restaurantList().filter(function (restaurant) {
                if (restaurant.cuisines.indexOf(self.selectedCuisine()) >= 0) {
                    return restaurant;
                }
            });
        }.bind(this));

        this.markers = ko.observableArray(markers);

        this.filteredMarkers = ko.computed(function () {
            var self = this;
            return this.restaurantList().filter(function (restaurant) {
                if (restaurant.cuisines.indexOf(self.selectedCuisine()) >= 0) {
                    return restaurant;
                }
            });
        }.bind(this));

        this.testVar = '';

    };

    var viewModel = new ViewModel();

    ko.applyBindings(viewModel);
}




// Get the locations from Zomato
function initLocations() {
    var mapLat = -33.910533;
    var mapLng = 151.15634;

    // Get the restaurants near the geocode above from the Zomato API
    $.ajax({
        url: 'https://developers.zomato.com/api/v2.1/geocode',
        headers: {
            'user-key': 'a67b3434b85fd6744185c6ed4b638ae4'
        },
        dataType: 'json',
        data: {
            lat: mapLat,
            lon: mapLng
        },
        success: function(res) {
            var zomatoResponse = res.nearby_restaurants;

            // Create a simpler object with just the data we need
            for (var i=0; i < zomatoResponse.length; i++) {
                var zRest = zomatoResponse[i].restaurant;
                var rest = {
                    name: zRest.name,
                    cuisines: zRest.cuisines,
                    address: zRest.location.address,
                    geocode: {
                        lat: Number(zRest.location.latitude),
                        lng: Number(zRest.location.longitude)
                    }
                }
                restaurants.push(rest);
            }
            console.log('restaurants object');
            console.log(restaurants);

            initCuisines();
            initMap(mapLat, mapLng);
        },
        error: function(err) {
            //TODO: make the UI show there was an error
            console.log('There was an error calling Zomato\'s API' + err.responseText);
        }
    });
}


function initCuisines() {
    var tmpSet = new Set();
    for(var i=0; i < restaurants.length; i++) {
        var cuisineList = restaurants[i].cuisines.split(', ');
        cuisineList.push('All');
        restaurants[i].cuisines = cuisineList;
        for (var j=0; j < cuisineList.length; j++) {
            tmpSet.add(cuisineList[j]);
        }
    }

    tmpSet.forEach(function(cuisine) {
        cuisines.push(cuisine);
    });
    cuisines.sort();
}


function initMap(mapLat, mapLng) {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map-panel'), {
        center: {lat: mapLat, lng: mapLng},
        zoom: 15
    });

    var largeInfowindow = new google.maps.InfoWindow();
    var bounds = new google.maps.LatLngBounds();


    //TODO: move adding the markers to knockItOut so the map loads and then the markers appear
    // also, the markers should be an computed/observable array like the filteredList

    // The following group uses the location array to create an array of markers on initialize.
    for (var i = 0; i < restaurants.length; i++) {
        // Get the position from the location array.
        var position = restaurants[i].geocode;
        var title = restaurants[i].name;
        // Create a marker per location, and put into markers array.
        var marker = new google.maps.Marker({
            map: map,
            position: position,
            title: title,
            animation: google.maps.Animation.DROP,
            id: i,
        });
        // Push the marker to our array of markers.
        markers.push(marker);
        // Create an onclick event to open an infowindow at each marker.
        marker.addListener('click', function() {
            populateInfoWindow(this, largeInfowindow);
        });
        bounds.extend(markers[i].position);
    }
    // Extend the boundaries of the map for each marker
    map.fitBounds(bounds);

    knockItOut();

}