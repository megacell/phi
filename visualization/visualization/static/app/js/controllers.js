'use strict';

/* Controllers */

var expenseControllers = angular.module('expenseControllers', ['ngCookies']);

expenseControllers.controller('SignInCtrl', ['$scope', '$location', '$cookieStore', 'Token',
  function($scope, $location, $cookieStore, Token) {
    $scope.token = $cookieStore.get('token');
    if ($scope.token !== undefined) {
        $location.path('/expenses');
        return;
    }

    $scope.save = function (user) {
      if (user === undefined) {
        return;
      }

      Token.signIn(user, function(token) {
        $cookieStore.put('token', token.token);
        $location.path('/expenses');
      });
    };
  }]);

expenseControllers.controller('SignUpCtrl', ['$scope', '$location', 'User',
  function($scope, $location, User) {

    $scope.save = function (user) {
      if (user === undefined) {
        return;
      }

      User.create(user,
        function(user) {
            $location.path('/signin');
        }
      );
    };
  }]);

expenseControllers.controller('ExpenseListCtrl', ['$scope', '$http', '$location', '$cookieStore', 'Expense',
  function($scope, $http, $location, $cookieStore, Expense) {
    $scope.token = $scope.token || $cookieStore.get('token');
    if ($scope.token === undefined){
        $location.path('/signin');
    }
    $http.defaults.headers.common['Authorization'] ='JWT ' + $scope.token;
    Expense.query({},function(list) {
        $scope.expenses = list
    });
  }]);
