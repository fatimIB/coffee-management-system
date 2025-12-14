document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const accessCodeInput = document.getElementById('access-code');
    const errorMessage = document.getElementById('error-message');
    
    // Check if already logged in
    const cafeId = sessionStorage.getItem('cafe_id');
    if (cafeId) {
        // Redirect to orders page if already logged in
        const redirectTo = sessionStorage.getItem('redirect_after_login') || '../orders/index.html';
        sessionStorage.removeItem('redirect_after_login');
        window.location.href = redirectTo;
        return;
    }
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const accessCode = accessCodeInput.value.trim();
        if (!accessCode) {
            showError('Please enter an access code');
            return;
        }
        
        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ access_code: accessCode })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Store cafe info in sessionStorage
                sessionStorage.setItem('cafe_id', data.cafe_id);
                sessionStorage.setItem('cafe_name', data.cafe_name);
                sessionStorage.setItem('location', data.location);
                
                // Redirect to orders page or the page they were trying to access
                const redirectTo = sessionStorage.getItem('redirect_after_login') || '../orders/index.html';
                sessionStorage.removeItem('redirect_after_login');
                window.location.href = redirectTo;
            } else {
                showError(data.message || 'Invalid access code');
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('Error connecting to server. Please try again.');
        }
    });
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
});