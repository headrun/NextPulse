Notification.requestPermission(function(status) {
  console.log('Notification permission status:', status);
});


function displayNotification() {
  if (Notification.permission == 'granted') {
    navigator.serviceWorker.getRegistration().then(function(reg) {
      var options = {
        body: 'Here is a notification body!',
        title:'NextPulse',
        icon: 'images/nextwealth256.png',
        vibrate: [100, 50, 100],
        data: {
          dateOfArrival: Date.now(),
          primaryKey: 1
        },
        actions: [
        {action: 'explore', title: 'Go to the site',
          icon: 'images/checkmark.png'},
        {action: 'close', title: 'Close the notification',
          icon: 'images/xmark.png'},
    ]
      };
      //tag: 'id1',
      reg.showNotification('Hello world!', options);
    });
  }
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').then(function(reg) {
    console.log('Service Worker Registered!', reg);
    reg.pushManager.getSubscription().then(function(sub) {
      if (sub === null) {
        // Update UI to ask user to register for Push
        console.log('Not subscribed to push service!');
      } else {
        // We have a subscription, update the database
        console.log('Subscription object: ', sub);
      }
    });
  })
   .catch(function(err) {
    console.log('Service Worker registration failed: ', err);
  });
}


function updateBtn() {
  if (isSubscribed) {
    pushButton.textContent = 'Disable Push Messaging';
  } else {
    pushButton.textContent = 'Enable Push Messaging';
  }

  pushButton.disabled = false;
}

function initializeUI() {
  // Set the initial subscription value
  pushButton.addEventListener('click', function() {
    pushButton.disabled = true;
    if (isSubscribed) {
      unsubscribeUser();
    } else {
      subscribeUser();
    }
  });

  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    isSubscribed = (subscription !== null);
    updateSubscriptionOnServer(subscription);

    if (isSubscribed) {
      console.log('User IS subscribed.');
    } else {
      console.log('User is NOT subscribed.');
    }
  updateBtn();
  });
}

/*function subscribeUser() {  
  return navigator.serviceWorker.register('sw.js')
  .then(function(registration) {
    const subscribeOptions = {
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        'BCVgjl1U6b3xB6i2_MbRvFzOwrd-vxFWRNMWK97_athwruUxtm9Aq12e8SNXV30s8eYmMP8PZhBXS3spdjD9_3A'
      )
    };

    return registration.pushManager.subscribe(subscribeOptions);
  })
  .then(function(pushSubscription) {
    console.log('Received PushSubscription: ', JSON.stringify(pushSubscription));
    return pushSubscription;
  });
}*/

function subscribeUser() {      
  var applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  swRegistration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: applicationServerKey
    //console.log(applicationServerKey);
  })
  .then(function(subscription) {
    console.log('User is subscribed:', subscription);
    updateSubscriptionOnServer(subscription);
    isSubscribed = true;
    updateBtn();
  })
  .catch(function(err) {
    if (Notification.permission === 'denied') {
      console.warn('Permission for notifications was denied');
    } else {
      console.error('Failed to subscribe the user: ', err);
    }
    updateBtn();
  });
}


function unsubscribeUser() {
  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    if (subscription) {
      return subscription.unsubscribe();
    }
  })
  .catch(function(error) {
    console.log('Error unsubscribing', error);
  })
  .then(function() {
    updateSubscriptionOnServer(null);

    console.log('User is unsubscribed');
    isSubscribed = false;

    updateBtn();
  });
}



