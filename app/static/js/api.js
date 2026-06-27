/* Small fetch wrapper that attaches the CSRF token to state-changing requests. */
function apiFetch(url, options = {}) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";
    const method = (options.method || "GET").toUpperCase();

    const headers = Object.assign({}, options.headers);
    if (method !== "GET") {
        headers["X-CSRFToken"] = csrfToken;
    }
    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    return fetch(url, Object.assign({}, options, { headers })).then((response) => {
        if (!response.ok) {
            return response.json().catch(() => ({})).then((data) => {
                throw new Error(data.error || `Request failed with status ${response.status}`);
            });
        }
        return response.json();
    });
}
