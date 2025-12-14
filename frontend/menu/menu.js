// Use Gateway URL for API
const API = "http://localhost:5000/api/menu";

let editId = null;
let currentPage = 1;
const itemsPerPage = 5;

let menuTable,
  addBtn,
  nameInput,
  categoryInput,
  priceInput,
  searchInput,
  paginationContainer,
  tableInfo;

document.addEventListener("DOMContentLoaded", () => {
  menuTable = document.getElementById("menu-table");
  addBtn = document.getElementById("add-btn");
  nameInput = document.getElementById("name");
  categoryInput = document.getElementById("category");
  priceInput = document.getElementById("price");
  searchInput = document.getElementById("search");
  paginationContainer = document.getElementById("pagination");
  tableInfo = document.getElementById("table-info");

  if (
    !menuTable ||
    !addBtn ||
    !nameInput ||
    !categoryInput ||
    !priceInput ||
    !searchInput ||
    !paginationContainer ||
    !tableInfo
  ) {
    console.error("Error: some DOM elements are missing");
    return;
  }

  loadMenu();

  searchInput.addEventListener("input", (e) => {
    currentPage = 1;
    loadMenu(e.target.value);
  });

  addBtn.addEventListener("click", handleAddUpdate);
});

async function loadMenu(search = "") {
  if (!menuTable) return;

  const url = search ? `${API}?search=${encodeURIComponent(search)}` : API;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);

    const data = await res.json();
    window.allMenuData = data;

    const totalPages = Math.ceil(data.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = data.slice(startIndex, endIndex);

    tableInfo.textContent =
      data.length === 0
        ? "No items found"
        : `Showing ${startIndex + 1}-${Math.min(
            endIndex,
            data.length
          )} of ${data.length} items`;

    menuTable.innerHTML = "";
    paginatedData.forEach((item, idx) => {
      const globalIndex = startIndex + idx;
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.category}</td>
                <td>${item.price.toFixed(2)} DH</td>
                <td>
                    <button class="edit-btn" data-index="${globalIndex}">Edit</button>
                    <button class="delete-btn" data-id="${item.id}" data-name="${item.name}">Delete</button>
                </td>
            `;
      menuTable.appendChild(row);
    });

    document.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", () =>
        editItem(window.allMenuData[parseInt(btn.dataset.index)])
      );
    });
    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () =>
        openDeleteModal(parseInt(btn.dataset.id))
      );
    });

    renderPagination(totalPages);
  } catch (err) {
    console.error("Error loading menu:", err);
    showMessage(`Error: ${err.message}`, "error");
    menuTable.innerHTML = `<tr><td colspan="4" style="color:red;text-align:center;">Error: ${err.message}</td></tr>`;
  }
}

function editItem(item) {
  editId = item.id;
  nameInput.value = item.name;
  categoryInput.value = item.category;
  priceInput.value = item.price;
  addBtn.innerText = "UPDATE";
  addBtn.scrollIntoView({ behavior: "smooth" });
}

async function handleAddUpdate() {
  const name = nameInput.value.trim();
  const category = categoryInput.value;
  const price = parseFloat(priceInput.value);
  if (!name || !category || isNaN(price) || price <= 0) {
    showMessage("Please fill in all fields with valid values", "error");
    return;
  }

  try {
    if (editId) {
      await fetch(`${API}/update`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: editId, name, category, price }),
      });
      showMessage("Item updated successfully", "success");
      editId = null;
      addBtn.innerText = "ADD";
    } else {
      await fetch(`${API}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, category, price }),
      });
      showMessage("Item added successfully", "success");
    }
    nameInput.value = categoryInput.value = priceInput.value = "";
    loadMenu(searchInput.value);
  } catch (err) {
    console.error(err);
    showMessage(`Error: ${err.message}`, "error");
  }
}

let deleteId = null;

function openDeleteModal(id) {
  deleteId = id;
  document.getElementById("delete-modal").style.display = "flex";
}

document.getElementById("cancel-delete").addEventListener("click", () => {
  deleteId = null;
  document.getElementById("delete-modal").style.display = "none";
});

document.getElementById("confirm-delete").addEventListener("click", () => {
  if (deleteId !== null) {
    deleteItem(deleteId);
  }
  deleteId = null;
  document.getElementById("delete-modal").style.display = "none";
});

async function deleteItem(id) {
  try {
    const res = await fetch(`${API}/delete`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    if (!res.ok) throw new Error("Error deleting item");
    showMessage("Item deleted successfully", "success");
    loadMenu(searchInput.value);
  } catch (err) {
    console.error(err);
    showMessage(`Error: ${err.message}`, "error");
  }
}

function renderPagination(totalPages) {
  if (!paginationContainer) return;
  if (totalPages <= 1) {
    paginationContainer.innerHTML = "";
    return;
  }

  let html = `<div class="pagination-controls">`;

  // PREVIOUS BUTTON
  html += currentPage > 1
    ? `<button class="page-btn" onclick="goToPage(${currentPage - 1})">‹ Previous</button>`
    : `<button class="page-btn disabled">‹ Previous</button>`;

  // PAGE NUMBERS
  for (let i = 1; i <= totalPages; i++) {
    html += i === currentPage
      ? `<button class="page-btn active">${i}</button>`
      : `<button class="page-btn" onclick="goToPage(${i})">${i}</button>`;
  }

  // NEXT BUTTON
  html += currentPage < totalPages
    ? `<button class="page-btn" onclick="goToPage(${currentPage + 1})">Next ›</button>`
    : `<button class="page-btn disabled">Next ›</button>`;

  html += `</div>`;

  paginationContainer.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  loadMenu(searchInput.value);
  document.querySelector(".table-card").scrollIntoView({ behavior: "smooth" });
}
window.goToPage = goToPage;

// --- Success/Error Popup Function ---
function showMessage(message, type) {
  const messageDiv = document.createElement('div');
  messageDiv.textContent = message;
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    z-index: 1000;
    transition: opacity 0.3s;
    background-color: ${type === 'success' ? '#28a745' : '#dc3545'};
  `;
  document.body.appendChild(messageDiv);
  setTimeout(() => {
    messageDiv.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(messageDiv)) document.body.removeChild(messageDiv);
    }, 300);
  }, 3000);
}
