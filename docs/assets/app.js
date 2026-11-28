/* MolDraft leaderboard. Plain ES2018 in an IIFE, no modules, no fetch: renders the table rows
   from the inline application/json block, cycles the SUCCESS RATE sort, drives the theme toggle
   and fills the About section. A missing value renders as an em dash or drops its clause; nothing
   is invented. Everything runs from init() at the bottom. */
(function () {
  'use strict';

  var DASH = '—';
  var THEME_KEY = 'moldraft-theme';
  var doc = document;

  /* ------------------------------------------------------------ value guards */
  function num(v) {
    return typeof v === 'number' && isFinite(v) ? v : null;
  }
  function str(v) {
    return typeof v === 'string' && v.length > 0 ? v : null;
  }
  function obj(v) {
    return v !== null && typeof v === 'object' && !Array.isArray(v) ? v : {};
  }
  function arr(v) {
    return Array.isArray(v) ? v : [];
  }
  function fmtPct(v) {
    var n = num(v);
    return n === null ? DASH : n.toFixed(1) + '%';
  }
  function fmtInt(v) {
    var n = num(v);
    return n === null ? DASH : String(Math.round(n));
  }
  function clamp(v, lo, hi) {
    return Math.min(hi, Math.max(lo, v));
  }
  function pct(v) {
    return (Math.round(v * 1000) / 1000) + '%';
  }
  /* Counts one to ten are spelt out in prose; anything else stays a numeral. */
  function words(n) {
    var small = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
    return Number.isInteger(n) && n >= 1 && n <= 10 ? small[n - 1] : String(n);
  }
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  /* "2026-09-25" -> "Sep 25, 2026", the same shape as build.py's display_date; withYear=false drops the year. */
  function fmtDate(iso, withYear) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    var month = m ? MONTHS[Number(m[2]) - 1] : null;
    if (!month) return null;
    return month + ' ' + Number(m[3]) + (withYear ? ', ' + m[1] : '');
  }
  /* "a", "a and b", "a, b and c"; items may be strings or nodes. */
  function joinList(items) {
    var out = [];
    items.forEach(function (it, i) {
      if (i > 0) out.push(i === items.length - 1 ? ' and ' : ', ');
      out.push(it);
    });
    return out;
  }

  /* ------------------------------------------------------------ DOM helpers */
  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }
  function fill(node, children) {
    clear(node);
    children.forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      node.appendChild(typeof c === 'string' ? doc.createTextNode(c) : c);
    });
  }
  function el(tag, attrs, children) {
    var node = doc.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      node.setAttribute(k, v === true ? '' : String(v));
    });
    if (children) fill(node, children);
    return node;
  }
  /* Monochrome vendor logo from the inline sprite (build.py injects <symbol id="logo-<slug>">). */
  var SVG_NS = 'http://www.w3.org/2000/svg';
  function logoUse(slug) {
    if (!slug || !doc.createElementNS) return null;
    var svg = doc.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'org-logo');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    var use = doc.createElementNS(SVG_NS, 'use');
    use.setAttribute('href', '#logo-' + slug);
    use.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', '#logo-' + slug);
    svg.appendChild(use);
    return svg;
  }
  function target(name) {
    return doc.querySelector('[data-fill="' + name + '"]');
  }

  /* ------------------------------------------------------------ data */
  function parse() {
    var node = doc.getElementById('leaderboard-data');
    var raw = null;
    if (node) {
      try { raw = JSON.parse(node.textContent); } catch (e) { raw = null; }
    }
    var data = obj(raw);
    return {
      entries: arr(data.entries).filter(function (e) {
        return e !== null && typeof e === 'object' && !Array.isArray(e);
      }),
      benchmark: obj(data.benchmark),
      sources: obj(data.sources)
    };
  }

  /* ------------------------------------------------------------ table rows */
  function rateTitle(e) {
    var f = obj(e.failures);
    var ci = obj(e.ci95);
    var low = num(ci.low);
    var high = num(ci.high);
    var ve = num(f.verifier_error);
    if (ve === null) ve = num(e.verifier_error);
    var parts = [
      fmtInt(e.passed) + '/' + fmtInt(e.n) + ' passed',
      '95% CI ' + (low !== null && high !== null ? low.toFixed(1) + '–' + high.toFixed(1) + '%' : DASH),
      'wrong connectivity ' + fmtInt(f.wrong_mol),
      'wrong stereochemistry ' + fmtInt(f.wrong_stereo),
      'wrong coordination geometry ' + fmtInt(f.wrong_geometry),
      'no answer ' + fmtInt(f.no_answer),
      'verifier error ' + (ve === null ? DASH : fmtInt(ve))
    ];
    var other = num(f.other);
    if (other !== null && other > 0) parts.push('other ' + other);
    arr(e.notes).forEach(function (n) { if (str(n)) parts.push(str(n)); });
    return parts.join(' · ');
  }

  /* RELEASE DATE: the vendor's release date when known; otherwise the evaluation date, muted. */
  function dateCell(e) {
    if (str(e.display_release_date)) {
      return el('td', { 'class': 'table-cell td-num td-date', title: 'Model release date' }, [str(e.display_release_date)]);
    }
    var d = str(e.display_date);
    return el('td', { 'class': 'table-cell td-num td-date', title: 'Evaluation date (model release date not recorded)' },
      [el('span', { 'class': 'effort' }, [d || DASH])]);
  }
  function costTitle(e) {
    var c = obj(e.cost_usd), parts = [];
    parts.push('mean cost per molecule at list prices (total run cost / all molecules attempted)');
    if (str(c.basis) && c.basis !== 'official list price') parts.push(str(c.basis));
    return parts.join(' · ');
  }
  function tokensTitle(e) {
    var k = obj(e.tokens), parts = [];
    if (num(k.input) !== null) parts.push('input ' + fmtTokTotal(num(k.input)) + ' (incl. cached reads)');
    if (num(k.output) !== null) parts.push('output ' + fmtTokTotal(num(k.output)));
    if (num(k.cache_hit_pct) !== null) parts.push('cache hit ' + num(k.cache_hit_pct).toFixed(0) + '%');
    if (num(e.sessions_without_usage) > 0) parts.push(num(e.sessions_without_usage) + ' sessions without a usage record');
    return parts.join(' · ');
  }

  /* The bar track only exists when there is a rate. No error bar: the user asked for the fill only. */
  function renderBar(e) {
    var rate = num(e.success_rate);
    if (rate === null) return null;
    var bar = el('div', { 'class': 'bar', 'aria-hidden': 'true' });
    var fillNode = el('div', { 'class': 'bar-fill' });
    fillNode.style.width = pct(clamp(rate, 0, 100));
    bar.appendChild(fillNode);
    return bar;
  }

  function renderRow(e) {
    var rank = num(e.rank);
    var rate = num(e.success_rate);
    var effort = str(e.effort);
    var url = str(e.org_url);
    var name = str(e.display_name) || str(e.model_id) || DASH;

    var model = [];
    var logo = logoUse(str(e.org_logo));
    if (logo) model.push(logo);
    model.push(url
      ? el('a', { href: url, target: '_blank', rel: 'noopener noreferrer', 'class': 'hover-underline', title: str(e.organization) }, [name])
      : el('span', null, [name]));
    /* leading space so copied text reads "GPT-6.1 Sol (high)"; the flex item swallows it visually */
    if (effort) model.push(el('span', { 'class': 'effort', title: 'Reasoning effort: ' + effort }, [' (' + effort + ')']));

    var number = [el('strong', null, [fmtPct(rate)])];

    return el('tr', { 'class': 'table-row', 'data-model': str(e.model_id) }, [
      el('td', { 'class': 'table-cell td-rank' }, [
        el('span', { 'class': 'rank' }, [rank === null ? DASH : String(rank)])
      ]),
      el('td', { 'class': 'table-cell td-model' }, [
        el('span', { 'class': 'model' }, model)
      ]),
      el('td', { 'class': 'table-cell td-rate', title: rateTitle(e) }, [
        el('div', { 'class': 'rate' }, [el('div', { 'class': 'rate-num' }, number), renderBar(e)])
      ]),
      dateCell(e),
      el('td', { 'class': 'table-cell td-num td-cost', title: costTitle(e) }, [fmtCostPerMolecule(num(obj(e.cost_usd).per_task_mean))]),
      el('td', { 'class': 'table-cell td-num td-tokens', title: tokensTitle(e) }, [fmtTokTotal(num(obj(e.tokens).total))])
    ]);
  }

  /* Missing ranks sort last; ties keep JSON order. */
  function byRankAsc(a, b) {
    var ra = num(a.entry.rank), rb = num(b.entry.rank);
    if (ra !== null && rb !== null && ra !== rb) return ra - rb;
    if (ra === null && rb !== null) return 1;
    if (rb === null && ra !== null) return -1;
    return a.index - b.index;
  }
  /* Missing rates sort last in both directions; ties fall back to rank order. */
  /* Sort by the displayed values: mean cost per molecule and total tokens. */
  var SORT_KEYS = {
    rate: function (e) { return num(e.success_rate); },
    date: function (e) { var v = str(e.release_date) || str(e.date); return v ? Date.parse(v) : null; },
    cost: function (e) { return num(obj(e.cost_usd).per_task_mean); },
    tokens: function (e) { return num(obj(e.tokens).total); }
  };
  function fmtCostPerMolecule(v) {
    if (v === null) return DASH;
    if (v >= 1000) return '$' + (v / 1000).toFixed(1) + 'k';
    return '$' + v.toFixed(v < 1 ? 4 : 2);
  }
  function fmtTokTotal(v) {
    if (v === null) return DASH;
    if (v >= 1e9) return (v / 1e9).toFixed(2) + 'B';
    if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (v >= 1e3) return (v / 1e3).toFixed(0) + 'k';
    return String(v);
  }
  function byKey(key, dir) {
    var get = SORT_KEYS[key] || SORT_KEYS.rate;
    return function (a, b) {
      var xa = get(a.entry), xb = get(b.entry);
      if (xa === null && xb === null) return byRankAsc(a, b);
      if (xa === null) return 1;
      if (xb === null) return -1;
      if (xa !== xb) return dir === 'asc' ? xa - xb : xb - xa;
      return byRankAsc(a, b);
    };
  }

  /* Rows are built once and re-appended on every sort, so a row's rank number never changes. */
  function renderTable(entries) {
    var body = doc.getElementById('leaderboard-body');
    var rows = entries.map(function (e, i) {
      return { entry: e, index: i, tr: renderRow(e) };
    });
    function paint(list) {
      if (!body) return;
      clear(body);
      if (!list.length) {
        body.appendChild(el('tr', { 'class': 'table-row' }, [
          el('td', { 'class': 'table-cell td-empty', colspan: '3' }, ['No leaderboard rows.'])
        ]));
        return;
      }
      list.forEach(function (r) { body.appendChild(r.tr); });
    }
    paint(rows.slice().sort(byRankAsc)); // initial: rank order, which is success rate descending
    return { rows: rows, paint: paint };
  }

  /* ------------------------------------------------------------ about section */
  function setText(name, text) {
    var node = target(name);
    if (node) node.textContent = str(text) || DASH;
  }
  function setList(name, items) {
    var node = target(name);
    if (!node) return;
    fill(node, (items.length ? items : [DASH]).map(function (it) { return el('li', null, [it]); }));
  }

  /* Builds the Setup paragraph from whatever fields exist; a missing field drops its clause. Shape:
     "The agent is <name>, built on <framework>, with <n> tools: <a>, <b> and <c>. Each molecule gets
     <k> attempt(s) of at most <m> LLM calls. <isolation sentence, verbatim> Reasoning effort is <x>
     for every model[ except <model> (<y>)]. Runs were made between <first> and <last>." */
  function setupSentences(agent, entries) {
    var name = str(agent.name);
    var framework = str(agent.framework);
    var github = obj(agent.github);
    var toolLinks = obj(github.tools);
    var isolation = str(agent.isolation);
    var tools = arr(agent.tools).filter(str);
    var maxCalls = num(agent.max_llm_calls);
    var attempts = num(agent.attempts_per_molecule);
    var sentences = [];

    function linkedLabel(href, label) {
      return str(href) ? el('a', { href: href }, [label]) : label;
    }

    var lead = [];
    if (name) lead.push('To run a new evaluation, use ', linkedLabel(github.agent, name));
    if (framework) lead.push(lead.length ? ', built on ' : 'The agent is built on ', linkedLabel(github.framework, framework));
    if (tools.length) {
      lead.push((lead.length ? ', with ' : 'The agent has ') + words(tools.length) + (tools.length === 1 ? ' tool: ' : ' tools: '));
      lead = lead.concat(joinList(tools.map(function (tool) {
        return linkedLabel(toolLinks[tool], el('code', null, [tool]));
      })));
    }
    if (lead.length) sentences.push(lead.concat(['.']));

    if (attempts !== null || maxCalls !== null) {
      var budget = 'Each molecule gets ';
      if (attempts !== null) budget += words(attempts) + (attempts === 1 ? ' attempt' : ' attempts');
      if (maxCalls !== null) {
        budget += (attempts !== null ? ' of ' : '') + 'at most ' + words(maxCalls) + ' LLM calls';
        if (attempts !== null && attempts !== 1) budget += ' each';
      }
      sentences.push([budget + '.']);
    }

    if (isolation) sentences.push([isolation]); // already a full sentence in the JSON

    /* the most common effort is the rule, every other model is named as an exception */
    var counts = {};
    entries.forEach(function (e) {
      var x = str(e.effort);
      if (x) counts[x] = (counts[x] || 0) + 1;
    });
    var efforts = Object.keys(counts);
    if (efforts.length) {
      var common = efforts.reduce(function (a, b) { return counts[b] > counts[a] ? b : a; });
      var exceptions = entries.filter(function (e) { return str(e.effort) && e.effort !== common; }).map(function (e) {
        return (str(e.display_name) || str(e.model_id) || DASH) + ' (' + e.effort + ')';
      });
      sentences.push(['Reasoning effort is ' + common + ' for every model' +
        (exceptions.length ? ' except ' + joinList(exceptions).join('') : '') + '.']);
    }

    var dates = entries.map(function (e) { return str(e.date); }).filter(function (d) { return fmtDate(d, true); }).sort();
    if (dates.length) {
      var first = dates[0];
      var last = dates[dates.length - 1];
      sentences.push([first === last
        ? 'Runs were made on ' + fmtDate(first, true) + '.'
        : 'Runs were made between ' + fmtDate(first, first.slice(0, 4) !== last.slice(0, 4)) + ' and ' + fmtDate(last, true) + '.']);
    }

    var out = [];
    sentences.forEach(function (parts, i) {
      if (i) out.push(' ');
      out = out.concat(parts);
    });
    return out;
  }

  function renderAbout(data) {
    var bench = data.benchmark;
    var agent = obj(bench.agent);
    var verifier = obj(bench.verifier);

    setText('task', bench.task);
    setText('prompt', bench.prompt);

    setList('sources', Object.keys(data.sources).map(function (k) {
      var s = obj(data.sources[k]);
      var n = num(s.n);
      return (str(s.label) || k) + ' · ' + (n === null ? DASH : String(n));
    }));

    setList('gates', arr(verifier.gates).filter(str));

    var setup = target('setup');
    if (setup) {
      var parts = setupSentences(agent, data.entries);
      fill(setup, parts.length ? parts : [DASH]);
    }
  }

  /* ------------------------------------------------------------ sorting (desc -> asc -> desc) */
  function wireSort(table) {
    var buttons = Array.prototype.slice.call(doc.querySelectorAll('.sort-btn[data-sort-key]'));
    if (!buttons.length) return;
    var active = 'rate', dir = 'desc';

    function show() {
      buttons.forEach(function (btn) {
        var key = btn.getAttribute('data-sort-key');
        var th = btn.parentNode;
        var state = key === active ? dir : 'none';
        if (th && th.setAttribute) th.setAttribute('aria-sort', state === 'none' ? 'none' : (state === 'asc' ? 'ascending' : 'descending'));
        Array.prototype.forEach.call(btn.querySelectorAll('.sort-icon'), function (svg) {
          if (svg.getAttribute('data-sort') === state) svg.removeAttribute('hidden');
          else svg.setAttribute('hidden', '');
        });
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-sort-key');
        if (key === active) dir = dir === 'desc' ? 'asc' : 'desc';
        else { active = key; dir = key === 'rate' ? 'desc' : 'asc'; }
        table.paint(table.rows.slice().sort(byKey(active, dir)));
        show();
      });
    });
    show();
  }

  /* ------------------------------------------------------------ theme toggle */
  function wireTheme() {
    var root = doc.documentElement;
    var mq = typeof window.matchMedia === 'function' ? window.matchMedia('(prefers-color-scheme: dark)') : null;
    var buttons = Array.prototype.slice.call(doc.querySelectorAll('.theme-btn[data-theme]'));

    function stored() {
      try {
        var v = localStorage.getItem(THEME_KEY);
        return v === 'light' || v === 'dark' ? v : 'system';
      } catch (e) {
        return 'system';
      }
    }
    function apply(choice) {
      root.classList.toggle('dark', choice === 'dark' || (choice === 'system' && !!(mq && mq.matches)));
      buttons.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-theme') === choice ? 'true' : 'false');
      });
    }

    var choice = stored(); // the live choice; storage is only a best-effort copy of it

    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        var next = b.getAttribute('data-theme');
        choice = next === 'light' || next === 'dark' ? next : 'system';
        try { localStorage.setItem(THEME_KEY, choice); } catch (e) { /* storage blocked: the choice still holds for this view */ }
        apply(choice);
      });
    });
    if (mq) {
      var onChange = function () { if (choice === 'system') apply('system'); };
      if (typeof mq.addEventListener === 'function') mq.addEventListener('change', onChange);
      else if (typeof mq.addListener === 'function') mq.addListener(onChange);
    }
    apply(choice);
  }

  /* ------------------------------------------------------------ boot */
  function init() {
    var data = parse();
    var table = renderTable(data.entries);
    renderAbout(data);
    wireSort(table);
    wireTheme();
  }

  init();
})();
