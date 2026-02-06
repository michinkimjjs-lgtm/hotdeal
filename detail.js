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
    // Layout: Header -> Meta -> Bar

    // Header
    const catEl = document.getElementById('deal-category');
    if (catEl) catEl.textContent = deal.category || '기타';
    document.getElementById('deal-title').textContent = deal.title;

    // Meta
    // Date Format: YYYY. MM. DD. hh:mm
    const d = new Date(deal.created_at);
    const dateStr = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} ${d.getHours()}:${d.getMinutes()}`;
    document.getElementById('deal-date').textContent = dateStr;

    document.getElementById('source-name-meta').textContent = deal.source;

    // Source Icon & Bar Info
    const sourceIcon = document.getElementById('source-icon');
    const sMap = { 'ppomppu': 'ppomppu', 'fmkorea': 'fmkorea', 'ruliweb': 'ruliweb' };
    let sKey = deal.source.toLowerCase();
    if (sKey.includes('ppomppu')) sKey = 'ppomppu';
    else if (sKey.includes('fmkorea')) sKey = 'fmkorea';
    else if (sKey.includes('ruliweb')) sKey = 'ruliweb';

    sourceIcon.src = `assets/${sKey}_icon.png`;

    // Mall Name Text (Priority: Hidden Content > Source)
    let displaySource = deal.source;
    if (deal.content) {
        const mallMatch = deal.content.match(/<!-- MALL_NAME: (.*?) -->/);
        if (mallMatch && mallMatch[1]) {
            displaySource = mallMatch[1];
        }
    }
    document.getElementById('source-name-bar').textContent = displaySource;
    document.getElementById('deal-price').textContent = deal.price || '가격 확인';

    // "Original Post" Button
    const origBtn = document.getElementById('original-link');
    if (origBtn) origBtn.href = deal.url;

    // Affiliate Link Generation
    const btn = document.getElementById('buy-link');

    // 1. Try to find hidden BUY_URL in content (Injected by Crawler)
    let targetUrl = deal.url; // Default: Post URL
    if (deal.content) {
        const match = deal.content.match(/<!-- BUY_URL: (.*?) -->/);
        if (match && match[1]) {
            targetUrl = match[1];
        }
    }

    btn.href = generateAffiliateLink(targetUrl, deal.source);

    // Open in new tab validation
    btn.target = '_blank';

    // Content (Modified: Hide section if empty, Hide redundant main image if content exists)
    const contentEl = document.getElementById('deal-content-html');
    const contentSection = document.querySelector('.content-section');

    if (deal.content && deal.content.trim().length > 0) {
        // Remove the hidden comment for display check, but keep it in HTML if needed or remove it.
        // Let's remove it from visual display to be clean, though browsers hide comments anyway.
        contentEl.innerHTML = deal.content;
        contentSection.style.display = 'block';
    } else {
        contentSection.style.display = 'none';
    }
}

/**
 * 수익화 링크 생성 함수
 */
function generateAffiliateLink(url, source) {
    let finalUrl = url;

    // Example: If it's a Coupang link, we could add tags here.
    // if (finalUrl.includes('coupang.com')) { ... }

    return finalUrl;
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
