const CACHE_NAME = 'travel-map-v46'; // Хувилбарыг нь нэмж шинэчлэв

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Шинэ хувилбарыг шууд идэвхжүүлэх
});

self.addEventListener('fetch', (event) => {
  // Энэ хэсэг нь сайтыг PWA шалгуур хангахад тусална
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});