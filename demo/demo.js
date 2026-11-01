const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
const panels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

function selectTab(tab) {
  for (const item of tabs) {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
  }

  for (const panel of panels) {
    panel.hidden = panel.id !== tab.getAttribute("aria-controls");
  }
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTab(tab));

  tab.addEventListener("keydown", (event) => {
    if (event.key === "Home" || event.key === "End") {
      event.preventDefault();
      const next = tabs[event.key === "Home" ? 0 : tabs.length - 1];
      next.focus();
      selectTab(next);
      return;
    }

    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = tabs[(index + step + tabs.length) % tabs.length];
    next.focus();
    selectTab(next);
  });
});

for (const button of document.querySelectorAll(".reveal")) {
  const value = document.getElementById(button.getAttribute("aria-controls"));

  button.addEventListener("click", () => {
    const shown = button.getAttribute("aria-expanded") === "true";
    value.textContent = shown ? button.dataset.masked : button.dataset.revealed;
    value.classList.toggle("is-revealed", !shown);
    button.setAttribute("aria-expanded", String(!shown));
    button.textContent = shown ? "Reveal" : "Hide";
  });
}
