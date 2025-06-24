function toggleMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

document.addEventListener("DOMContentLoaded", () => {
  const progressText = document.querySelector(".progress");
  const progressBar = document.querySelector(".progress-bar .progress");

  const expiryDateStr = document.querySelector(".progress-bar").dataset.expiry;

  if (!expiryDateStr) {
    progressText.textContent = "Brak danych o dacie ważności.";
    progressBar.style.backgroundColor = "gray";
    return;
  }

  const today = new Date();
  const expiryDate = new Date(expiryDateStr);
  today.setHours(0, 0, 0, 0);
  expiryDate.setHours(0, 0, 0, 0);
  const diffTime = expiryDate - today;
  const remainingDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  let percentage = 0;

  if (remainingDays < 0) {
    percentage = 100;
    progressText.textContent = "Produkt przeterminowany!";
    progressBar.style.backgroundColor = "#d9534f";
  } else if (remainingDays > 30) {
    percentage = 50;
    progressText.textContent = "Ważny jeszcze ponad 30 dni";
    progressBar.style.backgroundColor = "#5cb85c"; 
  } else {
    percentage = Math.round(((30 - remainingDays) / 30) * 100);
    progressText.textContent = `Pozostało ${remainingDays} dni`;
  
    let color = "#5cb85c"; 
    if (remainingDays <= 1) color = "#d9534f";
    else if (remainingDays <= 3) color = "#f0ad4e";
    progressBar.style.backgroundColor = color;
  }
  
  setTimeout(() => {
    progressBar.style.width = percentage + "%";
  }, 200);
});

document.getElementById("deleteBtn").addEventListener("click", async () => {
  const encodedName = encodeURIComponent(
    document.getElementById("deleteBtn").dataset.productName
  );  

  try {
    const res = await fetch(`/products/${encodedName}`, {
      method: "DELETE",
      credentials: "include"
    });

    if (res.ok) {
      document.getElementById("modalMessage").style.display = "block";
      document.getElementById("modalOverlay").style.display = "block";
      document.getElementById("modalMessage").textContent = "Produkt został usunięty.";

      const dashboardUrl = document.body.dataset.dashboardUrl;

      setTimeout(() => {
        window.location.href = dashboardUrl;
      }, 2000);
    } else {
      const data = await res.json();
      document.getElementById("productDetails").textContent = data.error || "Nie udało się usunąć produktu.";
    }
  } catch (error) {
    document.getElementById("productDetails").textContent = "Błąd połączenia z serwerem.";
  }
});

document.getElementById("modalOverlay").addEventListener("click", () => {
  document.getElementById("modalMessage").style.display = "none";
  document.getElementById("modalOverlay").style.display = "none";
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
