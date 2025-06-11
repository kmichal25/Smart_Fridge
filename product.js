function fetchNutritionData(productName) {
  const apiUrl = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(productName)}&search_simple=1&action=process&json=1`;

  return fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      const productData = data.products && data.products[0];

      if (!productData || !productData.nutriments) {
        console.warn("Nie znaleziono danych żywieniowych.");
        return null;
      }

      const nutriments = productData.nutriments;

      return {
        kcal: nutriments["energy-kcal_100g"] || "–",
        protein: nutriments["proteins_100g"] || "–",
        fat: nutriments["fat_100g"] || "–",
        carbs: nutriments["carbohydrates_100g"] || "–",
      };
    })
    .catch(error => {
      console.error("Błąd podczas pobierania danych z OpenFoodFacts:", error);
      return null;
    });
}

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const productName = urlParams.get("name");

  if (!productName) {
    alert("Brak nazwy produktu w URL.");
    return;
  }

  try {
    // 1. Wczytaj lokalny plik JSON z produktami
    const response = await fetch("products.json");
    const data = await response.json();

    // 2. Znajdź produkt pasujący po nazwie
    const product = data.find(p => p.name.toLowerCase() === productName.toLowerCase());

    if (!product) {
      alert(`Nie znaleziono produktu: ${productName}`);
      return;
    }

    // 3. Wypełnij dane w HTML
    document.querySelector(".product-card h2").textContent = product.name;

    document.querySelector(".product-card p").innerHTML = `
      <strong>Gramatura:</strong> ${product.amount} g<br>
      <strong>Data ważności:</strong> ${product.expiryDate}
    `;

    // 4. Oblicz dni do końca
    const today = new Date();
    const expiry = new Date(product.expiryDate);
    const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));

    // --- Nowa część: pasek postępu ---
    const shelfLifeDays = product.shelfLifeDays || 30;  // domyślnie 30 dni jeśli brak danych
    let progressPercent = (daysLeft / shelfLifeDays) * 100;
    if (progressPercent > 100) progressPercent = 100;

    const progressBar = document.querySelector(".progress-bar .progress");
    if (daysLeft <= 0) {
      progressBar.style.width = '100%';
      progressBar.style.backgroundColor = 'red';
      progressBar.textContent = "Produkt przeterminowany!";
    } else if (daysLeft <= 5) {
      progressBar.style.width = `${progressPercent}%`;
      progressBar.style.backgroundColor = 'orange';
      progressBar.textContent = `${daysLeft} dni do końca`;
    } else {
      progressBar.style.width = `${progressPercent}%`;
      progressBar.style.backgroundColor = 'green';
      progressBar.textContent = `${daysLeft} dni do końca`;
    }
    // --- koniec paska postępu ---

    // 5. Pobierz dane żywieniowe z OpenFoodFacts, czekaj na wynik
    const nutrition = await fetchNutritionData(product.name);

    if (nutrition) {
      document.querySelector(".nutrition").innerHTML = `
        <div><strong>${nutrition.kcal}</strong><br>kcal/100g</div>
        <div><strong>${nutrition.protein}g</strong><br>białko</div>
        <div><strong>${nutrition.fat}g</strong><br>tłuszcze</div>
        <div><strong>${nutrition.carbs}g</strong><br>węglowodany</div>
      `;
    } else {
      document.querySelector(".nutrition").innerHTML = "<p>Brak danych żywieniowych.</p>";
    }

  } catch (err) {
    console.error("Błąd podczas ładowania danych:", err);
  }
});
