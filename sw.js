// ── Bump this version number with every deploy to force cache refresh ──
const CACHE_VERSION = 4;
const CACHE_NAME = `catechism-v${CACHE_VERSION}`;

const ASSETS = [
  './',
  './index.html',
  './schedule.js',
  './manifest.json',
  './catechisms.json',
  './fonts/fonts.css',
  './fonts/PlayfairDisplay-roman.woff2',
  './fonts/PlayfairDisplay-italic.woff2',
  './fonts/EBGaramond-roman.woff2',
  './fonts/EBGaramond-italic.woff2'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys =>
        Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      // Claim only once the old caches are gone. Claiming first would let a
      // page start fetching while a previous version's entries were still
      // present, and an unscoped caches.match would serve them.
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Data: network-first so a regenerated catechisms.json shows up without a version bump
  if (url.pathname.endsWith('/catechisms.json')) {
    e.respondWith(
      fetch(e.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      }).catch(() => caches.match(e.request, { cacheName: CACHE_NAME }))
    );
    return;
  }

  // App shell + fonts: cache-first.
  // Always scope lookups to CACHE_NAME — a bare caches.match() searches every
  // cache oldest-first, so a stale entry from a previous version can win and
  // defeat the CACHE_VERSION bump.
  e.respondWith(
    caches.match(e.request, { cacheName: CACHE_NAME }).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      });
    }).catch(() => {
      if (e.request.mode === 'navigate') {
        return caches.match('./index.html', { cacheName: CACHE_NAME });
      }
      return Response.error();
    })
  );
});

// ── Notification click: open/focus the app ──
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const urlToOpen = e.notification.data?.url || self.registration.scope;
  const scope = self.registration.scope;

  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      // Match on scope rather than an exact URL: the stored url came from
      // location.href, so any hash, query string, or './' vs 'index.html'
      // difference would miss an already-open app and open a second window.
      for (const client of windowClients) {
        if (client.url.startsWith(scope) && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(urlToOpen);
    })
  );
});
