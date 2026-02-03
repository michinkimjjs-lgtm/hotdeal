// Supabase Configuration
const SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const dealGrid = document.getElementById('deal-grid');
const searchInput = document.getElementById('search-input');
const categoryBtns = document.querySelectorAll('.cat-btn');

let allDeals = [];
let currentCategory = 'ALL';

// Pagination State
let currentPage = 1;
const ITEMS_PER_PAGE = 20;
let totalCount = 0;

// Fetch deals from Supabase with Pagination
async function fetchDeals(page = 1) {
    currentPage = page;
    dealGrid.innerHTML = `<div class="loading">데이터를 불러오는 중입니다...</div>`;

    // Calculate range
    const from = (page - 1) * ITEMS_PER_PAGE;
    const to = from + ITEMS_PER_PAGE - 1;

    try {
        let query = supabaseClient
            .from('hotdeals')
            .select('*', { count: 'exact' });

        // Apply Category Filter
        if (currentCategory === 'HOT') {
            // 인기: 댓글 많은 순
            query = query.order('comment_count', { ascending: false });
        } else {
            // 일반 카테고리 필터
            if (currentCategory !== 'ALL') {
                query = query.eq('category', currentCategory);
            }
            // 기본 정렬: 최신순
            query = query.order('id', { ascending: false });
        }

        const { data, error, count } = await query.range(from, to);

        if (error) throw error;

        allDeals = data;
        totalCount = count;

        renderDeals(allDeals);
        renderPagination();
    } catch (error) {
        console.error('Error fetching deals:', error);
        dealGrid.innerHTML = `<div class="loading">데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.</div>`;
    }
}

// Category Button Event Listeners
categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Update Active State
        categoryBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update State
        currentCategory = btn.dataset.category;

        // Reset Search Input when changing category
        searchInput.value = '';

        // Fetch
        fetchDeals(1);
    });
});

// Render deals to the grid
function renderDeals(deals) {
    if (deals.length === 0) {
        dealGrid.innerHTML = `<div class="loading">해당하는 핫딜이 없습니다.</div>`;
        return;
    }

    dealGrid.innerHTML = deals.map((deal, index) => `
        <div class="deal-card" style="animation-delay: ${index * 0.05}s">
            <div class="image-container">
                <img src="${deal.img_url ? deal.img_url : 'https://via.placeholder.com/300x200?text=No+Image'}" 
                     alt="${deal.title}" 
                     loading="lazy"
                     referrerpolicy="no-referrer"
                     onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=No+Image';">
            </div>
            <div class="card-content">
                <div class="deal-source">${deal.source}</div>
                <div class="deal-title" title="${deal.title}">${deal.title}</div>
                <div class="deal-footer">
                    <div class="deal-price">${deal.price || '가격미상'}</div>
                    <a href="${deal.url}" target="_blank" class="view-btn">보러가기</a>
                </div>
            </div>
        </div>
    `).join('');

    // Scroll to top of grid
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Render Pagination Controls
function renderPagination() {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;

    const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

    paginationEl.innerHTML = `
        <button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="fetchDeals(${currentPage - 1})">
            이전
        </button>
        <span class="page-info">${currentPage} / ${totalPages} 페이지</span>
        <button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="fetchDeals(${currentPage + 1})">
            다음
        </button>
    `;
}

// Search functionality (Simple Filter on Current Page - Limitation)
// For fully correct search with pagination, we need server-side search.
// Implementing basic server-side search hook:
async function searchDeals(query) {
    if (!query) {
        fetchDeals(1);
        return;
    }

    currentPage = 1;
    dealGrid.innerHTML = `<div class="loading">검색 중...</div>`;

    try {
        const { data, error, count } = await supabaseClient
            .from('hotdeals')
            .select('*', { count: 'exact' })
            .ilike('title', `%${query}%`)
            .order('id', { ascending: false })
            .range(0, ITEMS_PER_PAGE - 1); // Only show first page of results for now

        if (error) throw error;

        allDeals = data;
        totalCount = count; // Result count
        renderDeals(allDeals);

        // Update pagination for search results (simplified)
        const paginationEl = document.getElementById('pagination');
        if (paginationEl) paginationEl.innerHTML = `<span class="page-info">검색 결과: ${count}개</span>`;

    } catch (error) {
        console.error('Search error:', error);
    }
}

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchDeals(e.target.value);
    }
});
// Debounce input for better UX? Or just button.
// Keeping existing input listener style but switching to server search
let debounceTimer;
searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        searchDeals(e.target.value);
    }, 500);
});

// Initial fetch
fetchDeals();

// Real-time updates (Refresh current page if on page 1)
const channel = supabaseClient
    .channel('hotdeals_changes')
    .on('postgres_changes', { event: '*', table: 'hotdeals' }, (payload) => {
        console.log('Change received!', payload);
        if (currentPage === 1 && !searchInput.value) {
            fetchDeals(1);
        }
    })
    .subscribe();
