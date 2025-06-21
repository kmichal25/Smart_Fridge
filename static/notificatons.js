function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('open');
  }

window.addEventListener('DOMContentLoaded', () => {
    const badge = document.getElementById('notifBadge');
  
    fetch('/api/notifications/count')
      .then(res => res.json())
      .then(data => {
        if (badge && data.count > 0) {
          badge.innerText = data.count;
          badge.style.display = 'inline-block';
        } else {
          badge.style.display = 'none';
        }
      })
      .catch(err => console.error('Błąd ładowania powiadomień:', err));
  });

async function fetchNotifications() {
    try {
      const res = await fetch('/products', { credentials: 'include' });
      const products = await res.json();
      const today = new Date();

      const notificationsContainer = document.getElementById('notificationsList');
      notificationsContainer.innerHTML = '';

      products.forEach(p => {
        const expiry = new Date(p.expiryDate);
        const diffDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
        if (diffDays <= 3) {
          const notif = document.createElement('div');
          notif.className = 'notification-item';

          if (diffDays <= 1) {
            notif.innerHTML = `
              <p><strong>${p.name}</strong> jest <span style="color:red;">przeterminowany</span>!</p>
              <div class="notification-buttons">
                <button class="btn-primary" onclick="deleteProduct('${p.name}')">Usuń produkt</button>
                <button class="btn-secondary" onclick="ignoreNotification('${p.name}', this)">Ignoruj</button>
              </div>
            `;
          } else {
            notif.innerHTML = `
              <p><strong>${p.name}</strong> wkrótce się zepsuje (za ${diffDays} dni).</p>
              <div class="notification-buttons">
              <button class="btn-primary" onclick="window.location.href='/recipes'">Zobacz dostępne przepisy</button>
              <button class="btn-secondary" onclick="ignoreNotification('${p.name}', this)">Ignoruj</button>
              </div>
            `;
          }

          notificationsContainer.appendChild(notif);
        }
      });

      if (notificationsContainer.children.length === 0) {
        notificationsContainer.innerHTML = '<p>Brak nowych powiadomień.</p>';
      }
    } catch (err) {
      console.error('Błąd ładowania powiadomień:', err);
    }
  }

  function showMessage(message) {
    const modalMessage = document.getElementById('modalMessage');
    const modalOverlay = document.getElementById('modalOverlay');

    modalMessage.textContent = message;
    modalMessage.style.display = 'block';
    modalOverlay.style.display = 'block';

    setTimeout(() => {
      modalMessage.style.display = 'none';
      modalOverlay.style.display = 'none';
    }, 2000);
  }

  function deleteProduct(name) {
    fetch(`/products/${encodeURIComponent(name)}`, {
      method: 'DELETE',
      credentials: 'include'
    })
    .then(res => {
      if (res.ok) {
        showMessage('Produkt został usunięty.');
        fetchNotifications();
      } else {
        showMessage('Błąd podczas usuwania produktu.');
        console.error('Błąd podczas usuwania produktu.');
      }
    })
    .catch(() => {
      showMessage('Błąd połączenia z serwerem.');
    });
  }

  function ignoreNotification(name, button) {
    const notifElement = button.closest('.notification-item');
    if (notifElement) {
      notifElement.remove();
    }

    const notificationsContainer = document.getElementById('notificationsList');
    if (notificationsContainer.children.length === 0) {
      notificationsContainer.innerHTML = '<p>Brak nowych powiadomień.</p>';
    }
  }

  document.getElementById('modalOverlay').addEventListener('click', () => {
    document.getElementById('modalMessage').style.display = 'none';
    document.getElementById('modalOverlay').style.display = 'none';
  });

  window.addEventListener('DOMContentLoaded', fetchNotifications);


  