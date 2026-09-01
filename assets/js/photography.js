(function () {
  "use strict";

  var filters = document.querySelectorAll(".photo-filter");
  var cards = document.querySelectorAll(".photo-card");

  filters.forEach(function (button) {
    button.addEventListener("click", function () {
      var selected = button.getAttribute("data-filter");
      filters.forEach(function (item) {
        item.classList.toggle("is-active", item === button);
      });
      cards.forEach(function (card) {
        card.hidden = selected !== "all" && card.getAttribute("data-category") !== selected;
      });
    });
  });

  var dialog = document.querySelector(".photo-lightbox");
  if (!dialog) return;

  var dialogImage = dialog.querySelector("img");
  var dialogTitle = dialog.querySelector("strong");
  var dialogMeta = dialog.querySelector(".photo-lightbox__caption span");
  var closeButton = dialog.querySelector(".photo-lightbox__close");

  document.querySelectorAll(".photo-open").forEach(function (button) {
    button.addEventListener("click", function () {
      dialogImage.src = button.getAttribute("data-image");
      dialogImage.alt = button.querySelector("img").alt;
      dialogTitle.textContent = button.getAttribute("data-title");
      dialogMeta.textContent = button.getAttribute("data-meta");
      if (typeof dialog.showModal === "function") dialog.showModal();
    });
  });

  closeButton.addEventListener("click", function () {
    dialog.close();
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });

  dialog.addEventListener("close", function () {
    dialogImage.src = "";
  });
})();
