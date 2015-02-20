var expenseServices = angular.module('expenseServices', ['ngResource']);

expenseServices.factory('Token', ['$resource',
  function($resource){
    return $resource('token-auth', {}, {
      signIn: {method:'POST', data:{username:'username', password:'password'}}
    });
  }]);

expenseServices.factory('User', ['$resource',
  function($resource){
    return $resource('users/register', {}, {
      create: {method:'POST', data:{username:'username', email:'email',  password:'password'}}
    });
  }]);


expenseServices.factory('Expense',['$resource', '$http',
    function($resource, $http) {
        $http.defaults.headers.put['Content-Type'] = 'application/json';

        return $resource('expenses', {}, {});
    }]);