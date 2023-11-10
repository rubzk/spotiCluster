
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

var PieColors = [
    'rgba(255, 99, 132, 1)',   // Red
    'rgba(54, 162, 235, 1)',    // Blue
    'rgba(255, 206, 86, 1)',    // Yellow
    'rgba(75, 192, 192, 1)',    // Green
    'rgba(153, 102, 255, 1)',   // Purple
    'rgba(255, 159, 64, 1)'     // Orange
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

function points(config, selectedX, selectedY, label) {
    var xValues = config[selectedX];
    var yValues = config[selectedY];

    var data = [];

    if (xValues && yValues) {
        var length = Math.min(xValues.length, yValues.length);

        for (var i = 0; i < length; i++) {
            var x = xValues[i];
            var y = yValues[i];

            // Include the name as part of the data object for each point
            data.push({ x, y, label: name });
        }
    }

    return data;
}

function createScatterChart(dataObj) {
    var dataPlots = {
        datasets: []
    };

    var { key, tempo, time_signature, track_cluster, duration_ms, mode, liveness, loudness, speechiness, acousticness, ...dataObj } = dataObj;


    for (var [index, [key, value]] of Object.entries(Object.entries(dataObj))) {
        var dataset = {
            label: key,
            data: points(value, selectedX = "energy", selectedY = "valence", label = "title"),
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.2', '5'), // Increase opacity
            fill: false,
            showLine: false
        };

        dataPlots.datasets.push(dataset);
    }

    var chartOptions = {
        scales: {
            y: {
                min: 0,
                max: 1,
                title: {
                    display: true,
                    text: 'valence',
                    font: {
                        size: 24,

                    },
                    color: 'white'

                },
                grid: {
                    display: false
                },
                ticks: {
                    color: 'white'
                }

            },
            x: {
                min: 0,
                max: 1,
                title: {
                    display: true,
                    text: 'energy',
                    font: {
                        size: 24,

                    },
                    color: 'white'
                },
                grid: {
                    display: false
                },
                ticks: {
                    color: 'white'
                }
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    title: function (tooltipItem) {
                        // Display the name as the tooltip title
                        return tooltipItem[0].label;
                    }
                }
            }
        }
    }

    var chartConfig = {
        type: 'scatter',
        data: dataPlots,
        options: chartOptions
    };


    return chartConfig


}

function updateScatter(property, chartObject, originalData, axis) {
    var currentX = chartObject.options.scales.x.title.text;
    var currentY = chartObject.options.scales.y.title.text;

    if (axis === 'x') {
        for (var dataset of chartObject.data.datasets) {
            dataset.data = points(originalData[dataset.label], property, currentY, "title");
        }
        chartObject.options.scales.x.title.text = property;
    }
    else if (axis === 'y') {
        for (var dataset of chartObject.data.datasets) {
            dataset.data = points(originalData[dataset.label], currentX, property, "title");
        }
        chartObject.options.scales.y.title.text = property;
    }

    chartObject.update();
}

function createPieChart(dataObj) {



    var dataPieChart = {
        labels: dataObj['cluster_name'],
        datasets: [{
            data: dataObj['number_of_tracks'],
            backgroundColor: colors,
            borderColor: PieColors,
            hoverOffset: 8
        }]

    }


    var chartOptions = {
        plugins: {
            datalabels: {
                font: {
                    size: 24,
                    family: 'Helvetica',
                    weight: 'bold'
                },
                align: 'start',
                anchor: 'center',
                color: 'white',
                formatter: function (value, context) {
                    return value; // You can customize the format as needed

                }
            }
        }
    };


    var chartConfig = {
        type: 'pie',
        data: dataPieChart,
        options: chartOptions,
        plugins: [ChartDataLabels],

    };

    return chartConfig;


}

function createRadarChart(dataObj) {


    var { key, tempo, time_signature, track_cluster, duration_ms, mode, loudness, ...dataObj } = dataObj;

    var options = {
        scales: {
            r: {
                grid: {
                    color: 'gray'
                },
                angleLines: {
                    color: 'gray'
                },
                ticks: {
                    display: false
                },
                pointLabels: {
                    color: 'white'
                }

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

    dataPlots.labels = Object.keys(dataObj).filter(function (label) {
        return label !== "cluster_name";
    });


    dataPlots.datasets = adaptDataForChart(dataObj);

    var chartConfig = {
        type: 'radar',
        data: dataPlots,
        options: options

    };

    return chartConfig;

}

function createBarChart(dataObj) {



    var options = {
        indexAxis: 'y',
        scales: {
            y: {
                title: {
                    font: {
                        size: 24,
                    },
                    color: 'white'
                },
                grid: {
                    display: false
                },
                ticks: {
                    color: 'white'
                }
            },
            x: {
                title: {
                    font: {
                        size: 24,
                    },
                    color: 'white'
                },
                grid: {
                    display: true
                },
                ticks: {
                    display: false,
                    font: {
                        size: 24
                    }
                }
            },
        },
        legend: {
            display: false,
        },
        plugins: {
            legend: {
                display: false,
            },
            datalabels: {
                font: {
                    size: 24,
                    family: 'Helvetica',
                    weight: 'bold'
                },
                anchor: 'end',
                align: function (context) {
                    if (context.dataset.data[context.dataIndex] < 0) {
                        return 'start'
                    }
                    return 'end'
                },
                color: 'white',
                formatter: function (value, context) {
                    // return value; // You can customize the format as needed
                    if (value < 1) {
                        return (parseFloat(value).toFixed(2));
                    }
                    return Math.round(value);
                }
            }
        }
    };


    var dataPlots = {
        labels: dataObj['cluster_name'],
        datasets: []
    };


    dataPlots.datasets = [{
        label: 'tempo',
        data: dataObj['tempo'],
        backgroundColor: 'rgba(0, 163, 108, 0.5)', // Background color for bars
        borderColor: 'rgba(0, 163, 108, 1)', // Border color for bars
        borderWidth: 1 // Border width for bars
    }]

    var chartConfig = {
        type: 'bar',
        data: dataPlots,
        options: options,
        plugins: [ChartDataLabels],
    };

    return chartConfig;

}



function createAreaChart(dataObj) {


    var { key, tempo, time_signature, track_cluster, duration_ms, mode, liveness, loudness, speechiness, acousticness, ...dataObj } = dataObj;

    var dataPlots = {
        labels: [],
        datasets: []
    };

    dataPlots.labels = dataObj["yyyy-mm"]

    var label_ds = Object.keys(dataObj)


    for (var [index, [key, value]] of Object.entries(Object.entries(dataObj))) {


        /// change colors of each feature

        if (key != "yyyy-mm") {


            var dataset = {
                label: key,
                data: value,
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace('0.2', '1'), // Increase opacity
                borderWidth: 2,
                pointBackgroundColor: colors[index % colors.length].replace('0.2', '1'),
                pointBorderColor: '#fff',
                pointBorderWidth: 1,
                pointRadius: 1,
                fill: true

            }

            dataPlots.datasets.push(dataset)

        }

    }


    var options = {

        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Year - Month', // X axis title
                    font: {
                        size: 16, // Customize the font size for X axis title
                    },
                    color: 'white'
                },
                ticks: {
                    color: 'white'
                },
                grid: {
                    borderDash: [10, 10], // This creates dashed lines
                    drawBorder: true
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Value', // Y axis title
                    font: {
                        size: 16, // Customize the font size for Y axis title
                    },
                    color: 'white'
                },
                ticks: {
                    color: 'white'
                }
            }
        },
        border: {
            display: true,
            color: 'white'
        },

    };

    var chartConfig = {
        type: 'line',
        data: dataPlots,
        options: options,

    }


    return chartConfig

}

function updateChartProperty(property, chartObject, originalData) {
    // Check if the property is already present in the chart
    var isPropertyPresent = chartObject.data.labels.includes(property);


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


    // Update the chart
}

function updateBarChart(property, chartObject, dataObj) {



    var isPropertyPresent = chartObject.data.labels.includes(property);

    if (!isPropertyPresent) {
        // If the property is not present, replace existing labels and datasets

        chartObject.data.datasets = [{
            label: property,
            data: dataObj[property],
            backgroundColor: 'rgba(0, 163, 108, 0.5)',
            borderColor: 'rgba(0, 163, 108, 1)',
            borderWidth: 1
        }];

        // Update the chart
        chartObject.update();
    }

}


var fetchNow = function () {
    fetch('/status/' + taskId, {
        headers: headers
    })
        .then(res => res.json())
        .then(data => {
            if (data['plots']) {

                test = data['plots']

                document.getElementById("loading-div").style.display = 'none';

                document.getElementById("done-text").innerHTML = "We analyzed " + data['plots']['number_of_tracks'] + " tracks and created " + data['plots']['number_of_clusters'] + " clusters"

                document.getElementById("done-text").style.display = 'flex';

                document.getElementById("div-test").style.display = 'flex';


                var ctx_radar = document.getElementById('radarChart').getContext('2d');
                var ctx_pie = document.getElementById('pieChart').getContext('2d');
                var ctx_area = document.getElementById('areaChart').getContext('2d');
                var ctx_scatter = document.getElementById('scatterChart').getContext('2d');
                var ctx_bar = document.getElementById('barChart').getContext('2d');


                var originalData = data['plots']['radar_chart']['data']

                var dataArea = createAreaChart(data['plots']['saved_tracks_timeline']['data'])

                var dataScatter = createScatterChart(data['plots']['scatter_chart']['data'])

                var dataPieChart = createPieChart(data['plots']['pie_chart']['data'])

                var dataRadarChart = createRadarChart(data['plots']['radar_chart']['data'])

                var dataBarChart = createBarChart(data['plots']['radar_chart']['data'])


                var myRadarChart = new Chart(ctx_radar, dataRadarChart);

                var myPieChart = new Chart(ctx_pie, dataPieChart);


                var myAreaChart = new Chart(ctx_area, dataArea);

                var myScatterChart = new Chart(ctx_scatter, dataScatter);

                var myBarChart = new Chart(ctx_bar, dataBarChart)


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


                var addEnergyScatterY = document.getElementById('add-energy-scatter-y');

                var addValenceScatterY = document.getElementById('add-valence-scatter-y');

                var addDanceabilityScatterY = document.getElementById('add-danceability-scatter-y');

                var addInstrumentalnessScatterY = document.getElementById('add-instrumentalness-scatter-y');


                addEnergyScatterY.addEventListener('click', function () {
                    var property = 'energy'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "y");
                });

                addValenceScatterY.addEventListener('click', function () {
                    var property = 'valence'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "y");
                });

                addDanceabilityScatterY.addEventListener('click', function () {
                    var property = 'danceability'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "y");
                });

                addInstrumentalnessScatterY.addEventListener('click', function () {
                    var property = 'instrumentalness'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "y");
                });


                var addEnergyScatterX = document.getElementById('add-energy-scatter-x');

                var addValenceScatterX = document.getElementById('add-valence-scatter-x');

                var addDanceabilityScatterX = document.getElementById('add-danceability-scatter-x');

                var addInstrumentalnessScatterX = document.getElementById('add-instrumentalness-scatter-x');


                addEnergyScatterX.addEventListener('click', function () {
                    var property = 'energy'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "x");
                });

                addValenceScatterX.addEventListener('click', function () {
                    var property = 'valence'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "x");
                });

                addDanceabilityScatterX.addEventListener('click', function () {
                    var property = 'danceability'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "x");
                });

                addInstrumentalnessScatterX.addEventListener('click', function () {
                    var property = 'instrumentalness'; // Replace with the desired property
                    var chartObject = myScatterChart; // Replace with your actual chart object


                    updateScatter(property, chartObject, data['plots']['scatter_chart']['data'], axis = "x");
                });




                var addEnergyBarChart = document.getElementById('add-energy-bar');

                var addTempoBarChart = document.getElementById('add-tempo-bar');

                var addDanceabilityBarChart = document.getElementById('add-danceability-bar');

                var addInstrumentalnessBarChart = document.getElementById('add-instrumentalness-bar');

                var addLoudnessBarChart = document.getElementById('add-loudness-bar');

                var addValenceBarChart = document.getElementById('add-valence-bar');

                var addSpeechinessBarChart = document.getElementById('add-speechiness-bar');

                addEnergyBarChart.addEventListener('click', function () {
                    var property = 'energy'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addTempoBarChart.addEventListener('click', function () {
                    var property = 'tempo'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addDanceabilityBarChart.addEventListener('click', function () {
                    var property = 'danceability'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addInstrumentalnessBarChart.addEventListener('click', function () {
                    var property = 'instrumentalness'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addLoudnessBarChart.addEventListener('click', function () {
                    var property = 'loudness'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addValenceBarChart.addEventListener('click', function () {
                    var property = 'valence'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });

                addSpeechinessBarChart.addEventListener('click', function () {
                    var property = 'speechiness'; // Replace with the desired property
                    var chartObject = myBarChart; // Replace with your actual chart object


                    updateBarChart(property, chartObject, originalData);
                });








            }
            else {
                fetchNow();
            }
        });
}






fetchNow();
