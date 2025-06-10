const gramRange = document.getElementById('gramRange');
const rangeValue = document.getElementById('rangeValue');

function toggleMenu() {
    document.getElementById('navLinks').classList.toggle('open');
    }

    function toggleExtra() {
    document.getElementById('extraPanel').classList.toggle('hidden');
    }

document.getElementById('goToAddProduct').addEventListener('click', () => {
    window.location.href = 'add-product.html';
  });

  const filterInput = document.getElementById('filterInput');
  const gramInput = document.getElementById('gramInput');
  
  function applyFilters() {
    const nameFilter = filterInput.value.toLowerCase();
    const gramLimit = parseInt(gramInput.value, 10);
  
    const allProducts = document.querySelectorAll('.product');
    const extraPanel = document.getElementById('extraPanel');
    let anyVisibleInExtra = false;
  
    allProducts.forEach(product => {
      const name = product.querySelector('strong')?.innerText.toLowerCase() || '';
      const amountMatch = product.innerText.match(/(\d+)g/);
      const grams = amountMatch ? parseInt(amountMatch[1], 10) : 0;
  
      const matchesName = name.includes(nameFilter) || !nameFilter;
      const matchesGrams = isNaN(gramLimit) || grams <= gramLimit;
  
      const shouldShow = matchesName && matchesGrams;
      product.style.display = shouldShow ? 'block' : 'none';
  
      if (shouldShow && extraPanel.contains(product)) {
        anyVisibleInExtra = true;
      }
    });
  
    if ((nameFilter || !isNaN(gramLimit)) && anyVisibleInExtra) {
      extraPanel.classList.remove('hidden');
    } else if (!nameFilter && isNaN(gramLimit)) {
      extraPanel.classList.add('hidden');
    }
  }
  
  filterInput.addEventListener('input', applyFilters);
  gramInput.addEventListener('input', applyFilters);
  
  

  window.addEventListener('DOMContentLoaded', async () => {
    const fridge = document.querySelector('.fridge-wrapper');
    const extra = document.getElementById('extraPanel');
  
    const positions = [
      { top: '30%', left: '5%' },
      { top: '30%', left: '30%' },
      { top: '41%', left: '5%' },
      { top: '41%', left: '30%' },
      { top: '50%', left: '5%' },
      { top: '50%', left: '30%' }
    ];
  
    try {
      const res = await fetch('http://localhost:3005/products');
      const products = await res.json();
  
      // ➕ Dodaj priorytet do każdego produktu
      const today = new Date();
      products.forEach(p => {
        const expiry = new Date(p.expiryDate);
        const diffInDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
  
        if (diffInDays <= 1) {
          p.priority = 1; // red
        } else if (diffInDays <= 3) {
          p.priority = 2; // orange
        } else {
          p.priority = 3; // green
        }
      });
  
      // 🔃 Sortuj według priorytetu
      products.sort((a, b) => a.priority - b.priority);
  
      // 🎨 Renderuj posortowane produkty
      products.forEach((p, i) => {
        const div = document.createElement('div');
  
        // Kolor
        let colorClass = 'green';
        if (p.priority === 1) colorClass = 'red';
        else if (p.priority === 2) colorClass = 'orange';
  
        div.className = `product ${colorClass}`;
        div.innerHTML = `<strong>${p.name}</strong><br>${p.amount}g<br>${p.expiryDate}`;
  
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'X';
        deleteBtn.classList.add('delete-btn');
        deleteBtn.onclick = () => deleteProduct(p.name);
        div.appendChild(deleteBtn);
  
        if (i < 6) {
          const pos = positions[i];
          div.style.position = 'absolute';
          div.style.top = pos.top;
          div.style.left = pos.left;
          fridge.appendChild(div);
        } else {
          extra.appendChild(div);
        }
      });
  
    } catch (e) {
      console.error('Błąd pobierania produktów', e);
    }
  });
  
  function deleteProduct(name) {
    fetch(`http://localhost:3005/products/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    })
    .then(res => res.json())
    .then(data => {
      console.log(data);
      location.reload(); // przeładuj widok
    })
    .catch(err => console.error('Błąd przy usuwaniu:', err));
  }
  

  