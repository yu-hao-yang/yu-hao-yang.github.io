(function () {
  "use strict";

  var page = document.querySelector(".photo-page");
  if (!page) return;
  var filters = Array.from(page.querySelectorAll(".photo-filter"));
  var cards = Array.from(page.querySelectorAll(".photo-card"));
  var buttons = Array.from(page.querySelectorAll(".photo-open"));
  var styleButtons = Array.from(document.querySelectorAll("[data-photo-style]"));
  var status = page.querySelector(".photo-style-status");
  var dialog = document.querySelector(".photo-lightbox");
  var dialogImage = dialog && dialog.querySelector(".photo-lightbox__stage img");
  var currentPhoto = null;
  var style = "original";
  var storageKey = "photography-image-style";

  function imageSource(button) {
    return button.getAttribute(style === "postcard" ? "data-postcard" : "data-image");
  }

  function imageAlt(button) {
    return button.getAttribute(style === "postcard" ? "data-postcard-alt" : "data-original-alt");
  }

  function updateDialog() {
    if (!currentPhoto || !dialogImage) return;
    dialogImage.src = imageSource(currentPhoto);
    dialogImage.alt = imageAlt(currentPhoto);
    dialog.querySelector(".photo-lightbox__caption strong").textContent = currentPhoto.getAttribute("data-title");
    dialog.querySelector(".photo-lightbox__caption span").textContent = currentPhoto.getAttribute("data-meta");
    dialog.setAttribute("data-style", style);
  }

  function setStyle(selected, remember) {
    style = selected === "postcard" ? "postcard" : "original";
    page.setAttribute("data-style", style);
    styleButtons.forEach(function (button) {
      var active = button.getAttribute("data-photo-style") === style;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    buttons.forEach(function (button) {
      var image = button.querySelector("img");
      image.src = imageSource(button);
      image.alt = imageAlt(button);
      image.width = style === "postcard" ? 1086 : Number(button.getAttribute("data-original-width"));
      image.height = style === "postcard" ? 1448 : Number(button.getAttribute("data-original-height"));
      button.setAttribute("aria-label", "View " + style + " from " + button.getAttribute("data-title") + ", " + button.getAttribute("data-meta") + " full screen");
    });
    updateDialog();
    if (status) status.textContent = style === "postcard" ? "Showing postcards" : "Showing original photographs";
    if (remember) {
      try { localStorage.setItem(storageKey, style); } catch (error) { /* Storage may be disabled. */ }
    }
  }

  styleButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setStyle(button.getAttribute("data-photo-style"), true);
    });
  });
  try { style = localStorage.getItem(storageKey) === "postcard" ? "postcard" : "original"; } catch (error) { /* Use the default. */ }
  setStyle(style, false);
  page.querySelector(".photo-style-switch").hidden = false;

  filters.forEach(function (button) {
    button.addEventListener("click", function () {
      var selected = button.getAttribute("data-filter");
      filters.forEach(function (item) {
        var active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      cards.forEach(function (card) {
        card.hidden = selected !== "all" && card.getAttribute("data-category") !== selected;
      });
    });
  });

  if (!dialog) return;
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      currentPhoto = button;
      updateDialog();
      if (typeof dialog.showModal === "function") dialog.showModal();
    });
  });
  dialog.querySelector(".photo-lightbox__close").addEventListener("click", function () { dialog.close(); });
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog || event.target === dialog.querySelector(".photo-lightbox__stage")) dialog.close();
  });
  dialog.addEventListener("close", function () {
    dialogImage.removeAttribute("src");
    currentPhoto = null;
  });
})();
