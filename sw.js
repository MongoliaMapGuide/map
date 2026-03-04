const CACHE_NAME = 'travel-map-v9';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Энэ хэсэг хоосон байсан ч 'fetch' эвент заавал байх ёстой
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});