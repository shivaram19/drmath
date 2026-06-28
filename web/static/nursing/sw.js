const CACHE_NAME = 'mathwise-nursing-v1';
const SHELL_ASSETS = [
  '/nursing/',
  '/nursing/index.html',
  '/nursing/privacy',
  '/nursing/privacy.html',
  '/nursing/styles.css',
  '/nursing/app.js',
  '/nursing/manifest.json',
  '/nursing/daily.json',
  '/nursing/og-image.png',
  '/nursing/icon-192.png',
  '/nursing/icon-512.png',
  '/nursing/favicon.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // API: network first, fallback to cache or offline daily.json
  if (request.url.includes('/api/nursing/questions')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          return caches.open(CACHE_NAME)
            .then((cache) => cache.put(request, clone))
            .then(() => response);
        })
        .catch(() => caches.match(request).then((r) => r || caches.match('/nursing/daily.json')))
    );
    return;
  }

  // Shell assets: cache first, network fallback
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        return response;
      });
    })
  );
});
