function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('open');
  }
  
  // Automatyczna poprawa nazwy po wyjściu z pola
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
      const res = await fetch('http://localhost:3005/add-product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

  document.getElementById('goToDashboard').addEventListener('click', () => {
    window.location.href = 'dashboard.html';
  });
  