var map, currentPosition;

function initStaticGoogleMap() {
  console.log("start initStaticGoogleMap");
  var mapContainer = document.getElementById("map");
  var latitude = 35.0;
  var longitude = 140.0;
  if (mapContainer.dataset) {
    var lat = parseFloat(mapContainer.dataset.latitude);
    var lng = parseFloat(mapContainer.dataset.longitude);
    if (!isNaN(lat) && !isNaN(lng)) {
      latitude = lat;
      longitude = lng;
    }
  }
  var zoom = parseInt(mapContainer.dataset.zoom);
  // mapContainer.
  map = new google.maps.Map(mapContainer, {
    center: {lat: latitude, lng: longitude},
    zoom: zoom,
    disableDefaultUI: true,
    draggable: false,
    scrollwheel: false
  });
  window.map = map;
  console.log("end initStaticGoogleMap");
}

function initGoogleMap() {
  console.log("start initGoogleMap");
  var mapContainer = document.getElementById("map");
  var lat = parseFloat(mapContainer.dataset.latitude);
  var lng = parseFloat(mapContainer.dataset.longitude);
  var zoom = parseInt(mapContainer.dataset.zoom);
  if (localStorage.lastPosition) {
    var last = JSON.parse(localStorage.lastPosition);
    if (isNaN(lat) && last.latitude) lat = last.latitude;
    if (isNaN(lng) && last.longitude) lng = last.longitude;
    if (isNaN(zoom) && last.zoom) zoom = last.zoom;
  }
  // mapContainer.
  map = new google.maps.Map(mapContainer, {
    center: {lat: lat, lng: lng},
    zoom: zoom,
  });
  google.maps.event.addListener(map, "center_changed", function(evt) {
    var latlng = map.getCenter();
    localStorage.lastPosition =
      JSON.stringify({ latitude:  latlng.lat(), 
                       longitude: latlng.lng(),
                       zoom: map.getZoom() });
  });
  console.log("end initGoogleMap");

  var mouseDown = undefined;
  google.maps.event.addListener(map, "mousedown", function(evt) {
    mouseDown = {
      "time": new Date(),
      "pixel": evt.pixel
    };
    cancel_info_window();
  });
  google.maps.event.addListener(map, "mouseup", function(evt) {
    if ((new Date()) - mouseDown.time > 400 &&
        calc_distance(mouseDown.pixel, evt.pixel) < 40) {
      longpress_listener(evt);
      mouseDown = undefined;
    }
  });
}

function calc_distance(p0, p1) {
  return Math.sqrt((p0.x - p1.x) * (p0.x - p1.x) +
                   (p0.y - p1.y) * (p0.y - p1.y));
}

var lastInfoWindow = null;
function showInfoWindowOnPoint(map, position, content) {
  var infowin = new google.maps.InfoWindow({
    content: content,
    maxWidth: 200,
    position: position
  });
  cancel_info_window();
  infowin.open(map);
  lastInfoWindow = infowin;
}
function showInfoWindowOnMarker(map, marker, content) {
  var infowin = new google.maps.InfoWindow({
    content: content,
    maxWidth: 200
  });
  cancel_info_window();
  infowin.open(map, marker);
  lastInfoWindow = infowin;
}

function cancel_info_window() {
  if (lastInfoWindow) lastInfoWindow.close();
}

function longpress_listener(evt) {
  var latlng =  + "," + evt.latLng.lng();
  var url = "/onsen/form" +
      "?latitude=" + evt.latLng.lat() +
      "&longitude=" + evt.latLng.lng();
  var content =
    "<div><h3>ここに温泉を登録しますか？</h3>" +
    "<div style='text-align:center'><a href=\""+url+"\">はい</a> / " +
    "<a href=\"javascript:cancel_info_window();\">いいえ</a></div>";
  showInfoWindowOnPoint(map, evt.latLng, content);
}

function success_list(list) {
  console.log("success", list);
  
  for (var i = 0; i < list.length; i++) {
    var onsen = list[i];
    
    // var $point = $make_point(p);
    // $points_list.append($point);
    
    var latlng = new google.maps.LatLng(onsen.latitude, onsen.longitude);
    var marker = new google.maps.Marker({
      position: latlng,
      // label: ""+i,
      title: onsen.name,
      // https://sites.google.com/site/gmapsdevelopment/
      icon: "http://maps.google.com/mapfiles/ms/micons/red-pushpin.png"
    });
    if (map) {
      function attach(o, marker) {
        google.maps.event.addListener(marker, "click", function(evt) {
          var content = 
              "<div><h3><a href=\"/onsen/" + o.id + "\">" + o.name + "</a></h3>" +
              "<p>" + o.character + "</p></div>" +
              "<p>" + o.address + "</p></div>";
          showInfoWindowOnMarker(map, marker, content);
        });
        marker.setMap(map);
      }
      attach(onsen, marker);
    }
  }
  // points_list[i] = {
  //   "point": list[i],
  //   "marker": marker,
  //   "element": $point, 
  //   "id": list[i].id
  // }
}

document.addEventListener('DOMContentLoaded', function() {
  url = '/api/onsen';

  fetch(url).then(response => response.json()).then(success_list);
  console.log('OK');
});

