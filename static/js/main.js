/* ==========================================================================
   StockPilot IMS - Global JS
   Handles: dark mode toggle, sidebar toggle, toast auto-init, loading
   spinner on navigation/form submit, and delete-confirmation dialogs.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
  /* ---------------- Dark mode ---------------- */
  const root = document.documentElement;
  const darkToggle = document.getElementById("darkModeToggle");
  const darkIcon = document.getElementById("darkModeIcon");

  function applyTheme(theme) {
    root.setAttribute("data-bs-theme", theme);
    if (darkIcon) {
      darkIcon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
    }
  }

  const savedTheme = localStorage.getItem("sp-theme") || "light";
  applyTheme(savedTheme);

  if (darkToggle) {
    darkToggle.addEventListener("click", function () {
      const current = root.getAttribute("data-bs-theme");
      const next = current === "dark" ? "light" : "dark";
      localStorage.setItem("sp-theme", next);
      applyTheme(next);
    });
  }

  /* ---------------- Sidebar toggle (mobile) ---------------- */
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
    document.addEventListener("click", function (e) {
      if (window.innerWidth < 992 && sidebar.classList.contains("show")) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
          sidebar.classList.remove("show");
        }
      }
    });
  }

  /* ---------------- Toasts ---------------- */
  document.querySelectorAll(".toast").forEach(function (toastEl) {
    const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
    toast.show();
  });

  /* ---------------- Bootstrap tooltips ---------------- */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ---------------- Loading overlay on navigation ---------------- */
  const overlay = document.getElementById("loadingOverlay");
  function showOverlay() { if (overlay) overlay.classList.remove("d-none"); }

  document.querySelectorAll("a.nav-link, a.page-link, .use-loading").forEach(function (link) {
    link.addEventListener("click", function () {
      if (link.target !== "_blank") showOverlay();
    });
  });

  document.querySelectorAll("form:not(.no-loading)").forEach(function (form) {
    form.addEventListener("submit", function () {
      if (form.checkValidity()) showOverlay();
    });
  });

  /* ---------------- Delete confirmation ---------------- */
  document.querySelectorAll(".confirm-delete-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const name = form.getAttribute("data-name") || "this item";
      if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  /* ---------------- Bootstrap client-side validation ---------------- */
  document.querySelectorAll(".needs-validation").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });
});
