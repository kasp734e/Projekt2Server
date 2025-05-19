const hourLabels = [
    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", 
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", 
    "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
];

const rollingLabels = [
    "-3h50m", "-3h40m", "-3h30m", "-3h20m", "-3h10m", "-3h", "-2h50m", "-2h40m",
    "-2h30m", "-2h20m", "-2h10m", "-2h", "-1h50m", "-1h40m", "-1h30m", "-1h20m",
    "-1h10m", "-1h", "-50m", "-40m", "-30m", "-20m", "-10m", "now"
];

const initialData = Array(24).fill(0);

const StandardData = {
    labels: rollingLabels,
    datasets: [{
        label: 'Data',
        data: initialData.slice()
    }]
};

const powerData = {
    labels: hourLabels,
    datasets: [{
        label: 'Strømpris',
        data: initialData.slice(),
        stepped: 'before',
        pointStyle: false
    }]
};

const charts = {};

/** Takes an array of labels for the x-axis and an array of data points. Returns a configuration object for the chart */
function createChartData(labels, data) {
    return {
        labels: labels,
        datasets: [{
            label: '',
            data: data,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    };
}
/** Iterates over the graphs in the graphs array, gets the HTML element with the corresponding id, and inits the chart */
function initCharts() {
    const graphs = ['graphPower',
                    'graphAirQuality',
                    'graphPowerPrice',
                    'graphAirTemp'
                    ];

    const datasets = [
        createChartData(rollingLabels, initialData.slice()),
        createChartData(rollingLabels, initialData.slice()),
        powerData,
        createChartData(rollingLabels, initialData.slice())
    ]; 

    const defaultConfig = {
        scales: { y: { beginAtZero: true } },
        plugins: { legend: { display: false } }
    };

     const configs = [
         {type: 'line', options: defaultConfig},
         {type: 'line', options: defaultConfig},
         {type: 'bar', options:defaultConfig},
         {type: 'line', options:defaultConfig}
    ];

    graphs.forEach((graph, index) => { // iterates over graphs, 
    // creats 'graph' variable with the name of the current graph and...
    // 'index' with the index int of the current chart 
        charts[graph] = new Chart(
            document.getElementById(graph), // gets the chart from the HTML with the id
            {
                type: configs[index].type,
                data: datasets[index],
                options: configs[index].options
            }
        );
    });
}

/** Calls /api/update */
function updateArduinoData() {
    fetch('/api/update')
        .then(response => response.json())
        .then(data => {
            console.log("Data updated:", data);
        })
        .catch(error => console.error('Error updating data:', error));
}

function updateChartData(chartObject, dataArray) {
    chartObject.data.datasets[0].data = dataArray;
    chartObject.update();
}
/** Gets newest data from the server and updates the charts */
function updateCharts() {
    fetch('/api/data')
        .then(response => response.json())
        .then(dataArray => {
            dataArray.sort((a, b) => {
                const timeA = new Date(a.time);
                const timeB = new Date(b.time);

                const diffMinutes = Math.abs((timeA - timeB) / (1000 * 60));
                if (diffMinutes <= 1) {
                    return 0;
                }
                return timeA - timeB;
            });

            const latestData = dataArray[dataArray.length - 1];
            const recentData = dataArray; // The server already ensures it contains 24 items

            const airQualityValues = recentData.map(item => item.airQuality || 0);
            const powerValues = recentData.map(item => item.power || 0);
            const airTemperatureValues = recentData.map(item => item.airTemp || 0); 

            updateChartData(charts['graphAirQuality'], airQualityValues);
            updateChartData(charts['graphPower'], powerValues);
            updateChartData(charts['graphAirTemp'], airTemperatureValues);
            updateChartData(charts['graphPowerPrice'], latestData.powerPrice);
 
            console.log('Charts updated');
        })
        .catch(error => console.error('Error fetching data:', error));
}

/** Takes a new update time in minutes and sends it to the server */
function changeUpdateTime(newUpdateTime) {
    fetch('/api/changeUpdateTime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({value: newUpdateTime})
    }) // Sends the newUpdateTime to the server as a JSON object with value key
    .then(response => response.json()) // Converts server response into a JS JSON object
    .then(data => { // Takes server response and logs it in browser console
        console.log('Server response:', data);
    })
    .catch(error => {
        console.error('Error sending time to server:', error);
    });
}

/** Gets the whole JSON file from the server and makes the user download it */
function downloadJSON() {
    fetch('/api/getJSON')
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'data.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

initCharts();
