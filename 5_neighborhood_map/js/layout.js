var $menuIcon = $('#menu-icon');
var $sidePanel = $('#side-panel');
var $mapPanel = $('#map-panel');

var isCollapsed = false;

$menuIcon.click(function() {
    if (isCollapsed) {
        $mapPanel.removeClass('col-md-12');
        $mapPanel.addClass('col-md-9');
    } else {
        $mapPanel.removeClass('col-md-9');
        $mapPanel.addClass('col-md-12');
    }
    $sidePanel.toggle();
    isCollapsed = !isCollapsed;
    google.maps.event.trigger(map, 'resize');
});
