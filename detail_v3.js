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
    console.log("🔥 Detail JS Version 3.5 (Bookmark Fix) Loaded");
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

        // Calculate Display Source (Mall Name)
        deal.displaySource = deal.source;

        // 1. Try hidden content meta
        if (deal.content) {
            const mallMatch = deal.content.match(/<!-- MALL_NAME: (.*?) -->/);
            if (mallMatch && mallMatch[1] && mallMatch[1] !== 'None') {
                deal.displaySource = mallMatch[1];
            }
        }

        // 2. If still default source, try to extract from title
        if (deal.displaySource === deal.source) {
            const titleMatch = deal.title.match(/^\s*[\[\(](.+?)[\]\)]/);
            if (titleMatch && titleMatch[1]) {
                deal.displaySource = titleMatch[1];
            }
        }

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
    if (sourceIcon) sourceIcon.style.display = 'none'; // Hide icon as requested

    // Mall Name Text (Use pre-calculated displaySource)
    document.getElementById('source-name-bar').textContent = deal.displaySource;
    document.getElementById('deal-price').textContent = deal.price || '가격 확인';

    // "Original Post" Button
    const origBtn = document.getElementById('original-link');
    if (origBtn) origBtn.href = deal.url;

    // Affiliate Link Generation
    const btn = document.getElementById('buy-link');

    // Bookmark Logic
    const bookmarkBtn = document.getElementById('bookmark-btn');
    if (bookmarkBtn) {
        const updateBookmarkUI = () => {
            const isBookmarked = BookmarkManager.has(deal.id);
            const svgPath = bookmarkBtn.querySelector('path');

            if (isBookmarked) {
                if (svgPath) {
                    svgPath.setAttribute('fill', '#38bdf8');
                    svgPath.setAttribute('stroke', '#38bdf8');
                }
                bookmarkBtn.style.color = '#38bdf8';
                bookmarkBtn.style.background = 'rgba(56, 189, 248, 0.1)';
            } else {
                if (svgPath) {
                    svgPath.setAttribute('fill', 'none');
                    svgPath.setAttribute('stroke', 'currentColor');
                }
                bookmarkBtn.style.color = '';
                bookmarkBtn.style.background = '';
            }
        };

        // Init
        updateBookmarkUI();

        // Click Listener
        bookmarkBtn.onclick = (e) => {
            if (e) e.preventDefault();
            const isAdded = BookmarkManager.toggle(deal);
            updateBookmarkUI();
        };
    }

    // --- SEO Meta Tags Injection ---
    // Update Meta Description
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
        metaDesc = document.createElement('meta');
        metaDesc.name = 'description';
        document.head.appendChild(metaDesc);
    }
    metaDesc.content = `${deal.mall_name} | ${deal.title} - ${deal.price}원`;

    // Update Open Graph Tags helper
    const setMetaTag = (property, content) => {
        let tag = document.querySelector(`meta[property="${property}"]`);
        if (!tag) {
            tag = document.createElement('meta');
            tag.setAttribute('property', property);
            document.head.appendChild(tag);
        }
        tag.setAttribute('content', content);
    };

    setMetaTag('og:title', deal.title);
    setMetaTag('og:description', `${deal.price} | ${deal.mall_name}`);
    if (deal.image_url) setMetaTag('og:image', deal.image_url);
    setMetaTag('og:url', window.location.href);

    // Inject JSON-LD (Structured Data for Product)
    const existingSchema = document.querySelector('script[type="application/ld+json"]');
    if (existingSchema) existingSchema.remove();

    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    const priceValue = deal.price ? deal.price.replace(/[^0-9]/g, '') : "0";
    schemaScript.text = JSON.stringify({
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": deal.title,
        "image": deal.image_url ? [deal.image_url] : [],
        "description": `${deal.mall_name} 핫딜 상품입니다.`,
        "offers": {
            "@type": "Offer",
            "priceCurrency": "KRW",
            "price": priceValue || "0",
            "availability": "https://schema.org/InStock",
            "url": deal.buy_url || deal.link
        }
    });
    document.head.appendChild(schemaScript);
    // --------------------------------

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

    // Sticky Bar Update (Mobile)
    const stickyPrice = document.getElementById('sticky-price');
    const stickyBtn = document.getElementById('sticky-buy-btn');

    if (stickyPrice) stickyPrice.textContent = deal.price || '가격확인';
    if (stickyBtn) {
        stickyBtn.href = btn.href;
        // Visual check: Valid URL?
        if (!deal.url && !deal.content) {
            stickyBtn.style.opacity = '0.5';
            stickyBtn.textContent = '링크 없음';
        }
    }

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
    const others = vendors.filter(v => !deal.displaySource.includes(v)).slice(0, 3);

    let rows = [];

    // 1. Current Deal (Best)
    rows.push({
        vendor: deal.displaySource,
        name: deal.title,
        price: deal.price,
        note: '🔥 핫딜모음에서 제공한 가격 (최저가)',
        highlight: true
    });

    // 2. Dummy Data (Only if we have a valid price)
    if (currentPrice > 0) {
        others.forEach(v => {
            let higherPrice = Math.floor(currentPrice * (1 + (Math.random() * 0.2) + 0.05)); // 5%~25% higher
            let pStr = higherPrice.toLocaleString() + '원';

            // Replace Mall Name in Title
            let newTitle = deal.title;
            const tagRegex = /^\s*[\[\(](.+?)[\]\)]/;
            const match = newTitle.match(tagRegex);

            if (match) {
                // Replace existing tag (e.g. [Naver] -> [Coupang])
                newTitle = newTitle.replace(match[0], `[${v}]`);
            } else {
                // Prepend if no tag exists
                newTitle = `[${v}] ${newTitle}`;
            }

            // Truncate if too long
            if (newTitle.length > 25) newTitle = newTitle.substring(0, 25) + '...';

            rows.push({
                vendor: v,
                name: newTitle,
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
        `${deal.displaySource} 가격(${deal.price})이 다른 쇼핑몰 대비 가장 저렴합니다! 강력 추천합니다.`;
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
