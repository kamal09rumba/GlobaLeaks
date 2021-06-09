GL.controller("ReceiverTipsCtrl", ["$scope", "$sce",  "$filter", "$http", "$route", "$location", "$uibModal", "$window", "RTipExport", "ReceiverTips", "TokenResource",
  function($scope, $sce, $filter, $http, $route, $location, $uibModal, $window, RTipExport, ReceiverTips, TokenResource) {
  $scope.search = undefined;
  $scope.currentPage = 1;
  $scope.itemsPerPage = 20;

  $http({
      method: "GET", url: "api/rtips/sync-with-sf", data: {}
  }).then(function (response) {
      let sf_gl_data = response.data;
      $scope.sf_data = sf_gl_data.sf_gl_ids;
      $scope.sf_gl_record_report = $sce.trustAsHtml("Sync to SF <div class=\"text-center\">" + "In SF: " + sf_gl_data.total_sf_data + "<br/>In GL: " + sf_gl_data.total_gl_data + "</div>");
  });


  $scope.save_to_sf = function () {
    $uibModal.open({
      templateUrl: "views/partials/tip_operation_sync_with_sf.html",
      controller: "TipBulkOperationsCtrl",
      resolve: {
        selected_tips: function () {
          return $scope.selected_tips;
        },
        operation: function() {
          return "sync-with-sf";
        }
      }
    });
  };
  $scope.tips = ReceiverTips.query(function(tips) {
    angular.forEach(tips, function (tip) {
      if ($scope.sf_data.indexOf(tip.id) > -1) {
          tip.sf_sync_status = "Synced";
      } else {
          tip.sf_sync_status = "Not Synced";
      }
      tip.context = $scope.contexts_by_id[tip.context_id];
      tip.context_name = tip.context.name;
      tip.submissionStatusStr = $scope.Utils.getSubmissionStatusText(tip.status, tip.substatus, $scope.submission_statuses);
    });
  });

  $scope.filteredTips = $scope.tips;

  $scope.$watch("search", function (value) {
    if (typeof value !== "undefined") {
      $scope.currentPage = 1;
      $scope.filteredTips = $filter("filter")($scope.tips, value);
    }
  });

  $scope.exportTip = RTipExport;

  $scope.selected_tips = [];

  $scope.select_all = function () {
    $scope.selected_tips = [];
    angular.forEach($scope.tips, function (tip) {
      $scope.selected_tips.push(tip.id);
    });
  };

  $scope.toggle_star = function(tip) {
    tip.important = !tip.important;

    return $http({method: "PUT",
                  url: "api/rtips/" + tip.id,
                  data: {"operation": "update_important",
                         "args": {"value": tip.important}}});
  };

  $scope.deselect_all = function () {
    $scope.selected_tips = [];
  };

  $scope.tip_switch = function (id) {
    var index = $scope.selected_tips.indexOf(id);
    if (index > -1) {
      $scope.selected_tips.splice(index, 1);
    } else {
      $scope.selected_tips.push(id);
    }
  };

  $scope.isSelected = function (id) {
    return $scope.selected_tips.indexOf(id) !== -1;
  };

  $scope.tip_delete_selected = function () {
    $uibModal.open({
      templateUrl: "views/partials/tip_operation_delete_selected.html",
      controller: "TipBulkOperationsCtrl",
      resolve: {
        selected_tips: function () {
          return $scope.selected_tips;
        },
        operation: function() {
          return "delete";
        }
      }
    });
  };

  $scope.tips_export = function () {
    return new TokenResource().$get().then(function(token) {
      $window.open("api/rtips/export?token=" + token.id);
    });
  };

  $scope.tip_postpone_selected = function () {
    $uibModal.open({
      templateUrl: "views/partials/tip_operation_postpone_selected.html",
      controller: "TipBulkOperationsCtrl",
      resolve: {
        selected_tips: function () {
          return $scope.selected_tips;
        },
        operation: function() {
          return "postpone";
        }
      }
    });
  };
}]).
controller("TipBulkOperationsCtrl", ["$scope", "$sce", "$http", "$route", "$location", "$uibModalInstance", "selected_tips", "operation",
  function ($scope, $sce, $http, $route, $location, $uibModalInstance, selected_tips, operation) {
  $scope.selected_tips = selected_tips;
  $scope.operation = operation;

  $scope.cancel = function () {
    $uibModalInstance.close();
  };

  $scope.confirm = function () {
    $uibModalInstance.close();

    if (["postpone", "delete", "sync-with-sf"].indexOf(operation) === -1) {
      return;
    }

    if(operation == "sync-with-sf"){
      return $http({
          method: "POST", url: "api/rtips/sync-with-sf", data: {
              "rtips": $scope.selected_tips
          }
      }).then(function (response) {
          let sf_gl_data = response.data;
          $scope.sf_data = sf_gl_data.sf_gl_ids;
          $scope.sf_gl_record_report = $sce.trustAsHtml("Sync to SF <div class=\"text-center\">" + "In SF: " + sf_gl_data.total_sf_data + "<br/>In GL: " + sf_gl_data.total_gl_data + "</div>");
      });
    }

    return $http({method: "PUT", url: "api/recipient/operations", data:{
      "operation": $scope.operation,
      "rtips": $scope.selected_tips
    }}).then(function(){
      $scope.selected_tips = [];
      $route.reload();
    });
  };
}]);
