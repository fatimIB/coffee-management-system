let menuItems = [];
let selectedItems = {}; // {item_id: {item, quantity}}

const GATEWAY_URL = 'http://localhost:5000';

let cafeId = null;

// Check session on page load
document.addEventListener('DOMContentLoaded', async () => {
    await checkSession();
    await loadMenuItems();
});

async function checkSession() {
    try {
        const response = await fetch(`${GATEWAY_URL}/api/session`, {
            credentials: 'include' // 🔥 REQUIRED
        });

        const data = await response.json();

        if (!data.authenticated) {
            window.location.href = '../login/index.html';
            return;
        }

        cafeId = data.cafe_id; // ✅ REAL SOURCE OF TRUTH

    } catch (error) {
        console.error('Session check failed:', error);
        window.location.href = '../login/index.html';
    }
}

// Load menu items on page load
document.addEventListener('DOMContentLoaded', () => {
    loadMenuItems();
});

async function loadMenuItems() {
    try {
        const response = await fetch(`${GATEWAY_URL}/menu/items`);
        const data = await response.json();
        menuItems = data.items || [];
        displayMenuItems();
    } catch (error) {
        console.error('Error loading menu items:', error);
        showMessage('Error loading menu items', 'error');
    }
}

function displayMenuItems() {
    const container = document.getElementById('menu-items');
    container.innerHTML = '';

    menuItems.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'menu-item-card';
        itemCard.innerHTML = `
            <h3>${item.name}</h3>
            <p class="category">${item.category}</p>
            <p class="price">${item.price} MAD</p>
            <div class="quantity-controls">
                <button onclick="decreaseQuantity(${item.id})" class="qty-btn">-</button>
                <span id="qty-${item.id}" class="quantity">0</span>
                <button onclick="increaseQuantity(${item.id})" class="qty-btn">+</button>
            </div>
        `;
        container.appendChild(itemCard);
    });
}

function increaseQuantity(itemId) {
    const item = menuItems.find(m => m.id === itemId);
    if (!item) return;

    if (!selectedItems[itemId]) {
        selectedItems[itemId] = { item, quantity: 0 };
    }
    selectedItems[itemId].quantity++;
    updateQuantityDisplay(itemId);
    updateCart();
}

function decreaseQuantity(itemId) {
    if (!selectedItems[itemId] || selectedItems[itemId].quantity <= 0) return;
    
    selectedItems[itemId].quantity--;
    if (selectedItems[itemId].quantity === 0) {
        delete selectedItems[itemId];
    }
    updateQuantityDisplay(itemId);
    updateCart();
}

function updateQuantityDisplay(itemId) {
    const qtyElement = document.getElementById(`qty-${itemId}`);
    if (qtyElement) {
        qtyElement.textContent = selectedItems[itemId]?.quantity || 0;
    }
}

function updateCart() {
    const cartContainer = document.getElementById('cart-items');
    const totalElement = document.getElementById('total-price');
    const confirmBtn = document.getElementById('confirm-order-btn');

    cartContainer.innerHTML = '';

    let total = 0;
    const itemIds = Object.keys(selectedItems);

    if (itemIds.length === 0) {
        cartContainer.innerHTML = '<p class="empty-cart">No items selected</p>';
        totalElement.textContent = '0.00';
        confirmBtn.disabled = true;
        return;
    }

    itemIds.forEach(itemId => {
        const { item, quantity } = selectedItems[itemId];
        const itemTotal = item.price * quantity;
        total += itemTotal;

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <span class="cart-item-name">${item.name}</span>
                <span class="cart-item-qty">x${quantity}</span>
            </div>
            <span class="cart-item-price">${itemTotal.toFixed(2)} MAD</span>
        `;
        cartContainer.appendChild(cartItem);
    });

    totalElement.textContent = total.toFixed(2);
    confirmBtn.disabled = false;
}

document.getElementById('confirm-order-btn').addEventListener('click', async () => {
    if (Object.keys(selectedItems).length === 0) {
        showMessage('Please select at least one item', 'error');
        return;
    }

    // Prepare order items
    const items = Object.values(selectedItems).map(({ item, quantity }) => ({
        item_id: item.id.toString(),
        quantity: quantity,
        price: item.price
    }));

    try {
        const response = await fetch(`${GATEWAY_URL}/orders/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 🔥 REQUIRED
            body: JSON.stringify({
                cafe_id: cafeId,
                items: items
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage(`Order created successfully!`, 'success');
            // Clear cart
            selectedItems = {};
            menuItems.forEach(item => {
                updateQuantityDisplay(item.id);
            });
            updateCart();
        } else {
            showMessage(data.message || 'Error creating order', 'error');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showMessage('Error creating order: ' + error.message, 'error');
    }
});

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}


document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${GATEWAY_URL}/api/userlogout`, {
            method: 'POST',
            credentials: 'include'
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = '../login/index.html'; // redirect to café login page
        } else {
            showMessage('Logout failed', 'error');
        }
    } catch (error) {
        console.error('Error logging out:', error);
        showMessage('Error logging out', 'error');
    }
});
