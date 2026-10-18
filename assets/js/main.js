/* Ahmed Iqbal — portfolio interactions.
   Plain JavaScript, no dependencies. Every effect is an enhancement:
   if anything here fails, the page content is already complete in HTML. */
(function () {
  'use strict';

  var doc = document.documentElement;
  var reduced = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)').matches : false;
  var finePointer = window.matchMedia ? matchMedia('(hover: hover) and (pointer: fine)').matches : false;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  function safe(name, fn) {
    try { fn(); } catch (err) { if (window.console) console.warn('[portfolio] ' + name + ' disabled:', err); }
  }

  doc.classList.add('app-ready');

  /* ---------------- toast ---------------- */
  var toastEl = $('#toast'), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2600);
  }

  /* ---------------- theme ---------------- */
  safe('theme', function () {
    var btn = $('#theme-btn');
    var mq = matchMedia('(prefers-color-scheme: dark)');
    function current() {
      var t = doc.getAttribute('data-theme');
      return t || (mq.matches ? 'dark' : 'light');
    }
    function label() { btn.setAttribute('aria-label', current() === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'); }
    label();
    btn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      doc.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      label();
      document.dispatchEvent(new CustomEvent('themechange'));
    });
    if (mq.addEventListener) mq.addEventListener('change', function () { label(); document.dispatchEvent(new CustomEvent('themechange')); });
  });

  /* ---------------- header, nav, mobile menu ---------------- */
  safe('nav', function () {
    var header = $('#site-header');
    var nav = $('#nav');
    var menuBtn = $('#menu-btn');
    var links = $$('.nav-list a');
    var pill = $('.nav-pill');

    function onScroll() { header.classList.toggle('is-scrolled', window.scrollY > 8); }
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    function movePill(a) {
      if (!pill) return;
      if (!a || getComputedStyle(pill).display === 'none') { pill.style.opacity = '0'; return; }
      var listBox = a.parentElement.parentElement.getBoundingClientRect();
      var box = a.getBoundingClientRect();
      pill.style.width = box.width + 'px';
      pill.style.transform = 'translateX(' + (box.left - listBox.left) + 'px)';
      pill.style.opacity = '1';
    }

    var sections = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    var active = null;
    function setActive(id) {
      if (active === id) return;
      active = id;
      var cur = null;
      links.forEach(function (a) {
        var on = a.getAttribute('href') === '#' + id;
        if (on) { a.setAttribute('aria-current', 'true'); cur = a; } else a.removeAttribute('aria-current');
      });
      movePill(cur);
    }
    function pickActive() {
      var line = window.innerHeight * 0.35;
      var found = null;
      sections.forEach(function (s) { var r = s.getBoundingClientRect(); if (r.top <= line && r.bottom > line) found = s.id; });
      if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 4) found = 'contact';
      setActive(found);
    }
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () { ticking = false; pickActive(); });
    }, { passive: true });
    window.addEventListener('resize', function () { active = null; pickActive(); });
    pickActive();

    function openMenu(open) {
      nav.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      menuBtn.querySelector('use').setAttribute('href', open ? '#i-close' : '#i-menu');
      if (open) { var first = nav.querySelector('a'); if (first) first.focus(); }
    }
    menuBtn.addEventListener('click', function () { openMenu(!nav.classList.contains('is-open')); });
    links.forEach(function (a) { a.addEventListener('click', function () { if (nav.classList.contains('is-open')) openMenu(false); }); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { openMenu(false); menuBtn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('is-open') && !nav.contains(e.target) && !menuBtn.contains(e.target)) openMenu(false);
    });
  });

  /* ---------------- hero: streamed headline ---------------- */
  safe('stream', function () {
    var thesis = $('#thesis');
    if (!thesis || reduced || !thesis.animate) return;
    var tokens = [];
    function split(node, into) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var span = document.createElement('span');
            span.className = 'tok'; span.textContent = part;
            frag.appendChild(span); into.push(span);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          split(child, into);
        }
      });
    }
    split(thesis, tokens);
    var marks = $$('mark', thesis);
    marks.forEach(function (m) { m.style.backgroundSize = '0% 100%'; });
    var step = 42, start = 320;
    tokens.forEach(function (t, i) {
      t.animate([{ opacity: .01, transform: 'translateY(.35em)', filter: 'blur(4px)' }, { opacity: 1, transform: 'none', filter: 'blur(0)' }],
        { duration: 520, delay: start + i * step, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
    });
    var caret = document.createElement('span');
    caret.className = 'caret'; caret.setAttribute('aria-hidden', 'true');
    thesis.appendChild(caret);
    var end = start + tokens.length * step + 300;
    marks.forEach(function (m, i) {
      m.animate([{ backgroundSize: '0% 100%' }, { backgroundSize: '100% 100%' }],
        { duration: 650, delay: end + i * 180, easing: 'cubic-bezier(.65,0,.35,1)', fill: 'forwards' })
        .finished.then(function () { m.style.backgroundSize = '100% 100%'; }).catch(function () {});
    });
    setTimeout(function () {
      caret.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 400, fill: 'forwards' });
      setTimeout(function () { caret.remove(); }, 450);
    }, end + marks.length * 180 + 900);

    var name = $('.hero h1 .name');
    if (name) name.animate([{ opacity: .01, transform: 'translateY(18px)' }, { opacity: 1, transform: 'none' }], { duration: 900, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
    $$('.hero-meta, .hero h1 .role, .proofs, .hero-ctas').forEach(function (el, i) {
      el.animate([{ opacity: .01, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }],
        { duration: 800, delay: 120 + i * 120, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
    });
    var frame = $('.portrait-frame');
    if (frame) frame.animate([{ clipPath: 'inset(100% 0 0 0 round 14px)' }, { clipPath: 'inset(0 0 0 0 round 14px)' }],
      { duration: 1100, delay: 150, easing: 'cubic-bezier(.65,0,.35,1)', fill: 'backwards' });
    var plaque = $('.plaque');
    if (plaque) {
      plaque.animate([{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }],
        { duration: 700, delay: 900, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
      setTimeout(function () { plaque.classList.add('is-shining'); }, 1500); // a single sheen, never repeats
    }
  });

  /* ---------------- hero: attention field ----------------
     A grid of points. The pointer acts as a query; the nearest points get
     softmax-weighted "attention" lines. Drawn only while the hero is visible. */
  safe('field', function () {
    var canvas = $('#hero-field');
    if (!canvas || !canvas.getContext) return;
    var hero = canvas.parentElement;
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var pts = [], W = 0, H = 0, gap = 34;
    var colors = {};
    var q = { x: -9999, y: -9999, tx: -9999, ty: -9999, active: false };
    var visible = true, raf = 0, fade = 0;

    function readColors() {
      var cs = getComputedStyle(doc);
      colors.dot = cs.getPropertyValue('--line').trim() || '#ccc';
      colors.ink = cs.getPropertyValue('--ink').trim() || '#000';
      colors.mark = cs.getPropertyValue('--mark').trim() || '#fc0';
    }
    function resize() {
      var r = hero.getBoundingClientRect();
      W = r.width; H = r.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      pts = [];
      gap = W < 640 ? 28 : 34;
      for (var y = gap / 2; y < H; y += gap) for (var x = gap / 2; x < W; x += gap) pts.push({ x: x, y: y });
      draw(performance.now());
    }
    function hexA(hex, a) {
      if (hex.charAt(0) !== '#') return hex;
      var h = hex.slice(1); if (h.length === 3) h = h.replace(/./g, '$&$&');
      var n = parseInt(h, 16);
      return 'rgba(' + (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')';
    }
    function draw(now) {
      ctx.clearRect(0, 0, W, H);
      // fade the field out on the left where the text sits
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        ctx.fillStyle = colors.dot;
        ctx.globalAlpha = clamp(.25 + (p.x / W) * .9, 0, 1);
        ctx.fillRect(p.x - 1, p.y - 1, 2, 2);
      }
      ctx.globalAlpha = 1;
      if (reduced || W < 900) return; // query lines only on wide screens with a pointer
      fade += ((q.active ? 1 : 0) - fade) * .12;
      if (fade < .01) return;
      ctx.globalAlpha = fade;
      q.x += (q.tx - q.x) * .14; q.y += (q.ty - q.y) * .14;
      if (q.x < -1000) { q.x = q.tx; q.y = q.ty; }
      // top-k by score, softmax over -distance
      var k = 8, best = [];
      for (var j = 0; j < pts.length; j++) {
        var dx = pts[j].x - q.x, dy = pts[j].y - q.y, d = Math.sqrt(dx * dx + dy * dy);
        if (d > 220) continue;
        best.push({ p: pts[j], s: -d / 26 });
      }
      best.sort(function (a, b) { return b.s - a.s; });
      best = best.slice(0, k);
      var max = best.length ? best[0].s : 0, sum = 0;
      best.forEach(function (b) { b.w = Math.exp(b.s - max); sum += b.w; });
      best.forEach(function (b) {
        var w = b.w / sum;
        ctx.strokeStyle = hexA(colors.ink, clamp(w * 2.6, .14, .7));
        ctx.lineWidth = .6 + w * 2.2;
        ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(b.p.x, b.p.y); ctx.stroke();
        ctx.fillStyle = hexA(colors.ink, clamp(w * 2, .2, .9));
        ctx.beginPath(); ctx.arc(b.p.x, b.p.y, 1.6 + w * 3, 0, Math.PI * 2); ctx.fill();
      });
      ctx.fillStyle = colors.mark;
      ctx.beginPath(); ctx.arc(q.x, q.y, 5, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = colors.ink; ctx.lineWidth = 1.2; ctx.stroke();
      ctx.globalAlpha = 1;
    }
    // The loop only runs while the pointer is over the hero (plus a short fade-out).
    function loop(now) {
      raf = 0;
      if (!visible || document.hidden) return;
      draw(now);
      if (q.active || fade > .01) raf = requestAnimationFrame(loop);
    }
    function kick() { if (!raf && !reduced && W >= 900 && finePointer) raf = requestAnimationFrame(loop); }

    readColors(); resize();
    window.addEventListener('resize', function () { clearTimeout(resize.t); resize.t = setTimeout(function () { resize(); kick(); }, 150); });
    document.addEventListener('themechange', function () { readColors(); draw(performance.now()); });
    document.addEventListener('visibilitychange', kick);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; kick(); }).observe(hero);
    }
    if (finePointer) {
      hero.addEventListener('pointermove', function (e) {
        var r = hero.getBoundingClientRect();
        q.tx = e.clientX - r.left; q.ty = e.clientY - r.top;
        if (!q.active) { q.x = q.tx; q.y = q.ty; }
        q.active = true; kick();
      });
      hero.addEventListener('pointerleave', function () { q.active = false; kick(); });
    }
  });

  /* ---------------- reveal on scroll ---------------- */
  safe('reveal', function () {
    if (reduced || !('IntersectionObserver' in window)) return;
    var els = $$('[data-reveal]').filter(function (el) { return !el.closest('.hero'); });
    var vh = window.innerHeight;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.remove('pre');
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    els.forEach(function (el) {
      // only hide what starts below the first screen, so the first frame is complete
      if (el.getBoundingClientRect().top < vh * 0.92) return;
      var sib = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      el.style.setProperty('--d', Math.min(sib % 4, 3) * 0.08 + 's');
      el.classList.add('pre');
      io.observe(el);
    });
  });

  /* ---------------- method loop ----------------
     Static and complete in HTML. With motion allowed, it fills once, step by
     step, the first time it scrolls into view. */
  safe('loop', function () {
    var loopEl = $('#loop');
    var nodes = $$('#loop .node');
    var ring = $('#ring-progress');
    if (!loopEl || reduced || !('IntersectionObserver' in window)) return;
    var C = 2 * Math.PI * 160;
    if (loopEl.getBoundingClientRect().top < window.innerHeight) return; // already on screen: leave complete
    nodes.forEach(function (n) { n.classList.remove('is-done'); });
    ring.style.transition = 'none'; ring.style.strokeDashoffset = String(C);
    var io = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      ring.style.transition = 'stroke-dashoffset 2.4s cubic-bezier(.65,0,.35,1)';
      requestAnimationFrame(function () { ring.style.strokeDashoffset = '0'; });
      nodes.forEach(function (n, i) {
        setTimeout(function () {
          nodes.forEach(function (m) { m.classList.remove('is-active'); });
          n.classList.add('is-done', 'is-active');
          if (i === nodes.length - 1) setTimeout(function () { n.classList.remove('is-active'); }, 600);
        }, 200 + i * 380);
      });
    }, { threshold: .45 });
    io.observe(loopEl);
  });

  /* ---------------- scroll-linked: work band, timeline ---------------- */
  safe('scrolllinked', function () {
    if (reduced) return;
    var band = $('#work');
    var tl = $('#timeline');
    var ticking = false;
    function update() {
      ticking = false;
      var vh = window.innerHeight;
      if (band) {
        if (window.innerWidth > 760) {
          var r = band.getBoundingClientRect();
          var p = clamp((vh - r.top) / (vh * 0.75), 0, 1);
          var e = 1 - Math.pow(1 - p, 3);
          band.style.setProperty('--band-inset', ((1 - e) * Math.min(window.innerWidth * 0.04, 48)).toFixed(2) + 'px');
          band.style.setProperty('--band-r', ((1 - e) * 36).toFixed(2) + 'px');
        } else {
          band.style.removeProperty('--band-inset'); band.style.removeProperty('--band-r');
        }
      }
      if (tl) {
        var t = tl.getBoundingClientRect();
        tl.style.setProperty('--tl', clamp((vh * 0.6 - t.top) / t.height, 0, 1).toFixed(4));
      }
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---------------- pointer niceties (desktop only) ---------------- */
  safe('pointer', function () {
    if (!finePointer || reduced) return;
    $$('[data-glow]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });
    $$('[data-magnetic]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - (r.left + r.width / 2)) / r.width;
        var y = (e.clientY - (r.top + r.height / 2)) / r.height;
        el.style.transform = 'translate(' + (x * 8).toFixed(1) + 'px,' + (y * 6).toFixed(1) + 'px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  });

  /* ---------------- project filters ---------------- */
  safe('filters', function () {
    var buttons = $$('.filter');
    var items = $$('#work .card, #work .archive-item');
    var status = $('#filter-status');
    var groups = [$('#sites'), $('#archive')];

    buttons.forEach(function (b) {
      var f = b.getAttribute('data-filter');
      var n = f === 'all' ? items.length : items.filter(function (it) { return it.getAttribute('data-tags').split(' ').indexOf(f) > -1; }).length;
      var span = b.querySelector('.n'); if (span) span.textContent = n;
    });

    function apply(f, animate) {
      var before = new Map();
      if (animate) items.forEach(function (it) { if (!it.classList.contains('is-filtered-out')) before.set(it, it.getBoundingClientRect()); });
      var shown = 0;
      items.forEach(function (it) {
        var on = f === 'all' || it.getAttribute('data-tags').split(' ').indexOf(f) > -1;
        it.classList.toggle('is-filtered-out', !on);
        if (on) { shown++; it.classList.remove('pre'); }
      });
      groups.forEach(function (g) {
        if (!g) return;
        var any = $$('.card, .archive-item', g).some(function (it) { return !it.classList.contains('is-filtered-out'); });
        g.hidden = !any;
      });
      status.textContent = 'Showing ' + shown + ' of ' + items.length + ' projects';
      if (!animate || reduced) return;
      items.forEach(function (it) {
        if (it.classList.contains('is-filtered-out')) return;
        var a = before.get(it), b = it.getBoundingClientRect();
        if (a) {
          var dx = a.left - b.left, dy = a.top - b.top;
          if (Math.abs(dx) > 1 || Math.abs(dy) > 1) it.animate([{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }], { duration: 550, easing: 'cubic-bezier(.16,1,.3,1)' });
        } else {
          it.animate([{ opacity: 0, transform: 'translateY(16px) scale(.98)' }, { opacity: 1, transform: 'none' }], { duration: 500, easing: 'cubic-bezier(.16,1,.3,1)' });
        }
      });
    }
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        buttons.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        apply(b.getAttribute('data-filter'), true);
      });
    });
    apply('all', false);
  });

  /* ---------------- case-study panel ---------------- */
  safe('cases', function () {
    var dialog = $('#case-dialog');
    if (!dialog || typeof dialog.showModal !== 'function') return; // fallback: in-page articles via anchors
    var body = $('#dialog-body');
    var titleEl = $('#dialog-title');
    var progress = $('#dialog-progress');
    var order = $$('.cases-fallback .case').map(function (a) { return a.id.replace('case-', ''); });
    var current = null, opener = null, pushed = false;

    function render(slug) {
      var src = document.getElementById('case-' + slug);
      if (!src) return false;
      var clone = src.cloneNode(true);
      clone.removeAttribute('id');
      body.innerHTML = '';
      body.appendChild(clone);
      var h = clone.querySelector('h2'); if (h) { h.id = 'dialog-h'; h.setAttribute('tabindex', '-1'); }
      var idx = order.indexOf(slug);
      titleEl.textContent = 'Case study ' + (idx + 1) + ' of ' + order.length;
      dialog.setAttribute('aria-labelledby', 'dialog-h');
      dialog.scrollTop = 0;
      current = slug;
      return true;
    }
    function open(slug, push) {
      if (!render(slug)) return;
      if (!dialog.open) {
        opener = document.activeElement;
        dialog.showModal();
        doc.style.overflow = 'hidden';
        if (!reduced && dialog.animate) dialog.animate([{ transform: 'translateX(48px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 480, easing: 'cubic-bezier(.16,1,.3,1)' });
      }
      var h = $('#dialog-h'); if (h) h.focus({ preventScroll: true });
      if (push) {
        if (pushed) history.replaceState({ case: slug }, '', '#case-' + slug);
        else { history.pushState({ case: slug }, '', '#case-' + slug); pushed = true; }
      }
      updateProgress();
    }
    function finishClose() {
      if (!dialog.open) return;
      dialog.close();
      doc.style.overflow = '';
      current = null;
      if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
    }
    function requestClose() {
      if (pushed) { pushed = false; history.back(); return; } // popstate finishes the close
      if (/^#case-/.test(location.hash)) history.replaceState(null, '', location.pathname + location.search);
      finishClose();
    }
    function updateProgress() {
      var max = dialog.scrollHeight - dialog.clientHeight;
      progress.style.transform = 'scaleX(' + (max > 0 ? dialog.scrollTop / max : 1) + ')';
    }

    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#case-"]');
      if (!a) return;
      var slug = a.getAttribute('href').slice(6);
      if (order.indexOf(slug) === -1) return;
      e.preventDefault();
      open(slug, true);
    });
    $('#case-close').addEventListener('click', requestClose);
    $('#case-prev').addEventListener('click', function () { var i = order.indexOf(current); open(order[(i - 1 + order.length) % order.length], true); });
    $('#case-next').addEventListener('click', function () { var i = order.indexOf(current); open(order[(i + 1) % order.length], true); });
    dialog.addEventListener('cancel', function (e) { e.preventDefault(); requestClose(); });
    dialog.addEventListener('click', function (e) { if (e.target === dialog) requestClose(); });
    dialog.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('popstate', function () {
      var m = location.hash.match(/^#case-(.+)$/);
      if (m && order.indexOf(m[1]) > -1) { pushed = false; open(m[1], false); }
      else { pushed = false; finishClose(); }
    });
    var m = location.hash.match(/^#case-(.+)$/);
    if (m && order.indexOf(m[1]) > -1) open(m[1], false);
  });

  /* ---------------- skills evidence (data: assets/js/skills-data.js) ---------------- */
  var SK = window.SKILLS || { skills: {}, projects: {}, levels: {} };
  function evidenceFor(id) {
    var s = SK.skills[id]; if (!s) return null;
    return { skill: s, items: (s.used || []).map(function (k) { return SK.projects[k]; }).filter(Boolean) };
  }
  safe('skills', function () {
    var chips = $$('.chip');
    var title = $('#ev-title'), text = $('#ev-text'), list = $('#ev-list');
    function show(chip) {
      chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
      var ev = evidenceFor(chip.getAttribute('data-skill')); if (!ev) return;
      title.textContent = ev.skill.name;
      text.textContent = (SK.levels[ev.skill.level] || '') + (ev.items.length ? '. Where it shows up:' : '.');
      list.innerHTML = '';
      var items = ev.items.length ? ev.items : (ev.skill.docs ? [{ title: 'Official documentation', href: ev.skill.docs, note: 'external' }] : []);
      items.forEach(function (it) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = it.href;
        if (/^https?:/.test(it.href)) { a.target = '_blank'; a.rel = 'noopener'; }
        var s1 = document.createElement('span'); s1.textContent = it.title + (/^https?:/.test(it.href) ? ' ↗' : ''); s1.style.cssText = 'padding:0;background:none';
        var s2 = document.createElement('small'); s2.textContent = it.note;
        a.appendChild(s1); a.appendChild(s2); li.appendChild(a); list.appendChild(li);
      });
    }
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); c.addEventListener('click', function () { show(c); }); });
    if (chips[0]) show(chips[0]);
  });

  /* ---------------- skills slider ----------------
     Each row is a native horizontal scroller, so touch, trackpad, keyboard
     focus and the arrow buttons all work. Auto-drift moves scrollLeft and
     stops on hover, focus, touch, the Pause button, off-screen, and always
     under reduced motion. Clones exist only to make the loop seamless and
     are hidden from assistive tech and the tab order. */
  safe('slider', function () {
    var root = $('#stack-slider'); if (!root) return;
    var rows = $$('.srow', root);
    var tip = $('#stip');
    var visible = true, last = 0, raf = 0;
    var SPEED = 30; // px per second

    var state = rows.map(function (row) {
      var vp = row.querySelector('.srow-viewport');
      var track = row.querySelector('.srow-track');
      var originals = Array.prototype.slice.call(track.children);
      // two extra copies so the row never runs out at any screen width.
      // Copies stay clickable (inert would swallow clicks) but are hidden from AT and the tab order.
      [0, 1].forEach(function () {
        originals.forEach(function (li) {
          var c = li.cloneNode(true);
          c.setAttribute('aria-hidden', 'true'); c.setAttribute('data-clone', '');
          $$('a', c).forEach(function (a) { a.setAttribute('tabindex', '-1'); });
          track.appendChild(c);
        });
      });
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('class', 'srow-line'); svg.setAttribute('aria-hidden', 'true');
      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      svg.appendChild(path); track.insertBefore(svg, track.firstChild);
      var st = { row: row, vp: vp, track: track, svg: svg, path: path, first: originals[0], dir: Number(row.getAttribute('data-dir')) || 1, pos: 0, period: 0, hold: 0, hover: false };
      return st;
    });

    function layout() {
      state.forEach(function (st) {
        var lis = $$('.snode', st.track);
        var n = lis.length / 3;
        st.period = lis[n].offsetLeft - lis[0].offsetLeft;
        // pipeline line through every dot centre (originals + clones)
        var tr = st.track.getBoundingClientRect();
        var pts = lis.map(function (li) { var d = li.querySelector('.snode-dot').getBoundingClientRect(); return [d.left - tr.left + d.width / 2, d.top - tr.top + d.height / 2]; });
        var dStr = 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1);
        for (var i = 1; i < pts.length; i++) {
          var p0 = pts[i - 1], p1 = pts[i], mx = (p0[0] + p1[0]) / 2;
          dStr += ' C' + mx.toFixed(1) + ' ' + p0[1].toFixed(1) + ' ' + mx.toFixed(1) + ' ' + p1[1].toFixed(1) + ' ' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1);
        }
        st.svg.setAttribute('width', st.track.scrollWidth); st.svg.setAttribute('height', st.track.offsetHeight);
        st.path.setAttribute('d', dStr);
        if (!st.pos) st.pos = st.period;
        st.vp.scrollLeft = st.pos;
      });
    }
    function wrap(st) {
      if (st.period <= 0) return;
      if (st.pos >= st.period * 1.5) st.pos -= st.period;
      if (st.pos < st.period * .5) st.pos += st.period;
    }
    function frame(t) {
      raf = 0;
      var dt = last ? Math.min((t - last) / 1000, .05) : 0; last = t;
      var moving = false;
      state.forEach(function (st) {
        if (reduced || !visible || document.hidden || st.hover || st.row.contains(document.activeElement) || t < st.hold) { st.pos = st.vp.scrollLeft; return; }
        moving = true;
        st.pos += st.dir * SPEED * dt; wrap(st);
        st.vp.scrollLeft = st.pos;
      });
      if (!reduced && visible) raf = requestAnimationFrame(frame); else last = 0;
    }
    function run() { if (!raf && !reduced && visible) { last = 0; raf = requestAnimationFrame(frame); } }

    state.forEach(function (st) {
      st.row.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') st.hover = true; });
      st.row.addEventListener('pointerleave', function () { st.hover = false; });
      ['pointerdown', 'wheel', 'touchstart'].forEach(function (ev) {
        st.vp.addEventListener(ev, function () { st.hold = performance.now() + 3000; }, { passive: true });
      });
      st.vp.addEventListener('scroll', function () {
        // keep the loop seamless when the user scrolls by hand
        if (st.period > 0 && (st.vp.scrollLeft < st.period * .25 || st.vp.scrollLeft > st.period * 1.75)) {
          st.vp.scrollLeft += st.vp.scrollLeft < st.period * .25 ? st.period : -st.period;
        }
      }, { passive: true });
    });

    // tooltip: shared element, positioned above the active node
    var tipFor = null;
    function showTip(a) {
      var ev = evidenceFor(a.getAttribute('data-skill')); if (!ev || !tip) return;
      var ext = /^https?:/.test(a.getAttribute('href'));
      var target = ev.items.length ? ev.items[0].title : 'official documentation';
      tip.innerHTML = '';
      var h = document.createElement('strong'); h.textContent = ev.skill.name; tip.appendChild(h);
      var l = document.createElement('span'); l.className = 'lvl'; l.textContent = (SK.levels[ev.skill.level] || '') + ' · ' + (SK.categories[ev.skill.cat] || ''); tip.appendChild(l);
      if (ev.items.length) {
        var ul = document.createElement('ul');
        ev.items.slice(0, 4).forEach(function (it) { var li = document.createElement('li'); li.textContent = it.title; ul.appendChild(li); });
        tip.appendChild(ul);
      } else { var sp = document.createElement('p'); sp.style.margin = '.5rem 0'; sp.textContent = 'No public project on this site yet.'; tip.appendChild(sp); }
      var hint = document.createElement('p'); hint.className = 'hint'; hint.textContent = 'Click: open ' + target + (ext ? ' ↗' : ''); tip.appendChild(hint);
      tip.hidden = false;
      var rr = root.getBoundingClientRect(), dr = a.querySelector('.snode-dot').getBoundingClientRect();
      var w = tip.offsetWidth, h2 = tip.offsetHeight;
      var x = clamp(dr.left - rr.left + dr.width / 2 - w / 2, 8, rr.width - w - 8);
      var y = dr.top - rr.top - h2 - 14;
      if (y < -40) y = dr.bottom - rr.top + 12;
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
      requestAnimationFrame(function () { tip.classList.add('is-on'); });
      if (tipFor && tipFor !== a) tipFor.classList.remove('is-tip');
      tipFor = a; a.classList.add('is-tip');
    }
    function hideTip(a) {
      if (a && a !== tipFor) return;
      if (tip) { tip.classList.remove('is-on'); tip.hidden = true; }
      if (tipFor) tipFor.classList.remove('is-tip');
      tipFor = null;
    }
    $$('.snode a', root).forEach(function (a) {
      if (a.closest('[data-clone]')) {
        a.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') showTip(a); });
        a.addEventListener('pointerleave', function () { hideTip(a); });
        return;
      }
      a.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') showTip(a); });
      a.addEventListener('pointerleave', function () { hideTip(a); });
      a.addEventListener('focus', function () { showTip(a); });
      a.addEventListener('blur', function () { hideTip(a); });
    });
    window.addEventListener('scroll', function () { if (tipFor && !tipFor.matches(':focus')) hideTip(); }, { passive: true });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) run(); }).observe(root);
    }
    document.addEventListener('visibilitychange', run);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { state.forEach(function (st) { st.pos = 0; }); layout(); }, 150); });
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () { layout(); run(); });
    layout(); run();
  });

  /* ---------------- copy email ---------------- */
  safe('copy', function () {
    var btn = $('#copy-email');
    var addr = $('#email-addr');
    if (!btn) return;
    function selectText() {
      var range = document.createRange(); range.selectNodeContents(addr);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
    }
    btn.addEventListener('click', function () {
      var value = btn.getAttribute('data-copy');
      var done = function () { toast('Email address copied'); };
      var fail = function () { selectText(); toast('Selected. Press Ctrl+C (or ⌘C) to copy'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(value).then(done, fail);
      else fail();
    });
  });

  /* ---------------- contact form ---------------- */
  safe('form', function () {
    var form = $('#contact-form');
    if (!form) return;
    var statusEl = $('#form-status');
    var submit = $('#f-submit');
    var fields = {
      name: { el: $('#f-name'), err: $('#f-name-err'), check: function (v) { return v.trim().length >= 2 ? '' : 'Please enter your name.'; } },
      email: { el: $('#f-email'), err: $('#f-email-err'), check: function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? '' : 'Please enter a valid email address, like name@company.com.'; } },
      message: { el: $('#f-msg'), err: $('#f-msg-err'), check: function (v) { return v.trim().length >= 20 ? '' : 'Please write at least 20 characters so I know what it is about.'; } }
    };
    var tried = false;
    function validate(key) {
      var f = fields[key], msg = f.check(f.el.value);
      f.err.textContent = msg;
      if (msg) f.el.setAttribute('aria-invalid', 'true'); else f.el.removeAttribute('aria-invalid');
      return !msg;
    }
    Object.keys(fields).forEach(function (k) {
      fields[k].el.addEventListener('blur', function () { if (tried) validate(k); });
      fields[k].el.addEventListener('input', function () { if (tried) validate(k); });
    });
    function setStatus(state, html) {
      statusEl.hidden = false; statusEl.setAttribute('data-state', state); statusEl.innerHTML = html;
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      tried = true;
      var ok = true, firstBad = null;
      Object.keys(fields).forEach(function (k) { if (!validate(k)) { ok = false; if (!firstBad) firstBad = fields[k].el; } });
      if (!ok) { firstBad.focus(); return; }
      if ($('#f-gotcha').value) { setStatus('ok', 'Thanks, your message was received.'); form.reset(); return; } // bot trap

      submit.disabled = true; submit.setAttribute('aria-busy', 'true');
      var label = submit.firstChild.nodeValue; submit.firstChild.nodeValue = 'Sending… ';
      setStatus('pending', 'Sending your message…');
      var ctrl = 'AbortController' in window ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, signal: ctrl ? ctrl.signal : undefined })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (data) {
            if (!r.ok) {
              var msg = data && data.errors && data.errors.length ? data.errors.map(function (x) { return x.message; }).join(' ') : 'The form service returned an error (' + r.status + ').';
              throw new Error(msg);
            }
          });
        })
        .then(function () {
          setStatus('ok', '<strong>Message sent.</strong> Thanks — I’ll reply to the email address you gave.');
          form.reset(); tried = false;
        })
        .catch(function (err) {
          var reason = err && err.name === 'AbortError' ? 'The request timed out.' : (err && err.message && err.message !== 'Failed to fetch' ? err.message : 'The form service could not be reached.');
          setStatus('error', '<strong>Your message wasn’t sent.</strong> ' + reason.replace(/</g, '&lt;') + ' Please email me directly at <a href="mailto:ahmedkhanswati82@gmail.com">ahmedkhanswati82@gmail.com</a>.');
        })
        .then(function () {
          clearTimeout(timer);
          submit.disabled = false; submit.removeAttribute('aria-busy'); submit.firstChild.nodeValue = label;
          statusEl.setAttribute('tabindex', '-1'); statusEl.focus();
        });
    });
  });

  /* ---------------- misc ---------------- */
  safe('year', function () { var y = $('#year'); if (y) y.textContent = String(new Date().getFullYear()); });
})();
