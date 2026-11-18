/* Use a still frame when reduced motion is requested; allow the visitor to pause. */
(function () {
  'use strict';
  var image = document.getElementById('demo-animation');
  var button = document.getElementById('demo-motion');
  if (!image || !button) return;
  var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  function setPlaying(playing) {
    image.src = playing ? image.dataset.animation : image.dataset.poster;
    button.textContent = playing ? 'Pause rotation' : 'Play rotation';
    button.setAttribute('aria-label', button.textContent);
    button.dataset.playing = String(playing);
  }
  setPlaying(!preference.matches);
  button.hidden = false;
  button.addEventListener('click', function () {
    setPlaying(button.dataset.playing !== 'true');
  });
  function preferenceChanged(event) { setPlaying(!event.matches); }
  if (preference.addEventListener) preference.addEventListener('change', preferenceChanged);
  else if (preference.addListener) preference.addListener(preferenceChanged);
})();
