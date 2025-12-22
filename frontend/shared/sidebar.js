const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');

function setActiveLink() {
  const currentPath = window.location.pathname; // e.g., /frontend/dashboard/index.html

  sidebarLinks.forEach(link => {
    link.classList.remove('active');
    const linkPath = new URL(link.href).pathname; // absolute path of the link
    if (linkPath === currentPath) {
      link.classList.add('active');
    }
  });
}

setActiveLink();


const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
  logoutBtn.addEventListener("click", async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/adminlogout", {
        method: "POST",
        credentials: "include"
      });

      const data = await response.json();

      if (data.success) {
        window.location.href = "/adminlogin/index.html";
      } else {
        alert("Logout failed");
      }

    } catch (error) {
      console.error("Logout error:", error);
      alert("Server error during logout");
    }
  });
}
