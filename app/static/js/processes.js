(function () {
    const refreshMs = window.LIVE_REFRESH_INTERVAL_MS || 5000;
    const tbody = document.getElementById("processTableBody");

    function refreshProcesses() {
        apiFetch("/api/processes?limit=50")
            .then((processes) => {
                if (!processes.length) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No processes found</td></tr>';
                    return;
                }
                tbody.innerHTML = processes
                    .map(
                        (p) => `
                        <tr>
                            <td>${p.pid}</td>
                            <td>${p.name}</td>
                            <td>${p.username || "-"}</td>
                            <td><span class="badge text-bg-secondary">${p.status}</span></td>
                            <td>${p.cpu_percent.toFixed(1)}%</td>
                            <td>${p.memory_percent.toFixed(1)}%</td>
                        </tr>`
                    )
                    .join("");
            })
            .catch((err) => console.error("Failed to load processes:", err));
    }

    refreshProcesses();
    setInterval(refreshProcesses, refreshMs);
})();
