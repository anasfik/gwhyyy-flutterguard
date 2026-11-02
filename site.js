/* Progressive media preferences only. All navigation and content work without JS. */
(() => {
  const video = document.querySelector('.device-video');
  const pause = document.querySelector('#pause-motion');
  if (!video || !pause) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const applyPreference = () => {
    if (reduce.matches || pause.checked) {
      video.pause();
    } else {
      // Autoplay denial is expected on some browsers; native controls stay usable.
      video.play().catch(() => {});
    }
  };
  const showFallback = () => video.parentElement.classList.add('media-error');
  video.addEventListener('error', showFallback);
  video.querySelector('source')?.addEventListener('error', showFallback);
  if (video.error || video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) showFallback();
  pause.addEventListener('change', applyPreference);
  reduce.addEventListener('change', applyPreference);
  applyPreference();
})();
