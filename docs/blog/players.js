/* Draw each verifier example at a deterministic time so every frame is seekable. */
document.querySelectorAll('.verifier-clip').forEach(figure => {
  const svg = figure.querySelector('svg');
  const label = svg.querySelector('title').textContent;
  const paths = [...svg.querySelectorAll('.mapping')];
  const duration = 6;
  let position = 0;
  let frame = null;
  let startedAt = 0;

  const bar = document.createElement('div');
  bar.className = 'clip-bar';
  const toggle = document.createElement('button');
  toggle.type = 'button';
  const seek = document.createElement('input');
  seek.type = 'range';
  seek.min = '0';
  seek.max = String(duration);
  seek.step = '0.1';
  seek.setAttribute('aria-label', 'Seek: ' + label);
  const time = document.createElement('span');
  bar.append(toggle, seek, time);
  svg.after(bar);

  function draw(seconds) {
    position = Math.min(duration, Math.max(0, seconds));
    if (paths.length) {
      paths.forEach((path, i) => {
        const fraction = Math.max(0, Math.min(1, (position - i * 1.6) / 1.5));
        path.style.strokeDashoffset = String(1 - fraction);
      });
    } else {
      // First highlight the two sites to watch, then switch the candidate.
      const focus = Math.max(0, Math.min(1, position - 0.6, 5.8 - position));
      svg.style.setProperty('--focus', String(focus));
      figure.classList.toggle('show-b', position >= duration / 2);
    }
    seek.value = String(position);
    time.textContent = '0:0' + Math.floor(position) + ' / 0:06';
    seek.setAttribute('aria-valuetext', position.toFixed(1) + ' of 6 seconds');
  }

  function updateButton() {
    toggle.textContent = frame !== null ? 'Pause' : position >= duration ? 'Replay' : 'Play';
    toggle.setAttribute('aria-label', toggle.textContent + ': ' + label);
  }

  function stop() {
    cancelAnimationFrame(frame);
    frame = null;
    updateButton();
  }

  function tick(now) {
    draw((now - startedAt) / 1000);
    if (position >= duration) stop();
    else frame = requestAnimationFrame(tick);
  }

  toggle.addEventListener('click', () => {
    if (frame !== null) {
      stop();
      return;
    }
    if (position >= duration) draw(0);
    startedAt = performance.now() - position * 1000;
    frame = requestAnimationFrame(tick);
    updateButton();
  });
  seek.addEventListener('input', () => {
    draw(Number(seek.value));
    stop();
  });
  draw(0);
  updateButton();
});
