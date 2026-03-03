const CACHE_NAME = 'travel-map-v47'; // Дахиад нэг нэмчихье
const urlsToCache = [
  '/',              // Үндсэн хаяг
  'index.html',
  'manifest.json',
  'img.png'         // Логогоо заавал кэшлэх хэрэгтэй!
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Opened cache');
      return cache.addAll(urlsToCache);
    })
  );
});

// Бусад хэсэг нь хэвээрээ байна...

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key); // Хуучин кэшийг устгах
      })
    ))
  );
});
