# Fancy Map App
This is a single page application that displays a list of restaurants and shows them on a map. It uses some of the following technologies:
* Google Maps API
* Zomato API
* Knockout JS framework
* jQuery
* Bootstrap CSS framework

## Installation
1. Download or clone this repo
1. Navigate to this folder in a terminal: `5_neighborhood_map`
1. Install dependencies using bower
    * `bower install`
    * If you don't have bower, install it by following the directions in [their documentation](https://bower.io/#install-bower)
1. Open up `index.html` in your browser of choice!    

## Usage
Should be pretty self explanatory. Load the page and click around. Some features to note:
* Filter the list of restaurants using the dropdown
* Select a restaurant by clicking either the list or the map pin
* See additional details in the info window on the map
* Hide/show the side panel by clicking the menu icon on the top left
* Change the location by opening app.js and changing the mapLat and mapLng variables at the top of the file and then reload the page