document.addEventListener("DOMContentLoaded", function () {

  // ── Bootstrap tooltip initialisation ─────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el, { trigger: "hover" });
  });

  // ── Auto-dismiss flash alerts after 4 seconds ─────────────────────────────
  document.querySelectorAll(".auto-dismiss").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      if (bsAlert) {
        bsAlert.close();
      } else {
        alertEl.style.opacity = "0";
        setTimeout(function () { alertEl.remove(); }, 500);
      }
    }, 4000);
  });

  // ── Quick-add modal: close on flash (page reload after POST/redirect) ──────
  // The modal is handled entirely by Bootstrap data attributes on matrix.html.
  // After the form redirects, the flash message appears on the reloaded page.

});
