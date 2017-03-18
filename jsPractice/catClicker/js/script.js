

var cat_list = [];

cat_list.push({name:"Magnus",imgSrc:"img/magnus.jpg"});
cat_list.push({name:"Nina",imgSrc:"img/nina.jpg"});
cat_list.push({name:"Bronson",imgSrc:"img/bronson.jpg"});
cat_list.push({name:"Lil Bub",imgSrc:"img/lilbub.jpg"});
cat_list.push({name:"Maru",imgSrc:"img/maru.jpg"});


for (var i = 0; i < cat_list.length; i++) {
    var cCat = cat_list[i];
    cCat.clickCount = 0;

    // Get the ul element
    var catUl = document.getElementById("top-cat-list");
    // Create new li element and add the name
    var catNameLi = document.createElement("li");
    catNameLi.appendChild(document.createTextNode(cat_list[i].name));
    // Add the click listener
    catNameLi.addEventListener('click', (function(catCopy) {
        return function() {
            // Clear the div
            var catDisplayDiv = document.getElementById("show-selected-cat");
            catDisplayDiv.innerHTML = "";
            // Add title
            var catTitle = document.createElement("h1");
            catTitle.appendChild(document.createTextNode(catCopy.name));
            catDisplayDiv.appendChild(catTitle);
            // Add click count
            var clickCountElem = document.createElement("h3");
            clickCountElem.appendChild(document.createTextNode(catCopy.clickCount.toString()));
            catDisplayDiv.appendChild(clickCountElem);

            // Add image
            var catImg = document.createElement("img");
            catImg.src = catCopy.imgSrc;
            catDisplayDiv.appendChild(catImg);

            catImg.addEventListener('click', function() {
                catCopy.clickCount++;
                clickCountElem.innerHTML = catCopy.clickCount.toString();
            });


        };
    })(cCat));
    // Add the new cat item to the list
    catUl.appendChild(catNameLi);
}