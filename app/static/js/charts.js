/* Chart.js instances shared by the dashboard page. */
function createCpuRamChart(ctx) {
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "CPU %", data: [], borderColor: "#0d6efd", tension: 0.3, pointRadius: 0 },
                { label: "RAM %", data: [], borderColor: "#198754", tension: 0.3, pointRadius: 0 },
            ],
        },
        options: {
            responsive: true,
            animation: false,
            scales: { y: { min: 0, max: 100 } },
        },
    });
}

function createNetworkChart(ctx) {
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "Upload KB/s", data: [], borderColor: "#dc3545", tension: 0.3, pointRadius: 0 },
                { label: "Download KB/s", data: [], borderColor: "#0dcaf0", tension: 0.3, pointRadius: 0 },
            ],
        },
        options: { responsive: true, animation: false, scales: { y: { min: 0 } } },
    });
}

function createDiskChart(ctx) {
    return new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Used", "Free"],
            datasets: [{ data: [0, 100], backgroundColor: ["#ffc107", "#e9ecef"] }],
        },
        options: { responsive: true, animation: false },
    });
}

function pushRollingPoint(chart, label, values, maxPoints = 30) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset, i) => dataset.data.push(values[i]));
    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach((dataset) => dataset.data.shift());
    }
    chart.update();
}
