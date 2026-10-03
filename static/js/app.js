(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };

  /* 0. Pasang nilai dari data attribute (latar donut, lebar, tinggi) */
  document.querySelectorAll('[data-bg]').forEach(function (el) { el.style.background = el.dataset.bg; });
  document.querySelectorAll('[data-width]').forEach(function (el) { el.style.width = el.dataset.width + '%'; });
  document.querySelectorAll('[data-height]').forEach(function (el) { el.style.height = el.dataset.height + '%'; });

  /* 1. Menu sidebar di ponsel */
  var toggle = document.querySelector('[data-menu-toggle]');
  var overlay = document.querySelector('[data-menu-overlay]');

  function setMenu(open) {
    document.body.classList.toggle('menu-open', open);
    if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (toggle) toggle.addEventListener('click', function () {
    setMenu(!document.body.classList.contains('menu-open'));
  });
  if (overlay) overlay.addEventListener('click', function () { setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* 2. Animasi masuk (sekali saat halaman dibuka, bukan saat muat ulang otomatis) */
  var auto = false;
  try {
    auto = sessionStorage.getItem('autoReload') === '1';
    sessionStorage.removeItem('autoReload');
  } catch (e) {}

  if (!reduce && !auto) {
    // angka KPI dan donut menghitung naik
    document.querySelectorAll('.kpi b, .donut b').forEach(function (el) {
      var m = el.textContent.trim().match(/^(\d+)(%?)$/);
      if (!m) return;
      var target = parseInt(m[1], 10), suffix = m[2], start = null, dur = 900;
      if (target === 0) return;
      el.textContent = '0' + suffix;
      requestAnimationFrame(function step(t) {
        if (start === null) start = t;
        var p = Math.min((t - start) / dur, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + suffix;
        if (p < 1) requestAnimationFrame(step);
      });
    });

    // batang dan grafik tren tumbuh dari nol
    var grow = document.querySelectorAll('.bar i, .stack');
    grow.forEach(function (el) {
      var prop = el.classList.contains('stack') ? 'height' : 'width';
      el.dataset.prop = prop;
      el.dataset.final = el.style[prop];
      el.style[prop] = prop === 'height' ? '3px' : '0';
    });
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        grow.forEach(function (el) { el.style[el.dataset.prop] = el.dataset.final; });
      });
    });
  }

  /* 3. Muat ulang dashboard otomatis tiap 60 detik */
  if (document.querySelector('.kpis')) {
    var head = document.querySelector('.head > div');
    if (head) {
      var now = new Date();
      var info = document.createElement('p');
      info.className = 'refresh';
      info.textContent = 'Diperbarui pukul ' + pad(now.getHours()) + ':' + pad(now.getMinutes()) +
                         ' · otomatis tiap 60 detik';
      head.appendChild(info);
    }
    setInterval(function () {
      if (document.hidden) return;
      try { sessionStorage.setItem('autoReload', '1'); } catch (e) {}
      location.reload();
    }, 60000);
  }
})();