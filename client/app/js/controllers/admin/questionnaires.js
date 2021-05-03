GL.controller("AdminQuestionnaireCtrl",
  ["$scope", "$http", "$route", "AdminQuestionnaireResource",
  function($scope, $http, $route, AdminQuestionnaireResource){
  $scope.tabs = [
    {
      title:"Questionnaires",
      template:"views/admin/questionnaires/main.html"
    },
    {
      title:"Question templates",
      template:"views/admin/questionnaires/questions.html"
    },
    {
      title: "SalesForce mapping",
      template: "views/admin/questionnaires/sfmapping.html",
    }
  ];

  $scope.deleted_fields_ids = [];

  $scope.resources.get_field_attrs = function(type) {
    if (type in $scope.resources.field_attrs) {
      return $scope.resources.field_attrs[type];
    } else {
      return {};
    }
  };

  $scope.showAddQuestionnaire = false;
  $scope.toggleAddQuestionnaire = function() {
    $scope.showAddQuestionnaire = !$scope.showAddQuestionnaire;
  };

  $scope.showAddQuestion = false;
  $scope.toggleAddQuestion = function() {
    $scope.showAddQuestion = !$scope.showAddQuestion;
  };

  $scope.importQuestionnaire = function(file) {
    $scope.Utils.readFileAsText(file).then(function(txt) {
      return $http({
        method: "POST",
        url: "api/admin/questionnaires?multilang=1",
        data: txt,
      });
    }).then(function() {
       $route.reload();
    }, $scope.Utils.displayErrorMsg);
  };

  $scope.save_questionnaire = function(questionnaire, cb) {
    var updated_questionnaire = new AdminQuestionnaireResource(questionnaire);

    return $scope.Utils.update(updated_questionnaire, cb);
  };

  $scope.delete_questionnaire = function(questionnaire) {
    $scope.Utils.deleteDialog().then(function() {
      return $scope.Utils.deleteResource(AdminQuestionnaireResource, $scope.resources.questionnaires, questionnaire);
    });
  };
}]).
controller("AdminQuestionnaireEditorCtrl", ["$scope", "$uibModal", "$http", "FileSaver", "AdminStepResource",
  function($scope, $uibModal, $http, FileSaver, AdminStepResource) {

  $scope.editing = false;

  $scope.toggleEditing = function () {
    $scope.editing = $scope.questionnaire.editable && !$scope.editing;
  };

  $scope.showAddStep = false;
  $scope.toggleAddStep = function() {
    $scope.showAddStep = !$scope.showAddStep;
  };

  $scope.parsedFields = $scope.fieldUtilities.parseQuestionnaire($scope.questionnaire, {});

  $scope.delStep = function(step) {
    $scope.Utils.deleteDialog().then(function() {
      return $scope.Utils.deleteResource(AdminStepResource, $scope.questionnaire.steps, step);
    });
  };

  $scope.duplicate_questionnaire = function(questionnaire) {
    $uibModal.open({
      templateUrl: "views/partials/questionnaire_duplication.html",
      controller: "QuestionaireOperationsCtrl",
      resolve: {
        questionnaire: function () {
          return questionnaire;
        },
        operation: function () {
          return "duplicate";
        }
      }
    });
  };

  $scope.exportQuestionnaire = function(obj) {
    $http({
      method: "GET",
      url: "api/admin/questionnaires/" + obj.id,
      responseType: "blob",
    }).then(function (response) {
      FileSaver.saveAs(response.data, obj.name + ".json");
    });
  };
}]).
controller("AdminQuestionnaireAddCtrl", ["$scope", function($scope) {
  $scope.new_questionnaire = {};

  $scope.add_questionnaire = function() {
    var questionnaire = new $scope.AdminUtils.new_questionnaire();

    questionnaire.name = $scope.new_questionnaire.name;

    questionnaire.$save(function(new_questionnaire){
      $scope.resources.questionnaires.push(new_questionnaire);
      $scope.new_questionnaire = {};
    });
  };
}]).
controller("QuestionaireOperationsCtrl",
  ["$scope", "$http", "$route", "$location", "$uibModalInstance", "questionnaire", "operation",
   function ($scope, $http, $route, $location, $uibModalInstance, questionnaire, operation) {
  $scope.questionnaire = questionnaire;
  $scope.operation = operation;

  $scope.cancel = function () {
    $uibModalInstance.close();
  };

  $scope.confirm = function () {
    $uibModalInstance.close();

    if ($scope.operation === "duplicate") {
      $http.post(
        "api/admin/questionnaires/duplicate",
        {
          questionnaire_id: $scope.questionnaire.id,
          new_name: $scope.duplicate_questionnaire.name
        }
      ).then(function () {
        $route.reload();
      });
    }
  };
}]).controller("AdminSalesForceMappingCtrl",
  ["$scope", "$http", "$route",
  function($scope, $http, $route){
    $scope.headers = ["SalesForce Field ID", "GL Questionnaire ID", "Options"]
    $scope.client_mapping = $scope.resources.sfmapping.client_mapping;
    $scope.issue_mapping = $scope.resources.sfmapping.issue_mapping;
}]);
