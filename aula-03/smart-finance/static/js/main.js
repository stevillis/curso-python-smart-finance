// Theme toggling logic
function updateThemeIcon(theme) {
    const icons = document.querySelectorAll('.theme-icon-indicator');
    icons.forEach(icon => {
        if (theme === 'dark') {
            icon.className = 'fa-solid fa-sun theme-icon-indicator';
            if (icon.nextSibling && icon.nextSibling.nodeType === 3 && icon.nextSibling.textContent.includes('Tema')) {
                icon.nextSibling.textContent = ' Tema Claro';
            }
        } else {
            icon.className = 'fa-solid fa-moon theme-icon-indicator';
            if (icon.nextSibling && icon.nextSibling.nodeType === 3 && icon.nextSibling.textContent.includes('Tema')) {
                icon.nextSibling.textContent = ' Tema Escuro';
            }
        }
    });
}

function toggleTheme(e) {
    e.preventDefault();
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    // Toggle the sidebar sliding in and out
    sidebar.classList.toggle('left-[-100%]');
    sidebar.classList.toggle('left-0');

    // Toggle the overlay visibility
    overlay.classList.toggle('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    updateThemeIcon(currentTheme);
});
