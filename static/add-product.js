function toggleMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

document.getElementById('productName').addEventListener('blur', () => {
  const input = document.getElementById('productName');
  let name = input.value.trim();
  if (name.length > 0) {
    name = name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
    input.value = name;
  }
});

document.getElementById('addProductBtn').addEventListener('click', async () => {
  const name = document.getElementById('productName').value.trim();
  const amount = parseFloat(document.getElementById('productAmount').value);
  const expiryDate = document.getElementById('expiryDate').value;

  const responseEl = document.getElementById('responseMessage');
  responseEl.textContent = '';
  responseEl.style.color = 'black';

  try {
    const res = await fetch('/add-product', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ name, amount, expiryDate })
    });

    const data = await res.json();
    responseEl.textContent = data.message || data.error;
    responseEl.style.color = res.ok ? 'green' : 'red';
  } catch (err) {
    responseEl.textContent = 'Błąd połączenia z backendem.';
    responseEl.style.color = 'red';
    console.error(err);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('expiryDate').value = today;
});

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
