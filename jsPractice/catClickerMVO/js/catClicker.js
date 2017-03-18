$(function(){

    ////////////////////////
    // MODEL
    ////////////////////////
    var model = {
        currentCat: null,

        cats: [],

        init: function() {
            this.cats.push({name:"Magnus",imgSrc:"img/magnus.jpg"});
            this.cats.push({name:"Nina",imgSrc:"img/nina.jpg"});
            this.cats.push({name:"Bronson",imgSrc:"img/bronson.jpg"});
            this.cats.push({name:"Lil Bub",imgSrc:"img/lilbub.jpg"});
            this.cats.push({name:"Maru",imgSrc:"img/maru.jpg"});

            for (var i=0; i<this.cats.length; i++) {
                this.cats[i].numClicks = 0;
            }
        }
    };


    ////////////////////////
    // OCTOPUS
    ////////////////////////
    var octopus = {
        init: function() {
            model.init();
            catListView.init();
            catPanelView.init();
        },

        getAllCats: function() {
            return model.cats;
        },

        getCurrentCat: function() {
            return model.currentCat;
        },

        setCurrentCat: function(aCat){
           model.currentCat = aCat;
           catPanelView.render();
        },

        clickCat: function() {
            model.currentCat.numClicks++;
            catPanelView.render(model.currentCat);
        }
    };


    ////////////////////////
    // VIEWS
    ////////////////////////
    var catListView = {
        init: function() {
            this.catList = document.getElementById('cat-list');
            catListView.render();
        },

        render: function(){
            // Go through and add li for each cat
            var self = this;
            octopus.getAllCats().forEach(function(cat){
                var catNameLi = document.createElement("li");
                catNameLi.appendChild(document.createTextNode(cat.name));
                // Add click listener
                catNameLi.addEventListener('click', (function(cat) {
                    return function() {
                        octopus.setCurrentCat(cat)
                    };
                })(cat));
                self.catList.appendChild(catNameLi);
            });
        }
    };


    var catPanelView = {
        init: function() {
            this.catName = document.getElementById('cat-name');
            this.numClicks = document.getElementById('num-clicks');
            this.catImg = document.getElementById('cat-img');
            this.catImg.addEventListener('click', function() {
                octopus.clickCat();
            });
        },

        render: function(){
            var currentCat = octopus.getCurrentCat();
            this.catName.textContent = currentCat.name;
            this.catImg.src = currentCat.imgSrc;
            this.numClicks.textContent = currentCat.numClicks + " clicks!";

        }
    };

    octopus.init();
});