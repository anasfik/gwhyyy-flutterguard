/* Progressive media preferences only. All navigation and content work without JS. */
(() => {
  const video = document.querySelector('.device-video');
  const pause = document.querySelector('#pause-motion');
  if (!video || !pause) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  let inView = false;
  const applyPreference = () => {
    if (!inView || reduce.matches || pause.checked) {
      video.pause();
    } else {
      // Autoplay denial is expected on some browsers; native controls stay usable.
      video.play().catch(() => {});
    }
  };
  const showFallback = () => video.parentElement.classList.add('media-error');
  video.addEventListener('error', showFallback);
  video.querySelector('source')?.addEventListener('error', showFallback);
  // A fast failure can land before this script runs; NETWORK_NO_SOURCE is the only
  // state that means "every source already failed", so it cannot fire on a healthy load.
  if (video.error) showFallback();
  if (video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) showFallback();
  pause.addEventListener('change', applyPreference);
  reduce.addEventListener('change', applyPreference);
  applyPreference();
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting && entry.intersectionRatio >= 0.4;
      applyPreference();
    }, { threshold: [0, 0.4] }).observe(video);
  }
})();
