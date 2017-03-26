/*
    Portions of the code relating to Google Maps were taken from the Udacity Google Maps course
    and modified. Also some structural inspiration from the todomvc knockout example.
 */


var map;
var mapConfig = {};
var restaurants = [];
var cuisines = [];
var markers = [];

var viewModel;

//Sydney
var mapLat = -33.910533;
var mapLng = 151.15634;

//NYC
// var mapLat = 40.787011;
// var mapLng = -73.975368;

function initMap() {
    // Constructor creates a new map - only center and zoom are required.
    map = new google.maps.Map(document.getElementById('map-canvas'), {
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
                    avgCostForTwo: zRest.average_cost_for_two,
                    geocode: {
                        lat: Number(zRest.location.latitude),
                        lng: Number(zRest.location.longitude)
                    }
                };
                restaurant.marker = createMarker(restaurant);

                restaurants.push(restaurant);
            }

            map.fitBounds(mapConfig.bounds);
            initCuisines();
        },
        error: function(err) {
            var errorMsg = '<div class="alert alert-danger" role="alert">Whoops!! <br><br>There was an error ' +
                'retrieving the restaurant details. Please try again later.<br><br>:(';
            $('#side-panel').html(errorMsg);
        }
    });
}


function createMarker(restaurant) {
    var marker = new google.maps.Marker({
        // map: null,
        position: restaurant.geocode,
        title: restaurant.name,
        animation: google.maps.Animation.DROP,
        id: restaurant.name
    });

    // Create an onclick event to open an infowindow at each marker.
    marker.addListener('click', function() {
        viewModel.selectedRestaurant(restaurant.name);
        populateInfoWindow(restaurant, mapConfig.largeInfowindow);
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


// This function populates the infowindow when the marker is clicked. We'll only allow
// one infowindow which will open at the marker that is clicked, and populate based
// on that markers position.
function populateInfoWindow(restaurant, infowindow) {
    var marker = restaurant.marker;
    // Check to make sure the infowindow is not already opened on this marker.
    if (infowindow.marker != marker) {
        var contentHtml = '<strong>' + restaurant.name + '</strong><br>' +
            'Average cost for two is $' + restaurant.avgCostForTwo + '<br><br>' +
            restaurant.address;

        infowindow.marker = marker;
        infowindow.setContent(contentHtml);
        infowindow.open(map, marker);
        marker.setAnimation(google.maps.Animation.DROP);

        // Make sure the marker property is cleared if the infowindow is closed.
        infowindow.addListener('closeclick',function(){
            infowindow.setMarker = null;
        });
    }
}


function getRestaurantByName(restName) {
    return restaurants.find(function (restaurant) {
        return restaurant.name === restName;
    });
}


// Knockout
function knockItOut() {
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

        this.selectedRestaurant = ko.observable();

        this.selectedRestaurant.subscribe(function (selection) {
            populateInfoWindow(getRestaurantByName(selection), mapConfig.largeInfowindow);
        }.bind(this));

    };

    viewModel = new ViewModel();

    ko.applyBindings(viewModel);
}