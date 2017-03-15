
var clickCount1 = 0;
var clickCount2 = 0;

var $countElem1 = $('#click-count1');
var $countElem2 = $('#click-count2');

var $cat1 = $('#cat-pic1');
var $cat2 = $('#cat-pic2');

var catName1 = 'Nina';
var catName2 = 'Magnus';

var catImgSrc1 = 'img/nina.jpg';
var catImgSrc2 = 'img/magnus.jpg';

$('#cat-name1').text(catName1);
$('#cat-name2').text(catName2);


$cat1.attr("src", catImgSrc1);
$cat2.attr("src", catImgSrc2);



$('#cat-pic1').click(function(e) {
    clickCount1++;
    $countElem1.text(clickCount1);
});

$('#cat-pic2').click(function(e) {
    clickCount2++;
    $countElem2.text(clickCount2);
});