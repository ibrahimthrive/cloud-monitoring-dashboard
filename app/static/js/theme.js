(function () {
    const STORAGE_KEY = "cloud-monitor-theme";
    const root = document.documentElement;
    const toggleBtn = document.getElementById("themeToggle");
    const icon = document.getElementById("themeIcon");

    function applyTheme(theme) {
        root.setAttribute("data-bs-theme", theme);
        if (icon) {
            icon.className = theme === "dark" ? "bi bi-sun" : "bi bi-moon-stars";
        }
    }

    const saved = localStorage.getItem(STORAGE_KEY) || "light";
    applyTheme(saved);

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
            localStorage.setItem(STORAGE_KEY, next);
            applyTheme(next);
        });
    }
})();
