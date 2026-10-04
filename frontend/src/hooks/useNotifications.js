import { useState, useEffect } from 'react';

export function useNotifications() {
  const [permission, setPermission] = useState(Notification.permission);

  useEffect(() => {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      if (permission === 'default') {
        Notification.requestPermission().then((perm) => setPermission(perm));
      }
      
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.error('Service Worker registration failed:', err);
      });
    }
  }, [permission]);

  const sendNotification = (title, body) => {
    if (permission === 'granted' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(registration => {
        registration.showNotification(title, {
          body,
          icon: '/vite.svg',
          badge: '/vite.svg',
          vibrate: [100, 50, 100],
        });
      });
    }
  };

  return { permission, sendNotification };
}
