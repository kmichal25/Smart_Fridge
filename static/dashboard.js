function toggleMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

window.addEventListener('DOMContentLoaded', async () => {
  const extraPanel = document.getElementById('extraPanel');

  try {
    const res = await fetch('/products', {
      method: 'GET',
      credentials: 'include'
    });
    const products = await res.json();

    const today = new Date();

    products.sort((a, b) => {
      const today = new Date();
      const aDays = Math.ceil((new Date(a.expiryDate) - today) / (1000 * 60 * 60 * 24));
      const bDays = Math.ceil((new Date(b.expiryDate) - today) / (1000 * 60 * 60 * 24));

      const priority = days => days <= 1 ? 0 : days <= 3 ? 1 : 2;
      return priority(aDays) - priority(bDays);
    });

    products.forEach(p => {
      const div = document.createElement('div');
      div.className = 'product';

      const expiry = new Date(p.expiryDate);
      const diffDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
      let color = 'green';
      if (diffDays <= 1) color = 'red';
      else if (diffDays <= 3) color = 'orange';

      div.classList.add(color);
      div.innerHTML = `
        <strong><a href="/product/${encodeURIComponent(p.name)}" style="color: inherit; text-decoration: none;">${p.name}</a></strong><br>
        ${p.amount}g<br>
        ${p.expiryDate}
      `;

      const deleteBtn = document.createElement('button');
      deleteBtn.textContent = 'X';
      deleteBtn.className = 'delete-btn';
      deleteBtn.onclick = () => deleteProduct(p.name);
      div.appendChild(deleteBtn);

      extraPanel.appendChild(div);
    });


    applyFilters();

  } catch (err) {
    console.error('Błąd ładowania produktów:', err);
  }
});

function applyFilters() {
  const nameFilter = document.getElementById('filterInput').value.toLowerCase();
  const maxGrams = parseInt(document.getElementById('maxGrams').value);

  const products = document.querySelectorAll('.product');
  products.forEach(p => {
    const name = p.querySelector('strong')?.innerText.toLowerCase() || '';
    const grams = parseInt(p.innerText.match(/(\d+)g/)?.[1] || '0');

    const nameMatch = name.includes(nameFilter);
    const gramsMatch = isNaN(maxGrams) ? true : grams <= maxGrams;

    p.style.display = nameMatch && gramsMatch ? 'block' : 'none';
  });
}

document.getElementById('filterInput').addEventListener('input', applyFilters);
document.getElementById('maxGrams').addEventListener('input', applyFilters);

function deleteProduct(name) {
  fetch(`/products/${encodeURIComponent(name)}`, {
    method: 'DELETE',
    credentials: 'include'
  })
    .then(res => res.json())
    .then(() => location.reload())
    .catch(err => console.error('Błąd przy usuwaniu:', err));
}
