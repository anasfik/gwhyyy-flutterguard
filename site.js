const menu = document.querySelector(".mobile-nav");

menu?.addEventListener("click", (event) => {
  if (event.target.closest("a")) menu.removeAttribute("open");
});
