export function createAreaChart(dataObj) {

    let dataPlots = {
        labels: [],
        datasets: []
    };

    dataPlots.labels = dataObj["yyyy-mm"]

    let label_ds = Object.keys(dataObj)


    for (let [key, value] of Object.entries(dataObj)) {
        /// change colors of each feature

        if (key != "yyyy-mm") {

            let dataset = {
                label: key,
                data: value,
                backgroundColor: colors[1 % colors.length],
                borderColor: colors[1 % colors.length].replace('0.2', '1'), // Increase opacity
                borderWidth: 2,
                pointBackgroundColor: colors[1 % colors.length].replace('0.2', '1'),
                pointBorderColor: '#fff',
                pointBorderWidth: 1,
                pointRadius: 1,
                fill: true

            }

            dataPlots.datasets.push(dataset)

        }

    }


    return dataPlots

}

export function test() {

    console.log("Test de modulo")

}