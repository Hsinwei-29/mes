/**
 * 加工鑄件即時看板 - 前端互動邏輯 (中英雙語版)
 */

const API_BASE = '';
let currentLang = 'zh'; // 預設語言

// 工廠篩選全域變數
let allOrders = [];  // 儲存所有工單資料
let currentFactory = 'all';  // 當前選中的工廠
let allShortageMap = {}; // 儲存缺料狀態 {OrderNo: [PartTypes]}

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
        KEY_WIP: '在製品',
        KEY_P1: '製程一',
        KEY_P2: '製程二',
        KEY_P3: '製程三',
        KEY_W1: 'W1',
        KEY_W2: 'W2',
        KEY_W3: 'W3',
        KEY_W4: 'W4',
        KEY_M3: 'M3',
        KEY_M4: 'M4',
        KEY_P5: '製程五',
        KEY_M5: 'M5',
        KEY_P6: '製程六',
        KEY_M6: 'M6',
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
        KEY_W1: 'W1',
        KEY_W2: 'W2',
        KEY_W3: 'W3',
        KEY_W4: 'W4',
        KEY_M3: 'M3',
        KEY_M4: 'M4',
        KEY_P5: 'Proc. 5',
        KEY_M5: 'M5',
        KEY_P6: 'Proc. 6',
        KEY_M6: 'M6',
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
    'W1': 'KEY_W1',
    'W2': 'KEY_W2',
    'W3': 'KEY_W3',
    'W4': 'KEY_W4',
    '製程四': 'KEY_P4',
    'W4': 'KEY_W4',
    '製程三': 'KEY_P3',
    'M3': 'KEY_M3',
    'M4': 'KEY_M4',
    '製程五': 'KEY_P5',
    'M5': 'KEY_M5',
    '製程六': 'KEY_P6',
    'M6': 'KEY_M6',
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
        const hasOrdersTable = document.getElementById('ordersTableBody');

        // 平行載入所有需要的資料，以加快速度
        const promises = [
            fetch(`${API_BASE}/api/summary`).then(r => r.json()),
            fetch(`${API_BASE}/api/orders`).then(r => r.json())
        ];

        // 只有在工單頁面才載入缺料資料
        if (hasOrdersTable) {
            promises.push(fetch(`${API_BASE}/api/shortage`).then(r => r.json()));
        } else {
            promises.push(Promise.resolve(null));
        }

        const [data, ordersData, shortageJson] = await Promise.all(promises);

        // 1. 處理庫存概要與供需 (api/summary)
        if (data) {
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
                const count = data.inventory_details ? data.inventory_details.length : 0;
                const titleEl = document.getElementById('titleDetails');
                if (titleEl) {
                    const baseTitle = t('TITLE_DETAILS');
                    titleEl.innerHTML = `${baseTitle} <span class="badge" style="background: var(--accent-blue); font-size: 0.8rem; padding: 2px 8px; border-radius: 10px; margin-left: 8px;">${count}</span>`;
                }
                renderInventoryDetails(data.inventory_details);
            }

            // 更新時間戳
            if (document.getElementById('lastUpdate')) {
                document.getElementById('lastUpdate').textContent =
                    `${t('LAST_UPDATE')}: ${data.timestamp}`;
            }
        }

        // 2. 處理缺料資料 (api/shortage)
        if (shortageJson && shortageJson.success) {
            allShortageMap = {};
            shortageJson.data.forEach(item => {
                if (item.缺料數量 > 0) {
                    if (!allShortageMap[item.工單號碼]) {
                        allShortageMap[item.工單號碼] = [];
                    }
                    allShortageMap[item.工單號碼].push(item.零件類型);
                }
            });
        }

        // 3. 處理工單資料 (api/orders)
        if (ordersData) {
            // 工單統計 - 只有工單頁
            if (document.getElementById('ordersStats')) {
                renderOrdersStats(ordersData.stats);
            }

            // 工單表格 - 只有工單頁
            if (hasOrdersTable) {
                allOrders = ordersData.orders || [];  // 儲存所有工單
                updateFactoryCounts();  // 更新工廠計數器
                const filteredOrders = filterOrdersByFactory(currentFactory);
                renderOrdersTable(filteredOrders);
                updateOrderStats(filteredOrders);  // 更新統計（使用篩選後的資料）
            }
        }

    } catch (error) {
        console.error('載入資料失敗:', error);
        if (document.getElementById('lastUpdate')) {
            document.getElementById('lastUpdate').textContent = t('LOAD_FAILED');
        }
    }
}

// ==================== 工廠篩選函數 ====================

/**
 * 載入並顯示零庫存警示
 */
async function loadZeroStockAlert() {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/zero-stock`);
        const data = await response.json();

        const zeroModels = data.zero_models || [];

        if (zeroModels.length > 0) {
            // 創建警示橫幅
            const factorySection = document.querySelector('.factory-selector-section');
            if (factorySection) {
                // 創建警示元素
                const alertDiv = document.createElement('div');
                alertDiv.className = 'zero-stock-alert';
                alertDiv.innerHTML = `
                    <div class="alert-header">
                        <span class="alert-icon">⚠️</span>
                        <strong>零庫存鑄件警示</strong>
                        <span class="alert-count">${zeroModels.length} 個機型</span>
                    </div>
                    <div class="alert-body">
                        <div class="zero-stock-list">
                            ${zeroModels.slice(0, 30).map(m => `<span class="zero-stock-item">${m.機型}</span>`).join('')}
                            ${zeroModels.length > 30 ? `<span class="zero-stock-more">... 及其他 ${zeroModels.length - 30} 個</span>` : ''}
                        </div>
                    </div>
                `;

                // 插入到工廠選擇器之前
                factorySection.parentNode.insertBefore(alertDiv, factorySection);
            }
        }
    } catch (error) {
        console.error('載入零庫存警示失敗:', error);
    }
}

/**
 * 切換工廠視圖
 */
function switchFactory(factory) {
    currentFactory = factory;

    // 更新卡片選中狀態
    document.querySelectorAll('.factory-card').forEach(card => {
        card.classList.remove('active');
    });
    const selectedCard = document.querySelector(`[data-factory="${factory}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }

    // 篩選並重新渲染
    const filteredOrders = filterOrdersByFactory(factory);
    renderOrdersTable(filteredOrders);
    updateOrderStats(filteredOrders);
}

/**
 * 根據工廠篩選工單
 */
function filterOrdersByFactory(factory) {
    if (factory === 'all') {
        return allOrders;
    }
    return allOrders.filter(order => order.工廠 === factory);
}

/**
 * 更新工廠計數器
 */
function updateFactoryCounts() {
    const all = allOrders.length;
    const main = allOrders.filter(o => o.工廠 === 'main').length;
    const factory3 = allOrders.filter(o => o.工廠 === 'factory3').length;

    const countAll = document.getElementById('countAll');
    const countMain = document.getElementById('countMain');
    const countFactory3 = document.getElementById('countFactory3');

    if (countAll) countAll.textContent = all;
    if (countMain) countMain.textContent = main;
    if (countFactory3) countFactory3.textContent = factory3;
}

/**
 * 更新工單統計（根據篩選後的資料）
 */
function updateOrderStats(orders) {
    const today = new Date();
    const inProgress = orders.filter(o => {
        const endDate = o.生產結束 ? new Date(o.生產結束) : null;
        return !endDate || endDate >= today;
    }).length;
    const completed = orders.length - inProgress;

    const stats = {
        total: orders.length,
        in_progress: inProgress,
        completed: completed
    };

    renderOrdersStats(stats);
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

        // 如果缺料 (差異 < 0)，強制顯示 -1
        const diffDisplay = item.差異 < 0 ? '-1' : `${diffSign}${item.差異}`;

        return `
            <div class="supply-card ${statusClass}" onclick="window.location.href='/casting/${encodeURIComponent(item.鑄件)}'" style="cursor: pointer;">
                <div class="card-header">
                    <span class="card-title">${PART_ICONS[item.鑄件] || '📦'} ${tDynamic(item.鑄件)}</span>
                    <span class="card-badge ${statusClass}">${badgeText}</span>
                </div>
                <div class="card-stats">
                    <div class="stat-item">
                        <div class="stat-label">在製品</div>
                        <div class="stat-value stock">${item.半品}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">成品</div>
                        <div class="stat-value stock">${item.成品}</div>
                    </div>
                    <div class="stat-item" 
                         style="cursor: pointer; transition: all 0.2s ease; border-radius: 6px; padding: 4px;" 
                         onclick="event.stopPropagation(); window.location.href='/shortage?part=${encodeURIComponent(item.鑄件)}'" 
                         onmouseover="this.style.background='rgba(37,99,235,0.1)'; this.style.outline='1.5px solid #2563eb';" 
                         onmouseout="this.style.background=''; this.style.outline='';"
                         title="點擊查看缺料分析">
                        <div class="stat-label">${t('DEMAND')} 🔗</div>
                        <div class="stat-value demand">${item.需求}</div>
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
 * 顯示入庫對話框
 */
function showStockInDialog(partName) {
    const quantity = prompt(`請輸入 ${partName} 的入庫數量：`);
    if (quantity === null) return;

    const qty = parseInt(quantity);
    if (isNaN(qty) || qty <= 0) {
        alert('請輸入有效的數量！');
        return;
    }

    // 調用入庫 API
    fetch(`${API_BASE}/api/stock/in`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            part_name: partName,
            quantity: qty
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert(`✅ ${partName} 入庫成功！已增加 ${qty} 件到素材`);
                loadData(); // 重新載入數據
            } else {
                alert(`❌ 入庫失敗：${data.error || '未知錯誤'}`);
            }
        })
        .catch(err => {
            alert(`❌ 入庫失敗：${err.message}`);
        });
}

/**
 * 顯示出庫對話框
 */
function showStockOutDialog(partName) {
    const workOrder = prompt(`請輸入工單號碼：`);
    if (workOrder === null || !workOrder.trim()) return;

    const quantity = prompt(`請輸入 ${partName} 的出庫數量：`);
    if (quantity === null) return;

    const qty = parseInt(quantity);
    if (isNaN(qty) || qty <= 0) {
        alert('請輸入有效的數量！');
        return;
    }

    // 調用出庫 API
    fetch(`${API_BASE}/api/stock/out`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            part_name: partName,
            work_order: workOrder.trim(),
            quantity: qty
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert(`✅ ${partName} 出庫成功！工單 ${workOrder}，已扣除 ${qty} 件成品`);
                loadData(); // 重新載入數據
            } else {
                alert(`❌ 出庫失敗：${data.error || '未知錯誤'}`);
            }
        })
        .catch(err => {
            alert(`❌ 出庫失敗：${err.message}`);
        });
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
        tbody.innerHTML = `<tr><td colspan="12" class="loading">${t('NO_ORDERS')}</td></tr>`;
        return;
    }

    const today = new Date();

    tbody.innerHTML = orders.map(order => {
        const endDate = order.生產結束 ? new Date(order.生產結束) : null;
        const isComplete = endDate && endDate < today;
        const statusClass = isComplete ? 'complete' : 'active';
        const statusText = isComplete ? t('ORDER_STATUS_COMPLETE') : t('ORDER_STATUS_ACTIVE');

        // 檢查缺料狀態 helper
        const getDisplayValue = (partName, demandValue) => {
            const shortageParts = allShortageMap[order.工單] || [];
            if (shortageParts.includes(partName)) {
                return '<span style="color: #ff4444; font-weight: bold;">-1</span>';
            }
            return (demandValue !== undefined && demandValue !== null) ? demandValue : '-';
        };

        return `
            <tr>
                <td>${order.工單 || ''}</td>
                <td title="${order.物料品號 || ''}">${order.物料品號 || '-'}</td>
                <td title="${order.品號說明 || ''}">${truncateText(order.品號說明 || '-', 20)}</td>
                <td title="${order.客戶 || ''}">${truncateText(order.客戶, 15)}</td>
                <td>${order.生產開始 || '-'}</td>
                <td>${order.生產結束 || '-'}</td>
                <td>${order.工廠 === 'main' ? '本廠' : (order.工廠 === 'factory3' ? '三廠' : order.工廠)}</td>
                <td>${getDisplayValue('工作台', order.需求_工作台)}</td>
                <td>${getDisplayValue('底座', order.需求_底座)}</td>
                <td>${getDisplayValue('橫樑', order.需求_橫樑)}</td>
                <td>${getDisplayValue('立柱', order.需求_立柱)}</td>
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
    if (count === 0 || count === '0') {
        return '<span style="color: var(--text-muted)">0</span>';
    }
    if (!count) {
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
    const supplyModal = document.getElementById('supplyDetailModal');
    if (event.target == supplyModal) {
        closeSupplyDetailModal();
    }
}

/**
 * 顯示不足缺料明細 Modal
 */
async function showShortageDetailModal(partName) {
    const modal = document.getElementById('supplyDetailModal');
    const modalBody = document.getElementById('supplyModalBody');
    const modalTitle = document.getElementById('supplyModalTitle');
    if (!modal || !modalBody || !modalTitle) return;

    modalTitle.textContent = `${PART_ICONS[partName] || '📦'} ${partName} - 缺料明細`;
    modalBody.innerHTML = '<div class="loading">載入缺料資料...</div>';
    modal.style.display = 'flex';

    try {
        const response = await fetch(`${API_BASE}/api/shortage/critical/${encodeURIComponent(partName)}`);
        const data = await response.json();
        if (!data.success) throw new Error(data.error || '載入失敗');

        const critical = data.critical || [];
        const withMaterial = data.with_material || [];

        const renderRows = (items) => items.map(item => `
            <tr>
                <td><code style="font-size:0.82em;">${item.工單號碼}</code></td>
                <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.客戶名稱}">${item.客戶名稱}</td>
                <td>${item.生產結束 ? new Date(item.生產結束).toLocaleDateString('zh-TW') : '-'}</td>
                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.物料說明}">${item.物料說明}</td>
                <td style="text-align:center;">${item.需求數量}</td>
                <td style="text-align:center;">${item.已領料}</td>
                <td style="text-align:center; font-weight:bold; color:#c00;">${item.缺料數量}</td>
                <td style="text-align:center;">${item.現有素材}</td>
            </tr>
        `).join('');

        const tableHeader = `
            <thead>
                <tr style="background: linear-gradient(135deg,#667eea,#764ba2); color:white;">
                    <th>工單號碼</th><th>客戶</th><th>生產結束</th><th>物料說明</th>
                    <th>需求</th><th>已領料</th><th>缺料數量</th><th>現有素材</th>
                </tr>
            </thead>`;

        let html = '';

        // --- 嚴重缺料區塊 ---
        if (critical.length > 0) {
            html += `
                <div style="margin-bottom:1.5rem;">
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                        <span style="background:#fee2e2;color:#c00;padding:3px 10px;border-radius:12px;font-size:0.85rem;font-weight:600;">🔴 嚴重缺料 — 完全沒有素材 (${critical.length} 筆)</span>
                    </div>
                    <div class="details-table-wrapper" style="border-radius:8px;overflow:hidden;border:1px solid #fca5a5;">
                        <table class="details-table" style="width:100%;border-collapse:collapse;font-size:0.88rem;">
                            ${tableHeader}
                            <tbody>${renderRows(critical)}</tbody>
                        </table>
                    </div>
                </div>`;
        }

        // --- 可加工區塊 ---
        if (withMaterial.length > 0) {
            html += `
                <div>
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                        <span style="background:#fef9c3;color:#92400e;padding:3px 10px;border-radius:12px;font-size:0.85rem;font-weight:600;">🟡 可加工中 — 有素材可繼續 (${withMaterial.length} 筆)</span>
                    </div>
                    <div class="details-table-wrapper" style="border-radius:8px;overflow:hidden;border:1px solid #fde68a;">
                        <table class="details-table" style="width:100%;border-collapse:collapse;font-size:0.88rem;">
                            ${tableHeader}
                            <tbody>${renderRows(withMaterial)}</tbody>
                        </table>
                    </div>
                </div>`;
        }

        if (!html) {
            html = '<div style="text-align:center;padding:2rem;color:#999;">目前沒有缺料項目</div>';
        }

        modalBody.innerHTML = html;
    } catch (error) {
        console.error('Error loading shortage detail:', error);
        modalBody.innerHTML = `<div class="loading" style="color:#c00;">載入失敗: ${error.message}</div>`;
    }
}

/**
 * 顯示供需詳細資訊模態視窗 (保留舊功能: 鐵件製程明細)
 */
async function showSupplyDetailModal(partName) {
    const modal = document.getElementById('supplyDetailModal');
    const modalBody = document.getElementById('supplyModalBody');
    const modalTitle = document.getElementById('supplyModalTitle');

    if (!modal || !modalBody || !modalTitle) return;

    // 設定標題
    modalTitle.textContent = `${PART_ICONS[partName] || '📦'} ${partName} - 在製品成品明細`;

    // 顯示載入中
    modalBody.innerHTML = '<div class="loading">載入中...</div>';
    modal.style.display = 'flex';

    try {
        // 呼叫 API 取得詳細資料
        const response = await fetch(`${API_BASE}/api/part/${encodeURIComponent(partName)}`);
        const data = await response.json();

        if (!data || !data.items || data.items.length === 0) {
            modalBody.innerHTML = '<div class="loading">無資料</div>';
            return;
        }

        // 根據 CONFIGS 取得該零件的欄位定義
        const configs = {
            '底座': ['素材', 'M4', 'M3', '成品研磨'],
            '工作台': ['素材', 'W1', 'W2', 'W3', 'W4', '成品'],
            '橫樑': ['素材', 'M6', 'M5', '成品研磨'],
            '立柱': ['素材', '半品', '成品銑工', '成品研磨']
        };

        const fields = configs[partName] || [];

        // 建立表格
        let html = `
            <div class="details-table-wrapper">
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>機型</th>
                            ${fields.map(f => `<th>${f}</th>`).join('')}
                            <th>總數</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.items.forEach(item => {
            html += '<tr>';
            html += `<td><strong>${item.機型 || ''}</strong></td>`;
            fields.forEach(field => {
                const value = item[field] || 0;
                html += `<td>${value}</td>`;
            });
            html += `<td><strong>${item.總數 || 0}</strong></td>`;
            html += '</tr>';
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        modalBody.innerHTML = html;

    } catch (error) {
        console.error('Error loading supply detail:', error);
        modalBody.innerHTML = '<div class="loading">載入失敗</div>';
    }
}

/**
 * 關閉供需詳細資訊模態視窗
 */
function closeSupplyDetailModal() {
    const modal = document.getElementById('supplyDetailModal');
    if (modal) modal.style.display = 'none';
}
