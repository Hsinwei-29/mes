/**
 * 加工鑄件即時看板 - 前端互動邏輯 (中英雙語版)
 */

const API_BASE = '';
let currentLang = 'zh'; // 預設語言

// 翻譯字典
const TRANSLATIONS = {
    zh: {
        APP_TITLE: '協鴻工業 加工鑄件看板系統',
        NAV_INVENTORY: '庫存看板',
        NAV_ORDERS: '工單需求',
        TITLE_SUPPLY_DEMAND: '📊 供需即時分析',
        TITLE_OVERVIEW: '📦 鑄件庫存總覽',
        TITLE_DETAILS: '📝 機型庫存明細',
        TH_MODEL: '機型',
        TH_WORKTABLE: '工作台',
        TH_BASE: '底座',
        TH_CROSSBEAM: '橫樑',
        TH_COLUMN: '立柱',
        LAST_UPDATE: '最後更新',
        LOADING: '載入中...',
        LOAD_FAILED: '載入失敗，請重新整理',
        STOCK: '庫存量',
        DEMAND: '需求量',
        DIFF: '差異',
        STATUS_SUFFICIENT: '充足',
        STATUS_WARNING: '不足',
        STATUS_SHORTAGE: '嚴重短缺',
        MODAL_TITLE_SUFFIX: '詳細製程追蹤',
        MODAL_LOADING: '正在讀取製程細節...',
        MODAL_NO_DATA: '無詳細製程資料',
        PART_BASE: '底座',
        PART_WORKTABLE: '工作台',
        PART_CROSSBEAM: '橫樑',
        PART_COLUMN: '立柱',
        KEY_RAW: '素材',
        KEY_WIP: '半品',
        KEY_P1: '製程一',
        KEY_P2: '製程二',
        KEY_P3: '製程三',
        KEY_P4: '製程四',
        KEY_P5: '製程五',
        KEY_P6: '製程六',
        KEY_P7: '製程七',
        KEY_FINISHED: '成品',
        KEY_FIN_GRINDING: '成品研磨',
        KEY_FIN_MILLING: '成品銑工',
        KEY_TOTAL: '總數',
        KEY_MODEL: '機型',
        ORDER_TOTAL: '總工單數',
        ORDER_IN_PROGRESS: '進行中',
        ORDER_COMPLETED: '已完成',
        ORDER_STATUS_ACTIVE: '進行中',
        ORDER_STATUS_COMPLETE: '已完成',
        NO_ORDERS: '無工單資料',
        NO_INVENTORY: '無庫存資料'
    },
    en: {
        APP_TITLE: 'Shieh Hung Casting Inventory Dashboard',
        NAV_INVENTORY: 'Inventory',
        NAV_ORDERS: 'Orders',
        TITLE_SUPPLY_DEMAND: '📊 Supply & Demand Analysis',
        TITLE_OVERVIEW: '📦 Inventory Overview',
        TITLE_DETAILS: '📝 Stock Details by Model',
        TH_MODEL: 'Model',
        TH_WORKTABLE: 'Worktable',
        TH_BASE: 'Base',
        TH_CROSSBEAM: 'Crossbeam',
        TH_COLUMN: 'Column',
        LAST_UPDATE: 'Last Updated',
        LOADING: 'Loading...',
        LOAD_FAILED: 'Load Failed, please refresh',
        STOCK: 'Stock',
        DEMAND: 'Demand',
        DIFF: 'Diff',
        STATUS_SUFFICIENT: 'OK',
        STATUS_WARNING: 'Low',
        STATUS_SHORTAGE: 'Critical',
        MODAL_TITLE_SUFFIX: 'Process Details',
        MODAL_LOADING: 'Loading process details...',
        MODAL_NO_DATA: 'No detailed process data',
        PART_BASE: 'Base',
        PART_WORKTABLE: 'Worktable',
        PART_CROSSBEAM: 'Crossbeam',
        PART_COLUMN: 'Column',
        KEY_RAW: 'Raw',
        KEY_WIP: 'WIP',
        KEY_P1: 'Proc. 1',
        KEY_P2: 'Proc. 2',
        KEY_P3: 'Proc. 3',
        KEY_P4: 'Proc. 4',
        KEY_P5: 'Proc. 5',
        KEY_P6: 'Proc. 6',
        KEY_P7: 'Proc. 7',
        KEY_FINISHED: 'Finished',
        KEY_FIN_GRINDING: 'Fin. Grinding',
        KEY_FIN_MILLING: 'Fin. Milling',
        KEY_TOTAL: 'Total',
        KEY_MODEL: 'Model',
        ORDER_TOTAL: 'Total Orders',
        ORDER_IN_PROGRESS: 'In Progress',
        ORDER_COMPLETED: 'Completed',
        ORDER_STATUS_ACTIVE: 'Active',
        ORDER_STATUS_COMPLETE: 'Done',
        NO_ORDERS: 'No Order Data',
        NO_INVENTORY: 'No Inventory Data'
    }
};

// 鑄件圖示對應
const PART_ICONS = {
    '底座': '🔲',
    '工作台': '🔳',
    '橫樑': '📏',
    '立柱': '🏛️'
};

// 鍵值對應 (Backend Key -> Translation Key)
const KEY_MAP = {
    '底座': 'PART_BASE',
    '工作台': 'PART_WORKTABLE',
    '橫樑': 'PART_CROSSBEAM',
    '立柱': 'PART_COLUMN',
    '素材': 'KEY_RAW',
    '半品': 'KEY_WIP',
    '製程一': 'KEY_P1',
    '製程二': 'KEY_P2',
    '製程三': 'KEY_P3',
    '製程四': 'KEY_P4',
    '製程五': 'KEY_P5',
    '製程六': 'KEY_P6',
    '製程七': 'KEY_P7',
    '成品': 'KEY_FINISHED',
    '成品研磨': 'KEY_FIN_GRINDING',
    '成品銑工': 'KEY_FIN_MILLING',
    '總數': 'KEY_TOTAL',
    '機型': 'KEY_MODEL',
    '進行中': 'ORDER_STATUS_ACTIVE',
    '已完成': 'ORDER_STATUS_COMPLETE'
};

/**
 * 取得翻譯文字 helper
 */
function t(key) {
    return TRANSLATIONS[currentLang][key] || key;
}

/**
 * 取得動態鍵值的翻譯 (例如後端傳來的 '底座')
 */
function tDynamic(backendKey) {
    const transKey = KEY_MAP[backendKey];
    if (transKey) {
        return t(transKey);
    }
    return backendKey; // 未定義則回傳原值
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    // 每 5 分鐘自動更新
    setInterval(loadDashboardData, 300000);
});

/**
 * 切換語言
 */
function toggleLanguage() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    document.getElementById('langSwitch').textContent = currentLang === 'zh' ? 'EN' : '中文';
    updateStaticUI();
    loadDashboardData(); // 重新載入數據以應用翻譯
}

/**
 * 更新靜態 UI 文字
 */
function updateStaticUI() {
    const mapping = {
        'navInventory': 'NAV_INVENTORY',
        'navOrders': 'NAV_ORDERS',
        'titleSupplyDemand': 'TITLE_SUPPLY_DEMAND',
        'titleOverview': 'TITLE_OVERVIEW',
        'titleDetails': 'TITLE_DETAILS',
        'thModel': 'TH_MODEL',
        'thWorktable': 'TH_WORKTABLE',
        'thBase': 'TH_BASE',
        'thCrossbeam': 'TH_CROSSBEAM',
        'thColumn': 'TH_COLUMN'
    };

    for (const [id, key] of Object.entries(mapping)) {
        const el = document.getElementById(id);
        if (el) el.textContent = t(key);
    }
}

/**
 * 載入所有儀表板資料
 */
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/api/summary`);
        const data = await response.json();

        // 供需分析 - 兩頁都有
        if (document.getElementById('supplyDemandCards')) {
            renderSupplyDemand(data.supply_demand);
        }

        // 庫存總覽 - 只有首頁
        if (document.getElementById('inventoryGrid')) {
            renderInventory(data.inventory);
        }

        // 庫存明細 - 只有首頁
        if (document.getElementById('detailsTableBody')) {
            renderInventoryDetails(data.inventory_details);
        }

        // 載入工單資料
        const ordersResponse = await fetch(`${API_BASE}/api/orders`);
        const ordersData = await ordersResponse.json();

        // 工單統計 - 只有工單頁
        if (document.getElementById('ordersStats')) {
            renderOrdersStats(ordersData.stats);
        }

        // 工單表格 - 只有工單頁
        if (document.getElementById('ordersTableBody')) {
            renderOrdersTable(ordersData.orders);
        }

        // 更新時間戳
        if (document.getElementById('lastUpdate')) {
            document.getElementById('lastUpdate').textContent =
                `${t('LAST_UPDATE')}: ${data.timestamp}`;
        }

    } catch (error) {
        console.error('載入資料失敗:', error);
        if (document.getElementById('lastUpdate')) {
            document.getElementById('lastUpdate').textContent = t('LOAD_FAILED');
        }
    }
}

/**
 * 渲染供需分析卡片
 */
function renderSupplyDemand(data) {
    const container = document.getElementById('supplyDemandCards');
    if (!container) return;

    if (!data || data.length === 0) {
        container.innerHTML = `<div class="loading">${t('LOADING')}</div>`;
        return;
    }

    container.innerHTML = data.map(item => {
        let statusKey = 'STATUS_WARNING';
        if (item.差異 >= 0) {
            statusKey = (item.差異 > 5 ? 'STATUS_SUFFICIENT' : 'STATUS_WARNING');
        } else {
            statusKey = 'STATUS_SHORTAGE';
        }

        const statusClass = item.差異 >= 0 ?
            (item.差異 > 5 ? 'sufficient' : 'warning') : 'shortage';

        const badgeText = t(statusKey); // 使用翻譯後的狀態文字

        const diffClass = item.差異 >= 0 ? 'positive' : 'negative';
        const diffSign = item.差異 >= 0 ? '+' : '';

        return `
            <div class="supply-card ${statusClass}">
                <div class="card-header">
                    <span class="card-title">${PART_ICONS[item.鑄件] || '📦'} ${tDynamic(item.鑄件)}</span>
                    <span class="card-badge ${statusClass}">${badgeText}</span>
                </div>
                <div class="card-stats">
                    <div class="stat-item">
                        <div class="stat-label">${t('STOCK')}</div>
                        <div class="stat-value stock">${item.庫存}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">${t('DEMAND')}</div>
                        <div class="stat-value demand">${item.需求}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">${t('DIFF')}</div>
                        <div class="stat-value diff ${diffClass}">${diffSign}${item.差異}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 渲染庫存總覽
 */
function renderInventory(data) {
    const container = document.getElementById('inventoryGrid');
    if (!container) return;

    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = `<div class="loading">${t('LOADING')}</div>`;
        return;
    }

    container.innerHTML = Object.entries(data).map(([name, count]) => `
        <div class="inventory-item" onclick="location.href='/casting/${name}'">
            <div class="inventory-icon">${PART_ICONS[name] || '📦'}</div>
            <div class="inventory-name">${tDynamic(name)}</div>
            <div class="inventory-count">${count}</div>
        </div>
    `).join('');
}

/**
 * 渲染工單統計
 */
function renderOrdersStats(stats) {
    const container = document.getElementById('ordersStats');
    if (!container) return;

    if (!stats) {
        container.innerHTML = `<div class="loading">${t('LOADING')}</div>`;
        return;
    }

    container.innerHTML = `
        <div class="stat-card total">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
                <div class="stat-title">${t('ORDER_TOTAL')}</div>
                <div class="stat-number">${stats.total || 0}</div>
            </div>
        </div>
        <div class="stat-card progress">
            <div class="stat-icon">🔄</div>
            <div class="stat-content">
                <div class="stat-title">${t('ORDER_IN_PROGRESS')}</div>
                <div class="stat-number">${stats.in_progress || 0}</div>
            </div>
        </div>
        <div class="stat-card completed">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
                <div class="stat-title">${t('ORDER_COMPLETED')}</div>
                <div class="stat-number">${stats.completed || 0}</div>
            </div>
        </div>
    `;
}

/**
 * 渲染工單表格
 */
function renderOrdersTable(orders) {
    const tbody = document.getElementById('ordersTableBody');
    if (!tbody) return;

    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="loading">${t('NO_ORDERS')}</td></tr>`;
        return;
    }

    const today = new Date();

    tbody.innerHTML = orders.map(order => {
        const endDate = order.生產結束 ? new Date(order.生產結束) : null;
        const isComplete = endDate && endDate < today;
        const statusClass = isComplete ? 'complete' : 'active';
        const statusText = isComplete ? t('ORDER_STATUS_COMPLETE') : t('ORDER_STATUS_ACTIVE');

        return `
            <tr>
                <td>${order.工單 || ''}</td>
                <td title="${order.品號說明 || ''}">${order.品號說明 || '-'}</td>
                <td title="${order.客戶 || ''}">${truncateText(order.客戶, 15)}</td>
                <td>${order.生產開始 || '-'}</td>
                <td>${order.生產結束 || '-'}</td>
                <td>${order.需求日期 || '-'}</td>
                <td>${(order.需求_工作台 !== undefined && order.需求_工作台 !== null) ? order.需求_工作台 : '-'}</td>
                <td>${(order.需求_底座 !== undefined && order.需求_底座 !== null) ? order.需求_底座 : '-'}</td>
                <td>${(order.需求_橫樑 !== undefined && order.需求_橫樑 !== null) ? order.需求_橫樑 : '-'}</td>
                <td>${(order.需求_立柱 !== undefined && order.需求_立柱 !== null) ? order.需求_立柱 : '-'}</td>
                <td><span class="status-tag ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    }).join('');
}

/**
 * 渲染庫存明細表格
 */
function renderInventoryDetails(details) {
    const tbody = document.getElementById('detailsTableBody');
    if (!tbody) return;

    if (!details || details.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="loading">${t('NO_INVENTORY')}</td></tr>`;
        return;
    }

    tbody.innerHTML = details.map(item => `
        <tr>
            <td><strong>${item.機型}</strong></td>
            <td>${formatCount(item.工作台)}</td>
            <td>${formatCount(item.底座)}</td>
            <td>${formatCount(item.橫樑)}</td>
            <td>${formatCount(item.立柱)}</td>
        </tr>
    `).join('');
}

/**
 * 格式化數量顯示
 */
function formatCount(count) {
    if (!count || count === 0) {
        return '<span style="color: var(--text-muted)">-</span>';
    }
    return `<span style="color: var(--accent-cyan)">${count}</span>`;
}

/**
 * 截斷過長文字
 */
function truncateText(text, maxLength) {
    if (!text) return '-';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}
/**
 * 彈出鑄件詳細資料
 */
async function showPartDetails(partName) {
    const modal = document.getElementById('worktableModal');
    const body = document.getElementById('modalBody');
    const title = modal.querySelector('h2');
    if (!modal || !body) return;

    modal.style.display = 'flex';
    title.innerHTML = `${PART_ICONS[partName] || '📦'} ${tDynamic(partName)} ${t('MODAL_TITLE_SUFFIX')}`;
    body.innerHTML = `<div class="loading">${t('MODAL_LOADING')}</div>`;

    try {
        const response = await fetch(`${API_BASE}/api/inventory/details/${partName}`);
        const data = await response.json(); // Data is now {headers: [], rows: []}

        if (!data || !data.rows || data.rows.length === 0) {
            body.innerHTML = `<div class="loading">${t('MODAL_NO_DATA')}</div>`;
            return;
        }

        const headers = data.headers;
        const rows = data.rows;

        // 翻譯標頭
        const translatedHeaders = headers.map(h => tDynamic(h));

        let html = `
            <table class="details-table">
                <thead>
                    <tr>
                        ${translatedHeaders.map((h, i) => `<th class="${i === headers.length - 1 ? 'highlight-final' : ''}">${h}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
        `;

        html += rows.map(row => `
            <tr>
                ${headers.map((h, i) => {
            const val = row[h];
            const isFinal = (i === headers.length - 1);
            const cellClass = isFinal ? 'highlight-final' : '';
            // 如果只有數值就不需要翻譯內容 (機型除外)
            let displayVal = val;
            // 如果是標頭為 "機型"，則加粗顯示
            if (h === '機型') {
                return `<td class="${cellClass}"><strong>${displayVal}</strong></td>`;
            }
            return `<td class="${cellClass}">${formatCount(displayVal)}</td>`;
        }).join('')}
            </tr>
        `).join('');

        html += '</tbody></table>';
        body.innerHTML = html;

    } catch (error) {
        console.error('讀取細節失敗:', error);
        body.innerHTML = `<div class="loading">${t('LOAD_FAILED')}</div>`;
    }
}

/**
 * 關閉彈窗
 */
function closeModal() {
    const modal = document.getElementById('worktableModal');
    if (modal) modal.style.display = 'none';
}

// 點擊遮罩關閉
window.onclick = function (event) {
    const modal = document.getElementById('worktableModal');
    if (event.target == modal) {
        closeModal();
    }
}
