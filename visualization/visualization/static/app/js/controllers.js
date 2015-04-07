'use strict';

/* Controllers */
var mapControllers = angular.module('mapControllers',['phiServices']);
mapControllers.controller('LinkCtrl', ['$scope', '$q', 'Links', 'LinkFlows',
    function($scope, $q, Links, LinkFlows) {
        var map = L.map('map');
        // create the tile layer with correct attribution
        var bwUrl = 'http://{s}.www.toolserver.org/tiles/bw-mapnik/{z}/{x}/{y}.png'
	    var osmUrl= bwUrl;//'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

	    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	    var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});
	    map.setView(new L.LatLng(33.996806,-118.308935),12);
	    map.addLayer(osm);

        $q.all([Links.get(), LinkFlows.get()]).then(
            function(data) {
                var links = data[0];
                var flows = data[1];

                var values = Object.keys(flows).map(function(key){return flows[key];});

                var colormap = RedGreenColorMapper(values, LogScaler);
                var style = function (feature) {
                    var style = {
                        "color": colormap(flows[feature.id]),
                        "weight": 3,
                        "opacity": 0.65
                    };
                    return style;
                };

                L.geoJson(links.features, {
                    style: style
                }).addTo(map);
            });
    }]);

function HoverFilter(links, linkLinkMap, flows, colormap) {
    this.allLinks = new Set(links);
    this.linkSet = this.allLinks;
    this.layers = {};
    this.colors = {};
    this.clear = true;
    this.setLayers = function(layers) {
        for (var i of layers){
            this.layers[i.feature.id] = i;
        }
    }

    this.onUnhover = function() {
            this.clear = true;
            for(var i in this.layers){
                this.layers[i].setStyle({"color": "blue", "weight" : 2});
            }
        };

    var t = this;
    this.onHover = function(linkId) {
        if (!t.clear){
            t.onUnhover();
        }
        linkLinkMap.get(linkId).then( function(linkSet) {
            t.clear = false;
            linkSet = new Set(linkSet) || new Set();
            for(var i of linkSet){
                t.layers[i].setStyle({"color": '#00ff00',
                                      "weight" : 4,
                                      "opacity": 0.6});
                t.layers[i].bringToFront();
            }
            t.layers[linkId].setStyle({"color": 'magenta',
                                       "weight" : 10});
        });

    };

}

mapControllers.controller('RouteCtrl', ['$scope', '$q', 'Links', 'LinkFlows','LinkLinkMap',
    function($scope, $q, Links, LinkFlows, LinkLinkMap) {
        var map = L.map('map');
        // create the tile layer with correct attribution
        // var bwUrl = 'http://{s}.www.toolserver.org/tiles/bw-mapnik/{z}/{x}/{y}.png'
	    var osmUrl= 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

	    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	    var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});
	    map.setView(new L.LatLng(33.996806,-118.308935),12);
	    map.addLayer(osm);

        $q.all([Links.get(), LinkFlows.get()]).then(
            function(data) {
                var links = data[0];
                var flows = data[1];
                var linkLinkMap = LinkLinkMap;

                var linkids = [];
                links.features.forEach(function(val){linkids.push(val.id);});

                var values = Object.keys(flows).map(function(key){return flows[key];});

                var colormap = RedGreenColorMapper(values, LinearScaler);

                var hoverFilter = new HoverFilter(linkids, linkLinkMap, flows, colormap);

                var style = function (feature) {
                    var style = {
                        "color": "blue",
                        "weight": 2,
                        "opacity": .65
                    };
                    return style;
                };
                var highlightFeature = function (e) {
                    console.log(e.target.feature);
                    var linkid = e.target.feature.id;
                    hoverFilter.onHover(linkid);

                };

                var resetHighlight = function (e) {
                    hoverFilter.onUnhover();
                    console.log("resethover");
                };

                var onEachFeature = function (feature, layer) {
                    layer.on({
                        //mouseover: highlightFeature,
                        //mouseout: resetHighlight
                        click: highlightFeature
                    });
                };

                var geoLayer = L.geoJson(links.features, {
                    style: style,
                    onEachFeature: onEachFeature,
                });
                osm.on('click', resetHighlight);
                map.on('click', resetHighlight);
                geoLayer.addTo(map);
                hoverFilter.setLayers(geoLayer.getLayers());

            });
    }]);

function ToggledRegion(){
    this.regions = new Set();

    this.toggle = function (item){
        if (this.regions.has(item)){
            this.regions.delete(item);
        }
        else {
            this.regions.add(item);
        }
    };

    this.has = function (item){
        return this.regions.has(item);
    };
}

function StyleManager(defaultStyle, onStyle){
    this.default = defaultStyle;
    this.on = onStyle
    this.layers = {};
    this.applyStyle = function(predicate){
        for(var i in this.layers){
            if (predicate(this.layers[i].feature.id)){
                this.layers[i].setStyle(this.on);
            }
            else{
                this.layers[i].setStyle(this.default);
            }
        }
    };
}

mapControllers.controller('CellCtrl', ['$scope', '$q', 'Links', 'LinkFlows', 'Cells', 'ActiveCellLinks',
    function($scope, $q, Links, LinkFlows, Cells, ActiveCellLinks) {
        var map = L.map('map');
        // create the tile layer with correct attribution
        var bwUrl = 'http://{s}.www.toolserver.org/tiles/bw-mapnik/{z}/{x}/{y}.png'
	    var osmUrl= bwUrl;//'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

	    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	    var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});
	    map.setView(new L.LatLng(33.996806,-118.308935),12);
	    map.addLayer(osm);

        $q.all([Links.get(), LinkFlows.get(), Cells.get()]).then(
            function(data) {
                var links = data[0];
                var flows = data[1];
                var cells = data[2];
                console.log(cells);
                var values = Object.keys(flows).map(function(key){return flows[key];});

                var colormap = RedGreenColorMapper(values, LogScaler);
                var style = function (feature) {
                    var style = {
                        "color": colormap(flows[feature.id]),
                        "weight": 3,
                        "opacity": 0.65
                    };
                    return style;
                };

                var linkLayer = L.geoJson(links.features, {
                    style: style
                });
                linkLayer.addTo(map);
                var linkLayerStyleManager = new StyleManager({'opacity': 0}, {'opacity': .65});
                linkLayerStyleManager.layers = linkLayer.getLayers();

                var toggledRegions = new ToggledRegion();

                var defaultCellStyle = {
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0
                };

                var toggledCellStyle = {
                    "color": "orange",
                    "weight": 1,
                    "fillOpacity": 0.7
                };

                var cellStyleManager = new StyleManager(defaultCellStyle, toggledCellStyle);

                var toggleFeature = function(e) {
                    var cellid = e.target.feature.id;
                    toggledRegions.toggle(cellid);
                    cellStyleManager.applyStyle(function(x){return toggledRegions.has(x);});
                    var activecells = [];
                    for(var c of toggledRegions.regions){
                        activecells.push(c);
                    }
                    ActiveCellLinks.get(activecells).then(function(data) {linkLayerStyleManager.applyStyle(function(x){return data.has(x);})});
                };

                var onEachFeature = function (feature, layer) {
                    layer.on({
                        click: toggleFeature
                    });
                };

                var geoLayer = L.geoJson(cells.features, {
                    style: defaultCellStyle,
                    onEachFeature: onEachFeature
                });

                cellStyleManager.layers = geoLayer.getLayers();

                geoLayer.addTo(map);
            });
    }]);
