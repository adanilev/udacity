
function loadData() {

    var $body = $('body');
    var $wikiElem = $('#wikipedia-links');
    var $nytHeaderElem = $('#nytimes-header');
    var $nytElem = $('#nytimes-articles');
    var $greeting = $('#greeting');

    // clear out old data before new request
    $wikiElem.text("");
    $nytElem.text("");

    // load streetview
    var street = $('#street').val();
    var city = $('#city').val();
    var address = street + ", " + city;

    var streetviewURL = 'http://maps.googleapis.com/maps/api/streetview?size=600x400&location=' + address + '&key=AIzaSyACnZ38LHwK-2Xj9bqybTDmmf3te98y6Wc';
    $greeting.text('So you want to live at ' + address + '?');
    $body.append('<img class="bgimg" src="'+ streetviewURL+ '">');


    // load nytimes articles
    var url = "https://api.nytimes.com/svc/search/v2/articlesearch.json";
    url += '?' + $.param({
            'api-key': "75930e5ac1e44882843d295501da4e50",
            'q': address
        });

    $.getJSON(url, function(result) {
        var articles = [];

        $.each(result.response.docs, function( key, doc ) {
            $nytElem.append('<li class="article">' +
                '<a href="' + doc.web_url + '">' + doc.headline.main + '</a>' +
                '<p>' + doc.snippet + '</p>' +
            '</li>');
        });

        $( "<ul/>", {
            "class": "article-list",
            html: articles.join("")
        });
    }).error(function(e){
        $nytElem.text('Whoops! NY Times articles could not be loaded at this time.');
    });

    // load wikipedia links
    var wikiUrl = 'https://en.wikipedia.org/w/api.php?action=opensearch&search=' +
        city + '&format=json&callback=wikiCallback';

    //doing this because jsonp doesn't let you have a .error style construct
    var wikiReqTimout = setTimeout(function() {     // ### This line is "binding" wikiReqTimeout to the setTimeout function
       $wikiElem.text('Failed to get Wikipedia articles!'); //this is
    }, 8000);

    $.ajax({
        url: wikiUrl,
        dataType: "jsonp",
        success: function(res) {
            var articleList = res[1];

            for (var i=0; i<articleList.length; i++) {
                var articleStr = articleList[i];
                var url = 'https://en.wikipedia.org/wiki/' + articleStr;
                $wikiElem.append('<li><a href="' + url + '">' + articleStr + '</a></li>');
            }
            clearTimeout(wikiReqTimout);

        }
    });

    return false;
}


$('#form-container').submit(loadData);
