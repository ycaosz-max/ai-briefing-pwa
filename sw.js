// Service Worker - PWA离线支持
const CACHE_NAME = 'ai-briefing-pwa-v1';

self.addEventListener('install', function(event) {
  console.log('Service Worker 安装成功');
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  console.log('Service Worker 激活成功');
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    fetch(event.request).catch(function() {
      return new Response('离线模式：请检查网络连接');
    })
  );
});