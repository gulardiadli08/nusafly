document.addEventListener("DOMContentLoaded", () => {
  const swap = document.getElementById("swap-cities");
  if (swap) {
    swap.addEventListener("click", () => {
      const selects = document.querySelectorAll('.search-form select[name="origin"], .search-form select[name="destination"]');
      if (selects.length === 2) {
        const value = selects[0].value;
        selects[0].value = selects[1].value;
        selects[1].value = value;
      }
    });
  }
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm || "Lanjutkan tindakan ini?")) event.preventDefault();
    });
  });
});
