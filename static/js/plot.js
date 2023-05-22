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

var fetchNow = function () {
    fetch('/status/' + taskId)
        .then(res => res.json())
        .then(data => {
            if (data['plots']) {
                console.log(data['plots'])

                document.getElementById("loading-text").style.display = 'none';

                var ctx = document.getElementById('radarChart').getContext('2d');


                var dataPlots = {
                    labels: data['plots']['radar_chart']['categories'],
                    datasets: []
                };



                // Iterate over the data and generate datasets
                for (var i = 0; i < Object.keys(data['plots']['radar_chart']).length - 1; i++) {
                    var clusterLabel = 'Cluster ' + (i);
                    var dataset = {
                        label: clusterLabel,
                        data: data['plots']['radar_chart'][clusterLabel],
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
                        pointLabels: {
                            fontSize: 14,
                            fontColor: 'white'
                        }
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            fontColor: 'white'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Audio Features by Cluster',
                        fontColor: 'white'
                    },
                    pointLabels: {
                        fontColor: 'white'
                    }
                };

                // Create the chart
                var myRadarChart = new Chart(ctx, {
                    type: 'radar',
                    data: dataPlots,
                    options: options
                });

                var dataPieChart = {
                    labels: data['plots']['pie_chart']['cluster_name'],
                    datasets: [{
                        data: data['plots']['pie_chart']['number_of_songs']
                    }]
                }
                var ctx_pie = document.getElementById('pieChart').getContext('2d');

                var myPieChart = new Chart(ctx_pie, {
                    type: 'pie',
                    data: dataPieChart,
                    options: options
                });
            }
            else {
                fetchNow();
            }
        });
}

fetchNow();
