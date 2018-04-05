
self.addEventListener('notificationclose', function(e) {
  var notification = e.notification;
  var primaryKey = notification.data.primaryKey;

  console.log('Closed notification: ' + primaryKey);
});

self.addEventListener('notificationclick', function(e) {
  var notification = e.notification;
  var primaryKey = notification.data.primaryKey;
  var action = e.action;
    
  if (action === 'close') {
    notification.close();
  } else {
    e.waitUntil(
      clients.matchAll().then(function(clis) {
        var client = clis.find(function(c) {
          return c.visibilityState === 'visible';
        });
        if (client !== undefined) {
          client.navigate('/#!/page1/Salem%20-%20Probe');
          client.focus();
        } else {
          // there are no visible windows. Open one.
          clients.openWindow('https:nextpulse.nextwealth.in');
          notification.close();
        }
      })
    );
  }

  // TODO 5.3 - close all notifications when one is clicked
  //added 5.3 code
  self.registration.getNotifications().then(function(notifications) {
    notifications.forEach(function(notification) {
      notification.close();
    });
  });

});

self.addEventListener('push', function(e) {
  var body;

  if (e.data) {
    body = e.data.text();
  } else {
    body = 'Default body';
  }

  var options = {
    body: body,
    icon: 'images/nextwealth128.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {action: 'explore', title: 'Go to the site NextPulse',
        icon: 'images/nextwealth128.png'},
      {action: 'close', title: 'Close the notification',
        icon: 'images/nextwealth128.png'},
    ]
  };

  e.waitUntil(
    self.registration.showNotification('Push Notification', options)
  );
});


/*self.addEventListener('notificationclick', function(e) {

  // TODO 2.8 - change the code to open a custom page

  clients.openWindow('http://google.com');
});*/