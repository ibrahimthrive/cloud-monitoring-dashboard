(function () {
    const tbody = document.getElementById("serviceTableBody");

    function refreshServices() {
        apiFetch("/api/services")
            .then((services) => {
                if (!services.length) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No services found on this platform</td></tr>';
                    return;
                }
                tbody.innerHTML = services
                    .map(
                        (s) => `
                        <tr>
                            <td>${s.name}</td>
                            <td>${s.display_name || "-"}</td>
                            <td><span class="badge text-bg-secondary">${s.status}</span></td>
                            <td>${s.start_type || "-"}</td>
                        </tr>`
                    )
                    .join("");
            })
            .catch((err) => console.error("Failed to load services:", err));
    }

    refreshServices();
    setInterval(refreshServices, 15000);
})();
