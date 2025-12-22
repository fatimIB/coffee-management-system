// ---------------- PROTECT DASHBOARD ----------------
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

// ---------------- SETTINGS FORM ----------------
const settingsForm = document.getElementById('settings-form');
settingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username && !password) {
        showMessage("Please enter a new username or password", "error");
        return;
    }

    // Show confirmation modal before updating
    openModal("Are you sure you want to update your settings?", async () => {
        try {
            const res = await fetch('http://localhost:5000/api/admin/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            showMessage(data.message, data.success ? "success" : "error");

            // Clear inputs after successful update
            if (data.success) {
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
            }
        } catch (err) {
            console.error(err);
            showMessage('Error updating settings', "error");
        }
    });
});

// ---------------- MODAL ----------------
function openModal(message, onConfirm) {
    let modal = document.getElementById("confirm-modal");
    if (!modal) {
        // Create modal dynamically if it doesn't exist
        modal = document.createElement("div");
        modal.id = "confirm-modal";
        modal.className = "modal-overlay";
        modal.innerHTML = `
            <div class="modal-box">
                <p id="modal-message">${message}</p>
                <div class="modal-actions">
                    <button id="cancel-modal" class="modal-btn cancel">Cancel</button>
                    <button id="confirm-modal-btn" class="modal-btn confirm">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Cancel button
        document.getElementById("cancel-modal").addEventListener("click", () => {
            modal.style.display = "none";
        });

        // Confirm button
        document.getElementById("confirm-modal-btn").addEventListener("click", () => {
            modal.style.display = "none";
            if (typeof onConfirm === "function") onConfirm();
        });
    }

    // Update message and show modal
    document.getElementById("modal-message").textContent = message;
    modal.style.display = "flex";
}

// ---------------- SUCCESS / ERROR MESSAGE ----------------
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
