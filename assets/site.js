/* iamjax.me motion + forms. No libraries. Everything degrades to a static page. */
(function () {
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;

  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  requestAnimationFrame(function () { document.body.classList.add('loaded'); });

  /* nav state */
  var nav = document.querySelector('.nav');
  function onScroll() { if (nav) nav.classList.toggle('scrolled', window.scrollY > 30); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* scroll reveal */
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
    // Safety net for fast flings: anything already above the fold bottom is shown.
    var pending = false;
    window.addEventListener('scroll', function () {
      if (pending) return; pending = true;
      requestAnimationFrame(function () {
        pending = false;
        document.querySelectorAll('[data-reveal]:not(.in)').forEach(function (el) {
          if (el.getBoundingClientRect().top < innerHeight) { el.classList.add('in'); io.unobserve(el); }
        });
      });
    }, { passive: true });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* count-up stats */
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var end = parseInt(el.getAttribute('data-count'), 10), suffix = el.getAttribute('data-suffix') || '';
    if (reduce || !('IntersectionObserver' in window)) { el.textContent = end + suffix; return; }
    var o = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return; o.disconnect();
      var t0 = performance.now();
      (function step(t) {
        var k = Math.min(1, (t - t0) / 1400), v = Math.round(end * (1 - Math.pow(1 - k, 3)));
        el.textContent = v + suffix; if (k < 1) requestAnimationFrame(step);
      })(t0);
    });
    o.observe(el);
  });

  if (!reduce && finePointer) {
    /* card tilt + spotlight */
    document.querySelectorAll('[data-tilt]').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.setProperty('--mx', (x * 100) + '%'); card.style.setProperty('--my', (y * 100) + '%');
        card.style.setProperty('--ry', ((x - .5) * 7) + 'deg'); card.style.setProperty('--rx', ((.5 - y) * 7) + 'deg');
      });
      card.addEventListener('pointerleave', function () { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); });
    });

    /* hero portrait: follows the pointer in 3D */
    var stage = document.querySelector('.stage');
    if (stage) {
      window.addEventListener('pointermove', function (e) {
        var x = e.clientX / window.innerWidth - .5, y = e.clientY / window.innerHeight - .5;
        stage.style.setProperty('--ry', (x * 14) + 'deg'); stage.style.setProperty('--rx', (-y * 10) + 'deg');
        stage.style.setProperty('--gx', (50 + x * 60) + '%'); stage.style.setProperty('--gy', (30 + y * 50) + '%');
      }, { passive: true });
    }
  }

  /* signal mesh: drifting nodes that link when close, with scroll parallax */
  var cv = document.getElementById('mesh');
  if (cv && !reduce && cv.getContext) {
    var ctx = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2), W, H, nodes = [], px = 0, py = 0, running = true;
    var colors = ['232,185,106', '139,92,246', '34,211,238', '244,114,182'];
    function size() {
      W = cv.width = innerWidth * dpr; H = cv.height = innerHeight * dpr;
      cv.style.width = innerWidth + 'px'; cv.style.height = innerHeight + 'px';
      var count = Math.round(Math.min(90, innerWidth * innerHeight / 18000));
      nodes = [];
      for (var i = 0; i < count; i++) nodes.push({
        x: Math.random() * W, y: Math.random() * H, z: Math.random() * .9 + .1,
        vx: (Math.random() - .5) * .18 * dpr, vy: (Math.random() - .5) * .18 * dpr, c: colors[i % colors.length]
      });
    }
    size(); window.addEventListener('resize', size);
    if (finePointer) window.addEventListener('pointermove', function (e) { px = (e.clientX / innerWidth - .5); py = (e.clientY / innerHeight - .5); }, { passive: true });
    document.addEventListener('visibilitychange', function () { running = !document.hidden; if (running) requestAnimationFrame(draw); });
    var link = 130 * dpr;
    function draw() {
      if (!running) return;
      ctx.clearRect(0, 0, W, H);
      var sy = window.scrollY * dpr;
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > W) n.vx *= -1; if (n.y < 0 || n.y > H) n.vy *= -1;
        n.sx = n.x + px * 40 * n.z * dpr; n.sy = ((n.y - sy * .15 * n.z) % H + H) % H + py * 40 * n.z * dpr;
      }
      for (i = 0; i < nodes.length; i++) {
        var a = nodes[i];
        for (var j = i + 1; j < nodes.length; j++) {
          var b = nodes[j], dx = a.sx - b.sx, dy = a.sy - b.sy, d = dx * dx + dy * dy;
          if (d < link * link) {
            ctx.strokeStyle = 'rgba(' + a.c + ',' + (0.22 * (1 - Math.sqrt(d) / link)) + ')';
            ctx.lineWidth = dpr * .6; ctx.beginPath(); ctx.moveTo(a.sx, a.sy); ctx.lineTo(b.sx, b.sy); ctx.stroke();
          }
        }
        ctx.fillStyle = 'rgba(' + a.c + ',' + (0.35 + a.z * .5) + ')';
        ctx.beginPath(); ctx.arc(a.sx, a.sy, (0.8 + a.z * 1.6) * dpr, 0, 6.283); ctx.fill();
      }
      requestAnimationFrame(draw);
    }
    requestAnimationFrame(draw);
  }

  /* talk cards prefill the booking form */
  var sel = document.getElementById('btalk');
  document.querySelectorAll('[data-talk]').forEach(function (a) {
    a.addEventListener('click', function () {
      if (!sel) return;
      var want = a.getAttribute('data-talk');
      for (var i = 0; i < sel.options.length; i++) if (sel.options[i].text.indexOf(want) === 0) { sel.selectedIndex = i; break; }
    });
  });

  /* booking form: composes an email to jax@thezaraai.com in the visitor's mail app */
  var form = document.getElementById('bookform');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.website && form.website.value) return; // honeypot
      var d = new FormData(form), lines = [];
      [['name', 'Name'], ['email', 'Email'], ['organization', 'Organization'], ['event', 'Event'], ['date', 'Event date'],
       ['location', 'Location / format'], ['audience', 'Audience size'], ['talk', 'Talk'], ['message', 'Message']].forEach(function (f) {
        var v = (d.get(f[0]) || '').toString().trim(); if (v) lines.push(f[1] + ': ' + v);
      });
      var subject = 'Speaking enquiry: ' + ((d.get('event') || d.get('organization') || d.get('name') || '').toString().trim() || 'iamjax.me');
      window.location.href = 'mailto:jax@thezaraai.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      var s = document.getElementById('form-status'); if (s) s.classList.add('show');
    });
  }
})();

/* copy-to-clipboard for speaker kit bios: <button data-copy="#id"> */
(function () {
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    var label = btn.textContent;
    btn.addEventListener('click', function () {
      var el = document.querySelector(btn.getAttribute('data-copy'));
      if (!el) return;
      var text = el.innerText.trim();
      function done(ok) {
        btn.textContent = ok ? 'Copied' : 'Select and copy';
        setTimeout(function () { btn.textContent = label; }, 2000);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
      } else {
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        var ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
        done(ok);
      }
    });
  });
})();
