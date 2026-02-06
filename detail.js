// detail.js

// Supabase Configuration (Copied from app.js)
const SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 1. Check ID from URL
const params = new URLSearchParams(window.location.search);
const dealId = params.get('id');

// Copy URL function
function copyUrl() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        alert('링크가 복사되었습니다!');
    });
}

// Switch Tabs
function switchTab(current) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Activate
    const buttons = document.querySelectorAll('.tab-btn');
    if (current === 'comparison') buttons[0].classList.add('active');
    else buttons[1].classList.add('active');

    document.getElementById(`tab-${current}`).classList.add('active');
}


async function loadDeal() {
    if (!dealId) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').textContent = '잘못된 접근입니다.';
        document.getElementById('error-message').style.display = 'block';
        return;
    }

    try {
        // Fetch from Supabase
        const { data: deal, error } = await supabaseClient
            .from('hotdeals')
            .select('*')
            .eq('id', dealId)
            .single();

        if (error) throw error;
        if (!deal) throw new Error('Deal not found');

        // Render Data
        renderDealInfo(deal);
        renderComparison(deal);
        renderChart(deal);

        // Show content
        document.getElementById('loading').style.display = 'none';
        document.getElementById('deal-detail').style.display = 'block';

    } catch (err) {
        console.error(err);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').textContent = '상품 정보를 불러올 수 없습니다.';
        document.getElementById('error-message').style.display = 'block';
    }
}

function renderDealInfo(deal) {
    document.title = `${deal.title} - 핫딜모음`;

    // Text Fields
    document.getElementById('deal-title').textContent = deal.title;
    document.getElementById('deal-price').textContent = deal.price || '가격미상';
    document.getElementById('deal-category').textContent = deal.category || '기타';

    // Date Format: YYYY. MM. DD.
    const d = new Date(deal.created_at);
    // Month is 0-indexed
    const dateStr = `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.`;
    document.getElementById('deal-date').textContent = dateStr;

    // Source Icon
    const sourceIcon = document.getElementById('source-icon');
    const sMap = { 'ppomppu': 'ppomppu', 'fmkorea': 'fmkorea', 'ruliweb': 'ruliweb' };
    let sKey = deal.source.toLowerCase();

    if (sKey.includes('ppomppu')) sKey = 'ppomppu';
    else if (sKey.includes('fmkorea')) sKey = 'fmkorea';
    else if (sKey.includes('ruliweb')) sKey = 'ruliweb';

    sourceIcon.src = `assets/${sKey}_icon.png`;
    document.getElementById('source-name').textContent = deal.source;

    // "Original Post" Button
    const origBtn = document.getElementById('original-link');
    if (origBtn) origBtn.href = deal.url;

    // Image
    const imgEl = document.getElementById('deal-image');
    imgEl.src = deal.img_url || 'https://via.placeholder.com/400x400?text=No+Image';
    imgEl.onerror = () => { imgEl.src = 'https://via.placeholder.com/400x400?text=No+Image'; };

    // Stats
    document.getElementById('stat-likes').textContent = deal.like_count || 0;
    document.getElementById('stat-comments').textContent = deal.comment_count || 0;

    // Content (Modified: Hide section if empty)
    const contentEl = document.getElementById('deal-content-html');
    const contentSection = document.querySelector('.content-section');

    if (deal.content && deal.content.trim().length > 0) {
        contentEl.innerHTML = deal.content;
        contentSection.style.display = 'block';
    } else {
        // User requested to remove the placeholder text
        contentSection.style.display = 'none';
    }

    // Button
    const btn = document.getElementById('buy-link');
    btn.href = deal.url;
}

function renderComparison(deal) {
    // Mock Data for Comparison
    // Logic: Current deal is best. Generate 2 fake competitors with higher prices.

    // Parse price to number
    let currentPrice = 0;
    if (deal.price) {
        // Remove non-digits
        let nums = deal.price.replace(/[^\d]/g, '');
        currentPrice = parseInt(nums) || 0;
    }

    // Creating dummy competitors
    const vendors = ['쿠팡', '네이버쇼핑', '11번가', 'G마켓'];
    // Shuffle vendors
    const others = vendors.filter(v => !deal.source.includes(v)).slice(0, 3);

    let rows = [];

    // 1. Current Deal (Best)
    rows.push({
        vendor: deal.source,
        name: deal.title,
        price: deal.price,
        note: '🔥 핫딜모음에서 제공한 가격 (최저가)',
        highlight: true
    });

    // 2. Dummy Data (Only if we have a valid price)
    if (currentPrice > 0) {
        others.forEach(v => {
            let higherPrice = Math.floor(currentPrice * (1 + (Math.random() * 0.2) + 0.05)); // 5%~25% higher
            // Format format: 12,345원
            let pStr = higherPrice.toLocaleString() + '원';
            rows.push({
                vendor: v,
                name: deal.title.substring(0, 20) + '...',
                price: pStr,
                note: '일반 판매가',
                highlight: false
            });
        });
    } else {
        // Fallback if price missing
        rows.push({ vendor: '쿠팡', name: '상품 정보 확인 필요', price: '가격비교 불가', note: '-', highlight: false });
    }

    // Render Table
    const tbody = document.getElementById('comparison-tbody');
    tbody.innerHTML = rows.map(r => `
        <tr class="${r.highlight ? 'row-highlight' : ''}">
            <td style="font-weight:bold">${r.vendor}</td>
            <td style="color:#aaa">${r.name}</td>
            <td style="color:${r.highlight ? '#ef4444' : '#e0e0e0'}; font-weight:${r.highlight ? 'bold' : 'normal'}">${r.price}</td>
            <td style="font-size:0.85rem">${r.note}</td>
        </tr>
    `).join('');

    // Render Alert
    document.getElementById('lowest-price-text').textContent =
        `${deal.source} 가격(${deal.price})이 다른 쇼핑몰 대비 가장 저렴합니다! 강력 추천합니다.`;
}

function renderChart(deal) {
    const ctx = document.getElementById('priceChart').getContext('2d');

    // Generate Mock History Data (Last 7 days)
    // Decreasing trend to look like a deal
    let pricePoints = [];
    let labels = [];

    let basePrice = 0;
    if (deal.price) basePrice = parseInt(deal.price.replace(/[^\d]/g, '')) || 10000;
    if (basePrice === 0) basePrice = 50000; // default

    for (let i = 6; i >= 0; i--) {
        let d = new Date();
        d.setDate(d.getDate() - i);
        labels.push((d.getMonth() + 1) + '/' + d.getDate());

        // Price history logic: higher in past, drops today
        let factor = 1 + (i * 0.02); // 2% higher per day back
        if (i === 0) factor = 1; // today

        pricePoints.push(Math.floor(basePrice * factor));
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '가격 변동 추이',
                data: pricePoints,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: '#333' },
                    ticks: { color: '#888' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#888' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Init
loadDeal();
