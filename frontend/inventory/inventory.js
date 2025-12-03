// Résout dynamiquement l'URL de la Gateway (port configurable)
const DEFAULT_GATEWAY_PORT = '5000';

function resolveGatewayUrl() {
    if (window.GATEWAY_URL && window.GATEWAY_URL.trim()) {
        return window.GATEWAY_URL.trim().replace(/\/$/, '');
    }

    const rawProtocol = window.location.protocol || 'http:';
    const protocol = rawProtocol.startsWith('http') ? rawProtocol : 'http:';
    const hostname = window.location.hostname || 'localhost';
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
    const port = isLocalhost
        ? DEFAULT_GATEWAY_PORT
        : (window.__GATEWAY_PORT__ || DEFAULT_GATEWAY_PORT);

    return `${protocol}//${hostname}${port ? `:${port}` : ''}`;
}

const GATEWAY_URL = resolveGatewayUrl();

let allInventoryItems = [];

document.addEventListener('DOMContentLoaded', () => {
    // Initialisation
    loadInventory();
    setupModalListeners();
});

// ----------------------
// GESTION DU CHARGEMENT DES DONNÉES
// ----------------------

async function loadInventory() {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '<tr><td colspan="4">Chargement des données...</td></tr>';

    try {
        // 1. Appel de l'endpoint API de la Gateway
        const response = await fetch(`${GATEWAY_URL}/api/inventory/all`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();

        // Stocker toutes les données pour permettre les filtres
        allInventoryItems = data || [];

        // Initialiser les filtres (cafés + recherche)
        initFilters(allInventoryItems);

        // 2. Affichage des données
        renderTable(allInventoryItems);

    } catch (error) {
        console.error('Erreur lors du chargement de l\'inventaire:', error);
        tbody.innerHTML = `<tr><td colspan="4" style="color: red;">Erreur: ${error.message}. Vérifiez la Gateway et le Service Inventaire (port 5006).</td></tr>`;
    }
}

function initFilters(items) {
    const cafeSelect = document.getElementById('cafeFilter');
    const searchInput = document.getElementById('searchInput');

    if (!cafeSelect) return;

    // Remplir le dropdown des cafés avec les valeurs uniques
    const cafesMap = new Map();
    (items || []).forEach(item => {
        if (item.cafe_id && item.cafe_name && !cafesMap.has(item.cafe_id)) {
            cafesMap.set(item.cafe_id, item.cafe_name);
        }
    });

    // Réinitialiser les options
    cafeSelect.innerHTML = '<option value="">Tous les cafés</option>';
    cafesMap.forEach((name, id) => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = name;
        cafeSelect.appendChild(opt);
    });

    // (Ré)attacher les écouteurs une seule fois
    cafeSelect.onchange = applyFilters;
    if (searchInput) {
        searchInput.oninput = applyFilters;
    }
}

function applyFilters() {
    const cafeSelect = document.getElementById('cafeFilter');
    const searchInput = document.getElementById('searchInput');

    const selectedCafeId = cafeSelect ? cafeSelect.value : '';
    const searchTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();

    let filtered = allInventoryItems || [];

    if (selectedCafeId) {
        filtered = filtered.filter(item => String(item.cafe_id) === String(selectedCafeId));
    }

    if (searchTerm) {
        filtered = filtered.filter(item =>
            (item.item_name && item.item_name.toLowerCase().includes(searchTerm)) ||
            (item.cafe_name && item.cafe_name.toLowerCase().includes(searchTerm))
        );
    }

    renderTable(filtered);
}

function renderTable(items) {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = ''; // Nettoyer le contenu existant

    items.forEach(item => {
        const row = tbody.insertRow();
        
        // Mettre en évidence la ligne si le stock est bas
        if (item.is_low_stock) {
            row.classList.add('low-stock');
        }

        row.insertCell().textContent = item.item_name;
        row.insertCell().textContent = item.cafe_name;
        row.insertCell().textContent = item.stock_quantity;
        
        // Cellule du bouton Restock
        const restockCell = row.insertCell();
        const button = document.createElement('button');
        button.className = 'restock-btn';
        button.textContent = 'Restock';
        
        // Attacher les IDs nécessaires au bouton pour le modal
        button.dataset.itemId = item.item_id;
        button.dataset.cafeId = item.cafe_id;
        button.dataset.itemName = item.item_name;
        
        button.onclick = () => openRestockModal(button.dataset);
        restockCell.appendChild(button);
    });
}

// ----------------------
// GESTION DU MODAL ET DU REAPPROVISIONNEMENT
// ----------------------

function setupModalListeners() {
    const modal = document.getElementById("restockModal");
    const closeBtn = modal.querySelector(".close-btn");
    const saveBtn = document.getElementById("saveRestockBtn");
    
    // Fermer le modal en cliquant sur 'x'
    closeBtn.onclick = () => {
        modal.style.display = "none";
        document.getElementById("modalMessage").textContent = ''; // Vider le message
    }
    
    // Fermer le modal en cliquant en dehors
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
            document.getElementById("modalMessage").textContent = '';
        }
    }
    
    // Définir la date par défaut du champ Date
    document.getElementById("restockDate").valueAsDate = new Date();
    
    // Événement pour le bouton "Enregistrer Réapprovisionnement"
    saveBtn.onclick = handleRestockSubmission;
}

function openRestockModal(data) {
    const modal = document.getElementById("restockModal");
    
    // Remplir les champs cachés et le titre
    document.getElementById("modalItemId").value = data.itemId;
    document.getElementById("modalCafeId").value = data.cafeId;
    document.getElementById("modalItemName").textContent = data.itemName;
    document.getElementById("modalMessage").textContent = ''; 
    
    modal.style.display = "block";
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
        messageDisplay.textContent = 'Veuillez entrer une quantité valide et une date.';
        messageDisplay.style.color = 'red';
        return;
    }

    // Si on choisit "diminuer la quantité", on envoie une valeur négative
    const quantity = operation === 'subtract'
        ? -Math.abs(baseQuantity)
        : Math.abs(baseQuantity);

    messageDisplay.textContent = 'Enregistrement...';
    messageDisplay.style.color = 'blue';
    saveBtn.disabled = true;

    try {
        // 3. Envoi des données de réapprovisionnement à la Gateway (POST)
        const response = await fetch(`${GATEWAY_URL}/api/inventory/restock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId,
                cafe_id: cafeId,
                quantity_added: quantity,
                restock_date: date
            })
        });

        const result = await response.json();

        if (result.success) {
            messageDisplay.textContent = 'Réapprovisionnement réussi !';
            messageDisplay.style.color = 'green';
            // Recharger le tableau pour voir la nouvelle quantité
            setTimeout(() => {
                document.getElementById("restockModal").style.display = "none";
                loadInventory();
            }, 1000);
        } else {
            throw new Error(result.message || 'Erreur inconnue du serveur.');
        }

    } catch (error) {
        messageDisplay.textContent = `Échec: ${error.message}`;
        messageDisplay.style.color = 'red';
    } finally {
        saveBtn.disabled = false;
    }
}