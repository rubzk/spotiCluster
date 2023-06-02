
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



function updateChartProperty(property, chartObject, originalData) {
    // Check if the property is already present in the chart
    var isPropertyPresent = chartObject.data.labels.includes(property);


    console.log(isPropertyPresent)

    if (isPropertyPresent) {
        // Remove the property from the chart

        console.log("Remove data")


        var newLabels = chartObject.data.labels.filter(function (label) {
            return label !== property;
        });

        var newData = chartObject.data.labels.filter(function (label) {
            return label !== property;
        });



        newData.push("cluster_name");




        console.log(chartObject.data.labels)
        console.log(newLabels)


        var filteredData = newData.reduce(function (obj, key) {
            if (key in originalData) {
                obj[key] = originalData[key];
            }
            return obj;
        }, {});

        console.log(originalData)
        console.log(filteredData)



        // var dataObj = originalData;

        // delete dataObj[property];


        // Adapt the updated data for the chart
        var updatedDatasets = adaptDataForChart(filteredData);
        chartObject.data.datasets = updatedDatasets;
        chartObject.data.labels = newLabels;



    } else {

        console.log("Add data")
        // Add the property to the chart
        chartObject.data.labels.push(property)

        console.log(chartObject.data.labels)

        var newData = chartObject.data.labels.slice()

        newData.push("cluster_name")

        console.log(newData)


        var filteredData = newData.reduce(function (obj, key) {
            if (key in originalData) {
                obj[key] = originalData[key];
            }
            return obj;
        }, {});

        console.log(originalData)
        console.log(filteredData)

        // You can populate the values for the new property here

        // Adapt the updated data for the chart
        var updatedDatasets = adaptDataForChart(filteredData);

        console.log

        chartObject.data.datasets = updatedDatasets;

        // chartObject.update();
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

                document.getElementById("loading-text").style.display = 'none';

                document.getElementById("done-text").innerHTML = "We analyzed " + data['plots']['number_of_tracks'] + " tracks and created " + data['plots']['number_of_clusters'] + " clusters"

                document.getElementById("done-text").style.display = 'flex';

                document.getElementById("div-test").style.display = 'flex';


                var ctx_radar = document.getElementById('radarChart').getContext('2d');
                var ctx_pie = document.getElementById('pieChart').getContext('2d');

                var dataPlots = {
                    labels: data['plots']['radar_chart']['categories'].slice(0, 4),
                    datasets: []
                };


                var originalData = data['plots']['radar_chart_test']


                // Iterate over the data and generate datasets
                for (var i = 0; i < Object.keys(data['plots']['radar_chart']).length - 1; i++) {
                    var clusterLabel = 'Cluster ' + (i);
                    var dataset = {
                        label: clusterLabel,
                        data: data['plots']['radar_chart'][clusterLabel].slice(0, 4),
                        backgroundColor: colors[i % colors.length],
                        borderColor: colors[i % colors.length].replace('0.2', '1'), // Increase opacity
                        borderWidth: 2,
                        pointBackgroundColor: colors[i % colors.length].replace('0.2', '1'),
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 3
                    };

                    dataPlots.datasets.push(dataset);
                }



                var dataPieChart = {
                    labels: data['plots']['pie_chart']['cluster_name'],
                    datasets: [{
                        data: data['plots']['pie_chart']['number_of_songs']
                    }]
                }



                // console.log(dataPlots)




                // var datasetTest = adaptDataForChart(data['plots']['radar_chart_test']);
                // console.log(datasetTest);



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

                // Create the charts  
                var myRadarChart = new Chart(ctx_radar, {
                    type: 'radar',
                    data: dataPlots,
                    options: options
                });

                // var myRadarChartTest = new Chart(ctx_radar_test, {
                //     type: 'radar',
                //     data: dataPlotsTest,
                //     options: options
                // });


                var myPieChart = new Chart(ctx_pie, {
                    type: 'pie',
                    data: dataPieChart,
                    options: options
                });


                console.log(myRadarChart.data.labels)
                console.log(myRadarChart.data.datasets)


                var addButton = document.getElementById('add-valence');

                addButton.addEventListener('click', function () {
                    var property = 'energy'; // Replace with the desired property
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
