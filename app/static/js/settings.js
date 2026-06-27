(function () {
    const cpuInput = document.getElementById("cpuThreshold");
    const ramInput = document.getElementById("ramThreshold");
    const diskInput = document.getElementById("diskThreshold");
    const emailInput = document.getElementById("emailEnabled");
    const saveBtn = document.getElementById("saveSettingsBtn");
    const successMsg = document.getElementById("saveSuccessMsg");
    const historyList = document.getElementById("alertHistoryList");

    function loadSettings() {
        apiFetch("/api/alerts/settings").then((settings) => {
            cpuInput.value = settings.cpu_threshold;
            ramInput.value = settings.ram_threshold;
            diskInput.value = settings.disk_threshold;
            emailInput.checked = settings.email_enabled;
        });
    }

    function loadHistory() {
        apiFetch("/api/alerts/logs?limit=20").then((logs) => {
            if (!logs.length) {
                historyList.innerHTML = '<li class="list-group-item text-muted">No alerts recorded</li>';
                return;
            }
            historyList.innerHTML = logs
                .map(
                    (log) => `
                    <li class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <strong>${log.metric_type.toUpperCase()}</strong>
                            <small class="text-muted">${new Date(log.timestamp).toLocaleString()}</small>
                        </div>
                        <div class="small">${log.message}</div>
                    </li>`
                )
                .join("");
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener("click", () => {
            apiFetch("/api/alerts/settings", {
                method: "POST",
                body: JSON.stringify({
                    cpu_threshold: parseFloat(cpuInput.value),
                    ram_threshold: parseFloat(ramInput.value),
                    disk_threshold: parseFloat(diskInput.value),
                    email_enabled: emailInput.checked,
                }),
            })
                .then(() => {
                    successMsg.classList.remove("d-none");
                    setTimeout(() => successMsg.classList.add("d-none"), 2000);
                })
                .catch((err) => alert(`Failed to save settings: ${err.message}`));
        });
    }

    loadSettings();
    loadHistory();
})();
