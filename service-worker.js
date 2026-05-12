/**
 * XAU/USD Trading System - Service Worker
 * Enables offline access, push notifications, and background sync
 * @version 1.0.0
 */

const CACHE_NAME = 'gold-trader-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/XAU_USD Trading System — Nairobi.html',
  '/manifest.json',
  '/typescript-adapter.js',
  '/dist/index.js',
  '/dist/utils/StateManager.js',
  '/dist/utils/statistics.js',
  // Chart.js CDN - cached on install
  'https://cdn.jsdelivr.net/npm/chart.js',
  // Fonts
  'https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap',
  'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap'
];

// ═══════════════════════════════════════════════════════════════
// INSTALL - Cache static assets
// ═══════════════════════════════════════════════════════════════
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets...');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Static assets cached successfully');
        return self.skipWaiting();
      })
      .catch((err) => {
        console.error('[SW] Cache failed:', err);
      })
  );
});

// ═══════════════════════════════════════════════════════════════
// ACTIVATE - Clean old caches
// ═══════════════════════════════════════════════════════════════
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activated and controlling clients');
        return self.clients.claim();
      })
  );
});

// ═══════════════════════════════════════════════════════════════
// FETCH - Cache strategies
// ═══════════════════════════════════════════════════════════════
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Strategy 1: Network First for API calls
  if (url.pathname.includes('/api/') || url.search.includes('data=')) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Strategy 2: Cache First for static assets
  if (STATIC_ASSETS.includes(url.pathname) || 
      request.destination === 'script' ||
      request.destination === 'style' ||
      request.destination === 'font') {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Strategy 3: Stale While Revalidate for HTML pages
  if (request.mode === 'navigate') {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }
  
  // Default: Network with cache fallback
  event.respondWith(networkWithCacheFallback(request));
});

// ═══════════════════════════════════════════════════════════════
// CACHE STRATEGIES
// ═══════════════════════════════════════════════════════════════

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Update cache with fresh data
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, using cache:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for API
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'No network connection available',
        cached: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Revalidate in background
    fetch(request).then((response) => {
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, response);
      });
    }).catch(() => {});
    
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  const networkFetch = fetch(request).then((networkResponse) => {
    cache.put(request, networkResponse.clone());
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || networkFetch;
}

async function networkWithCacheFallback(request) {
  try {
    return await fetch(request);
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) return cached;
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════
// PUSH NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received:', event);
  
  const data = event.data?.json() || {
    title: 'Gold Trading Alert',
    body: 'New trading signal available',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'trading-signal',
    requireInteraction: true,
    actions: [
      { action: 'view', title: 'View Signal' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: data.badge,
      tag: data.tag,
      requireInteraction: data.requireInteraction,
      actions: data.actions,
      data: data.data || {}
    })
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const { action, notification } = event;
  
  if (action === 'view' || !action) {
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Focus existing window
        for (const client of clientList) {
          if (client.url.includes('/') && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow('/#' + (notification.data?.tab || 'dashboard'));
        }
      })
    );
  }
});

// ═══════════════════════════════════════════════════════════════
// BACKGROUND SYNC
// ═══════════════════════════════════════════════════════════════
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-trades') {
    event.waitUntil(syncPendingTrades());
  }
  
  if (event.tag === 'sync-alerts') {
    event.waitUntil(syncPendingAlerts());
  }
});

async function syncPendingTrades() {
  // Sync trades that were saved while offline
  const cache = await caches.open(CACHE_NAME);
  const pendingTrades = await cache.match('pending-trades');
  
  if (pendingTrades) {
    const trades = await pendingTrades.json();
    
    for (const trade of trades) {
      try {
        await fetch('/api/trades', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(trade)
        });
      } catch (err) {
        console.error('[SW] Failed to sync trade:', trade.id);
      }
    }
    
    // Clear pending trades
    await cache.delete('pending-trades');
  }
}

async function syncPendingAlerts() {
  console.log('[SW] Syncing pending alerts...');
}

// ═══════════════════════════════════════════════════════════════
// PERIODIC BACKGROUND SYNC (for price updates)
// ═══════════════════════════════════════════════════════════════
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'price-update') {
    event.waitUntil(fetchAndCachePrice());
  }
});

async function fetchAndCachePrice() {
  try {
    const response = await fetch('https://api.goldprice.org/v1/price/XAU/USD');
    const data = await response.json();
    
    const cache = await caches.open(CACHE_NAME);
    await cache.put(
      'latest-gold-price',
      new Response(JSON.stringify(data), {
        headers: { 'Content-Type': 'application/json' }
      })
    );
    
    // Notify clients
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'PRICE_UPDATE',
        price: data.price
      });
    });
  } catch (err) {
    console.error('[SW] Failed to fetch price:', err);
  }
}

// ═══════════════════════════════════════════════════════════════
// MESSAGE HANDLING (from main thread)
// ═══════════════════════════════════════════════════════════════
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_NAME });
      break;
      
    case 'CACHE_TRADE':
      cachePendingTrade(data);
      break;
      
    case 'CLEAR_CACHE':
      clearAllCaches();
      break;
  }
});

async function cachePendingTrade(trade) {
  const cache = await caches.open(CACHE_NAME);
  const existing = await cache.match('pending-trades');
  const trades = existing ? await existing.json() : [];
  
  trades.push(trade);
  
  await cache.put(
    'pending-trades',
    new Response(JSON.stringify(trades), {
      headers: { 'Content-Type': 'application/json' }
    })
  );
}

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('[SW] All caches cleared');
}

console.log('[SW] Service Worker loaded');
