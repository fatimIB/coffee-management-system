window.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("loginForm");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const usernameError = document.getElementById("usernameError");
  const passwordError = document.getElementById("passwordError");
  const inputs = document.querySelectorAll("input");

  const API_URL = "http://localhost:5000"; // Flask API Gateway

  // Animate inputs on focus/blur
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.02)";
      this.parentElement.style.transition = "transform 0.2s ease";
    });
    input.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)";
    });
  });

  // Form submission
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    let isValid = true;
    usernameError.classList.remove("show");
    passwordError.classList.remove("show");
    usernameInput.style.borderColor = "#e0e0e0";
    passwordInput.style.borderColor = "#e0e0e0";

    if (!usernameInput.value.trim()) {
      usernameError.textContent = "Please enter a username";
      usernameError.classList.add("show");
      usernameInput.style.borderColor = "#e74c3c";
      isValid = false;
    }

    if (!passwordInput.value.trim()) {
      passwordError.textContent = "Please enter a password";
      passwordError.classList.add("show");
      passwordInput.style.borderColor = "#e74c3c";
      isValid = false;
    }

    if (!isValid) return;

    await handleLogin();
  });

  // Handle login
  async function handleLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in...";

    try {
      const response = await fetch(`${API_URL}/adminlogin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (data.success) {
        showSuccess(username);
        setTimeout(() => {
          window.location.href = "/dashboard/index.html";
        }, 1000);
      } else {
        showError(data.message || "Invalid credentials");
      }
    } catch (error) {
      console.error("Login error:", error);
      showError("Server connection error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "LOG IN";
    }
  }

  // Show success message
  function showSuccess(username) {
    passwordError.textContent = `✓ Welcome ${username}!`;
    passwordError.style.color = "#27ae60";
    passwordError.classList.add("show");

    form.style.opacity = "0.8";
    setTimeout(() => {
      form.style.opacity = "1";
    }, 300);
  }

  // Show error message
  function showError(message) {
    passwordError.textContent = message;
    passwordError.style.color = "#e74c3c";
    passwordError.classList.add("show");
    passwordInput.style.borderColor = "#e74c3c";

    passwordInput.style.animation = "shake 0.3s ease";
    setTimeout(() => {
      passwordInput.style.animation = "";
    }, 300);
  }
});
