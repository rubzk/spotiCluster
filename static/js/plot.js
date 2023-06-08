
var taskId = '{{task_id | safe}}'

var resultFound = false;

var colors = [
    'rgba(255, 99, 132, 0.2)',   // Red
    'rgba(54, 162, 235, 0.2)',    // Blue
    'rgba(255, 206, 86, 0.2)',    // Yellow
    'rgba(75, 192, 192, 0.2)',    // Green
    'rgba(153, 102, 255, 0.2)',   // Purple
    'rgba(255, 159, 64, 0.2)'     // Orange
];

var headers = new Headers();
headers.append('Content-Type', 'application/json');


function adaptDataForChart(dataObj) {
    var datasets = [];

    // Iterate over the clusters
    for (var i = 0; i < dataObj.cluster_name.length; i++) {
        var clusterLabel = dataObj.cluster_name[i];
        var dataset = {
            label: clusterLabel,
            data: [],
            backgroundColor: colors[i % colors.length],
            borderColor: colors[i % colors.length].replace('0.2', '1'), // Increase opacity
            borderWidth: 2,
            pointBackgroundColor: colors[i % colors.length].replace('0.2', '1'),
            pointBorderColor: '#fff',
            pointBorderWidth: 1,
            pointRadius: 3
        };

        // Iterate over the properties in each cluster
        for (var prop in dataObj) {
            if (prop !== 'cluster_name' && dataObj.hasOwnProperty(prop)) {
                dataset.data.push(dataObj[prop][i]);
            }
        }



        datasets.push(dataset);
    }


    return datasets;
}


function createAreaChart(dataObj) {

    var dataPlots = {
        labels: [],
        datasets: []
    };

    dataPlots.labels = dataObj["yyyy-mm"]

    var label_ds = Object.keys(dataObj)


    for (var [key, value] of Object.entries(dataObj)) { /// change colors of each feature

        if (key != "yyyy-mm") {

            var dataset = {
                label: key,
                data: value,
                backgroundColor: colors[0 % colors.length],
                borderColor: colors[0 % colors.length].replace('0.2', '1'), // Increase opacity
                borderWidth: 2,
                pointBackgroundColor: colors[0 % colors.length].replace('0.2', '1'),
                pointBorderColor: '#fff',
                pointBorderWidth: 1,
                pointRadius: 3

            }

            dataPlots.datasets.push(dataset)

        }

    }


    return dataPlots

}

function updateChartProperty(property, chartObject, originalData) {
    // Check if the property is already present in the chart
    var isPropertyPresent = chartObject.data.labels.includes(property);


    console.log(isPropertyPresent)

    if (isPropertyPresent) {
        // Remove the property from the chart


        var newLabels = chartObject.data.labels.filter(function (label) {
            return label !== property;
        });

        var newData = chartObject.data.labels.filter(function (label) {
            return label !== property;
        });

        newData.push("cluster_name");

        var filteredData = newData.reduce(function (obj, key) {
            if (key in originalData) {
                obj[key] = originalData[key];
            }
            return obj;
        }, {});
        // Adapt the updated data for the chart
        var updatedDatasets = adaptDataForChart(filteredData);
        chartObject.data.datasets = updatedDatasets;
        chartObject.data.labels = newLabels;



    } else {

        // Add the property to the chart
        chartObject.data.labels.push(property)


        var newData = chartObject.data.labels.slice()

        newData.push("cluster_name")



        var filteredData = newData.reduce(function (obj, key) {
            if (key in originalData) {
                obj[key] = originalData[key];
            }
            return obj;
        }, {});

        var updatedDatasets = adaptDataForChart(filteredData);


        chartObject.data.datasets = updatedDatasets;


    }


    chartObject.update();

    console.log(chartObject.data.labels)
    console.log(chartObject.data.datasets)

    // Update the chart
}

var fetchNow = function () {
    fetch('/status/' + taskId, {
        headers: headers
    })
        .then(res => res.json())
        .then(data => {
            if (data['plots']) {
                console.log(data['plots'])

                document.getElementById("loading-div").style.display = 'none';

                document.getElementById("done-text").innerHTML = "We analyzed " + data['plots']['number_of_tracks'] + " tracks and created " + data['plots']['number_of_clusters'] + " clusters"

                document.getElementById("done-text").style.display = 'flex';

                document.getElementById("div-test").style.display = 'flex';


                var ctx_radar = document.getElementById('radarChart').getContext('2d');
                var ctx_pie = document.getElementById('pieChart').getContext('2d');
                var ctx_area = document.getElementById('areaChart').getContext('2d');


                var originalData = data['plots']['radar_chart']



                var dataPieChart = {
                    labels: data['plots']['pie_chart']['cluster_name'],
                    datasets: [{
                        data: data['plots']['pie_chart']['number_of_songs'],
                        backgroundColor: colors
                    }]
                }



                var options = {
                    scale: {
                        angleLines: {
                            color: 'white'
                        },
                        gridLines: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        },
                        ticks: {
                            beginAtZero: true,
                            max: 1,
                            fontColor: 'white'
                        },
                        pointcluster_name: {
                            fontSize: 14,
                            fontColor: 'white'
                        }
                    },
                    legend: {
                        position: 'top',
                        cluster_name: {
                            fontColor: 'white'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Audio Features by Cluster',
                        fontColor: 'white'
                    },
                    pointcluster_name: {
                        fontColor: 'white'
                    }
                };

                var dataPlots = {
                    labels: [],
                    datasets: []
                };

                var dataArea = createAreaChart(data['plots']['saved_tracks'])

                dataPlots.labels = Object.keys(originalData).filter(function (label) {
                    return label !== "cluster_name";
                });


                dataPlots.datasets = adaptDataForChart(originalData);

                // Create the charts  
                var myRadarChart = new Chart(ctx_radar, {
                    type: 'radar',
                    data: dataPlots,
                    options: options
                });

                var myPieChart = new Chart(ctx_pie, {
                    type: 'pie',
                    data: dataPieChart,
                    options: options
                });

                var myAreaChart = new Chart(ctx_area, {
                    type: 'line',
                    data: dataArea,
                    options: options
                });



                var addButtonEnergy = document.getElementById('add-energy');

                var addButtonTempo = document.getElementById('add-tempo');

                var addButtonLiveness = document.getElementById('add-liveness');

                var addButtonLoudness = document.getElementById('add-loudness');

                var addButtonSpeechiness = document.getElementById('add-speechiness');

                var addButtonDanceability = document.getElementById('add-danceability');

                var addButtonAcousticness = document.getElementById('add-acousticness');

                addButtonEnergy.addEventListener('click', function () {
                    var property = 'energy'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });

                addButtonTempo.addEventListener('click', function () {
                    var property = 'tempo'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });



                addButtonLiveness.addEventListener('click', function () {
                    var property = 'liveness'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });

                addButtonLoudness.addEventListener('click', function () {
                    var property = 'loudness'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });

                addButtonSpeechiness.addEventListener('click', function () {
                    var property = 'speechiness'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });

                addButtonDanceability.addEventListener('click', function () {
                    var property = 'danceability'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });

                addButtonAcousticness.addEventListener('click', function () {
                    var property = 'acousticness'; // Replace with the desired property
                    var chartObject = myRadarChart; // Replace with your actual chart object


                    updateChartProperty(property, chartObject, originalData);
                });





            }
            else {
                fetchNow();
            }
        });
}






fetchNow();
