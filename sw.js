const CACHE_NAME = 'travelmap-v61';
// sw.js файл доторх URLsToCache хэсэг
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo192.png',  // Шинэ 192px лого (Заавал байх ёстой)
  '/logo512.png',  // 512px лого
  '/favicon.ico'   // Хайлтын лого
];
self.addEventListener('install', event => {
self.skipWaiting();
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