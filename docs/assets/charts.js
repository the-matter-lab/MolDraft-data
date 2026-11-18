/* MolDraft charts: TABLE | COST | TOKENS view toggle (tbench-style) and a hover tooltip
   for the pre-rendered SVG scatter charts. Plain ES5, no dependencies, textContent only. */
(function () {
  'use strict';
  var doc = document;
  var VIEWS = ['table', 'cost', 'tokens', 'atoms'];

  function readData() {
    var node = doc.getElementById('leaderboard-data');
    try { return JSON.parse(node.textContent); } catch (e) { return null; }
  }
  var data = readData();
  var entries = (data && Array.isArray(data.entries)) ? data.entries : [];
  var byId = {};
  entries.forEach(function (e) { if (e && e.model_id) byId[e.model_id] = e; });

  /* ---------------------------------------------------------------- view toggle (?view=) */
  function setView(name, push) {
    if (VIEWS.indexOf(name) < 0) name = 'table';
    var panels = doc.querySelectorAll('.view[data-view]');
    for (var i = 0; i < panels.length; i++) {
      if (panels[i].getAttribute('data-view') === name) panels[i].removeAttribute('hidden');
      else panels[i].setAttribute('hidden', '');
    }
    var btns = doc.querySelectorAll('.view-btn');
    for (var j = 0; j < btns.length; j++) {
      btns[j].setAttribute('aria-pressed', btns[j].getAttribute('data-view') === name ? 'true' : 'false');
    }
    var details = doc.querySelectorAll('[data-table-only]');
    for (var k = 0; k < details.length; k++) {
      details[k].hidden = name !== 'table';
    }
    if (push && window.history && window.history.replaceState) {
      try {
        var url = new URL(window.location.href);
        if (name === 'table') url.searchParams['delete']('view'); else url.searchParams.set('view', name);
        window.history.replaceState(null, '', url.toString());
      } catch (e) { /* ignore */ }
    }
  }
  function initialView() {
    try {
      var v = new URL(window.location.href).searchParams.get('view');
      if (v && VIEWS.indexOf(v) >= 0) return v;
    } catch (e) { /* ignore */ }
    return 'table';
  }
  function wireToggle() {
    var btns = doc.querySelectorAll('.view-btn');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function (ev) {
        setView(ev.currentTarget.getAttribute('data-view'), true);
      });
    }
    var aboutLinks = doc.querySelectorAll('a[href="#about"]');
    for (var j = 0; j < aboutLinks.length; j++) {
      aboutLinks[j].addEventListener('click', function () {
        setView('table', true);
      });
    }
    setView(initialView(), false);
  }

  /* ---------------------------------------------------------------- tooltip */
  function fmtCost(v) {
    if (v == null) return '—';
    if (v >= 1000) return '$' + (v / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    if (v >= 1) return '$' + v.toFixed(2);
    return '$' + v.toFixed(4).replace(/0+$/, '');
  }
  function fmtTok(v) {
    if (v == null) return '—';
    if (v >= 1e9) return (v / 1e9).toFixed(2).replace(/\.?0+$/, '') + 'B';
    if (v >= 1e6) return (v / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (v >= 1e3) return (v / 1e3).toFixed(0) + 'k';
    return String(v);
  }
  var tip = null;
  function tooltip() {
    if (tip) return tip;
    tip = doc.createElement('div');
    tip.className = 'chart-tip';
    tip.setAttribute('role', 'status');
    tip.hidden = true;
    doc.body.appendChild(tip);
    return tip;
  }
  function row(label, value, muted) {
    var r = doc.createElement('div');
    r.className = 'chart-tip-row' + (muted ? ' muted' : '');
    var l = doc.createElement('span'); l.textContent = label;
    var v = doc.createElement('span'); v.textContent = value;
    r.appendChild(l); r.appendChild(v);
    return r;
  }
  function fill(e, variant, frontier) {
    var t = tooltip();
    while (t.firstChild) t.removeChild(t.firstChild);
    var h = doc.createElement('div');
    h.className = 'chart-tip-head';
    h.textContent = (e.display_name || e.model_id) + (e.effort ? ' (' + e.effort + ')' : '');
    t.appendChild(h);
    if (e.organization) t.appendChild(row('', e.organization, true));
    var c = e.cost_usd || {}, k = e.tokens || {};
    t.appendChild(row('Success rate', (e.success_rate != null ? e.success_rate.toFixed(1) + '%' : '—') +
      (e.passed != null && e.n != null ? ' (' + e.passed + '/' + e.n + ')' : '')));
    t.appendChild(row('Cost/molecule', fmtCost(c.per_task_mean), variant !== 'cost'));
    t.appendChild(row('Tokens of run', fmtTok(k.total) + (k.input != null ? ' · in ' + fmtTok(k.input) + ' / out ' + fmtTok(k.output) : ''), variant !== 'tokens'));
    if (k.cache_hit_pct != null) t.appendChild(row('Cache hit', k.cache_hit_pct.toFixed(0) + '%', true));
    t.appendChild(row('Pareto frontier', frontier ? 'yes' : 'no'));
  }
  function show(x, y) {
    var t = tooltip();
    t.hidden = false;
    var pad = 14, w = t.offsetWidth, hgt = t.offsetHeight;
    var left = x + pad, top = y + pad;
    if (left + w > window.innerWidth - 8) left = x - pad - w;
    if (top + hgt > window.innerHeight - 8) top = y - pad - hgt;
    t.style.left = left + 'px'; t.style.top = top + 'px';
  }
  function hide() { if (tip) tip.hidden = true; }

  function wireChart(svg) {
    var variant = svg.getAttribute('data-variant');
    var pts = svg.querySelectorAll('rect.pt');
    function enter(ev) {
      var id = ev.currentTarget.getAttribute('data-id');
      var e = byId[id];
      if (!e) return;
      fill(e, variant, ev.currentTarget.classList.contains('pt-frontier'));
      var r = ev.currentTarget.getBoundingClientRect();
      show(ev.clientX != null && ev.type !== 'focus' ? ev.clientX : r.right, ev.clientY != null && ev.type !== 'focus' ? ev.clientY : r.top);
    }
    for (var i = 0; i < pts.length; i++) {
      pts[i].addEventListener('mouseenter', enter);
      pts[i].addEventListener('mousemove', function (ev) { if (tip && !tip.hidden) show(ev.clientX, ev.clientY); });
      pts[i].addEventListener('mouseleave', hide);
      pts[i].addEventListener('focus', enter);
      pts[i].addEventListener('blur', hide);
    }
  }

  /* atom-size bars: pooled rate plus each model's rate in the bin */
  function fillBin(bin) {
    var t = tooltip();
    while (t.firstChild) t.removeChild(t.firstChild);
    var h = doc.createElement('div');
    h.className = 'chart-tip-head';
    h.textContent = bin.label + ' atoms · ' + bin.n + ' molecules';
    t.appendChild(h);
    var p = bin.pooled || {};
    t.appendChild(row('All models', (p.rate != null ? p.rate.toFixed(1) + '%' : '—') + ' (' + p.passed + '/' + p.total + ')'));
    var ids = Object.keys(bin.models || {});
    ids.sort(function (a, b) { return (bin.models[b].rate || 0) - (bin.models[a].rate || 0); });
    ids.forEach(function (id) {
      var m = bin.models[id], e = byId[id] || {};
      t.appendChild(row(e.display_name || id, (m.rate != null ? m.rate.toFixed(1) + '%' : '—') + ' (' + m.passed + '/' + m.n + ')', true));
    });
  }
  function fillSeries(bin, id) {
    var t = tooltip();
    while (t.firstChild) t.removeChild(t.firstChild);
    var e = byId[id] || {}, m = (bin.models || {})[id] || {};
    var h = doc.createElement('div');
    h.className = 'chart-tip-head';
    h.textContent = (e.display_name || id) + ' · ' + bin.label + ' atoms';
    t.appendChild(h);
    t.appendChild(row('Success rate', (m.rate != null ? m.rate.toFixed(1) + '%' : '—') + ' (' + (m.passed || 0) + '/' + (m.n || 0) + ')'));
    var p = bin.pooled || {};
    t.appendChild(row('All models', (p.rate != null ? p.rate.toFixed(1) + '%' : '—'), true));
  }
  function wireChips() {
    var chips = doc.querySelectorAll('.chip[data-mode]');
    var panels = doc.querySelectorAll('.atoms-mode[data-mode]');
    function pick(mode) {
      for (var i = 0; i < panels.length; i++) {
        if (panels[i].getAttribute('data-mode') === mode) panels[i].removeAttribute('hidden');
        else panels[i].setAttribute('hidden', '');
      }
      for (var j = 0; j < chips.length; j++) {
        chips[j].setAttribute('aria-pressed', chips[j].getAttribute('data-mode') === mode ? 'true' : 'false');
      }
    }
    for (var k = 0; k < chips.length; k++) {
      chips[k].addEventListener('click', function (ev) { pick(ev.currentTarget.getAttribute('data-mode')); });
    }
  }
  function wireBars(svg) {
    var bins = (data && data.atom_bins && data.atom_bins.bins) || [];
    var bars = svg.querySelectorAll('rect.bin-bar');
    function enter(ev) {
      var i = parseInt(ev.currentTarget.getAttribute('data-bin'), 10);
      if (!bins[i]) return;
      var series = ev.currentTarget.getAttribute('data-series');
      if (series && series !== 'all') fillSeries(bins[i], series); else fillBin(bins[i]);
      var r = ev.currentTarget.getBoundingClientRect();
      show(ev.type === 'focus' ? r.right : ev.clientX, ev.type === 'focus' ? r.top : ev.clientY);
    }
    for (var i = 0; i < bars.length; i++) {
      bars[i].addEventListener('mouseenter', enter);
      bars[i].addEventListener('mousemove', function (ev) { if (tip && !tip.hidden) show(ev.clientX, ev.clientY); });
      bars[i].addEventListener('mouseleave', hide);
      bars[i].addEventListener('focus', enter);
      bars[i].addEventListener('blur', hide);
    }
  }

  function init() {
    wireToggle();
    wireChips();
    var svgs = doc.querySelectorAll('svg.chart-svg');
    for (var i = 0; i < svgs.length; i++) {
      if (svgs[i].getAttribute('data-variant') === 'atoms') wireBars(svgs[i]); else wireChart(svgs[i]);
    }
    doc.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hide(); });
  }
  init();
})();
