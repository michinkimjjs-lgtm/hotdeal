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

// Bookmark Manager
const BookmarkManager = {
    KEY: 'hotdeal_bookmarks',

    get() {
        try {
            const data = localStorage.getItem(this.KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Bookmark load error:', e);
            return [];
        }
    },

    save(bookmarks) {
        localStorage.setItem(this.KEY, JSON.stringify(bookmarks));
        // Dispatch event for real-time UI updates
        window.dispatchEvent(new CustomEvent('bookmarkUpdated'));
    },

    add(deal) {
        const bookmarks = this.get();
        if (bookmarks.some(b => b.id === deal.id)) return; // Already exists

        // Minimal data to save storage
        const newBookmark = {
            id: deal.id,
            title: deal.title,
            price: deal.price,
            source: deal.source || deal.displaySource, // Use displaySource if available
            img_url: deal.img_url,
            url: deal.url,
            category: deal.category,
            created_at: new Date().toISOString(), // Use current time as added time? Or keep original?
            // Let's keep original created_at for "Latest" sort if we want, or add 'saved_at'.
            // The reference sorts by "Latest", which usually implies "Recently Added".
            saved_at: new Date().toISOString()
        };

        // Add to beginning
        bookmarks.unshift(newBookmark);
        this.save(bookmarks);
        return true;
    },

    remove(id) {
        let bookmarks = this.get();
        const initialLen = bookmarks.length;
        bookmarks = bookmarks.filter(b => b.id != id); // Loose equality for string/number safety

        if (bookmarks.length !== initialLen) {
            this.save(bookmarks);
            return true;
        }
        return false;
    },

    toggle(deal) {
        if (this.has(deal.id)) {
            this.remove(deal.id);
            return false; // Removed
        } else {
            this.add(deal);
            return true; // Added
        }
    },

    has(id) {
        const bookmarks = this.get();
        return bookmarks.some(b => b.id == id);
    },

    clear() {
        localStorage.removeItem(this.KEY);
        window.dispatchEvent(new CustomEvent('bookmarkUpdated'));
    }
};

window.BookmarkManager = BookmarkManager;

// Copy URL Function
function copyCurrentUrl() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('링크가 복사되었습니다!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

// Global Toast Notification
window.showToast = function (message) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);

    // Animation: Enter
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Remove after delay
    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, 2500); // 2.5 seconds
};
