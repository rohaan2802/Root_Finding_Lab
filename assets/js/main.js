"use strict";

const root = document.documentElement;
const themeButton = document.querySelector("#theme");

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeButton.setAttribute("aria-pressed", theme === "dark");
  themeButton.textContent = theme === "dark" ? "Light" : "Dark";
}

let savedTheme;
try {
  savedTheme = localStorage.getItem("root-lab-theme");
} catch {
  // The site also works from a local file with storage blocked.
}
const prefersDark = matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(savedTheme === "dark" || (!savedTheme && prefersDark) ? "dark" : "light");
themeButton.addEventListener("click", () => {
  const theme = root.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(theme);
  try {
    localStorage.setItem("root-lab-theme", theme);
  } catch {
    // The theme remains active for this page.
  }
});

const backTop = document.querySelector("#back-top");
const brand = document.querySelector(".brand");
function updateBackTop() {
  backTop.hidden = scrollY < 500;
}
window.addEventListener("scroll", updateBackTop, { passive: true });
backTop.addEventListener("click", () => {
  brand.focus({ preventScroll: true });
  window.scrollTo({ top: 0 });
});
updateBackTop();

const cards = [...document.querySelectorAll(".shot")];
const filters = [...document.querySelectorAll("[data-filter]")];
const search = document.querySelector("#search");
const count = document.querySelector("#count");
let category = "All";
let visible = cards;

function filterGallery() {
  const term = search.value.trim().toLowerCase();
  visible = cards.filter(card => {
    const match = (category === "All" || card.dataset.category === category)
      && card.textContent.toLowerCase().includes(term);
    card.hidden = !match;
    return match;
  });
  count.textContent = visible.length
    ? `${visible.length} ${visible.length === 1 ? "figure" : "figures"}`
    : "No figures match your search.";
}

search.addEventListener("input", filterGallery);
for (const filter of filters) {
  filter.addEventListener("click", () => {
    category = filter.dataset.filter;
    for (const button of filters) button.setAttribute("aria-pressed", button === filter);
    filterGallery();
  });
}

const viewer = document.querySelector("#viewer");
const title = document.querySelector("#viewer-title");
const caption = document.querySelector("#viewer-caption");
const position = document.querySelector("#position");
const imageArea = document.querySelector("#viewer-image");
const image = imageArea.querySelector("img");
const zoom = document.querySelector("#zoom");
const prev = document.querySelector("#prev");
const next = document.querySelector("#next");
let index = 0;
let opener;
let touchStart;

function setZoom(on) {
  imageArea.classList.toggle("zoomed", on);
  imageArea.scrollTo(0, 0);
  zoom.setAttribute("aria-pressed", on);
  zoom.textContent = on ? "Zoom out" : "Zoom in";
}

function showFigure(delta) {
  index = (index + delta + visible.length) % visible.length;
  const card = visible[index];
  title.textContent = card.querySelector("strong").textContent;
  caption.textContent = card.querySelector("p").textContent;
  image.src = card.querySelector("a").href;
  image.alt = title.textContent;
  position.textContent = `${index + 1} / ${visible.length}`;
  prev.disabled = next.disabled = visible.length < 2;
  setZoom(false);
}

for (const card of cards) {
  const link = card.querySelector("a");
  link.addEventListener("click", event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    index = visible.indexOf(card);
    showFigure(0);
    viewer.showModal();
  });
}

document.querySelector("#close").addEventListener("click", () => viewer.close());
viewer.addEventListener("close", () => opener.focus());
prev.addEventListener("click", () => showFigure(-1));
next.addEventListener("click", () => showFigure(1));
zoom.addEventListener("click", () => setZoom(zoom.getAttribute("aria-pressed") !== "true"));
viewer.addEventListener("keydown", event => {
  if (event.target === imageArea && imageArea.classList.contains("zoomed")) return;
  if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
    event.preventDefault();
    showFigure(event.key === "ArrowRight" ? 1 : -1);
  }
});
imageArea.addEventListener("touchstart", event => {
  touchStart = event.touches.length === 1 ? event.touches[0] : null;
}, { passive: true });
imageArea.addEventListener("touchcancel", () => touchStart = null);
imageArea.addEventListener("touchend", event => {
  if (!touchStart || imageArea.classList.contains("zoomed")) return;
  const touch = event.changedTouches[0];
  const dx = touch.clientX - touchStart.clientX;
  const dy = touch.clientY - touchStart.clientY;
  touchStart = null;
  if (Math.abs(dx) > 50 && Math.abs(dx) > 1.3 * Math.abs(dy)) {
    showFigure(dx < 0 ? 1 : -1);
  }
}, { passive: true });
