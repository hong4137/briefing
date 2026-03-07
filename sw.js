// Service Worker for Jae's Foreign News Briefing PWA
const CACHE_NAME = 'jfnb-cache-v1';
const OFFLINE_URL = '/briefing/offline.html';

// Core assets to cache on install (App Shell)
const APP_SHELL = [
  '/briefing/',
  '/briefing/index.html',
  '/briefing/archive.html',
  '/briefing/about.html',
  '/briefing/search.html',
  '/briefing/briefings.json',
  '/briefing/list.json',
  '/briefing/search-index.json',
  '/briefing/offline.html',
  '/briefing/manifest.json',
  '/briefing/icons/icon-192x192.png',
  '/briefing/icons/icon-512x512.png'
];

// Google Fonts to cache
const FONT_URLS = [
  'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Playfair+Display:wght@700;900&family=JetBrains+Mono:wght@400;500&display=swap'
];

// Install - cache app shell
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Caching app shell');
      // Cache fonts separately (may fail due to CORS)
      FONT_URLS.forEach(url => {
        cache.add(url).catch(() => console.log('[SW] Font cache skipped:', url));
      });
      return cache.addAll(APP_SHELL);
    }).then(() => {
      // Activate immediately
      return self.skipWaiting();
    })
  );
});

// Activate - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Strategy for briefing article HTML files (archive/*.html)
  // -> Network first, fallback to cache (articles update infrequently once published)
  if (url.pathname.startsWith('/briefing/archive/') && url.pathname.endsWith('.html')) {
    event.respondWith(networkFirstThenCache(request));
    return;
  }

  // Strategy for JSON data (briefings.json, list.json, search-index.json)
  // -> Stale-while-revalidate (show cached, update in background)
  if (url.pathname.endsWith('.json') && url.pathname.startsWith('/briefing/')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Strategy for app shell pages (index, archive, about, search .html)
  // -> Stale-while-revalidate  
  if (url.pathname.startsWith('/briefing/') && url.pathname.endsWith('.html')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Strategy for Google Fonts
  if (url.hostname.includes('fonts.googleapis.com') || url.hostname.includes('fonts.gstatic.com')) {
    event.respondWith(cacheFirstThenNetwork(request));
    return;
  }

  // Default: network first with cache fallback
  event.respondWith(networkFirstThenCache(request));
});

// --- Caching Strategies ---

// Network first, fallback to cache
async function networkFirstThenCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // If it's a navigation request, show offline page
    if (request.mode === 'navigate') {
      return caches.match(OFFLINE_URL);
    }
    return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
  }
}

// Cache first, fallback to network
async function cacheFirstThenNetwork(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

// Stale-while-revalidate
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    // Network failed, that's ok if we have cache
    return null;
  });

  // Return cached version immediately, or wait for network
  if (cachedResponse) {
    // Update in background
    fetchPromise;
    return cachedResponse;
  }
  
  const networkResponse = await fetchPromise;
  if (networkResponse) {
    return networkResponse;
  }
  
  // Both failed - show offline page for navigation
  if (request.mode === 'navigate') {
    return caches.match(OFFLINE_URL);
  }
  return new Response('Offline', { status: 503 });
}

// Listen for messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  // Cache specific briefing articles on demand
  if (event.data && event.data.type === 'CACHE_ARTICLE') {
    const url = event.data.url;
    caches.open(CACHE_NAME).then((cache) => {
      cache.add(url).then(() => {
        console.log('[SW] Cached article:', url);
      }).catch((err) => {
        console.log('[SW] Failed to cache article:', url, err);
      });
    });
  }
});
