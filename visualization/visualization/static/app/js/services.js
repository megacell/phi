var phiServices = angular.module('phiServices', []);
phiServices.factory('Links', ['$http',
    function($http) {
        var service = {
        get: function() {
            return $http.get('/phidata/links/').then(
                function(result) {
                    return result.data;
                });}
        };
        return service;
    }]);

phiServices.factory('LinkFlows', ['$http',
    function($http) {
        var service = {
        get: function() {
            return $http.get('/phidata/flows/').then(
                function(result) {
                    var dictionary = {};
                    result.data.forEach(function (flow) {dictionary[flow.link_id] = flow.flow;});
                    return dictionary;
                });}
        };
        return service;
    }]);

function createLinkRouteMap(routeLinkMap) {
    var linkRouteMap = {};
    for (var route in routeLinkMap) {
        var links = routeLinkMap[route];
        links.forEach(
            function (link){
                if (!(link in linkRouteMap)){
                    linkRouteMap[link] = new Set();
                }
                linkRouteMap[link].add(route);
            }
        );
    }
    return linkRouteMap
}

function convertLrMapToLMap(linkRouteMap, routeLinkMap){
    var linkMap = {};
    for (var key in linkRouteMap) {
        if (!(key in linkMap)) {
            linkMap[key] = new Set();
        }

        var routes = linkRouteMap[key];
        routes.forEach(
            function(route) {
                routeLinkMap[route].forEach(
                    function(link) {
                        linkMap[key].add(link);
                    }
                );
            }
        );
    }
    return linkMap;
}

function routeLinkMapFromData(data){
    var routes = {};
    data.forEach(function(val){
        routes[val.id] = new Set(eval(val.links));
    });
    return routes;
}

phiServices.factory('LinkLinkMap', ['$http',
    function($http) {
        var service = {
            get: function(link_id) {
                url = '/phidata/linktable/' + link_id + '/';
                return $http.get(url).then(
                    function(result) {
                        return result.data[0]['links'];
                    });}
        };
        return service;
    }]);
phiServices.factory('Cells', ['$http',
    function($http) {
        var service = {
            get: function(){
                url = '/phidata/cells/';
                return $http.get(url).then(function(results) {
                    return results.data;
                });
            }
        }
        return service;
    }]);

phiServices.factory('ActiveCellLinks', ['$http',
    function($http) {
        var service = {
            get: function(list){
                url = '/phidata/cells/' + JSON.stringify(list) +'/';
                return $http.get(url).then(function(results) {
                    return new Set(results.data[0].links);
                });
            }
        }
        return service;
    }]);