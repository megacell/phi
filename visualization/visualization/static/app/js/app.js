'use strict';

/* App Module */

var phonecatApp = angular.module('expenseApp', [
  'ngRoute',
  'expenseControllers',
  'expenseServices',
]);

phonecatApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/home', {
        templateUrl: 'static/app/partials/home.html',
      }).
      when('/expenses', {
        templateUrl: 'static/app/partials/expenses.html',
        controller: 'ExpenseListCtrl',
      }).
      when('/signin', {
        templateUrl: 'static/app/partials/signin.html',
        controller: 'SignInCtrl'
      }).
      when('/signup', {
        templateUrl: 'static/app/partials/signup.html',
        controller: 'SignUpCtrl'
      }).
      otherwise({
        redirectTo: '/home'
      });
  }]);