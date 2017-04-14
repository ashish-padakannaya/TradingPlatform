'use strict';

/**
 * @ngdoc function
 * @name gjainApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the gjainApp
 */
angular.module('gjainApp')
    .controller('MainCtrl', function($scope, $http) {

        $http({
            method: 'GET',
            url: '/app/data/NSE-datasets-codes.csv'
        }).then(function successCallback(response) {
            var rawData = Papa.parse(response.data);
            for (var i in rawData.data) {
                rawData.data[i][0] = rawData.data[i][0].substring(4);
            }
            $scope.nseCodesArray = rawData;
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
  


        this.awesomeThings = [
            'HTML5 Boilerplate',
            'AngularJS',
            'Karma'
        ];

        $scope.scripCode = '';
        $scope.getData = function() {
            $scope.history = true;
            $scope.ticker = false;
            $scope.data = '';
            $scope.errorCode = '';
            $scope.errorMessage = '';
            console.log($scope.startDate);
            var startDateParameter = $scope.startDate ? '&start_date=' + $scope.startDate : '';
            var endDateParameter = $scope.endDate ? '&end_date=' + $scope.endDate : '';
            $.ajax({
                url: ('https://www.quandl.com/api/v3/datasets/NSE/' + $scope.scripCode + '.json?api_key=-Q-zpXxS1SEg8TJQEi1L' + startDateParameter + endDateParameter),
                dataType: 'json',
                type: 'get',
                success: function(response) {
                    console.log(response);
                    $scope.data = response;
                    $scope.$digest();
                    $scope.draw();
                },
                error: function(response) {
                    console.log(response);
                    $scope.errorCode = response.status;
                    if (response.status == 404) {
                        $scope.errorMessage = 'Invalid Scrip Code';
                    }
                    $scope.$digest();
                }
            });
        }

        $scope.draw = function() {
            var formattedData = [];
            var shareData = $scope.data.dataset.data;
            for (var item in shareData) {
                var itemData = shareData[item];
                var itemObj = { x: new Date(itemData[0]), y: [itemData[1], itemData[2], itemData[3], itemData[5]] };
                formattedData.push(itemObj);
            }

            var chart = new CanvasJS.Chart("chartContainer", {
                title: {
                    text: $scope.data.dataset.name + " Candlestick Chart",
                },
                exportEnabled: true,
                axisY: {
                    includeZero: false,
                    prefix: "₹",
                },
                axisX: {
                    valueFormatString: "DD-MMM",
                },
                data: [{
                    type: "candlestick",
                    dataPoints: formattedData
                        // dataPoints: [
                        //     { x: new Date(1970, 0, 1), y: [99.91, 100.15, 99.33, 99.61] },
                        //     { x: new Date(1970, 0, 2), y: [100.12, 100.45, 99.28, 99.51] },
                        //     { x: new Date(1970, 0, 3), y: [99.28, 100.36, 99.27, 99.79] },
                        //     { x: new Date(1970, 0, 4), y: [99.44, 100.62, 99.41, 99.62] },
                        //     { x: new Date(1970, 0, 5), y: [99.74, 100.45, 99.72, 99.96] },
                        //     { x: new Date(1970, 0, 6), y: [99.31, 100.46, 98.93, 99.50] },
                        //     { x: new Date(1970, 0, 7), y: [100.27, 100.27, 99.64, 100.19] },
                        //     { x: new Date(1970, 0, 8), y: [100.61, 100.67, 100.05, 100.38] },
                        //     { x: new Date(1970, 0, 9), y: [99.96, 100.11, 98.81, 99.21] },
                        //     { x: new Date(1970, 0, 10), y: [100.40, 100.52, 99.45, 100.35] },
                        //     { x: new Date(1970, 0, 11), y: [100.88, 100.93, 100.28, 100.65] },
                        //     { x: new Date(1970, 0, 12), y: [100.30, 100.52, 99.76, 99.92] },
                        //     { x: new Date(1970, 0, 13), y: [99.52, 100.29, 99.06, 99.45] },
                        //     { x: new Date(1970, 0, 14), y: [99.25, 100.00, 99.18, 99.56] },
                        //     { x: new Date(1970, 0, 15), y: [99.41, 100.10, 98.78, 99.67] },
                        //     { x: new Date(1970, 0, 16), y: [100.45, 100.62, 100.19, 100.50] },
                        //     { x: new Date(1970, 0, 17), y: [100.36, 100.54, 99.60, 100.52] },
                        //     { x: new Date(1970, 0, 18), y: [99.52, 100.02, 99.32, 99.70] },
                        //     { x: new Date(1970, 0, 19), y: [99.82, 100.66, 99.07, 99.73] },
                        //     { x: new Date(1970, 0, 20), y: [100.05, 100.96, 99.51, 100.38] },
                        //     { x: new Date(1970, 0, 21), y: [100.22, 100.66, 100.20, 100.22] },
                        //     { x: new Date(1970, 0, 22), y: [99.05, 100.29, 98.97, 99.62] },
                        //     { x: new Date(1970, 0, 23), y: [100.33, 100.90, 100.13, 100.78] },
                        //     { x: new Date(1970, 0, 24), y: [100.78, 100.93, 100.75, 100.85] },
                        //     { x: new Date(1970, 0, 25), y: [100.78, 100.92, 100.25, 100.33] },
                        //     { x: new Date(1970, 0, 26), y: [99.75, 100.72, 99.63, 100.58] },
                        //     { x: new Date(1970, 0, 27), y: [100.02, 100.36, 99.59, 99.85] },
                        //     { x: new Date(1970, 0, 28), y: [100.58, 100.81, 100.56, 100.72] },
                        //     { x: new Date(1970, 0, 29), y: [99.73, 100.08, 99.42, 99.51] },
                        //     { x: new Date(1970, 0, 30), y: [100.16, 100.47, 99.50, 100.26] },
                        //     { x: new Date(1970, 0, 31), y: [100.43, 100.95, 100.39, 100.88] }
                        // ]
                }]
            });
            chart.render();
        }

        $scope.getTicker = function() {
            $scope.history = false;
            $scope.ticker = true;
            console.log('Getting Ticker')
            var postdata = {}
            postdata.ticker = $scope.scripCode;
            if ($scope.startDate) {
                postdata.start_date = $scope.startDate;
            }
            if ($scope.endDate) {
                postdata.end_date = $scope.endDate;
            }
            $.ajax({
                url: ('http://localhost:8000/stock/'),
                dataType: 'json',
                type: 'post',
                data: postdata,
                success: function(response) {
                    console.log(response);
                    $scope.tickerData = response;
                    $scope.$digest();
                },
                error: function(response) {
                    console.log(response);
                    $scope.errorCode = response.status;
                    if (response.status == 404) {
                        $scope.errorMessage = 'Invalid Scrip Code';
                    }
                    $scope.$digest();
                }
            });

            var tickerPostData = {}
            tickerPostData.ticker = $scope.scripCode;
            $.ajax({
                url: ('http://localhost:8000/pointers/'),
                dataType: 'json',
                type: 'post',
                data: tickerPostData,
                success: function(response) {
                    console.log(response);
                    $scope.pointers = response;
                    $scope.$digest();
                },
                error: function(response) {
                    console.log(response);
                    $scope.errorCode = response.status;
                    if (response.status == 404) {
                        $scope.errorMessage = 'Invalid Scrip Code';
                    }
                    $scope.$digest();
                }
            });
        }

        $scope.setScrip = function(scripSelected)
        {
            $scope.scripCode = scripSelected;
            $scope.dismissSearch = true;
        }
    });

angular.module('gjainApp').directive('datePicker', function() {
    var link = function(scope, element, attrs) {
        var modelName = attrs['datePicker'];
        $(element).datepicker(
            {
                dateFormat: 'yy-mm-dd',
                onSelect: function(dateText) {
                    scope[modelName] = dateText;
                    scope.$apply();
                }
            });
    };
    return {
        require: 'ngModel',
        restrict: 'A',
        link: link
    }
});