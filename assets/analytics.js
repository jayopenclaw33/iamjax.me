/* Google Analytics 4, consent-first.
   Nothing loads and no cookie is set until the visitor clicks Accept.
   If GA_ID is ever cleared, this file does nothing at all (no banner either). */
(function () {
  var GA_ID = 'G-G1CZ4KG2QK'; // GA4 > Admin > Data streams > iamjax.me
  var KEY = 'iamjax_consent_v1';
  if (!/^G-[A-Z0-9]{4,}$/.test(GA_ID)) return;

  document.addEventListener('click', function (e) {
    var r = e.target && e.target.closest && e.target.closest('[data-consent-reset]');
    if (!r) return;
    e.preventDefault();
    try { localStorage.removeItem(KEY); } catch (err) {}
    document.cookie.split(';').forEach(function (c) { var n = c.split('=')[0].trim(); if (/^_ga/.test(n)) document.cookie = n + '=; Max-Age=0; path=/; domain=.' + location.hostname.replace(/^www\./, ''); });
    location.reload();
  });

  function load() {
    if (window.gtag) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { cookie_expires: 34190000, allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement('script');
    s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch (e) {}
  if (choice === 'accept') { load(); return; }
  if (choice === 'decline') return;

  function banner() {
    var b = document.createElement('div');
    b.className = 'consent';
    b.setAttribute('role', 'region');
    b.setAttribute('aria-label', 'Cookie choice');
    b.innerHTML = '<p>I use Google Analytics to see which pages people read. No ads, no selling data. ' +
      '<a href="/legal/privacy.html">Privacy</a></p>' +
      '<div><button type="button" class="btn btn-ghost btn-sm" data-c="decline">Decline</button>' +
      '<button type="button" class="btn btn-primary btn-sm" data-c="accept">Accept</button></div>';
    b.addEventListener('click', function (e) {
      var c = e.target.getAttribute && e.target.getAttribute('data-c');
      if (!c) return;
      try { localStorage.setItem(KEY, c); } catch (err) {}
      if (c === 'accept') load();
      b.remove();
    });
    document.body.insertBefore(b, document.body.firstChild);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', banner); else banner();
})();
