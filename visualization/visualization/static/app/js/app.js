'use strict';

/* App Module */

var phonecatApp = angular.module('visApp', [
  'ngRoute',
  'mapControllers',
]);

phonecatApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/links', {
        templateUrl: 'static/app/partials/links.html',
      }).
      when('/routes', {
        templateUrl: 'static/app/partials/routes.html',
      }).
      when('/cells', {
        templateUrl: 'static/app/partials/cells.html',
      }).
      otherwise({
        redirectTo: '/links'
      });
  }]);