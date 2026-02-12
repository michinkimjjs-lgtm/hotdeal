// theme.js - Shared Theme Logic

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        themeToggleBtn.innerText = theme === 'dark' ? '🌙' : '☀️';
    }

    if (themeToggleBtn) {
        // Init icon based on current attribute
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        updateThemeIcon(currentTheme);

        themeToggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    // Dropdown Menu Logic
    const menuToggleBtn = document.getElementById('menu-toggle');
    const dropdownMenu = document.getElementById('dropdown-menu');

    if (menuToggleBtn && dropdownMenu) {
        menuToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent closing immediately
            dropdownMenu.classList.toggle('show');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdownMenu.contains(e.target) && !menuToggleBtn.contains(e.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }
});

// Copy URL Function
function copyCurrentUrl() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('링크가 복사되었습니다!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}
