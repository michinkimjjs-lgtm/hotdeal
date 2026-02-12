// bookmarks.js

document.addEventListener('DOMContentLoaded', () => {
    const listEl = document.getElementById('bookmark-list');
    const sortBtns = document.querySelectorAll('.sort-btn');
    const deleteAllBtn = document.getElementById('delete-all-btn');

    let currentSort = 'latest';

    // 1. Initial Load
    renderList();

    // 2. Sort Listeners
    sortBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update UI
            sortBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update Sort State
            currentSort = btn.dataset.sort;
            renderList();
        });
    });

    // 3. Delete All Listener
    if (deleteAllBtn) {
        deleteAllBtn.addEventListener('click', () => {
            if (confirm('모든 북마크를 삭제하시겠습니까?')) {
                BookmarkManager.clear();
                renderList();
            }
        });
    }

    // 4. Listen for external updates (e.g. from other tabs)
    window.addEventListener('bookmarkUpdated', () => {
        renderList();
    });

    function renderList() {
        let bookmarks = BookmarkManager.get();

        if (bookmarks.length === 0) {
            listEl.innerHTML = `<div class="bm-empty">저장된 핫딜이 없습니다.</div>`;
            return;
        }

        // Sort Logic
        bookmarks.sort((a, b) => {
            if (currentSort === 'latest') {
                // Newest first (saved_at or created_at)
                const timeA = new Date(a.saved_at || a.created_at || 0);
                const timeB = new Date(b.saved_at || b.created_at || 0);
                return timeB - timeA;
            } else if (currentSort === 'title') {
                return a.title.localeCompare(b.title);
            } else if (currentSort === 'category') {
                return (a.category || '').localeCompare(b.category || '');
            }
            return 0;
        });

        // Render
        listEl.innerHTML = bookmarks.map(deal => {
            // Fallback for missing data
            const imgSrc = deal.img_url || 'https://via.placeholder.com/140?text=No+Image';
            const price = deal.price || '가격미상';
            const mall = deal.source || '쇼핑몰';
            const category = deal.category || '기타';
            const timeStr = getRelativeTime(deal.created_at || deal.saved_at);

            return `
            <a href="detail.html?id=${deal.id}" class="bookmark-card">
                <div class="bm-image">
                    <img src="${imgSrc}" loading="lazy" alt="${deal.title}" onerror="this.src='https://via.placeholder.com/140?text=No+Image'">
                </div>
                <div class="bm-content">
                    <div class="bm-info-row">
                        <div class="bm-header">
                            <span class="bm-category">${category}</span>
                            <span class="bm-mall">${mall}</span>
                        </div>
                        <div class="bm-title">${deal.title}</div>
                    </div>
                    <div class="bm-footer">
                        <div class="bm-price">${price}</div>
                        <div class="bm-time">${timeStr}</div>
                    </div>
                </div>
            </a>
            `;
        }).join('');
    }

    function getRelativeTime(dateString) {
        if (!dateString) return '';
        const now = new Date();
        const past = new Date(dateString);
        const diffInMs = now - past;
        const diffInMins = Math.floor(diffInMs / (1000 * 60));
        const diffInHours = Math.floor(diffInMins / 60);
        const diffInDays = Math.floor(diffInHours / 24);

        if (diffInMins < 1) return '방금 전';
        if (diffInMins < 60) return `${diffInMins}분 전`;
        if (diffInHours < 24) return `${diffInHours}시간 전`;
        if (diffInDays < 7) return `${diffInDays}일 전`;
        return past.toLocaleDateString();
    }
});
