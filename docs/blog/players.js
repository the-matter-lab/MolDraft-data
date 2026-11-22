/* A visible timeline for short, silent diagrams. Native controls work without JS. */
document.querySelectorAll('video.clip').forEach(video => {
  const label = video.getAttribute('aria-label');
  const bar = document.createElement('div');
  bar.className = 'clip-bar';
  const toggle = document.createElement('button');
  toggle.type = 'button';
  const seek = document.createElement('input');
  seek.type = 'range';
  seek.min = '0';
  seek.step = '0.05';
  seek.value = '0';
  seek.disabled = true;
  seek.setAttribute('aria-label', 'Seek: ' + label);
  const time = document.createElement('span');
  const format = seconds => '0:' + String(Math.floor(seconds)).padStart(2, '0');
  function update() {
    const duration = video.duration;
    const playing = !video.paused && !video.ended;
    toggle.textContent = playing ? 'Pause' : video.ended ? 'Replay' : 'Play';
    toggle.setAttribute('aria-label', toggle.textContent + ': ' + label);
    if (Number.isFinite(duration) && duration > 0) {
      seek.max = String(duration);
      seek.disabled = false;
      seek.value = String(video.currentTime);
      time.textContent = format(video.currentTime) + ' / ' + format(duration);
      seek.setAttribute('aria-valuetext', time.textContent);
    }
  }
  toggle.addEventListener('click', () => {
    if (!video.paused && !video.ended) video.pause();
    else {
      if (video.ended) video.currentTime = 0;
      video.play().catch(() => { video.controls = true; bar.hidden = true; });
    }
  });
  seek.addEventListener('input', () => { video.currentTime = Number(seek.value); });
  ['loadedmetadata', 'durationchange', 'timeupdate', 'seeked', 'play', 'pause', 'ended'].forEach(event => video.addEventListener(event, update));
  bar.append(toggle, seek, time);
  video.after(bar);
  video.controls = false;
  update();
});
