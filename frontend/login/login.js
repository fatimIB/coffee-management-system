window.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("loginForm");
  const cafeSelect = document.getElementById("cafe");
  const codeInput = document.getElementById("code");
  const cafeError = document.getElementById("cafeError");
  const codeError = document.getElementById("codeError");
  const inputs = document.querySelectorAll("input, select");

  const API_URL = "http://localhost:5000/api";

  // Load cafes from API
  await loadCafes();

  async function loadCafes() {
    try {
      const response = await fetch(`${API_URL}/cafes`);
      const data = await response.json();

      if (data.success && data.cafes) {
        cafeSelect.innerHTML =
          '<option value="" disabled selected>Ex: Café Salam</option>';

        data.cafes.forEach((cafe) => {
          const option = document.createElement("option");
          option.value = cafe.id;
          option.textContent = `${cafe.name} - ${cafe.location}`;
          cafeSelect.appendChild(option);
        });
      } else {
        console.error("Error loading cafes");
      }
    } catch (error) {
      console.error("Connection error:", error);
      cafeError.textContent = "Failed to load cafes";
      cafeError.classList.add("show");
    }
  }

  // Input focus animation
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.02)";
      this.parentElement.style.transition = "transform 0.2s ease";
    });

    input.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)";
    });
  });

  // Form validation and submission
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    let isValid = true;

    cafeError.classList.remove("show");
    codeError.classList.remove("show");
    cafeSelect.style.borderColor = "#e0e0e0";
    codeInput.style.borderColor = "#e0e0e0";

    if (!cafeSelect.value) {
      cafeError.textContent = "Please select a cafe";
      cafeError.classList.add("show");
      cafeSelect.style.borderColor = "#e74c3c";
      isValid = false;
    }

    if (codeInput.value.length !== 5) {
      codeError.textContent = "Code must be 5 digits";
      codeError.classList.add("show");
      codeInput.style.borderColor = "#e74c3c";
      isValid = false;
    }

    if (isValid) {
      await handleLogin();
    }
  });

  // Handle login
  async function handleLogin() {
    const cafe_id = cafeSelect.value;
    const access_code = codeInput.value;

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in...";

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          cafe_id: parseInt(cafe_id),
          access_code: access_code,
        }),
      });

      const data = await response.json();

      if (data.success) {
        showSuccess(data.cafe_name);

        setTimeout(() => {
          window.location.href = "/orders/index.html";
        }, 1000);
      } else {
        showError(data.message);
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
  function showSuccess(cafeName) {
    codeError.textContent = `✓ Welcome ${cafeName}!`;
    codeError.style.color = "#27ae60";
    codeError.classList.add("show");

    form.style.opacity = "0.8";
    setTimeout(() => {
      form.style.opacity = "1";
    }, 300);
  }

  // Show error message
  function showError(message) {
    codeError.textContent = message;
    codeError.style.color = "#e74c3c";
    codeError.classList.add("show");
    codeInput.style.borderColor = "#e74c3c";

    codeInput.style.animation = "shake 0.3s ease";
    setTimeout(() => {
      codeInput.style.animation = "";
    }, 300);
  }

  // Limit input length
  codeInput.addEventListener("input", function () {
    if (this.value.length > 5) {
      this.value = this.value.slice(0, 5);
    }
  });
});
