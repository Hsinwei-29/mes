/**
 * 加工鑄件即時看板 - 前端互動邏輯
 */

const API_BASE = '';

// 鑄件圖示對應
const PART_ICONS = {
    '底座': '🔲',
    '工作台': '🔳',
    '橫樑': '📏',
    '立柱': '🏛️'
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    // 每 30 秒自動更新
    setInterval(loadDashboardData, 30000);
});

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
                `最後更新: ${data.timestamp}`;
        }

    } catch (error) {
        console.error('載入資料失敗:', error);
        if (document.getElementById('lastUpdate')) {
            document.getElementById('lastUpdate').textContent = '載入失敗，請重新整理';
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
        container.innerHTML = '<div class="loading">載入中...</div>';
        return;
    }

    container.innerHTML = data.map(item => {
        const statusClass = item.差異 >= 0 ?
            (item.差異 > 5 ? 'sufficient' : 'warning') : 'shortage';
        const badgeText = item.狀態;
        const diffClass = item.差異 >= 0 ? 'positive' : 'negative';
        const diffSign = item.差異 >= 0 ? '+' : '';

        return `
            <div class="supply-card ${statusClass}">
                <div class="card-header">
                    <span class="card-title">${PART_ICONS[item.鑄件] || '📦'} ${item.鑄件}</span>
                    <span class="card-badge ${statusClass}">${badgeText}</span>
                </div>
                <div class="card-stats">
                    <div class="stat-item">
                        <div class="stat-label">庫存量</div>
                        <div class="stat-value stock">${item.庫存}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">需求量</div>
                        <div class="stat-value demand">${item.需求}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">差異</div>
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
        container.innerHTML = '<div class="loading">載入中...</div>';
        return;
    }

    container.innerHTML = Object.entries(data).map(([name, count]) => `
        <div class="inventory-item">
            <div class="inventory-icon">${PART_ICONS[name] || '📦'}</div>
            <div class="inventory-name">${name}</div>
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
        container.innerHTML = '<div class="loading">載入中...</div>';
        return;
    }

    container.innerHTML = `
        <div class="stat-card total">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
                <div class="stat-title">總工單數</div>
                <div class="stat-number">${stats.total || 0}</div>
            </div>
        </div>
        <div class="stat-card progress">
            <div class="stat-icon">🔄</div>
            <div class="stat-content">
                <div class="stat-title">進行中</div>
                <div class="stat-number">${stats.in_progress || 0}</div>
            </div>
        </div>
        <div class="stat-card completed">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
                <div class="stat-title">已完成</div>
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
        tbody.innerHTML = '<tr><td colspan="6" class="loading">無工單資料</td></tr>';
        return;
    }

    // 只顯示前 20 筆
    const displayOrders = orders.slice(0, 20);
    const today = new Date();

    tbody.innerHTML = displayOrders.map(order => {
        const endDate = order.生產結束 ? new Date(order.生產結束) : null;
        const isComplete = endDate && endDate < today;
        const statusClass = isComplete ? 'complete' : 'active';
        const statusText = isComplete ? '已完成' : '進行中';

        return `
            <tr>
                <td>${order.工單 || ''}</td>
                <td title="${order.品號說明 || ''}">${order.品號說明 || '-'}</td>
                <td title="${order.客戶 || ''}">${truncateText(order.客戶, 15)}</td>
                <td>${order.生產開始 || '-'}</td>
                <td>${order.生產結束 || '-'}</td>
                <td>${order.需求日期 || '-'}</td>
                <td>${(order.需求_底座 !== undefined && order.需求_底座 !== null) ? order.需求_底座 : '-'}</td>
                <td>${(order.需求_工作台 !== undefined && order.需求_工作台 !== null) ? order.需求_工作台 : '-'}</td>
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
        tbody.innerHTML = '<tr><td colspan="5" class="loading">無庫存資料</td></tr>';
        return;
    }

    tbody.innerHTML = details.map(item => `
        <tr>
            <td><strong>${item.機型}</strong></td>
            <td>${formatCount(item.底座)}</td>
            <td>${formatCount(item.工作台)}</td>
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
