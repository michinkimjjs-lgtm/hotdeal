// admin.js
// Supabase Configuration
const SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// DOM Elements
const searchLogTbody = document.getElementById('search-log-tbody');
const visitLogTbody = document.getElementById('visit-log-tbody');
const searchLogCount = document.getElementById('search-log-count');
const visitLogCount = document.getElementById('visit-log-count');
const refreshBtn = document.getElementById('refresh-btn');

// Chart globals
let trafficChartInstance = null;
let browserChartInstance = null;
let visitDataForChart = [];
let searchDataForChart = [];
let browserDataForChart = {};

// --- Login Logic ---
const ADMIN_PW = "michin2002@"; // 임시 비밀번호

document.addEventListener('DOMContentLoaded', () => {
    const loginOverlay = document.getElementById('login-overlay');
    const adminContent = document.getElementById('admin-content');
    const pwInput = document.getElementById('admin-password');
    const loginBtn = document.getElementById('login-btn');
    const loginError = document.getElementById('login-error');

    // Check localStorage for session
    if (localStorage.getItem('admin_auth') === 'true') {
        initAdmin();
    }

    loginBtn.addEventListener('click', attemptLogin);
    pwInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') attemptLogin();
    });

    function attemptLogin() {
        if (pwInput.value === ADMIN_PW) {
            localStorage.setItem('admin_auth', 'true');
            initAdmin();
        } else {
            loginError.style.display = 'block';
            pwInput.value = '';
            pwInput.focus();
        }
    }

    function initAdmin() {
        loginOverlay.style.display = 'none';
        adminContent.style.display = 'flex'; // 컨테이너 보이게

        // 날짜 기본 설정 및 데이터 로드 시작
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date-start').value = today;
        document.getElementById('date-end').value = today;

        fetchData();

        refreshBtn.addEventListener('click', fetchData);
        document.getElementById('search-filter-btn').addEventListener('click', fetchData);

        // 날짜 퀵 필터 설정
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const daysToSubtract = parseInt(e.target.getAttribute('data-days'));
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(endDate.getDate() - daysToSubtract);
                
                document.getElementById('date-start').value = startDate.toISOString().split('T')[0];
                document.getElementById('date-end').value = endDate.toISOString().split('T')[0];
                
                fetchData();
            });
        });
    }
});

function formatDateTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    
    let hours = date.getHours();
    const ampm = hours >= 12 ? '오후' : '오전';
    hours = hours % 12;
    hours = hours ? hours : 12; 
    
    const h = String(hours).padStart(2, '0');
    const min = String(date.getMinutes()).padStart(2, '0');
    const s = String(date.getSeconds()).padStart(2, '0');

    return `${m}. ${d}. ${ampm} ${h}:${min}:${s}`;
}

async function fetchData() {
    const startDate = document.getElementById('date-start').value + "T00:00:00.000Z";
    const endDate = document.getElementById('date-end').value + "T23:59:59.999Z";

    visitDataForChart = [];
    searchDataForChart = [];
    browserDataForChart = {};

    await Promise.all([
        fetchSearchLogs(startDate, endDate),
        fetchVisitLogs(startDate, endDate),
        fetchHotdealsCount(startDate, endDate),
        fetchClickLogs(startDate, endDate),
        fetchCrawlerStatus()
    ]);

    updateCharts();
}

async function fetchHotdealsCount(startDate, endDate) {
    try {
        const { count, error } = await supabaseClient
            .from('hotdeals')
            .select('*', { count: 'exact', head: true })
            .gte('created_at', startDate)
            .lte('created_at', endDate);
            
        if (error) throw error;
        document.getElementById('stat-hotdeals').textContent = count || 0;
    } catch(err) {
        document.getElementById('stat-hotdeals').textContent = '오류';
    }
}

async function fetchSearchLogs(startDate, endDate) {
    try {
        const { data, error, count } = await supabaseClient
            .from('search_logs')
            .select('*', { count: 'exact' })
            .gte('searched_at', startDate)
            .lte('searched_at', endDate)
            .order('searched_at', { ascending: false });

        if (error) {
            console.error('Error fetching search logs:', error);
            if(error.code === '42P01') {
                searchLogTbody.innerHTML = '<tr><td colspan="4" class="text-center">Supabase에 search_logs 테이블이 없습니다.</td></tr>';
                return;
            }
            throw error;
        }

        searchLogCount.textContent = count || 0;
        
        if (!data || data.length === 0) {
            searchLogTbody.innerHTML = '<tr><td colspan="4" class="text-center">조회된 검색 로그가 없습니다.</td></tr>';
            document.getElementById('top-keywords-tbody').innerHTML = '<tr><td colspan="3" class="text-center">데이터 없음</td></tr>';
            return;
        }

        const keywordCounts = {};

        data.forEach(log => {
            if (log.searched_at) {
                const day = log.searched_at.split('T')[0];
                searchDataForChart.push(day);
            }
            keywordCounts[log.keyword] = (keywordCounts[log.keyword] || 0) + 1;
        });

        searchLogTbody.innerHTML = data.slice(0, 50).map(log => {
            const hasResult = log.result_count > 0;
            const resultText = hasResult ? '찾음' : '없음';
            const resultClass = hasResult ? 'text-success' : 'text-error';

            return `
                <tr>
                    <td>${formatDateTime(log.searched_at)}</td>
                    <td>${log.ip || '-'}</td>
                    <td>${log.keyword}</td>
                    <td class="${resultClass}">${resultText}</td>
                </tr>
            `;
        }).join('');

        const topKeywords = Object.entries(keywordCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);
        document.getElementById('top-keywords-tbody').innerHTML = topKeywords.map((kw, i) => `
            <tr>
                <td>${i + 1}</td>
                <td>${kw[0]}</td>
                <td>${kw[1]}</td>
            </tr>
        `).join('');

    } catch (err) {
        searchLogTbody.innerHTML = '<tr><td colspan="4" class="text-center">오류가 발생했습니다.</td></tr>';
    }
}

async function fetchVisitLogs(startDate, endDate) {
    try {
        const { data, error, count } = await supabaseClient
            .from('visit_logs')
            .select('*', { count: 'exact' })
            .gte('visited_at', startDate)
            .lte('visited_at', endDate)
            .order('visited_at', { ascending: false });

        if (error) {
            if(error.code === '42P01') {
                visitLogTbody.innerHTML = '<tr><td colspan="5" class="text-center">Supabase에 visit_logs 테이블이 없습니다.</td></tr>';
                return;
            }
            throw error;
        }

        visitLogCount.textContent = count || 0;

        if (!data || data.length === 0) {
            visitLogTbody.innerHTML = '<tr><td colspan="5" class="text-center">조회된 접속 로그가 없습니다.</td></tr>';
            return;
        }

        data.forEach(log => {
            if (log.visited_at) {
                const day = log.visited_at.split('T')[0];
                visitDataForChart.push(day);
            }
            const b = log.browser || 'Unknown';
            browserDataForChart[b] = (browserDataForChart[b] || 0) + 1;
        });

        visitLogTbody.innerHTML = data.slice(0, 50).map(log => {
            return `
                <tr>
                    <td>${log.ip || '-'}</td>
                    <td>${log.source_path || 'index.html'}</td>
                    <td>${log.browser || 'Unknown'}</td>
                    <td>${log.os || 'Unknown'}</td>
                    <td>${formatDateTime(log.visited_at)}</td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        visitLogTbody.innerHTML = '<tr><td colspan="5" class="text-center">오류가 발생했습니다.</td></tr>';
    }
}

async function fetchClickLogs(startDate, endDate) {
    try {
        const { data, error } = await supabaseClient
            .from('click_logs')
            .select('*')
            .gte('clicked_at', startDate)
            .lte('clicked_at', endDate);
            
        const tbody = document.getElementById('top-deals-tbody');
        if (error || !data || data.length === 0) {
            if(error && error.code === '42P01') {
                 tbody.innerHTML = '<tr><td colspan="3" class="text-center">click_logs 테이블이 없습니다.</td></tr>';
                 return;
            }
            tbody.innerHTML = '<tr><td colspan="3" class="text-center">데이터 없음</td></tr>';
            return;
        }

        const dealCounts = {};
        data.forEach(log => {
            const key = log.deal_id + "|||" + log.deal_title;
            dealCounts[key] = (dealCounts[key] || 0) + 1;
        });

        const topDeals = Object.entries(dealCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);

        tbody.innerHTML = topDeals.map((item, i) => {
            const [id, title] = item[0].split("|||");
            return `
                <tr>
                    <td>${i + 1}</td>
                    <td><a href="../detail.html?id=${id}" target="_blank" style="color: var(--text-primary); text-decoration: underline;">${title}</a></td>
                    <td>${item[1]}</td>
                </tr>
            `;
        }).join('');
    } catch(err) {
        document.getElementById('top-deals-tbody').innerHTML = '<tr><td colspan="3" class="text-center">오류 발생</td></tr>';
    }
}

async function fetchCrawlerStatus() {
    try {
        const { data, error } = await supabaseClient
            .from('hotdeals')
            .select('created_at')
            .order('created_at', { ascending: false })
            .limit(1);
            
        const statEl = document.getElementById('stat-crawler');
        if (error || !data || data.length === 0) {
            statEl.textContent = '데이터 없음';
            return;
        }
        
        const lastTime = new Date(data[0].created_at);
        const diffMinutes = Math.floor((new Date() - lastTime) / (1000 * 60));
        
        if (diffMinutes > 60) {
            statEl.innerHTML = `<span style="color: var(--error-color)">🚨 ${diffMinutes}분 전 (장애 의심)</span>`;
        } else {
            statEl.innerHTML = `<span style="color: var(--success-color)">🟢 ${diffMinutes}분 전 (정상)</span>`;
        }
    } catch(err) {
        document.getElementById('stat-crawler').textContent = '오류';
    }
}

function updateCharts() {
    // defaults
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';

    // 1. Traffic Chart (Line)
    const dates = Array.from(new Set([...visitDataForChart, ...searchDataForChart])).sort();
    const visitCounts = dates.map(d => visitDataForChart.filter(x => x === d).length);
    const searchCounts = dates.map(d => searchDataForChart.filter(x => x === d).length);
    
    const ctxTraffic = document.getElementById('trafficChart').getContext('2d');
    if (trafficChartInstance) trafficChartInstance.destroy();
    
    trafficChartInstance = new Chart(ctxTraffic, {
        type: 'line',
        data: {
            labels: dates.length ? dates : ['오늘'],
            datasets: [
                {
                    label: '방문자',
                    data: visitCounts.length ? visitCounts : [0],
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3, fill: true
                },
                {
                    label: '검색량',
                    data: searchCounts.length ? searchCounts : [0],
                    borderColor: '#E83E8C',
                    backgroundColor: 'rgba(232, 62, 140, 0.1)',
                    tension: 0.3, fill: true
                }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 2. Browser Chart (Doughnut)
    const ctxBrowser = document.getElementById('browserChart').getContext('2d');
    if (browserChartInstance) browserChartInstance.destroy();

    const bLabels = Object.keys(browserDataForChart);
    const bData = Object.values(browserDataForChart);
    
    browserChartInstance = new Chart(ctxBrowser, {
        type: 'doughnut',
        data: {
            labels: bLabels.length ? bLabels : ['데이터 없음'],
            datasets: [{
                data: bData.length ? bData : [1],
                backgroundColor: ['#E83E8C', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'right' } }
        }
    });
}
