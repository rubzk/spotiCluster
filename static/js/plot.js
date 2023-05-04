var taskId = '{{task_id | safe}}'

var resultFound = false;

var fetchNow = function () {
    fetch('/status/' + taskId)
        .then(res => res.json())
        .then(data => {
            if (data['plots']) {
                console.log(data['plots'])

                var ctx = document.getElementById('radarChart').getContext('2d');

                // Define data for the chart
                var dataPlots = {
                    labels: data['plots']['radar_chart']['categories'],
                    datasets: [{
                        label: 'Cluster 1',
                        data: data['plots']['radar_chart']['Cluster 0'],
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 3
                    }, {
                        label: 'Cluster 2',
                        data: data['plots']['radar_chart']['Cluster 1'],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 3
                    }]
                };

                var options = {
                    scale: {
                        ticks: {
                            beginAtZero: true,
                            max: 1
                        },
                        pointLabels: {
                            fontSize: 14
                        }
                    },
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Audio Features by Cluster'
                    }
                };

                // Create the chart
                var myRadarChart = new Chart(ctx, {
                    type: 'radar',
                    data: dataPlots,
                    options: options
                });
            }
            else {
                fetchNow();
            }
        });
}

fetchNow();
