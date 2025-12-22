(async function protectDashboard() {
  try {
    const response = await fetch("http://localhost:5000/api/admin/session", {
      method: "GET",
      credentials: "include"
    });

    if (!response.ok) {
      window.location.href = "/adminlogin/index.html";
    }
  } catch (error) {
    console.error("Admin session check failed:", error);
    window.location.href = "/adminlogin/index.html";
  }
})();



// Gateway URL
const GATEWAY_URL = 'http://localhost:5000'; 

let allInventoryItems = [];
let currentPage = 1;
const itemsPerPage = 5;
let filteredItems = []; // items after search/filter

let paginationContainer;
let tableInfo;

document.addEventListener('DOMContentLoaded', () => {
    paginationContainer = document.getElementById('pagination');
    tableInfo = document.getElementById('table-info');
    loadInventory();
    setupModalListeners();
});

// ----------------------
// LOAD INVENTORY
// ----------------------
async function loadInventory() {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '<tr><td colspan="4">Loading data...</td></tr>';

    try {
        const response = await fetch(`${GATEWAY_URL}/api/inventory/all`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        allInventoryItems = data || [];
        filteredItems = [...allInventoryItems];

        initFilters(allInventoryItems);
        renderTablePage();
    } catch (error) {
        console.error('Error loading inventory:', error);
        tbody.innerHTML = `<tr><td colspan="4" style="color: red;">Error: ${error.message}</td></tr>`;
    }
}

// ----------------------
// FILTERS
// ----------------------
function initFilters(items) {
    const cafeSelect = document.getElementById('cafeFilter');
    const searchInput = document.getElementById('searchInput');

    if (!cafeSelect) return;

    const cafesMap = new Map();
    items.forEach(item => {
        if (item.cafe_id && item.cafe_name && !cafesMap.has(item.cafe_id)) {
            cafesMap.set(item.cafe_id, item.cafe_name);
        }
    });

    cafeSelect.innerHTML = '<option value="">All Cafes</option>';
    cafesMap.forEach((name, id) => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = name;
        cafeSelect.appendChild(opt);
    });

    cafeSelect.onchange = applyFilters;
    if (searchInput) searchInput.oninput = applyFilters;
}

function applyFilters() {
    const cafeSelect = document.getElementById('cafeFilter');
    const searchInput = document.getElementById('searchInput');

    const selectedCafeId = cafeSelect.value;
    const searchTerm = searchInput.value.toLowerCase().trim();

    filteredItems = allInventoryItems.filter(item => {
        let matchCafe = selectedCafeId ? String(item.cafe_id) === selectedCafeId : true;
        let matchSearch = searchTerm
            ? item.item_name.toLowerCase().includes(searchTerm) || item.cafe_name.toLowerCase().includes(searchTerm)
            : true;
        return matchCafe && matchSearch;
    });

    currentPage = 1; // reset to first page
    renderTablePage();
}

// ----------------------
// RENDER TABLE PAGE
// ----------------------
function renderTablePage() {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '';

    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredItems.length);
    const pageItems = filteredItems.slice(startIndex, endIndex);

    // Update table info
    if (tableInfo) {
        tableInfo.textContent =
            filteredItems.length === 0
                ? "No items found"
                : `Showing ${startIndex + 1}-${endIndex} of ${filteredItems.length} items`;
    }

    pageItems.forEach(item => {
        const row = tbody.insertRow();
        row.insertCell().textContent = item.item_name;
        row.insertCell().textContent = item.cafe_name;
        row.insertCell().textContent = item.stock_quantity;

        const restockCell = row.insertCell();
        const button = document.createElement('button');
        button.className = 'restock-btn';
        button.textContent = 'Restock';
        button.dataset.itemId = item.item_id;
        button.dataset.cafeId = item.cafe_id;
        button.dataset.itemName = item.item_name;
        button.onclick = () => openRestockModal(button.dataset);
        restockCell.appendChild(button);
    });

    renderLowStockAlerts();
    renderPagination(totalPages);
}

// ----------------------
// LOW STOCK ALERTS
// ----------------------
function renderLowStockAlerts() {
    const alertsContainer = document.getElementById('lowStockAlerts');
    alertsContainer.innerHTML = '';

    const lowStockItems = filteredItems.filter(item => item.is_low_stock);

    if (lowStockItems.length === 0) return;

    lowStockItems.forEach(item => {
        const alert = document.createElement('div');
        alert.className = 'alert-item';
        alert.textContent = `⚠️ Low stock for "${item.item_name}" at ${item.cafe_name}: ${item.stock_quantity}`;
        alertsContainer.appendChild(alert);
    });
}

// ----------------------
// PAGINATION
// ----------------------
function renderPagination(totalPages) {
    if (!paginationContainer) return;
    paginationContainer.innerHTML = '';

    if (totalPages <= 1) return;

    const controls = document.createElement('div');
    controls.className = 'pagination-controls';
    paginationContainer.appendChild(controls);

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '‹ Previous';
    prevBtn.className = 'page-btn';
    if (currentPage === 1) prevBtn.classList.add('disabled');
    else prevBtn.onclick = () => goToPage(currentPage - 1);
    controls.appendChild(prevBtn);

    const pages = [];
    pages.push(1);
    if (currentPage > 3) pages.push('...');
    for (let i = currentPage - 1; i <= currentPage + 1; i++) {
        if (i > 1 && i < totalPages) pages.push(i);
    }
    if (currentPage < totalPages - 2) pages.push('...');
    if (totalPages > 1) pages.push(totalPages);

    pages.forEach(p => {
        if (p === '...') {
            const span = document.createElement('span');
            span.textContent = '…';
            span.className = 'page-ellipsis';
            controls.appendChild(span);
        } else {
            const btn = document.createElement('button');
            btn.textContent = p;
            btn.className = 'page-btn';
            if (p === currentPage) btn.classList.add('active');
            else btn.onclick = () => goToPage(p);
            controls.appendChild(btn);
        }
    });

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next ›';
    nextBtn.className = 'page-btn';
    if (currentPage === totalPages) nextBtn.classList.add('disabled');
    else nextBtn.onclick = () => goToPage(currentPage + 1);
    controls.appendChild(nextBtn);
}

function goToPage(page) {
    currentPage = page;
    renderTablePage();
    document.querySelector(".table-card").scrollIntoView({ behavior: "smooth" });
}
window.goToPage = goToPage;

// ----------------------
// MODAL & RESTOCK
// ----------------------
// ----------------------
// MODAL & RESTOCK
// ----------------------
function setupModalListeners() {
    const modal = document.getElementById("restockModal");
    const closeBtn = modal.querySelector(".close-btn");
    const saveBtn = document.getElementById("saveRestockBtn");
    const quantityLabel = document.querySelector('label[for="restockQuantity"]');
    const quantityInput = document.getElementById("restockQuantity");
    const operationRadios = document.querySelectorAll('input[name="restockOperation"]');

    // Update label based on selected operation
    function updateQuantityLabel() {
        const operation = document.querySelector('input[name="restockOperation"]:checked')?.value;
        if (operation === 'add') {
            quantityLabel.textContent = "Quantity to Add:";
        } else {
            quantityLabel.textContent = "Quantity to Subtract:";
        }
        quantityInput.value = 0; // reset to 0 each time
    }

    operationRadios.forEach(radio => {
        radio.addEventListener('change', updateQuantityLabel);
    });

    updateQuantityLabel(); // initialize label on load

    closeBtn.onclick = () => {
        modal.style.display = "none";
        document.getElementById("modalMessage").textContent = '';
    }

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
            document.getElementById("modalMessage").textContent = '';
        }
    }

    document.getElementById("restockDate").valueAsDate = new Date();
    saveBtn.onclick = handleRestockSubmission;
}

function openRestockModal(data) {
    const modal = document.getElementById("restockModal");
    document.getElementById("modalItemId").value = data.itemId;
    document.getElementById("modalCafeId").value = data.cafeId;
    document.getElementById("modalItemName").textContent = data.itemName;
    document.getElementById("modalMessage").textContent = ''; 

    // Reset operation and quantity input
    document.querySelector('input[name="restockOperation"][value="add"]').checked = true;
    const quantityLabel = document.querySelector('label[for="restockQuantity"]');
    const quantityInput = document.getElementById("restockQuantity");
    quantityLabel.textContent = "Quantity to Add:";
    quantityInput.value = 0;

    modal.style.display = "flex";
}


async function handleRestockSubmission() {
    const saveBtn = document.getElementById("saveRestockBtn");
    const messageDisplay = document.getElementById("modalMessage");
    
    const itemId = document.getElementById("modalItemId").value;
    const cafeId = document.getElementById("modalCafeId").value;
    const quantityInput = document.getElementById("restockQuantity").value;
    const operation = document.querySelector('input[name="restockOperation"]:checked')?.value || 'add';
    const baseQuantity = parseInt(quantityInput, 10);
    const date = document.getElementById("restockDate").value;

    if (!baseQuantity || baseQuantity <= 0 || !date) {
        messageDisplay.textContent = 'Please enter a valid quantity and date.';
        messageDisplay.style.color = 'red';
        return;
    }

    const quantity = operation === 'subtract' ? -Math.abs(baseQuantity) : Math.abs(baseQuantity);
    messageDisplay.textContent = 'Saving...';
    messageDisplay.style.color = 'blue';
    saveBtn.disabled = true;

    try {
        const response = await fetch(`${GATEWAY_URL}/api/inventory/restock`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: itemId,
                cafe_id: cafeId,
                quantity_added: quantity,
                restock_date: date
            })
        });

        const result = await response.json();
        if (result.success) {
            messageDisplay.textContent = 'Restock successful!';
            messageDisplay.style.color = 'green';
            setTimeout(() => {
                document.getElementById("restockModal").style.display = "none";
                loadInventory();
            }, 1000);
        } else {
            throw new Error(result.message || 'Unknown server error.');
        }

    } catch (error) {
        messageDisplay.textContent = `Failed: ${error.message}`;
        messageDisplay.style.color = 'red';
    } finally {
        saveBtn.disabled = false;
    }
}
