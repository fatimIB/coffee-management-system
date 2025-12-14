class CafeManager {
    constructor() {
        this.cafes = [];
        this.isEditing = false;
        this.currentEditId = null;
        this.deleteId = null;
        this.initializeEventListeners();
        this.loadCafes();
    }

    initializeEventListeners() {
        document.getElementById('cafe-form').addEventListener('submit', (e) => this.handleSubmit(e));
        document.getElementById('cancel-btn').addEventListener('click', () => this.cancelEdit());

        // Modal buttons
        document.getElementById("cancel-delete").addEventListener("click", () => {
            this.deleteId = null;
            document.getElementById("delete-modal").style.display = "none";
        });

        document.getElementById("confirm-delete").addEventListener("click", async () => {
            if (this.deleteId !== null) {
                await this.deleteCafe(this.deleteId);
            }
            this.deleteId = null;
            document.getElementById("delete-modal").style.display = "none";
        });
    }

    // ---------------- LOAD CAFES ----------------
    async loadCafes() {
        try {
            const response = await fetch('http://localhost:5000/api/cafes', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.success) {
                this.cafes = data.cafes;
                this.renderCafes();
            } else {
                throw new Error(data.error || 'Error loading cafes');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Error loading cafes', 'error');
        }
    }

    // ---------------- SUBMIT ----------------
    async handleSubmit(e) {
        e.preventDefault();
        const cafeData = {
            name: document.getElementById('nom').value,
            location: document.getElementById('localisation').value,
            access_code: document.getElementById('code-acces').value
        };
    
        try {
            let response, data;
    
            if (this.isEditing) {
                response = await fetch(`http://localhost:5000/api/cafes/${this.currentEditId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(cafeData)
                });
                data = await response.json();
                if (data.success) {
                    this.showMessage('Cafe updated successfully', 'success');

                    // Instant update in table
                    const index = this.cafes.findIndex(c => c.id === this.currentEditId);
                    if (index !== -1) {
                        this.cafes[index] = { ...this.cafes[index], ...cafeData };
                        this.renderCafes();
                    }
                } else {
                    throw new Error(data.error || 'Error updating cafe');
                }
            } else {
                // Add new cafe
                response = await fetch('http://localhost:5000/api/cafes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(cafeData)
                });
                data = await response.json();
                if (data.success) {
                    this.showMessage('Cafe added successfully', 'success');

                    // Instant add to table
                    this.cafes.push(data.cafe);
                    this.renderCafes();
                } else {
                    throw new Error(data.error || 'Error adding cafe');
                }
            }
    
            this.resetForm();
    
        } catch (error) {
            console.error('Error:', error);
            this.showMessage(error.message || 'Error saving cafe', 'error');
        }
    }

    // ---------------- EDIT ----------------
    editCafe(cafe) {
        this.isEditing = true;
        this.currentEditId = cafe.id;

        document.getElementById('nom').value = cafe.name;
        document.getElementById('localisation').value = cafe.location;
        document.getElementById('code-acces').value = cafe.access_code;

        document.getElementById('form-title').textContent = 'Edit Cafe';
        document.getElementById('submit-btn').textContent = 'Update';
        document.getElementById('cancel-btn').style.display = 'inline-block';
        document.getElementById('nom').focus();
    }

    cancelEdit() {
        this.resetForm();
    }

    resetForm() {
        document.getElementById('cafe-form').reset();
        document.getElementById('form-title').textContent = 'Add New Cafe';
        document.getElementById('submit-btn').textContent = 'Add Cafe';
        document.getElementById('cancel-btn').style.display = 'none';
        this.isEditing = false;
        this.currentEditId = null;
    }

    // ---------------- DELETE ----------------
    openDeleteModal(cafeId) {
        this.deleteId = cafeId;
        document.getElementById("delete-modal").style.display = "flex";
    }

    async deleteCafe(cafeId) {
        try {
            const response = await fetch(`http://localhost:5000/api/cafes/${cafeId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (data.success) {
                this.showMessage('Cafe deleted successfully', 'success');
                this.loadCafes();
            } else {
                throw new Error(data.error || 'Error deleting cafe');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage(error.message || 'Error deleting cafe', 'error');
        }
    }

    // ---------------- RENDER ----------------
    renderCafes() {
        const tableBody = document.getElementById('cafe-table-body');
        if (!this.cafes || this.cafes.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No cafes found</td></tr>';
            return;
        }

        tableBody.innerHTML = this.cafes.map(cafe => `
            <tr>
                <td>${this.escapeHtml(cafe.name)}</td>
                <td>${this.escapeHtml(cafe.location)}</td>
                <td>${this.escapeHtml(cafe.access_code)}</td>
                <td>
                    <button class="edit-btn" onclick='cafeManager.editCafe(${JSON.stringify(cafe)})'>Edit</button>
                    <button class="delete-btn" onclick='cafeManager.openDeleteModal(${cafe.id})'>Delete</button>
                </td>
            </tr>
        `).join('');
    }

    // ---------------- UTILS ----------------
    showMessage(message, type) {
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

    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return unsafe;
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// ---------------- INIT ----------------
const cafeManager = new CafeManager();
