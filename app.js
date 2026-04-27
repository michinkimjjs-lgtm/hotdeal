// Supabase Configuration
const SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const dealGrid = document.getElementById('deal-grid');
const searchInput = document.getElementById('search-input');
const categoryBtns = document.querySelectorAll('.cat-link');

let allDeals = [];
let currentCategory = 'ALL';
let filterPopular = false;

// Pagination State
let currentPage = 1;
let itemsPerPage = window.innerWidth < 1024 ? 10 : 20;
let totalCount = 0;

// Update items per page on resize
window.addEventListener('resize', () => {
    const newItemsPerPage = window.innerWidth < 1024 ? 10 : 20;
    if (newItemsPerPage !== itemsPerPage) {
        itemsPerPage = newItemsPerPage;
        fetchDeals(1); // Reset to page 1 to avoid range issues
    }
});

// Fetch deals from Supabase with Pagination
async function fetchDeals(page = 1) {
    currentPage = page;
    dealGrid.innerHTML = `<div class="loading">데이터를 불러오는 중입니다...</div>`;

    // Calculate range
    const from = (page - 1) * itemsPerPage;
    const to = from + itemsPerPage - 1;

    try {
        let query = supabaseClient
            .from('hotdeals')
            .select('*', { count: 'exact' });

        // Apply Category Filter
        if (currentCategory === 'HOT') {
            // 핫/인기: 최신순 (단, '전체'와 구분을 위해 댓글 3개 이상 필터링)
            query = query.gte('comment_count', 3);
            query = query.order('id', { ascending: false });
        } else {
            // 일반 카테고리 필터
            if (currentCategory !== 'ALL') {
                query = query.eq('category', currentCategory);
            }
            // 기본 정렬: 최신순
            query = query.order('id', { ascending: false });
        }

        // Apply Popular Filter
        // General: 10+ Likes
        // Ruliweb: 100+ Likes (due to generous like culture)
        if (filterPopular) {
            query = query.or('and(source.eq.Ruliweb,like_count.gte.100),and(source.neq.Ruliweb,like_count.gte.10)');
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

// Helper to get relative time
function getRelativeTime(dateString) {
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

// Render deals to the grid
function renderDeals(deals) {
    if (deals.length === 0) {
        dealGrid.innerHTML = `<div class="loading">해당하는 핫딜이 없습니다.</div>`;
        return;
    }

    dealGrid.innerHTML = deals.map((deal, index) => {
        // Hot Deal Logic (Robust Type Check)
        const likes = parseInt(deal.like_count) || 0;

        let hotTier = 0; // 0: Normal, 1: Hot, 2: Super Hot (God)

        if (deal.source === 'Ruliweb') {
            if (likes >= 100) hotTier = 2;
            else if (likes >= 30) hotTier = 1;
        } else {
            if (likes >= 30) hotTier = 2;
            else if (likes >= 10) hotTier = 1;
        }

        // Class and Badge Logic based on Tier
        let cardClass = '';
        if (hotTier === 2) cardClass = 'super-hot-deal';
        else if (hotTier === 1) cardClass = 'hot-deal';

        // Merit Badge Logic
        let badgeHtml = '';

        // 1. Discount Pattern (e.g. 50%, 30프로)
        const discountMatch = deal.title.match(/(\d+)(%|프로|퍼센트)/);
        if (discountMatch) {
            const discountRate = parseInt(discountMatch[1]);
            if (discountRate >= 30) { // Only show significant discounts
                badgeHtml = `<span class="merit-badge discount">${discountRate}%↓</span>`;
            }
        }

        // 2. Keyword Pattern (If no discount badge yet)
        if (!badgeHtml) {
            if (deal.title.match(/역대|최저|대란|오류|끝판/)) {
                badgeHtml = `<span class="merit-badge keyword">역대급</span>`;
            }
        }

        return `
        <div class="deal-card ${cardClass}" style="animation-delay: ${index * 0.05}s">
            <div class="image-container">
                <img src="${deal.img_url ? deal.img_url : 'https://via.placeholder.com/300x200?text=No+Image'}" 
                     alt="${deal.title}" 
                     loading="lazy"
                     referrerpolicy="no-referrer"
                     onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=No+Image';">
            </div>
            <div class="card-content">
                <div class="card-header-row">
                    <div class="deal-source">
                        <img src="assets/${deal.source.toLowerCase()}_icon.png" alt="${deal.source}" class="source-icon">
                        ${deal.source}
                    </div>
                    <div class="deal-time">${getRelativeTime(deal.created_at)}</div>
                </div>
                <div class="deal-title" title="${deal.title}">
                    ${badgeHtml} ${deal.title}
                </div>
                <div class="deal-footer">
                    <div class="deal-info-stats">
                        <span class="deal-likes">👍 ${deal.like_count || 0}</span>
                        <span class="deal-comment">💬 ${deal.comment_count || 0}</span>
                    </div>
                    <div class="deal-price">${deal.price || '가격미상'}</div>
                    <a href="detail.html?id=${deal.id}" class="view-btn">상세보기</a>
                </div>
            </div>
        </div>
    `}).join('');

    // Scroll to top of grid
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Render Pagination Controls
function renderPagination() {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;

    const totalPages = Math.ceil(totalCount / itemsPerPage);

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
            .range(0, itemsPerPage - 1); // Only show first page of results for now

        if (error) throw error;

        // --- SEARCH LOG TRACKING ---
        try {
            await supabaseClient.from('search_logs').insert([{
                ip: window.cachedIP || 'Unknown',
                keyword: query,
                result_count: count || 0,
                searched_at: new Date().toISOString()
            }]);
        } catch(e) { console.error('Search track error', e); }
        // ---------------------------

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

// Popular Filter Toggle
const popularBtn = document.getElementById('popular-filter');
popularBtn.addEventListener('click', () => {
    filterPopular = !filterPopular;
    popularBtn.classList.toggle('active', filterPopular);
    fetchDeals(1);
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

// --- VISIT LOG TRACKING ---
window.cachedIP = 'Unknown';
async function logVisit() {
    try {
        // Fetch IP address
        const ipRes = await fetch('https://api.ipify.org?format=json');
        const ipData = await ipRes.json();
        window.cachedIP = ipData.ip;

        // Parse basic Browser / OS
        let os = 'Unknown OS';
        if (navigator.userAgent.indexOf("Win") !== -1) os = "Windows";
        if (navigator.userAgent.indexOf("Mac") !== -1) os = "MacOS";
        if (navigator.userAgent.indexOf("Android") !== -1) os = "Android";
        if (navigator.userAgent.indexOf("like Mac") !== -1) os = "iOS";

        let browser = 'Unknown Browser';
        if (navigator.userAgent.indexOf("Chrome") !== -1) browser = "Chrome";
        else if (navigator.userAgent.indexOf("Safari") !== -1) browser = "Safari";
        else if (navigator.userAgent.indexOf("Firefox") !== -1) browser = "Firefox";
        else if (navigator.userAgent.indexOf("SamsungBrowser") !== -1) browser = "Samsung Internet";

        await supabaseClient.from('visit_logs').insert([{
            ip: window.cachedIP,
            browser: browser,
            os: os,
            visited_at: new Date().toISOString(),
            source_path: 'hotdealmoa.co.kr'
        }]);
    } catch(e) { console.error('Visit track error', e); }
}
logVisit();
// ----------------------------
