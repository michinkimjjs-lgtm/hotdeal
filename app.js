// Supabase Configuration
const SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const dealGrid = document.getElementById('deal-grid');
const searchInput = document.getElementById('search-input');

let allDeals = [];

// Fetch deals from Supabase
async function fetchDeals() {
    try {
        const { data, error } = await supabaseClient
            .from('hotdeals')
            .select('*')
            .order('id', { ascending: false });

        if (error) throw error;

        allDeals = data;
        renderDeals(allDeals);
    } catch (error) {
        console.error('Error fetching deals:', error);
        dealGrid.innerHTML = `<div class="loading">데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.</div>`;
    }
}

// Render deals to the grid
function renderDeals(deals) {
    if (deals.length === 0) {
        dealGrid.innerHTML = `<div class="loading">검색 결과가 없습니다.</div>`;
        return;
    }

    dealGrid.innerHTML = deals.map((deal, index) => `
        <div class="deal-card" style="animation-delay: ${index * 0.05}s">
            <div class="image-container">
                <img src="${deal.img_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${deal.title}" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
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
}

// Search functionality
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const filteredDeals = allDeals.filter(deal =>
        deal.title.toLowerCase().includes(searchTerm) ||
        deal.source.toLowerCase().includes(searchTerm)
    );
    renderDeals(filteredDeals);
});

// Initial fetch
fetchDeals();

// Real-time updates
const channel = supabaseClient
    .channel('hotdeals_changes')
    .on('postgres_changes', { event: '*', table: 'hotdeals' }, (payload) => {
        console.log('Change received!', payload);
        fetchDeals(); // Simplest way to keep in sync
    })
    .subscribe();
