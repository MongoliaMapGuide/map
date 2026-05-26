const CACHE_NAME = 'travelmap-v76';

const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo192.png',
  '/logo512.png',
  '/favicon.ico'
];

// 1. Суурилуулах (Install) - Шинэ хувилбарыг шууд идэвхжүүлнэ
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.all(
        urlsToCache.map(url => cache.add(url).catch(err => console.log('Файл татахад алдаа: ' + url)))
      );
    })
  );
});

// 2. Идэвхжүүлэх (Activate) - Хуучин кэшийг шууд устгах
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

// 3. Мэдээлэл татах (Fetch) - Сүлжээний гацалтаас бүрэн хамгаалсан хувилбар ⚡
self.addEventListener('fetch', event => {
  // Зөвхөн http эсвэл https хүсэлтүүдийг барина (chrome-extension болон бусад зүйлсийг алгасна)
  if (!event.request.url.startsWith('http')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Хэрэв сервер зөв хариу өгсөн бол (status 200) шууд буцаана
        if (response && response.status === 200) {
          return response;
        }
        // Хэрэв 404, 400 зэрэг алдаа ирвэл кэшээс хайж үзнэ
        return caches.match(event.request).then(cachedResponse => {
          return cachedResponse || response; // Кэшид байвал кэшийг, байхгүй бол уг алдааны хариуг хэвээр нь буцаана
        });
      })
      .catch(() => {
        // Сүлжээ бүрмөсөн тасрах эсвэл сүлжээний ноцтой алдаа үед
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // Кэшид ч байхгүй, сүлжээ ч байхгүй бол хоосон хариу буцааж хөтөчийг гацахаас аварна ✨
          return new Response('Сүлжээний алдаа эсвэл файл олдсонгүй', {
            status: 404,
            statusText: 'Not Found',
            headers: new Headers({ 'Content-Type': 'text/plain; charset=utf-8' })
          });
        });
      })
  );
});