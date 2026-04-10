const CACHE_NAME = 'travelmap-v47';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  'https://github.com/MongoliaMapGuide/map/blob/main/logo512.png?raw=true'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        // addAll-ийн оронд нэг бүрчлэн нэмэх нь илүү найдвартай
        return Promise.all(
          urlsToCache.map(url => {
            return cache.add(url).catch(err => console.log('Файл татахад алдаа гарлаа: ' + url));
          })
        );
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});