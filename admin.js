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

document.addEventListener('DOMContentLoaded', () => {
    // 날짜 기본 설정
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date-start').value = today;
    document.getElementById('date-end').value = today;

    // 데이터 로드
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

    await Promise.all([
        fetchSearchLogs(startDate, endDate),
        fetchVisitLogs(startDate, endDate),
        fetchHotdealsCount(startDate, endDate)
    ]);
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
            // 테이블이 아직 없으면 무시
            if(error.code === '42P01') {
                searchLogTbody.innerHTML = '<tr><td colspan="4" class="text-center">Supabase에 search_logs 테이블이 없습니다.</td></tr>';
                return;
            }
            throw error;
        }

        searchLogCount.textContent = count || 0;
        
        if (!data || data.length === 0) {
            searchLogTbody.innerHTML = '<tr><td colspan="4" class="text-center">조회된 검색 로그가 없습니다.</td></tr>';
            return;
        }

        searchLogTbody.innerHTML = data.map(log => {
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

        visitLogTbody.innerHTML = data.map(log => {
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
