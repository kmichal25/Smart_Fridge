function showModal(message) {
  const modal = document.getElementById('modalMessage');
  const overlay = document.getElementById('modalOverlay');
  modal.textContent = message;
  modal.style.display = 'block';
  overlay.style.display = 'block';

  setTimeout(() => {
    modal.style.display = 'none';
    overlay.style.display = 'none';
  }, 3000);
}

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
    const response = await fetch("products.json");
    const data = await response.json();

    let product = data.find(p => p.name.toLowerCase() === productName.toLowerCase());

    if (!product) {
      alert(`Nie znaleziono produktu: ${productName}`);
      return;
    }

    function renderProduct() {
      document.querySelector(".product-card h2").textContent = product.name;

      document.querySelector(".product-card p").innerHTML = `
        <strong>Gramatura:</strong> ${product.amount} g<br>
        <strong>Data ważności:</strong> ${product.expiryDate}
      `;

      const today = new Date();
      const expiry = new Date(product.expiryDate);
      const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));

      const shelfLifeDays = product.shelfLifeDays || 30;
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

      fetchNutritionData(product.name).then(nutrition => {
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

         if (product) {
    loadMatchingRecipes(product.name);
  }
      });
    }

    renderProduct();

    document.querySelector(".btn-primary").addEventListener("click", () => {
      product = null;

      document.querySelector(".product-card h2").textContent = "";
      document.querySelector(".product-card p").innerHTML = "";
      const progressBar = document.querySelector(".progress-bar .progress");
      progressBar.style.width = '0';
      progressBar.style.backgroundColor = 'transparent';
      progressBar.textContent = "";

      document.querySelector(".nutrition").innerHTML = "";

      // Tu pokazujemy modal zamiast wstawiać do jakiegoś diva
       showModal("Ten produkt został usunięty i nie istnieje już w Twojej lodówce.");

  // Przekierowanie na dashboard po krótkim opóźnieniu, np. 1,5 sekundy, żeby komunikat zdążył się pokazać
  setTimeout(() => {
    window.location.href = "dashboard.html";
  }, 1500);
});

  } catch (err) {
    console.error("Błąd podczas ładowania danych:", err);
  }
});

async function loadMatchingRecipes(productName) {
  try {
    const response = await fetch("recipes.json");
    const recipes = await response.json();

    const lowerName = productName.toLowerCase();

    const matching = recipes.filter(recipe =>
      recipe.title.toLowerCase().includes(lowerName) ||
      recipe.description.toLowerCase().includes(lowerName) ||
      recipe.instructions.some(instr => instr.toLowerCase().includes(lowerName))
    );

    const section = document.querySelector(".recipe-section");

    if (!section) {
      console.warn("Brak kontenera .recipe-section w HTML.");
      return;
    }

    if (matching.length === 0) {
      section.innerHTML = `
        <h2>Przepisy z tym produktem</h2>
        <p>Brak przepisów z tym składnikiem.</p>
      `;
      return;
    }

    section.innerHTML = `<h2>Przepisy z tym produktem</h2>`;

    matching.forEach(recipe => {
      const recipeDiv = document.createElement("div");
      recipeDiv.classList.add("recipe-card");

      // Update the recipe card template in loadMatchingRecipes function
// Utwórz wrapper na tekst przepisu
recipeDiv.innerHTML = `
  <h3>${recipe.title}</h3>
  <p>${recipe.description}</p>
  <p><strong>Czas:</strong> ${recipe.prep_time + recipe.cook_time} min</p>
  <p><strong>Porcje:</strong> ${recipe.servings}</p>
`;

// Dodaj przycisk "Zobacz przepis"
const viewBtn = document.createElement("button");
viewBtn.textContent = "Zobacz przepis";
viewBtn.classList.add("btn-primary", "view-recipe");
viewBtn.dataset.id = recipe.id;
viewBtn.style.marginTop = "10px"; // opcjonalne

// Dodaj przycisk do diva z przepisem
recipeDiv.appendChild(viewBtn);

    });

  } catch (error) {
    console.error("Błąd podczas ładowania recipes.json:", error);
  }
}

// Add to existing product.js
async function loadMatchingRecipes(productName) {
  try {
    const response = await fetch("recipes.json");
    const recipes = await response.json();
    const lowerName = productName.toLowerCase();

    const matching = recipes.filter(recipe =>
      recipe.title.toLowerCase().includes(lowerName) ||
      recipe.description.toLowerCase().includes(lowerName) ||
      recipe.instructions.some(instr => instr.toLowerCase().includes(lowerName))
    );

    const section = document.querySelector(".recipe-section");

    section.innerHTML = `<h2>Przepisy z produktem: ${productName}</h2>`;

    const recipeGrid = document.createElement("div");
    recipeGrid.classList.add("recipe-grid");

    // Wyświetl tylko dwa przepisy
    matching.slice(0, 2).forEach(recipe => {
      const recipeDiv = document.createElement("div");
      recipeDiv.classList.add("recipe-card");

      recipeDiv.innerHTML = `
        <h3>${recipe.title}</h3>
        <p>${recipe.description}</p>
        <p><strong>Czas:</strong> ${recipe.prep_time + recipe.cook_time} min</p>
        <p><strong>Porcje:</strong> ${recipe.servings}</p>
        <button class="btn-primary - view-recipe" data-id="${recipe.id}">Zobacz przepis</button>
      `;

      recipeGrid.appendChild(recipeDiv);
    });

    section.appendChild(recipeGrid);

    // Dodaj przycisk do pełnej wyszukiwarki przepisów
    const moreBtn = document.createElement("button");
    moreBtn.textContent = "Zobacz więcej przepisów";
    moreBtn.classList.add("btn-primary");
moreBtn.style.marginTop = "20px"; // opcjonalne

    moreBtn.style.marginTop = "20px";
    moreBtn.onclick = () => window.location.href = "recipes.html";

    section.appendChild(moreBtn);

    // Obsługa kliknięcia na "Zobacz przepis"
    section.querySelectorAll('.view-recipe').forEach(button => {
      button.addEventListener('click', (e) => {
        const recipeId = e.target.dataset.id;
        window.location.href = `recipe.html?id=${recipeId}`;
      });
    });

  } catch (error) {
    console.error("Błąd podczas ładowania przepisów:", error);
    document.querySelector(".recipe-section").innerHTML = `
      <h2>Błąd ładowania przepisów</h2>
      <p>${error.message}</p>
    `;
  }
}

