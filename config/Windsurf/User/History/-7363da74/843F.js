const script = (() => {
  let marketItems = [];
  let orderList = [];
  let total = 0;

  const themeToggleButton = document.getElementById("theme-toggle");
  const productList = document.getElementById("product-list");
  const orderListElement = document.getElementById("order-list");
  const totalElement = document.getElementById("total");
  const successScreen = document.getElementById("success-screen");
  const backToMainButton = document.getElementById("back-to-main");
  const cancelEditButton = document.getElementById("cancel-edit");

  function initializeLogin() {
    const adminButton = document.getElementById("admin-button");
    const loginCancel = document.getElementById("login-cancel");
    const loginSubmit = document.getElementById("login-submit");

    if (adminButton) {
      adminButton.addEventListener("click", () => {
        document.getElementById("admin-login").style.display = "block";
      });
    }

    if (loginCancel) {
      loginCancel.addEventListener("click", () => {
        document.getElementById("admin-login").style.display = "none";
        document.getElementById("admin-username").value = "";
        document.getElementById("admin-password").value = "";
        document.getElementById("login-error").style.display = "none";
      });
    }

    if (loginSubmit) {
      loginSubmit.addEventListener("click", async () => {
        const username = document.getElementById("admin-username").value;
        const password = document.getElementById("admin-password").value;

        try {
          const response = await fetch("/api/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
          });

          if (response.ok) {
            window.location.href = "/admin";
          } else {
            document.getElementById("login-error").style.display = "block";
          }
        } catch (error) {
          document.getElementById("login-error").style.display = "block";
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeLogin);
  } else {
    initializeLogin();
  }

  if (backToMainButton) {
    backToMainButton.addEventListener("click", () => {
      window.location.href = "index.html";
    });
  }

  if (cancelEditButton) {
    cancelEditButton.addEventListener("click", cancelEdit);
  }

  function cancelEdit() {
    const nameInput = document.getElementById("item-name");
    const priceInput = document.getElementById("item-price");
    const categoryInput = document.getElementById("item-category");
    const addItemButton = document.getElementById("add-item");
    const updateItemButton = document.getElementById("update-item");
    const cancelEditButton = document.getElementById("cancel-edit");

    if (nameInput) nameInput.value = "";
    if (priceInput) priceInput.value = "";
    if (categoryInput) categoryInput.value = "";

    if (addItemButton) addItemButton.style.display = "block";
    if (updateItemButton) updateItemButton.style.display = "none";
    if (cancelEditButton) cancelEditButton.style.display = "none";

    window.selectedItemId = null;
  }

  async function fetchItems() {
    try {
      const response = await fetch("http://localhost:3000/api/items");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      marketItems = data.items;

      if (window.location.pathname.includes("/admin")) {
        loadAdminView();
      } else if (window.location.pathname.includes("/customer")) {
        loadCustomerView();
      }
    } catch (error) {
      console.error("Error loading items:", error);
      marketItems = [
        { id: 1, name: "Apple", price: 6.71, category: "Fruits" },
        { id: 2, name: "Banana", price: 1.11, category: "Fruits" },
        { id: 3, name: "Red meat", price: 8.0, category: "Meat" },
        { id: 4, name: "Chicken", price: 6.0, category: "Meat" },
        { id: 5, name: "Cucumber", price: 16.5, category: "Vegetables" },
        { id: 6, name: "Carrot", price: 2.87, category: "Vegetables" },
      ];
      if (window.location.pathname.includes("/admin")) {
        loadAdminView();
      } else if (window.location.pathname.includes("/customer")) {
        loadCustomerView();
      }
    }
  }

  const currentTheme = localStorage.getItem("theme") || "dark";
  document.body.classList.add(currentTheme);
  updateTheme();

  if (themeToggleButton) {
    themeToggleButton.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      document.body.classList.toggle("light");
      localStorage.setItem(
        "theme",
        document.body.classList.contains("dark") ? "dark" : "light",
      );
      updateTheme();
    });
  }

  function updateTheme() {
    if (themeToggleButton) {
      themeToggleButton.textContent = document.body.classList.contains("dark")
        ? "☀️"
        : "🌙";
    }
    const themeClass = document.body.classList.contains("dark")
      ? "dark"
      : "light";
    document
      .querySelectorAll(
        "#product-list, #order-list, input, button, #admin-panel, #admin-item-list",
      )
      .forEach((element) => {
        element.classList.remove("dark", "light");
        element.classList.add(themeClass);
      });
  }

  function loadCustomerView() {
    console.log("Loading customer view with items:", marketItems);
    if (!productList) return;

    productList.innerHTML = "";
    marketItems.forEach((item) => {
      const listItem = document.createElement("li");
      listItem.textContent = `${item.name} - $${item.price.toFixed(2)}`;
      const addButton = document.createElement("button");
      addButton.textContent = "Add";
      addButton.addEventListener("click", () => {
        orderList.push(item);
        updateOrderList();
        showFeedback("Item added to cart!");
      });
      listItem.appendChild(addButton);
      productList.appendChild(listItem);
    });

    const searchInput = document.getElementById("search-customer");
    if (searchInput) {
      searchInput.addEventListener("input", () =>
        filterItems(searchInput.value, productList),
      );
    }

    const categoryFilter = document.getElementById("category-filter");
    if (categoryFilter) {
      categoryFilter.addEventListener("change", () => {
        const searchTerm = document.getElementById("search-customer").value;
        const selectedCategory = categoryFilter.value;

        if (!productList) return;

        productList.innerHTML = "";
        marketItems.forEach((item) => {
          if (
            (selectedCategory === "" || item.category === selectedCategory) &&
            item.name.toLowerCase().includes(searchTerm.toLowerCase())
          ) {
            const listItem = document.createElement("li");
            listItem.textContent = `${item.name} - $${item.price.toFixed(2)}`;
            const addButton = document.createElement("button");
            addButton.textContent = "Add";
            addButton.addEventListener("click", () => {
              orderList.push(item);
              updateOrderList();
              showFeedback("Item added to cart!");
            });
            listItem.appendChild(addButton);
            productList.appendChild(listItem);
          }
        });
      });
    }

    updateOrderList();
  }

  function updateOrderList() {
    if (!orderListElement) return;

    orderListElement.innerHTML = "";
    total = 0;

    if (orderList.length === 0) {
      const emptyMessage = document.createElement("li");
      emptyMessage.textContent =
        "Your cart is empty! Click 'Add' on any product to start shopping.";
      emptyMessage.style.fontStyle = "italic";
      emptyMessage.style.color = "#666";
      orderListElement.appendChild(emptyMessage);
    } else {
      orderList.forEach((item, index) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
                    ${item.name} - $${item.price.toFixed(2)}
                    <button onclick="script.removeFromCart(${index})" style="background-color: #f44336;">Remove</button>
                `;
        orderListElement.appendChild(listItem);
        total += item.price;
      });
    }

    if (totalElement) {
      totalElement.textContent = total.toFixed(2);
    }
  }

  function loadAdminView() {
    const itemsList = document.getElementById("items-list");
    const addItemButton = document.getElementById("add-item");
    const updateItemButton = document.getElementById("update-item");
    const cancelEditButton = document.getElementById("cancel-edit");

    function refreshItemsList() {
      if (!itemsList) return;

      itemsList.innerHTML = "";
      marketItems.forEach((item) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${item.name} - $${item.price.toFixed(2)} (${item.category})</span>
                <div>
                    <button onclick="script.editItem(${item.id})">Edit</button>
                    <button onclick="script.deleteItem(${item.id})" style="background-color: #f44336;">Delete</button>
                </div>
            </div>
        `;
        itemsList.appendChild(li);
      });
      updateStats();
    }

    function updateStats() {
      const totalItemsElement = document.getElementById("total-items");
      const totalValueElement = document.getElementById("total-value");

      if (totalItemsElement && totalValueElement) {
        totalItemsElement.textContent = marketItems.length;
        const totalValue = marketItems.reduce(
          (sum, item) => sum + item.price,
          0,
        );
        totalValueElement.textContent = totalValue.toFixed(2);
      }
    }

    if (addItemButton) {
      addItemButton.addEventListener("click", async () => {
        const name = document.getElementById("item-name").value;
        const price = parseFloat(document.getElementById("item-price").value);
        const category = document.getElementById("item-category").value;

        if (name && price && category) {
          try {
            const response = await fetch("http://localhost:3000/api/items", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ name, price, category }),
            });

            if (!response.ok) throw new Error("Failed to add item");

            await fetchItems();
            clearForm();
            showFeedback("Item added successfully!");
          } catch (error) {
            showFeedback("Error adding item", true);
          }
        }
      });
    }

    function clearForm() {
      const nameInput = document.getElementById("item-name");
      const priceInput = document.getElementById("item-price");
      const categoryInput = document.getElementById("item-category");

      if (nameInput) nameInput.value = "";
      if (priceInput) priceInput.value = "";
      if (categoryInput) categoryInput.value = "";

      if (addItemButton) addItemButton.style.display = "block";
      if (updateItemButton) updateItemButton.style.display = "none";
      if (cancelEditButton) cancelEditButton.style.display = "none";
    }

    refreshItemsList();

    if (updateItemButton) {
      updateItemButton.addEventListener("click", async () => {
        if (window.selectedItemId) {
          try {
            const response = await fetch(
              `http://localhost:3000/api/items/${window.selectedItemId}`,
              {
                method: "PUT",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  name: document.getElementById("item-name").value,
                  price: parseFloat(
                    document.getElementById("item-price").value,
                  ),
                  category: document.getElementById("item-category").value,
                }),
              },
            );

            if (!response.ok) throw new Error("Failed to update item");

            await fetchItems();
            document.getElementById("item-name").value = "";
            document.getElementById("item-price").value = "";
            document.getElementById("item-category").value = "";
            document.getElementById("add-item").style.display = "block";
            document.getElementById("update-item").style.display = "none";
            document.getElementById("cancel-edit").style.display = "none";
            window.selectedItemId = null;
            showFeedback("Item updated successfully!");
          } catch (error) {
            showFeedback("Error updating item", true);
            console.error("Error:", error);
          }
        }
      });
    }

    window.script = {
      ...window.script,
      editItem: (id) => {
        const item = marketItems.find((item) => item.id === id);
        if (item) {
          document.getElementById("item-name").value = item.name;
          document.getElementById("item-price").value = item.price;
          document.getElementById("item-category").value = item.category;
          window.selectedItemId = id;
          addItemButton.style.display = "none";
          updateItemButton.style.display = "block";
          cancelEditButton.style.display = "block";
        }
      },

      deleteItem: async (id) => {
        if (confirm("Are you sure you want to delete this item?")) {
          try {
            const response = await fetch(
              `http://localhost:3000/api/items/${id}`,
              {
                method: "DELETE",
              },
            );

            if (!response.ok) throw new Error("Failed to delete item");

            await fetchItems();
            showFeedback("Item deleted successfully!");
          } catch (error) {
            showFeedback("Error deleting item", true);
          }
        }
      },
    };

    const searchInput = document.getElementById("search-admin");
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        filterItems(searchInput.value, itemsList);
      });
    }
  }

  function filterItems(searchTerm, listElement) {
    if (!listElement) return;

    const selectedCategory =
      document.getElementById("category-filter")?.value || "";

    const listItems = marketItems.filter((item) => {
      const matchesSearch = item.name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesCategory =
        selectedCategory === "" || item.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });

    listElement.innerHTML = "";
    listItems.forEach((item) => {
      const listItem = document.createElement("li");
      listItem.textContent = `${item.name} - $${item.price.toFixed(2)}`;
      const addButton = document.createElement("button");
      addButton.textContent = "Add";
      addButton.addEventListener("click", () => {
        orderList.push(item);
        updateOrderList();
        showFeedback("Item added to cart!");
      });
      listItem.appendChild(addButton);
      listElement.appendChild(listItem);
    });
  }

  function showFeedback(message, isError = false) {
    const feedbackEl = document.getElementById("feedback-message");
    if (feedbackEl) {
      feedbackEl.textContent = message;
      feedbackEl.style.backgroundColor = isError ? "#f44336" : "#4caf50";
      feedbackEl.style.display = "block";

      setTimeout(() => {
        feedbackEl.style.display = "none";
      }, 3000);
    }
  }

  function checkout() {
    const overlay = document.querySelector(".overlay");
    if (overlay) overlay.style.display = "block";
    if (successScreen) {
      successScreen.style.display = "block";
    }
    const successMessage = document.getElementById("success-message");
    if (successMessage) {
      successMessage.style.display = "block";
    }

    setTimeout(() => {
      orderList = [];
      if (orderListElement) {
        orderListElement.innerHTML = "";
      }
      if (totalElement) {
        totalElement.textContent = "0.00";
      }
    }, 2000);
  }

  function backToShopping() {
    const overlay = document.querySelector(".overlay");
    if (overlay) overlay.style.display = "none";
    if (successScreen) {
      successScreen.style.display = "none";
    }
    orderList = [];
    updateOrderList();
    loadCustomerView();
  }

  const checkoutButton = document.getElementById("checkout");
  if (checkoutButton) {
    checkoutButton.addEventListener("click", checkout);
  }

  const backToShoppingButton = document.getElementById("back-to-shopping");
  if (backToShoppingButton) {
    backToShoppingButton.addEventListener("click", backToShopping);
  }

  fetchItems();

  return {
    loadCustomerView,
    loadAdminView,
    fetchItems,
    removeFromCart: (index) => {
      orderList.splice(index, 1);
      updateOrderList();
      showFeedback("Item removed from cart!");
    },
    editItem: (id) => {
      const item = marketItems.find((item) => item.id === id);
      if (item) {
        document.getElementById("item-name").value = item.name;
        document.getElementById("item-price").value = item.price;
        document.getElementById("item-category").value = item.category;
        document.getElementById("add-item").style.display = "none";
        document.getElementById("update-item").style.display = "block";
        document.getElementById("cancel-edit").style.display = "block";
        window.selectedItemId = id;
      }
    },
    deleteItem: async (id) => {
      if (confirm("Are you sure you want to delete this item?")) {
        try {
          const response = await fetch(
            `http://localhost:3000/api/items/${id}`,
            {
              method: "DELETE",
            },
          );

          if (!response.ok) throw new Error("Failed to delete item");

          await fetchItems();
          showFeedback("Item deleted successfully!");
        } catch (error) {
          showFeedback("Error deleting item", true);
          console.error("Error:", error);
        }
      }
    },
    cancelEdit,
    initializeLogin,
  };
})();
