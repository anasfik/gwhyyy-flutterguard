const menu = document.querySelector(".mobile-nav");

menu?.addEventListener("click", (event) => {
  if (event.target.closest("a")) menu.removeAttribute("open");
});

const root = document.documentElement;
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ponytail: one observer, reveal only. No scroll listeners, no library.
if (!reduced && "IntersectionObserver" in window) {
  root.classList.add("reveal-ready");

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );

  document.querySelectorAll("[data-reveal]").forEach((el) => observer.observe(el));
}
