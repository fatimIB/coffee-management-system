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
