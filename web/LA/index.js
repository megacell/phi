function objToString (obj) {
  var str = '';
  for (var p in obj) {
    if (obj.hasOwnProperty(p)) {
      str += (p + ':' + obj[p] + '<br>');
    }
  }
  return str;
}

function interpolate( val, y0, x0, y1, x1 ) {
  return (val-x0)*(y1-y0)/(x1-x0) + y0;
}

function base( val ) {
  if ( val <= -0.75 ) return 0;
  else if ( val <= -0.25 ) return interpolate( val, 0.0, -0.75, 1.0, -0.25 );
  else if ( val <= 0.25 ) return 1.0;
  else if ( val <= 0.75 ) return interpolate( val, 1.0, 0.25, 0.0, 0.75 );
  else return 0.0;
}

function red( gray ) {
  return Math.floor(255*base( gray - 0.5 ));
}
function green( gray ) {
  return Math.floor(255*base( gray ));
}
function blue( gray ) {
  return Math.floor(255*base( gray + 0.5 ));
}

function color_from_taz( TAZ ) {
  TAZ = parseFloat(TAZ);
  if (valid_taz.indexOf(TAZ) >= 0) {
    return '#0000ff';
  } else {
    return '#000000';
  }
}

function jet_colors(value) {
  var s = 'rgb('+[red(value), green(value), blue(value)].join(',')+')';
  return s;
}

var colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];

start = undefined;
end = undefined;
var count = 0;
var map = L.map('map', {attributionControl: false}).setView([34.096, -117.948], 12);

var routes = L.featureGroup();
routes.addTo(map);

var worst_routes = L.featureGroup();

var sensors = L.featureGroup();
sensors.addTo(map);

var intersects = L.featureGroup();
var waypoints = L.featureGroup();
intersects.addTo(map);
waypoints.addTo(map);
function handle_sensor(sensor_data){
  var d = sensor_data['loc'];
  var percent_error = Math.abs(sensor_data['true'] - sensor_data['predicted']) / sensor_data['true'];
  var sensor = L.circle([d[1], d[0]], 25, {
    color: '#000000',
    fillColor: jet_colors(percent_error),
    weight: 1,
    fillOpacity: 1.0
  });
  sensor.bindPopup('True value: '+sensor_data['true']+'<br />\n'+'Predicted: '+sensor_data['predicted']);
  intersects.addLayer(sensor);
}

function handle_waypoint(waypoint_data){
  var c = waypoint_data.color;
  var geo = waypoint_data.geom.coordinates[0].map(function (d) {
    return [d[1], d[0]];
  });
  var waypoint = L.polygon(geo, {
    color: c[0],
    fillColor: c[1],
    fillOpacity: 0.6
  });
  waypoints.addLayer(waypoint);
}

function handle_routes(rts, fg) {
  rts.routes.forEach(function(d, i){
    var split_color = jet_colors(Math.abs(d.split_error));
    polyline = new L.Polyline(decode(d.overview_polyline.points), {
      color: split_color,
      opacity: 1.0
    });

    var distance = 0.0;
    var duration = 0.0;
    d.legs.forEach(function(leg){
      distance += leg.distance.value;
      duration += leg.duration.value;
    })
    polyline.bindPopup("alternative: " + i + "<br>distance: " + (Math.round((distance / 5280.0) * 100) / 100.0) + " miles<br>duration: " + (Math.round((duration / 60.0) * 100) / 100.0)  + " mins<br />True split: "+d.true_split+"<br />Predicted split: "+d.predicted_split+"<br />Number of sensors: "+d.num_sensors);
    polyline.on('popupopen', function(e){ e.target.setStyle({weight:10, color:'black'})});
    polyline.on('popupclose', function(e){ e.target.setStyle({weight:5, color:split_color})});
    fg.addLayer(polyline);
  });
}

var ods = new L.Shapefile('data/ods.zip',{onEachFeature:function(feature, layer) {
  if (feature.properties) {
    layer.id = count;
    taz = feature.properties.TAZ_ID + '.0';
    layer.setStyle({weight: 3, opacity: 0.4, color: color_from_taz(taz)});
  }

  layer.on("click", function(l){
    routes.clearLayers();
    intersects.clearLayers();
    waypoints.clearLayers();

    if (start == layer){
      start_taz = start.feature.properties.TAZ_ID + '.0';
      start.setStyle({color: color_from_taz(start_taz)});
      start = undefined;
      if (end != undefined) {
        o = end.feature.properties.TAZ_ID + '.0';

        values = [];
        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          values.push(TMP[o][d].value);
        }
        var extent = d3.extent(values);
        var scale = d3.scale.linear()
        .domain(extent)
        .range([0, 10]);

        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          for(p in TMP[o][d].polys){
            var polyline = TMP[o][d].polys[0];
            var pointList = [];
            polyline.forEach(function(p){
              pointList.push(new L.LatLng(p[1], p[0]));
            });
            if (scale(TMP[o][d].value) > 1) {
              routing.sensors(pointList, function(data) {
                data.forEach(handle_sensor);
              });
            }
            var pl = new L.Polyline(pointList, {
              color: 'red',
              weight: scale(TMP[o][d].value),
              opacity: 1,
              smoothFactor: 1
            }).addTo(routes);
          }
        }
      }
    } else if (end == layer){
      end_taz = end.feature.properties.TAZ_ID + '.0';
      end.setStyle({color: color_from_taz(end_taz)});
      end = undefined;
      if (start != undefined) {
        o = start.feature.properties.TAZ_ID + '.0';

        values = [];
        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          values.push(TMP[o][d].value);
        }
        var extent = d3.extent(values);
        var scale = d3.scale.linear()
        .domain(extent)
        .range([0, 10]);

        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          for(p in TMP[o][d].polys){
            var polyline = TMP[o][d].polys[0];
            var pointList = [];
            polyline.forEach(function(p){
              pointList.push(new L.LatLng(p[1], p[0]));
            });
            if (scale(TMP[o][d].value) > 1) {
              routing.sensors(pointList, function(data) {
                data.forEach(handle_sensor);
              });
            }
            var pl = new L.Polyline(pointList, {
              color: 'red',
              weight: scale(TMP[o][d].value),
              opacity: 1,
              smoothFactor: 1
            }).addTo(routes);
          }
        }
      }
    } else if(start == undefined){
      start = layer;
      layer.setStyle({color: '#00ff00'});
      if (end == undefined) {

        o = start.feature.properties.TAZ_ID + '.0';
        layer.setStyle({color: '#00ff00'});

        values = [];
        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          values.push(TMP[o][d].value);
        }
        var extent = d3.extent(values);
        var scale = d3.scale.linear()
        .domain(extent)
        .range([0, 10]);

        for(index in Object.keys(TMP[o])){
          d = Object.keys(TMP[o])[index];
          for(p in TMP[o][d].polys){
            polyline = TMP[o][d].polys[0];
            var pointList = [];
            polyline.forEach(function(p){
              pointList.push(new L.LatLng(p[1], p[0]));
            });
            if (scale(TMP[o][d].value) > 1) {
              routing.sensors(pointList, function(data) {
                data.forEach(handle_sensor);
              });
            }
            var pl = new L.Polyline(pointList, {
              color: 'red',
              weight: scale(TMP[o][d].value),
              opacity: 1,
              smoothFactor: 1
            }).addTo(routes);
          }
        }
      }
    } else if (end == undefined){
      end = layer;
      layer.setStyle({color: '#ff0000'});
    }

    if (start != undefined && end != undefined){
      var origin = start.getBounds().getCenter();
      var destination = end.getBounds().getCenter();
      var o = start.feature.properties.TAZ_ID + '.0';
      var d = end.feature.properties.TAZ_ID + '.0';
      console.log(o);
      console.log(d);
      routing.plan(origin.lat, origin.lng, destination.lat, destination.lng, o, d, function(data){
        intersects.clearLayers();
        waypoints.clearLayers();
        data[2].forEach(handle_waypoint);
        handle_routes(data[0], routes);
        data[1].forEach(handle_sensor);

      })
    }
    worst_routes.bringToFront();
  });

  count += 1;
  if(count == 321){
    d3.select('#loading').transition()
    .duration(1000)
    .style("opacity", 0.0).remove();
    d3.json("data/data.json", function(data) {
      TMP = data;
    });

    d3.csv("data/sensors.csv", function(data) {
      data.forEach(function(d){
        var sensor = L.circle([d.Latitude, d.Longitude], 25, {
          color: 'black',
          fillColor: '#f03',
          weight: 1,
          fillOpacity: 0.5
        });
        sensor.bindPopup(objToString(d));
        sensors.addLayer(sensor);
      });
    });
  }
}});
ods.addTo(map);

routing.get_worst_routes(function(data) {
  handle_routes(data, worst_routes);
});

var defaultLayer = L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);

var baseLayers = {
  'OpenStreetMap.Mapnik': defaultLayer,
  'Stamen.Toner': L.tileLayer.provider('Stamen.Toner'),
  'Stamen Watercolor': L.tileLayer.provider('Stamen.Watercolor'),
  "OpenStreetMap (Black & White)": L.tileLayer.provider('OpenStreetMap.BlackAndWhite'),
  "MapBox Example": L.tileLayer.provider('MapBox.examples.map-zr0njcqy'),
  "Thunderforest Transport": L.tileLayer.provider('Thunderforest.Transport'),
  "MapQuest Aerial": L.tileLayer.provider('MapQuestOpen.Aerial'),
  "Stamen Toner": L.tileLayer.provider('Stamen.Toner'),
  "Stamen Watercolor": L.tileLayer.provider('Stamen.Watercolor'),
  "Esri DeLorme": L.tileLayer.provider('Esri.DeLorme'),
  "Esri NatGeoWorldMap": L.tileLayer.provider('Esri.NatGeoWorldMap'),
  "Esri WorldGrayCanvas": L.tileLayer.provider('Esri.WorldGrayCanvas')
};

var overlayMaps = {
  'Routes': routes,
  'ODs': ods,
  'Sensors': sensors,
  'Worst Routes': worst_routes,
  'Yellows': intersects,
  'Waypoints': waypoints,
};

var controls = L.control.layers(baseLayers, overlayMaps, {collapsed: false});
controls.addTo(map);

function decode(encoded){

  // array that holds the points

  var points=[ ]
  var index = 0, len = encoded.length;
  var lat = 0, lng = 0;
  while (index < len) {
    var b, shift = 0, result = 0;
    do {

      b = encoded.charAt(index++).charCodeAt(0) - 63;//finds ascii
      //and substract it by 63
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);


    var dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
    lat += dlat;
    shift = 0;
    result = 0;
    do {
      b = encoded.charAt(index++).charCodeAt(0) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);
    var dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
    lng += dlng;


    points.push(new L.LatLng(lat / 1E5, lng / 1E5));
  }
  return points
}

function decode2(encoded){

  // array that holds the points

  var points="[";
    var index = 0, len = encoded.length;
    var lat = 0, lng = 0;
    while (index < len) {
      var b, shift = 0, result = 0;
      do {

        b = encoded.charAt(index++).charCodeAt(0) - 63;//finds ascii                                                                                    //and substract it by 63
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);


      var dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lat += dlat;
      shift = 0;
      result = 0;
      do {
        b = encoded.charAt(index++).charCodeAt(0) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      var dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
      lng += dlng;


      points += "[" + (lat / 1E5) + ","  + (lng / 1E5) + "]";
    }
    return points + "]"
}
