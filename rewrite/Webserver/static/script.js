function generateLabels(mode) {
    const labels = [];
    for (let i = 0; i < 24; i++) {
        if (mode === 'hour') {
            labels.push(`${i.toString().padStart(2, '0')}:00`);
        } else if (mode === 'rolling') {
            const minutes = (23 - i) * 10;
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;

            if (i === 23) {
                labels.push("now");
            } else if (hours === 0) {
                labels.push(`-${mins}m`);
            } else if (mins === 0) {
                labels.push(`-${hours}h`);
            } else {
                labels.push(`-${hours}h${mins}m`);
            }
        }
    }
    return labels;
}

const hourLabels = generateLabels('hour');
const rollingLabels = generateLabels('rolling');
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

function initCharts() {
    const graphs = ['graphPower', 'graphUV', 'graphAirQuality', 'graphPowerPrice', 'graphAirTemp', 'graphTouchTemp'];
    const datasets = [
        createChartData(rollingLabels, initialData.slice()),
        createChartData(rollingLabels, initialData.slice()),
        createChartData(rollingLabels, initialData.slice()),
        powerData,
        createChartData(rollingLabels, initialData.slice()),
        createChartData(rollingLabels, initialData.slice()) 
    ];

    const defaultConfig = {
        scales: { y: { beginAtZero: true } },
        plugins: { legend: { display: false } }
    };

    const configs = [
         {type: 'line', options: defaultConfig},
         {type: 'bar', options: defaultConfig},
         {type: 'line', options: defaultConfig},
         {type: 'bar', options:defaultConfig},
         {type: 'line', options:defaultConfig},
         {type: 'line', options: defaultConfig} 
    ];

    graphs.forEach((graph, index) => {
        charts[graph] = new Chart(
            document.getElementById(graph),
            {
                type: configs[index].type,
                data: datasets[index],
                options: configs[index].options
            }
        );
    });
}

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

initCharts();

function updateArduinoData() {
    fetch('/api/update')
        .then(response => response.json())
        .then(data => {
            console.log("Data updated:", data);
        })
        .catch(error => console.error('Error updating data:', error));
}

function updateCharts() {
    fetch('/api/data')
        .then(response => response.json())
        .then(dataArray => {
            if (!Array.isArray(dataArray) || dataArray.length === 0) {
                console.error('Invalid data format received');
                return;
            }

            dataArray.sort((a, b) => {
                if (!a.time) return -1;
                if (!b.time) return 1;

                const timeA = new Date(a.time);
                const timeB = new Date(b.time);

                const diffInMinutes = Math.abs((timeA - timeB) / (1000 * 60));
                if (diffInMinutes <= 1) {
                    return 0;
                }

                return timeA - timeB;
            });

            const latestData = dataArray[dataArray.length - 1];

            if (latestData.powerPrice && latestData.powerPrice.length > 0) {
                updateChartData(charts['graphPowerPrice'], latestData.powerPrice);
            }

            const recentData = dataArray.slice(-24);

            const uvValues = recentData.map(item => item.uv || 0);
            const airQualityValues = recentData.map(item => item.airQuality || 0);
            const powerValues = recentData.map(item => item.power || 0);
            const airTemperatureValues = recentData.map(item => item.airTemp || 0); 
            const touchTemperatureValues = recentData.map(item => item.touchTemp || 0); 

            updateChartData(charts['graphUV'], uvValues);
            updateChartData(charts['graphAirQuality'], airQualityValues);
            updateChartData(charts['graphPower'], powerValues);
            updateChartData(charts['graphAirTemp'], airTemperatureValues);
            updateChartData(charts['graphTouchTemp'], touchTemperatureValues); 
            updateChartData(charts['graphPowerPrice'], latestData.powerPrice);

            console.log('Charts updated with sorted data using 1-minute tolerance');
        })
        .catch(error => console.error('Error fetching data:', error));
}

function updateChartData(chartObject, dataArray) {
    chartObject.data.datasets[0].data = dataArray;
    chartObject.update();
}

function changeUpdateTime(newUpdateTime) {
    fetch('/api/changeUpdateTime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({value: newUpdateTime})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
    })
    .catch(error => {
        console.error('Error sending time to server:', error);
    });
}

function downloadJSON() {
    fetch('/api/getJSON')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
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
        })
        .catch(error => console.error('Error downloading JSON:', error));
}