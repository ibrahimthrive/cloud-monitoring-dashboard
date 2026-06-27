/* Polls /api/metrics/current every LIVE_REFRESH_INTERVAL_MS and updates cards + charts. */
(function () {
    const refreshMs = window.LIVE_REFRESH_INTERVAL_MS || 5000;

    const cpuRamChart = createCpuRamChart(document.getElementById("cpuRamChart"));
    const networkChart = createNetworkChart(document.getElementById("networkChart"));
    const diskChart = createDiskChart(document.getElementById("diskChart"));

    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    function setBar(id, percent) {
        const el = document.getElementById(id);
        if (el) el.style.width = `${Math.min(percent, 100)}%`;
    }

    function refreshMetrics() {
        apiFetch("/api/metrics/current")
            .then((data) => {
                const time = new Date(data.timestamp).toLocaleTimeString();

                setText("hostnameLabel", data.hostname);
                setText("osLabel", data.os);
                setText("uptimeLabel", data.uptime_human);

                setText("cpuValue", `${data.cpu.percent.toFixed(1)}%`);
                setBar("cpuBar", data.cpu.percent);

                setText("ramValue", `${data.ram.percent.toFixed(1)}%`);
                setBar("ramBar", data.ram.percent);

                setText("diskValue", `${data.disk.percent.toFixed(1)}%`);
                setBar("diskBar", data.disk.percent);

                setText("netUp", data.network.upload_kbps.toFixed(1));
                setText("netDown", data.network.download_kbps.toFixed(1));

                pushRollingPoint(cpuRamChart, time, [data.cpu.percent, data.ram.percent]);
                pushRollingPoint(networkChart, time, [data.network.upload_kbps, data.network.download_kbps]);

                diskChart.data.datasets[0].data = [data.disk.percent, Math.max(0, 100 - data.disk.percent)];
                diskChart.update();
            })
            .catch((err) => console.error("Failed to refresh metrics:", err));
    }

    function refreshAlerts() {
        apiFetch("/api/alerts/logs?limit=5")
            .then((logs) => {
                const list = document.getElementById("alertList");
                if (!list) return;
                if (!logs.length) {
                    list.innerHTML = '<li class="list-group-item text-muted">No alerts yet</li>';
                    return;
                }
                list.innerHTML = logs
                    .map(
                        (log) => `
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${log.metric_type.toUpperCase()}</strong> ${log.message}
                            </div>
                            <small class="text-muted">${new Date(log.timestamp).toLocaleString()}</small>
                        </li>`
                    )
                    .join("");
            })
            .catch((err) => console.error("Failed to refresh alerts:", err));
    }

    refreshMetrics();
    refreshAlerts();
    setInterval(refreshMetrics, refreshMs);
    setInterval(refreshAlerts, refreshMs * 4);
})();
