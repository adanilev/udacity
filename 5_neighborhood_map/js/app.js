/*
    Portions of the code relating to Google Maps were taken from the Udacity Google Maps course
    and modified. Also some structural inspiration from the todomvc knockout example.
 */


var map;
var mapConfig = {};
var restaurants = [];
var cuisines = [];
var markers = [];

//Sydney
var mapLat = -33.910533;
var mapLng = 151.15634;

//NYC
// var mapLat = 40.787011;
// var mapLng = -73.975368;

function initMap() {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map-panel'), {
        center: {lat: mapLat, lng: mapLng},
        zoom: 15
    });

    mapConfig.largeInfowindow = new google.maps.InfoWindow();
    mapConfig.bounds = new google.maps.LatLngBounds();

    initRestaurants();
}


// Get the locations from Zomato
function initRestaurants() {
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

                var restaurant = {
                    name: zRest.name,
                    cuisines: zRest.cuisines,
                    address: zRest.location.address,
                    geocode: {
                        lat: Number(zRest.location.latitude),
                        lng: Number(zRest.location.longitude)
                    }
                };
                restaurant.marker = createMarker(restaurant);

                restaurants.push(restaurant);
            }

            console.log('restaurants object');
            console.log(restaurants);

            map.fitBounds(mapConfig.bounds);
            initCuisines();
        },
        error: function(err) {
            //TODO: make the UI show there was an error
            console.log('There was an error calling Zomato\'s API' + err.responseText);
        }
    });
}


function createMarker(restaurant) {
    var marker = new google.maps.Marker({
        // map: null,
        position: restaurant.geocode,
        title: restaurant.name,
        animation: google.maps.Animation.DROP,
        id: Date.now()
    });

    // Create an onclick event to open an infowindow at each marker.
    marker.addListener('click', function() {
        //TODO: get this infoWindow working - need to create this function
        populateInfoWindow(this, mapConfig.largeInfowindow);
    });

    mapConfig.bounds.extend(marker.position);

    return marker;
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

    knockItOut();
}


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
                    restaurant.marker.setMap(map);
                    restaurant.marker.setAnimation(google.maps.Animation.DROP);
                    return restaurant;
                } else {
                    restaurant.marker.setMap(null);
                }
            });
        }.bind(this));

        this.testVar = '';

    };

    var viewModel = new ViewModel();

    ko.applyBindings(viewModel);
}