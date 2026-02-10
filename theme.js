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
});
