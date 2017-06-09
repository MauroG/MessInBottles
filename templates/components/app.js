(function() {
  //  APP DEFINITION AND ROUTE CONFIG
  angular.module('mib',['ngRoute', 'ngMessages']);
  angular.module('mib').config(function($routeProvider, $locationProvider) {
    $routeProvider
      .when('/', {
        redirectTo : '/question'
      })
      .when('/question', {
        templateUrl : 'components/pages/question.html',
        controller : 'question as ctrl'
      })
      .when('/notfound', {
        templateUrl : 'components/pages/notfound.html',
        controller : 'notfound as ctrl'
      })
      .when('/about', {
        templateUrl : 'components/pages/about.html',
        controller : 'about as ctrl'
      })
      .when('/report-bug', {
        templateUrl : 'components/pages/reportbug.html',
        controller : 'reportbug as ctrl'
      })
      .when('/login', {
        templateUrl : 'components/pages/login.html',
        controller : 'login as ctrl'
      })
      .when('/answer', {
        templateUrl : 'components/pages/answer.html',
        controller : 'answer as ctrl'
      })
      .otherwise({redirectTo : '/notfound'})
      ;
      $locationProvider.html5Mode(true);
  });

  //  CONSTANTS

  angular.module('mib').constant('API', {
    'restServer': "",
    'restEndPoint': "/api/v1/",
  });

  //  SERVICES
  angular.module('mib').service('QuestionService', function($http, $q, API) {
    var _response = {};
    this.askQuestion = function(question) {
      var deferred = $q.defer();
      $http({
        'method': "POST",
        'url': API.restServer + API.restEndPoint + 'test',
	'data': JSON.stringify(question),
      }).then(
        function(response) {
          _message = response.data.data;
          deferred.resolve(response.data);
        }, function(error) {
          deferred.reject(error);
        });
        return deferred.promise;
    };
    this.getResponse = function() {
      return _response;
    };
  });

  //  CONTROLLERS
  angular.module('mib').controller('question', function($location, QuestionService) {
    this.init = function() {changeCurrentPage('question')};
    this.question = {};
    this.submit = function(form) {
      if(this.question.question && this.question.email) {
        QuestionService.askQuestion(this.question).then(function(response) {
          this.question = {};
          form.$setUntouched();
          $location.path('/answer');
        }.bind(this), function(error) {
          console.log(error);
        });
      }
    }
  });
  angular.module('mib').controller('notfound', function() {
    this.init = function() {changeCurrentPage('notfound')};
  });
  angular.module('mib').controller('about', function() {
    this.init = function() {changeCurrentPage('about')};
  });
  angular.module('mib').controller('reportbug', function() {
    this.init = function() {changeCurrentPage('reportbug')};
  });
  angular.module('mib').controller('login', function() {
    this.init = function() {changeCurrentPage('login')};
  });
  angular.module('mib').controller('answer', function(QuestionService) {
    this.init = function() {changeCurrentPage()};
    this.response.answer = QuestionService.getResponse().response;
    this.response.heading = QuestionService.getResponse().heading;
  });

}());

function changeCurrentPage(target = null) {
  document.querySelectorAll('.active').forEach(function(item, index) {
    item.classList.remove('active');
  });
  if(target !== null)
    document.getElementById(target).classList.add('active');
}
