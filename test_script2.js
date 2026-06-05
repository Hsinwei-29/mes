<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>物料申請 - 協鴻工業</title>
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='favicon.svg') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='index.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .page-container { padding: 2rem; max-width: 1400px; margin: 0 auto; }
        .tabs { display: flex; gap: 0; margin-bottom: 2rem; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .tab-btn {
            flex: 1; padding: 1rem 1.5rem; border: none; font-size: 1rem; font-weight: 600;
            cursor: pointer; transition: all 0.2s; background: #f0f2f5; color: #666;
        }
        .tab-btn.active { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .tab-btn:hover:not(.active) { background: #e0e4f0; color: #333; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* --- Section Cards --- */
        .card {
            background: white; border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem;
        }
        .card-title {
            font-size: 1.1rem; font-weight: 700; color: #333;
            margin-bottom: 1.25rem; padding-bottom: 0.75rem;
            border-bottom: 2px solid #f0f0f0; display: flex; align-items: center; gap: 0.5rem;
        }

        /* --- Form Grid --- */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
        .form-group { display: flex; flex-direction: column; gap: 0.4rem; }
        .form-group label { font-size: 0.875rem; font-weight: 600; color: #555; }
        .form-group input, .form-group select, .form-group textarea {
            padding: 0.6rem 0.85rem; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 0.95rem; font-family: inherit; transition: border-color 0.2s;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: #667eea;
        }
        .form-group textarea { resize: vertical; min-height: 80px; }

        /* --- Delivery Table --- */
        .delivery-table { width: 100%; border-collapse: collapse; }
        .delivery-table th {
            padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.85rem;
            background: linear-gradient(135deg, #667eea, #764ba2); color: white;
        }
        .delivery-table td { padding: 0.6rem 1rem; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }
        .delivery-table tr:hover td { background: #f8f9ff; }
        .delivery-table input[type="date"] {
            padding: 0.4rem 0.7rem; border: 1.5px solid #d0d0d0; border-radius: 6px;
            font-size: 0.9rem; font-family: inherit; width: 100%;
        }
        .delivery-table input[type="date"]:focus { outline: none; border-color: #667eea; }
        .part-badge {
            display: inline-flex; align-items: center; gap: 0.3rem;
            padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;
        }
        .badge-base { background: #e0e7ff; color: #3730a3; }
        .badge-worktable { background: #d1fae5; color: #065f46; }
        .badge-beam { background: #fef3c7; color: #92400e; }
        .badge-column { background: #fce7f3; color: #9d174d; }
        .badge-fixed { background: #e0f2fe; color: #075985; }

        /* --- Action Buttons --- */
        .btn { padding: 0.65rem 1.5rem; border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
        .btn-success { background: linear-gradient(135deg, #10b981, #059669); color: white; }
        .btn-success:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16,185,129,0.4); }
        .btn-danger { background: #fee2e2; color: #dc2626; }
        .btn-danger:hover { background: #fecaca; }
        .btn-sm { padding: 0.35rem 0.85rem; font-size: 0.82rem; }

        /* --- Shipping Table --- */
        .shipping-table { width: 100%; border-collapse: collapse; }
        .shipping-table th {
            padding: 0.75rem 1rem; text-align: left; font-weight: 600; font-size: 0.85rem;
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            white-space: nowrap;
        }
        .shipping-table td { padding: 0.6rem 1rem; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }
        .shipping-table tr:hover td { background: #f0fdf4; }
        .status-tag {
            display: inline-block; padding: 0.2rem 0.65rem; border-radius: 20px;
            font-size: 0.8rem; font-weight: 600;
        }
        .status-pending { background: #fef3c7; color: #d97706; }
        .status-approved { background: #d1fae5; color: #059669; }
        .status-rejected { background: #fee2e2; color: #dc2626; }

        /* --- Toast --- */
        .toast {
            position: fixed; bottom: 2rem; right: 2rem; padding: 0.85rem 1.5rem;
            border-radius: 10px; font-weight: 600; font-size: 0.95rem; color: white;
            z-index: 9999; transform: translateY(100px); opacity: 0; transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .toast.show { transform: translateY(0); opacity: 1; }
        .toast.success { background: #10b981; }
        .toast.error { background: #ef4444; }

        .section-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1rem; }
        .btn-pdf { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
        .btn-pdf:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59,130,246,0.4); }
        .btn-sign { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
        .btn-sign:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(245,158,11,0.4); }

        /* --- Approval Modal --- */
        .modal-overlay {
            display: none; position: fixed; top:0; left:0; width:100%; height:100%;
            background: rgba(0,0,0,0.6); z-index: 3000;
            align-items: center; justify-content: center;
        }
        .modal-overlay.open { display: flex; }
        .modal-box {
            background: white; border-radius: 16px; width: 92%; max-width: 820px;
            max-height: 90vh; overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25);
            animation: slideUp 0.25s ease;
        }
        @keyframes slideUp {
            from { transform: translateY(40px); opacity:0; }
            to   { transform: translateY(0);    opacity:1; }
        }
        .modal-header {
            padding: 1.25rem 1.5rem; background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white; border-radius: 16px 16px 0 0;
            display: flex; justify-content: space-between; align-items: center;
        }
        .modal-header h3 { margin:0; font-size:1.15rem; }
        .modal-close { background:none; border:none; color:white; font-size:1.6rem; cursor:pointer; line-height:1; }
        .modal-body { padding: 1.5rem; }
        .info-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
            gap: 0.75rem; background:#f8f9ff; border-radius:10px; padding:1rem;
            margin-bottom:1.5rem;
        }
        .info-item { display:flex; flex-direction:column; gap:2px; }
        .info-label { font-size:0.75rem; color:#888; font-weight:600; text-transform:uppercase; }
        .info-value { font-size:0.95rem; font-weight:600; color:#222; }
        .form-section-title { grid-column: 1/-1; font-size: 0.9rem; font-weight: 700; color: #15803d; margin-top: 0.5rem; border-left: 4px solid #10b981; padding-left: 0.6rem; }

        /* Approval flow */
        .flow-title { font-size:1rem; font-weight:700; color:#333; margin-bottom:1rem;
            display:flex; align-items:center; gap:0.5rem; }
        .flow-steps { display: flex; gap: 0; align-items: stretch; flex-wrap: wrap; }
        .flow-arrow {
            display:flex; align-items:center; padding: 0 0.3rem;
            color:#ccc; font-size:1.5rem;
        }
        .step-card {
            flex: 1; min-width: 160px; border: 2px solid #e0e0e0; border-radius:12px;
            padding:1rem; text-align:center; transition: all 0.2s;
            background: white;
        }
        .step-card.signed { border-color:#10b981; background:#f0fdf4; }
        .step-card.pending { border-color:#e0e0e0; }
        .step-role { font-size:0.75rem; font-weight:700; color:#666; margin-bottom:0.5rem; letter-spacing:0.05em; }
        .step-signer { font-size:0.85rem; font-weight:700; color:#059669; margin-top:0.3rem; }
        .step-time { font-size:0.7rem; color:#888; margin-top:0.1rem; }
        .step-sig-img { width:100%; max-height:70px; object-fit:contain; border:1px solid #eee; border-radius:6px; background:white; }
        .step-pending-label { font-size:0.85rem; color:#bbb; margin-bottom:0.5rem;
            display:flex; align-items:center; justify-content:center; min-height:50px; }
        .btn-do-sign {
            padding: 0.45rem 1rem; background: linear-gradient(135deg, #f59e0b, #d97706);
            color:white; border:none; border-radius:8px; font-size:0.85rem;
            font-weight:600; cursor:pointer; width:100%; transition:all 0.2s;
        }
        .btn-do-sign:hover { box-shadow: 0 3px 8px rgba(245,158,11,0.5); }
        .signed-check { font-size:1.3rem; }

        /* --- Signature Pad Sub-modal --- */
        .pad-overlay {
            display:none; position:fixed; top:0;left:0;width:100%;height:100%;
            background:rgba(0,0,0,0.75); z-index:4000;
            align-items:center; justify-content:center;
        }
        .pad-overlay.open { display:flex; }
        .pad-box {
            background:white; border-radius:14px; padding:1.5rem;
            width:92%; max-width:500px;
            box-shadow:0 20px 40px rgba(0,0,0,0.3);
            animation: slideUp 0.2s ease;
        }
        .pad-title { font-size:1rem; font-weight:700; color:#333; margin-bottom:1rem; }
        #signatureCanvas {
            width:100%; height:200px; border:2px solid #d0d0d0;
            border-radius:8px; cursor:crosshair; touch-action:none;
            background: #fafafa;
        }
        .pad-actions { display:flex; gap:0.75rem; margin-top:0.75rem; justify-content:flex-end; }
        .btn-clear { padding:0.5rem 1.2rem; background:#f3f4f6; color:#555; border:none;
            border-radius:8px; font-size:0.9rem; font-weight:600; cursor:pointer; }
        .btn-clear:hover { background:#e5e7eb; }
        .btn-confirm-sign { padding:0.5rem 1.5rem; background:linear-gradient(135deg,#10b981,#059669);
            color:white; border:none; border-radius:8px; font-size:0.9rem; font-weight:600; cursor:pointer; }
        .btn-confirm-sign:hover { box-shadow:0 3px 8px rgba(16,185,129,0.4); }
    </style>
</head>
<body>
<div class="dashboard">
    <!-- 頂部標題列 -->
    <header class="header">
        <div class="header-left">
            <div class="logo-area">
                <img src="{{ url_for('static', filename='logo.jpg') }}" alt="協鴻" class="company-logo" onerror="this.style.display='none'">
            </div>
            <h1>協鴻工業 加工鑄件看板系統</h1>
            <nav class="main-nav">
                <a href="{{ url_for('main.index') }}" class="nav-link">庫存看板</a>
                {% if current_user.is_authenticated and current_user.is_admin() %}
                <a href="{{ url_for('main.orders_page') }}" class="nav-link">工單需求</a>
                <a href="{{ url_for('main.shortage_page') }}" class="nav-link">缺料分析</a>
                <a href="{{ url_for('main.material_request_page') }}" class="nav-link active">物料申請</a>
                {% endif %}
                <a href="{{ url_for('main.lifting_page') }}" class="nav-link">吊具管理</a>
            </nav>
        </div>
        <div class="header-right">
            {% if current_user.is_authenticated %}
            <a href="{{ url_for('auth.profile') }}" class="lang-btn">⚙️ 個人資料</a>
            {% if current_user.is_admin() %}
            <a href="{{ url_for('auth.admin_dashboard') }}" class="lang-btn" style="margin-left: 0.5rem;">👤 管理員</a>
            {% endif %}
            <a href="{{ url_for('auth.logout') }}" class="lang-btn" style="margin-left: 0.5rem;">登出</a>
            {% else %}
            <a href="{{ url_for('auth.login') }}" class="lang-btn">登入</a>
            {% endif %}
            <div class="update-info">
                <span class="status-dot"></span>
                <span id="lastUpdate">物料申請系統</span>
            </div>
        </div>
    </header>

    <!-- 主要內容區 -->
    <main class="page-container">
        <h2 style="margin-bottom: 1.5rem; color: #333;">📋 物料申請管理</h2>

        <!-- 頁籤 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('delivery')">📅 鑄件允收交期</button>
            <button class="tab-btn" onclick="switchTab('shipping')">🚚 出貨單申請</button>
            <button class="tab-btn" style="background:#fbbf24; color:#92400e; flex:0.4; font-size:0.9rem;" onclick="manualSync()">
                <span style="font-size:0.75em; margin-right:4px;">⬆️</span>尋找並上傳舊資料
            </button>
        </div>

        <!-- ===== Tab 1: 鑄件允收交期 ===== -->
        <div id="tab-delivery" class="tab-content active">
            <div class="card">
                <div class="card-title">📅 鑄件允收交期設定</div>
                <p style="color:#666; font-size:0.9rem; margin-bottom:1.25rem;">
                    設定各鑄件品號的預計允收日期，系統將依此追蹤交期進度。
                </p>

                <!-- 新增表單 -->
                <div class="card" style="background:#f8f9ff; border: 1.5px dashed #c7d2fe; box-shadow:none;">
                    <div class="card-title" style="font-size:0.95rem; color:#4338ca; display:flex; justify-content:space-between; align-items:center;">
                        <span>➕ 新增允收交期</span>
                        <button class="btn btn-primary btn-sm" style="font-size:0.8rem;" onclick="openShortagePicker('delivery')">📋 從缺料分析挑選</button>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>零件類型</label>
                            <select id="d-partType">
                                <option value="">請選擇</option>
                                <option value="底座">🔲 底座</option>
                                <option value="工作台">🔳 工作台</option>
                                <option value="橫樑">📏 橫樑</option>
                                <option value="立柱">🏛️ 立柱</option>
                                <option value="定樑">🏗️ 定樑</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>品號</label>
                            <input type="text" id="d-partNo" placeholder="例：LG1370NEO-1010">
                        </div>
                        <div class="form-group">
                            <label>物料說明</label>
                            <input type="text" id="d-partDesc" placeholder="例：底座加工品">
                        </div>
                        <div class="form-group">
                            <label>預計允收日期</label>
                            <input type="date" id="d-expectedDate">
                        </div>
                        <div class="form-group">
                            <label>加工課回覆交期</label>
                            <input type="date" id="d-replyDate">
                        </div>
                        <div class="form-group">
                            <label>數量</label>
                            <input type="number" id="d-quantity" min="1" placeholder="例：10">
                        </div>
                        <div class="form-group" style="grid-column: 1/-1;">
                            <label>備註</label>
                            <textarea id="d-remark" placeholder="其他說明..."></textarea>
                        </div>
                    </div>
                    <div class="section-actions">
                        <button class="btn btn-primary" onclick="addDeliveryRecord()">➕ 新增</button>
                    </div>
                </div>

                <!-- 交期列表 -->
                <div style="overflow-x:auto;">
                    <table class="delivery-table" id="deliveryTable">
                        <thead>
                            <tr>
                                <th>零件類型</th>
                                <th>品號</th>
                                <th>物料說明</th>
                                <th>數量</th>
                                <th>預計允收日期</th>
                                <th>加工課回覆交期</th>
                                <th>狀態</th>
                                <th>備註</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody id="deliveryTableBody">
                            <tr><td colspan="10" style="text-align:center; color:#999; padding:2rem;">尚無資料，請點擊「新增」</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ===== Tab 2: 出貨單申請 ===== -->
        <div id="tab-shipping" class="tab-content">
            <div class="card">
                <div class="card-title">🚚 出貨單申請</div>
                <p style="color:#666; font-size:0.9rem; margin-bottom:1.25rem;">
                    填寫出貨申請資訊，提交後系統將記錄並追蹤出貨狀態。
                </p>

                <!-- 新增出貨表單 -->
                <div class="card" style="background:#f0fdf4; border: 1.5px dashed #86efac; box-shadow:none;">
                    <div class="card-title" style="font-size:0.95rem; color:#15803d; display:flex; justify-content:space-between; align-items:center;">
                        <span>📝 填寫出貨申請單</span>
                        <button class="btn btn-success btn-sm" style="font-size:0.8rem;" onclick="openShortagePicker('shipping')">📋 從工單需求挑選</button>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>廠商編號 <span style="color:#dc2626">*</span></label>
                            <input type="text" id="s-vendorNo" value="1G0042" readonly style="background:#f5f5f5;">
                        </div>
                        <div class="form-group">
                            <label>廠商名稱 <span style="color:#dc2626">*</span></label>
                            <input type="text" id="s-vendorName" value="加工課" readonly style="background:#f5f5f5;">
                        </div>
                        <div class="form-group">
                            <label>交貨日期 <span style="color:#dc2626">*</span></label>
                            <input type="date" id="s-shipDate">
                        </div>
                        <div class="form-group">
                            <label>採購單號</label>
                            <input type="text" id="s-poNo" placeholder="例：PO-2026-001">
                        </div>
                        <div class="form-group">
                            <label>品號 <span style="color:#dc2626">*</span></label>
                            <input type="text" id="s-partNo" placeholder="例：LG1370NEO-1010">
                        </div>
                        <div class="form-group">
                            <label>品名</label>
                            <input type="text" id="s-partName" placeholder="例：底座加工品">
                        </div>
                        <div class="form-group">
                            <label>圖號</label>
                            <input type="text" id="s-drawingNo" placeholder="例：DWG-2026-001">
                        </div>
                        <div class="form-group">
                            <label>交貨數 <span style="color:#dc2626">*</span></label>
                            <input type="number" id="s-qty" min="1" placeholder="例：10">
                        </div>
                        <div class="form-group">
                            <label>工單號碼</label>
                            <input type="text" id="s-workOrder" placeholder="例：WO-2026-001">
                        </div>
                        <div class="form-group">
                            <label>申請人</label>
                            <input type="text" id="s-applicant" value="{{ current_user.chinese_name or current_user.username }}" readonly style="background:#f5f5f5;">
                        </div>
                        <div class="form-section-title">🆔 鑄件身分證 (選填)</div>
                        <div class="form-group">
                            <label>鑄件編碼</label>
                            <input type="text" id="s-castId1" placeholder="例：爐號">
                        </div>
                        <div class="form-group">
                            <label>銑工編碼</label>
                            <input type="text" id="s-castId2" placeholder="例：序號">
                        </div>
                        <div class="form-group">
                            <label>研磨編碼</label>
                            <input type="text" id="s-castId3" placeholder="例：批號">
                        </div>
                    </div>
                    <div class="section-actions">
                        <button class="btn btn-success" onclick="addShippingRequest()">🚚 提交申請</button>
                    </div>
                </div>

                <!-- 出貨申請列表 -->
                <div style="overflow-x:auto;">
                    <table class="shipping-table">
                        <thead>
                            <tr>
                                <th style="width: 15%;">廠商資訊</th>
                                <th style="width: 10%;">交貨日期</th>
                                <th style="width: 10%;">採購/工單</th>
                                <th style="width: 20%;">物料資訊</th>
                                <th style="width: 10%;">圖號</th>
                                <th style="width: 5%;">數量</th>
                                <th style="width: 15%;">鑄件身分證</th>
                                <th style="width: 5%;">狀態</th>
                                <th style="width: 10%;">操作</th>
                            </tr>
                        </thead>
                        <tbody id="shippingTableBody">
                            <tr><td colspan="12" style="text-align:center;color:#999;padding:2rem;">尚無出貨申請</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>
</div>

<!-- Toast 通知 -->
<div id="toast" class="toast"></div>

    // ===== 頁籤切換 =====
    function switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach((btn, i) => {
            btn.classList.toggle('active', ['delivery','shipping'][i] === tabName);
        });
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        const target = document.getElementById('tab-' + tabName);
        if (target) target.classList.add('active');
    }

    // ===== 資料儲存 (Server-side API) =====
    let deliveryRecords = [];
    let shippingRecords = [];

    async function fetchFromAPI(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: { 'Content-Type': 'application/json', ...options.headers }
            });
            return await response.json();
        } catch (err) {
            console.error('API Error:', err);
            return { success: false, error: err.message };
        }
    }

    async function loadDeliveryRecords() {
        const res = await fetchFromAPI('/api/material-request/delivery');
        if (res.success) {
            deliveryRecords = res.data;
            renderDelivery();
        }
    }

    async function loadShippingRecords() {
        const res = await fetchFromAPI('/api/material-request/shipping');
        if (res.success) {
            shippingRecords = res.data;
            renderShipping();
        }
    }

    // ===== 工具函數 =====
    function showToast(msg, type = 'success') {
        const t = document.getElementById('toast');
        if (!t) return;
        t.textContent = msg;
        t.className = `toast ${type} show`;
        setTimeout(() => t.classList.remove('show'), 3000);
    }

    function getStatusClass(dateStr) {
        if (!dateStr) return { label: '未設定', cls: 'status-pending' };
        const today = new Date(); today.setHours(0,0,0,0);
        const d = new Date(dateStr);
        const diff = Math.ceil((d - today) / 86400000);
        if (diff < 0) return { label: '已逾期', cls: 'status-rejected' };
        if (diff <= 7) return { label: `還有 ${diff} 天`, cls: 'status-pending' };
        return { label: '正常', cls: 'status-approved' };
    }

    const PART_BADGE = {
        '底座': 'badge-base', '工作台': 'badge-worktable',
        '橫樑': 'badge-beam', '立柱': 'badge-column', '定樑': 'badge-fixed'
    };

    // ===== 允收交期 =====
    function renderDelivery() {
        const tbody = document.getElementById('deliveryTableBody');
        if (!tbody) return;
        if (!deliveryRecords.length) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:#999;padding:2rem;">尚無資料，請點擊「新增」</td></tr>';
            return;
        }
        const sorted = [...deliveryRecords].sort((a, b) => (a.expectedDate || '9999') > (b.expectedDate || '9999') ? 1 : -1);
        tbody.innerHTML = sorted.map((r, i) => {
            const st = getStatusClass(r.expectedDate);
            const badgeCls = PART_BADGE[r.partType] || '';
            return `
            <tr>
                <td><span class="part-badge ${badgeCls}">${r.partType}</span></td>
                <td><code style="font-size:0.85rem;">${r.partNo}</code></td>
                <td>${r.partDesc || '-'}</td>
                <td style="font-weight:600;">${r.quantity || '-'}</td>
                <td>
                    <input type="date" value="${r.expectedDate || ''}"
                        onchange="updateDeliveryDate(${r.id}, 'expectedDate', this.value)"
                        style="font-size:0.85rem;">
                </td>
                <td>
                    <input type="date" value="${r.replyDate || ''}"
                        onchange="updateDeliveryDate(${r.id}, 'replyDate', this.value)"
                        style="font-size:0.85rem; border-color: #fbbf24;">
                </td>
                <td><span class="status-tag ${st.cls}">${st.label}</span></td>
                <td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${r.remark || ''}">${r.remark || '-'}</td>
                <td>
                    <div style="display:flex; gap:0.4rem;">
                        <button class="btn btn-pdf btn-sm" style="background: linear-gradient(135deg, #6366f1, #4f46e5); color:white;" onclick="sendDeliveryMail(${r.id})">📧 Mail</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteDelivery(${r.id})">🗑️ 刪除</button>
                    </div>
                </td>
            </tr>`;
        }).join('');
    }

    async function addDeliveryRecord() {
        const partType = document.getElementById('d-partType').value;
        const partNo = document.getElementById('d-partNo').value.trim();
        const partDesc = document.getElementById('d-partDesc').value.trim();
        const expectedDate = document.getElementById('d-expectedDate').value;
        const replyDate = document.getElementById('d-replyDate').value;
        const quantity = document.getElementById('d-quantity').value;
        const remark = document.getElementById('d-remark').value.trim();

        if (!partType || !partNo || !expectedDate) {
            showToast('請填寫零件類型、品號與預計允收日期', 'error');
            return;
        }
        
        const record = {
            partType, partNo, partDesc, expectedDate, replyDate, quantity, remark,
            createdAt: new Date().toLocaleDateString('zh-TW')
        };
        
        const res = await fetchFromAPI('/api/material-request/delivery', {
            method: 'POST',
            body: JSON.stringify(record)
        });

        if (res.success) {
            deliveryRecords.push(res.data);
            renderDelivery();
            ['d-partType','d-partNo','d-partDesc','d-expectedDate','d-replyDate','d-quantity','d-remark']
                .forEach(id => { document.getElementById(id).value = ''; });
            showToast('✅ 允收交期已新增');
        } else {
            showToast('新增失敗', 'error');
        }
    }

    async function updateDeliveryDate(id, field, value) {
        const res = await fetchFromAPI(`/api/material-request/delivery/${id}/update`, {
            method: 'POST',
            body: JSON.stringify({ field, value })
        });
        if (res.success) {
            const rec = deliveryRecords.find(r => r.id === id);
            if (rec) rec[field] = value;
            renderDelivery();
        }
    }

    async function deleteDelivery(id) {
        if (!confirm('確定要刪除這筆允收交期紀錄嗎？')) return;
        const res = await fetchFromAPI(`/api/material-request/delivery/${id}`, { method: 'DELETE' });
        if (res.success) {
            deliveryRecords = deliveryRecords.filter(r => r.id !== id);
            renderDelivery();
            showToast('已刪除', 'error');
        }
    }

    function sendDeliveryMail(id) {
        const r = deliveryRecords.find(x => x.id === id);
        if (!r) return;
        const subject = `【協鴻工業】鑄件允收交期通知 - ${r.partNo}`;
        const body = `您好：\n\n以下為鑄件允收交期更新資訊：\n\n● 零件類型：${r.partType}\n● 品號：${r.partNo}\n● 物料說明：${r.partDesc || '-'}\n● 數量：${r.quantity || '-'}\n● 預計允收日期：${r.expectedDate || '未設定'}\n● 加工課回覆交期：${r.replyDate || '未設定'}\n● 備註：${r.remark || '-'}\n\n此郵件由系統自動產生，謝謝。`;
        const mailtoUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.location.href = mailtoUrl;
        showToast('已開啟郵件軟體');
    }

    // ===== 出貨單申請 =====
    function renderShipping() {
        const tbody = document.getElementById('shippingTableBody');
        if (!tbody) return;
        if (!shippingRecords.length) {
            tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;color:#999;padding:2rem;">尚無出貨申請，請填寫上方表單</td></tr>';
            return;
        }
        const sorted = [...shippingRecords].sort((a, b) => b.id - a.id);
        tbody.innerHTML = sorted.map(r => `
            <tr>
                <td>
                    <div style="font-weight:600; color:#111;">${r.vendorName || '-'}</div>
                    <div style="font-size:0.75rem; color:#666;">${r.vendorNo || '-'}</div>
                </td>
                <td><strong style="font-size:0.9rem;">${r.shipDate || '-'}</strong></td>
                <td>
                    <div style="font-size:0.8rem;"><code>${r.poNo || '-'}</code></div>
                    <div style="font-size:0.8rem; margin-top:2px;"><code>${r.workOrder || '-'}</code></div>
                </td>
                <td>
                    <div style="font-weight:600; font-size:0.85rem;">${r.partNo || '-'}</div>
                    <div style="font-size:0.75rem; color:#666; white-space:normal;">${r.partName || '-'}</div>
                </td>
                <td style="font-size:0.8rem;">${r.drawingNo || '-'}</td>
                <td style="font-weight:700; color:#059669; font-size:1rem;">${r.qty || '-'}</td>
                <td style="font-size:0.75rem; color:#555;">
                    ${[r.castId1, r.castId2, r.castId3].filter(v => v).join('<br>') || '-'}
                </td>
                <td><span class="status-tag ${r.status === '已核准' ? 'status-approved' : 'status-pending'}" style="font-size:0.75rem; padding:2px 6px;">${r.status || '簽核'}</span></td>
                <td>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:4px; width: 100px;">
                        <button class="btn btn-sign btn-sm" onclick="openSignModal(${r.id})" title="簽核">✍️</button>
                        <button class="btn btn-pdf btn-sm" onclick="sendShippingMail(${r.id})" title="Mail">📧</button>
                        ${r.status === '已核准' ? `<button class="btn btn-pdf btn-sm" onclick="exportToPDF(${r.id})" title="PDF">📄</button>` : ''}
                        <button class="btn btn-danger btn-sm" onclick="deleteShipping(${r.id})" title="刪除">🗑️</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async function addShippingRequest() {
        const vendorNo = document.getElementById('s-vendorNo').value.trim();
        const vendorName = document.getElementById('s-vendorName').value.trim();
        const shipDate = document.getElementById('s-shipDate').value;
        const poNo = document.getElementById('s-poNo').value.trim();
        const partNo = document.getElementById('s-partNo').value.trim();
        const partName = document.getElementById('s-partName').value.trim();
        const drawingNo = document.getElementById('s-drawingNo').value.trim();
        const qty = document.getElementById('s-qty').value;
        const workOrder = document.getElementById('s-workOrder').value.trim();
        const applicant = document.getElementById('s-applicant').value;
        const castId1 = document.getElementById('s-castId1').value.trim();
        const castId2 = document.getElementById('s-castId2').value.trim();
        const castId3 = document.getElementById('s-castId3').value.trim();

        if (!vendorNo || !vendorName || !shipDate || !partNo || !qty) {
            showToast('請填寫必要欄位', 'error');
            return;
        }

        const record = {
            vendorNo, vendorName, shipDate, poNo, partNo, partName, drawingNo, qty, 
            workOrder, applicant, castId1, castId2, castId3,
            createdAt: new Date().toLocaleString('zh-TW')
        };
        
        const res = await fetchFromAPI('/api/material-request/shipping', {
            method: 'POST',
            body: JSON.stringify(record)
        });

        if (res.success) {
            shippingRecords.push(res.data);
            renderShipping();
            ['s-poNo','s-partNo','s-partName','s-drawingNo','s-qty','s-workOrder','s-castId1','s-castId2','s-castId3']
                .forEach(id => { document.getElementById(id).value = ''; });
            showToast('🚚 出貨申請已提交');
            switchTab('shipping');
        } else {
            showToast('提交失敗', 'error');
        }
    }

    async function deleteShippingRecord(id) {
        if (!confirm('確定要刪除這筆出貨申請紀錄嗎？')) return;
        const res = await fetchFromAPI(`/api/material-request/shipping/${id}`, { method: 'DELETE' });
        if (res.success) {
            shippingRecords = shippingRecords.filter(r => r.id !== id);
            renderShipping();
            showToast('已刪除', 'error');
        }
    }

    let currentPickerTarget = 'delivery';
    let shortageData = [];

    async function openShortagePicker(target) {
        try {
            currentPickerTarget = target;
            const pickerSearch = document.getElementById('pickerSearch');
            if (pickerSearch) pickerSearch.value = '';
            
            const modalTitle = document.querySelector('#pickerModal h3');
            if (modalTitle) {
                if (target === 'delivery') {
                    modalTitle.innerHTML = '📋 從缺料分析挑選項目';
                } else {
                    modalTitle.innerHTML = '📋 從工單需求挑選項目';
                }
            }

            const modal = document.getElementById('pickerModal');
            if (modal) {
                modal.classList.add('open');
            } else {
                alert('找不到彈出視窗元件 (pickerModal)');
                return;
            }
            
            const listBody = document.getElementById('pickerList');
            if (listBody) {
                listBody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;">載入中...</td></tr>';
            }

            try {
                const res = await fetch('/api/shortage');
                const data = await res.json();
                if (data.success) {
                    if (target === 'delivery') {
                        shortageData = data.data.filter(item => item.狀態 === '缺料');
                    } else {
                        shortageData = data.data;
                    }
                    renderPickerList(shortageData);
                }
            } catch (err) {
                if (listBody) listBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:red;padding:2rem;">載入失敗</td></tr>';
            }
        } catch (e) {
            alert('開啟挑選視窗時發生錯誤: ' + e.message);
        }
    }

    function renderPickerList(data) {
        const listBody = document.getElementById('pickerList');
        if (!data.length) {
            listBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:2rem;">查無符合資料</td></tr>';
            return;
        }

        listBody.innerHTML = data.map(item => {
            const isDelivery = currentPickerTarget === 'delivery';
            const showQty = isDelivery ? item.缺料數量 : (item.需求數量 - item.已領數量);
            
            return `
            <tr>
                <td>${item.工單編號 || '-'}</td>
                <td><strong style="color:#0f766e;">${item.零件品號 || '-'}</strong></td>
                <td><div style="font-size:0.8rem;color:#666;max-width:200px;white-space:normal;">${item.零件品名 || '-'}</div></td>
                <td>${item.零件類型 || '-'}</td>
                <td><span style="font-weight:bold;color:#b91c1c;">${showQty}</span></td>
                <td>
                    <span class="status-tag ${item.狀態 === '缺料' ? 'status-pending' : 'status-approved'}">${item.狀態 || '-'}</span>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="selectShortageItem('${item.工單編號}','${item.零件品號}','${item.零件品名}','${item.零件類型}','${item.缺料數量}','${item.需求數量}','${item.已領數量}')">選擇</button>
                </td>
            </tr>
            `;
        }).join('');
    }

    function filterPicker() {
        const query = document.getElementById('pickerSearch').value.toLowerCase();
        const filtered = shortageData.filter(item => 
            (item.工單編號 && item.工單編號.toLowerCase().includes(query)) ||
            (item.零件品號 && item.零件品號.toLowerCase().includes(query)) ||
            (item.零件品名 && item.零件品名.toLowerCase().includes(query))
        );
        renderPickerList(filtered);
    }

    function selectShortageItem(workOrder, partNo, partDesc, partType, shortageQty, demandQty, pickedQty) {
        if (currentPickerTarget === 'delivery') {
            document.getElementById('d-partType').value = partType;
            document.getElementById('d-partNo').value = partNo;
            document.getElementById('d-partDesc').value = partDesc;
            document.getElementById('d-quantity').value = Math.abs(shortageQty);
            switchTab('delivery');
            showToast('已帶入缺料資料');
        } else {
            const remainingQty = Math.max(0, parseInt(demandQty) - parseInt(pickedQty));
            document.getElementById('s-partNo').value = partNo;
            document.getElementById('s-partName').value = partDesc;
            document.getElementById('s-qty').value = remainingQty || demandQty;
            document.getElementById('s-workOrder').value = workOrder;
            switchTab('shipping');
            showToast('已帶入工單需求資料');
        }
        closePicker();
    }

    function closePicker() {
        document.getElementById('pickerModal').classList.remove('open');
    }

    async function manualSync() {
        try {
            const del = JSON.parse(localStorage.getItem('mes_delivery') || '[]');
            const ship = JSON.parse(localStorage.getItem('mes_shipping') || '[]');
            
            if (del.length === 0 && ship.length === 0) {
                alert('這台電腦的瀏覽器中沒有找到任何舊資料！\n請確定您是在「當初輸入資料的那台電腦」上點擊此按鈕。');
                return;
            }

            if (!confirm(`找到 ${del.length} 筆允收交期資料，以及 ${ship.length} 筆出貨申請資料。\n確定要將這些資料上傳到伺服器嗎？`)) return;

            showToast('正在上傳，請稍候...', 'success');
            
            for (const rec of del) {
                await fetchFromAPI('/api/material-request/delivery', { method: 'POST', body: JSON.stringify(rec) });
            }
            for (const rec of ship) {
                await fetchFromAPI('/api/material-request/shipping', { method: 'POST', body: JSON.stringify(rec) });
            }
            
            await loadDeliveryRecords();
            await loadShippingRecords();
            
            alert('上傳成功！現在所有電腦都可以看到這些資料了。');
        } catch (e) {
            alert('上傳失敗: ' + e.message);
        }
    }

    // ===== 初始化 =====
    document.addEventListener('DOMContentLoaded', async () => {
        // 先載入伺服器資料
        await loadDeliveryRecords();
        await loadShippingRecords();
        
        // 遷移邏輯: 如果伺服器沒資料但 localStorage 有，則上傳
        if (deliveryRecords.length === 0) {
            try {
                const local = JSON.parse(localStorage.getItem('mes_delivery') || '[]');
                if (local.length > 0) {
                    showToast('正在同步本機資料至伺服器...');
                    for (const rec of local) {
                        await fetchFromAPI('/api/material-request/delivery', { method: 'POST', body: JSON.stringify(rec) });
                    }
                    await loadDeliveryRecords();
                }
            } catch(e) {}
        }
        if (shippingRecords.length === 0) {
            try {
                const local = JSON.parse(localStorage.getItem('mes_shipping') || '[]');
                if (local.length > 0) {
                    showToast('正在同步本機資料至伺服器...');
                    for (const rec of local) {
                        await fetchFromAPI('/api/material-request/shipping', { method: 'POST', body: JSON.stringify(rec) });
                    }
                    await loadShippingRecords();
                }
            } catch(e) {}
        }
        
        const today = new Date().toISOString().split('T')[0];
        if (document.getElementById('d-expectedDate')) document.getElementById('d-expectedDate').value = today;
        if (document.getElementById('s-shipDate')) document.getElementById('s-shipDate').value = today;

        // 初始化手寫板事件
        const cv = document.getElementById('signatureCanvas');
        if (cv) {
            function startDraw(e) { e.preventDefault(); isDrawing = true; [lastX, lastY] = getPos(e, cv); }
            function draw(e) { 
                e.preventDefault(); 
                if (!isDrawing) return;
                const [x, y] = getPos(e, cv);
                signCtx.beginPath(); signCtx.moveTo(lastX, lastY);
                signCtx.lineTo(x, y); signCtx.stroke();
                [lastX, lastY] = [x, y]; 
            }
            function stopDraw(e) { e.preventDefault(); isDrawing = false; }

            cv.addEventListener('mousedown',  startDraw);
            cv.addEventListener('mousemove',  draw);
            cv.addEventListener('mouseup',    stopDraw);
            cv.addEventListener('mouseleave', stopDraw);
            cv.addEventListener('touchstart', startDraw, {passive:false});
            cv.addEventListener('touchmove',  draw,      {passive:false});
            cv.addEventListener('touchend',   stopDraw,  {passive:false});
        }
    });

    // ===== 手寫簽名板相關 =====
    const FLOW_ROLES = ['下流程簽收'];
    let currentSignId = null;
    let currentSignRole = null;
    let signCanvas, signCtx, isDrawing = false, lastX = 0, lastY = 0;

    function openSignModal(id) {
        const r = shippingRecords.find(x => x.id === id);
        if (!r) return;
        currentSignId = id;
        document.getElementById('sm-info').innerHTML = `
            <div class="info-item"><span class="info-label">廠商編號</span><span class="info-value">${r.vendorNo||'-'}</span></div>
            <div class="info-item"><span class="info-label">廠商名稱</span><span class="info-value">${r.vendorName||'-'}</span></div>
            <div class="info-item"><span class="info-label">交貨日期</span><span class="info-value">${r.shipDate||'-'}</span></div>
            <div class="info-item"><span class="info-label">採購單號</span><span class="info-value">${r.poNo||'-'}</span></div>
            <div class="info-item"><span class="info-label">品號</span><span class="info-value">${r.partNo||'-'}</span></div>
            <div class="info-item"><span class="info-label">品名</span><span class="info-value">${r.partName||'-'}</span></div>
            <div class="info-item"><span class="info-label">圖號</span><span class="info-value">${r.drawingNo||'-'}</span></div>
            <div class="info-item"><span class="info-label">交貨數</span><span class="info-value">${r.qty||'-'}</span></div>
            <div class="info-item"><span class="info-label">工單號碼</span><span class="info-value">${r.workOrder||'-'}</span></div>
            <div class="info-item"><span class="info-label">鑄件身分證</span><span class="info-value">${[r.castId1, r.castId2, r.castId3].filter(v => v).join(' / ')||'-'}</span></div>
        `;
        renderFlowSteps(r);
        document.getElementById('signModal').classList.add('open');
    }

    function closeSignModal() {
        document.getElementById('signModal').classList.remove('open');
        currentSignId = null;
    }

    function renderFlowSteps(r) {
        const sigs = r.signatures || {};
        const container = document.getElementById('sm-flow');
        if (!container) return;
        container.innerHTML = FLOW_ROLES.map((role, i) => {
            const sig = sigs[role];
            const arrow = i < FLOW_ROLES.length - 1 ? '<div class="flow-arrow">›</div>' : '';
            if (sig) {
                return `<div class="step-card signed"><div class="step-role">${role}</div><img class="step-sig-img" src="${sig.img}"><div class="step-signer">${sig.name}</div></div>${arrow}`;
            } else {
                return `<div class="step-card pending"><div class="step-role">${role}</div><button class="btn-do-sign" onclick="openPad('${role}')">✍️ 簽名</button></div>${arrow}`;
            }
        }).join('');
    }

    function openPad(role) {
        currentSignRole = role;
        document.getElementById('padRoleLabel').textContent = `「${role}」手寫簽名`;
        document.getElementById('padModal').classList.add('open');
        signCanvas = document.getElementById('signatureCanvas');
        signCanvas.width = signCanvas.offsetWidth || 440;
        signCanvas.height = signCanvas.offsetHeight || 200;
        signCtx = signCanvas.getContext('2d');
        signCtx.clearRect(0,0,signCanvas.width,signCanvas.height);
        signCtx.strokeStyle = '#1e3a8a';
        signCtx.lineWidth = 2.5;
        signCtx.lineCap = 'round';
        signCtx.lineJoin = 'round';
    }

    function closePad() { document.getElementById('padModal').classList.remove('open'); }
    function clearPad() { if (signCtx) signCtx.clearRect(0,0,signCanvas.width,signCanvas.height); }

    function getPos(e, canvas) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return [(clientX - rect.left) * scaleX, (clientY - rect.top) * scaleY];
    }

    async function confirmSign() {
        if (!currentSignId || !currentSignRole) return;
        const img = signCanvas.toDataURL('image/png');
        const res = await fetchFromAPI('/api/material-request/shipping/sign', {
            method: 'POST',
            body: JSON.stringify({
                id: currentSignId,
                role: currentSignRole,
                name: '{{ current_user.chinese_name or current_user.username }}',
                img: img
            })
        });

        if (res.success) {
            const r = shippingRecords.find(x => x.id === currentSignId);
            if (r) {
                if (!r.signatures) r.signatures = {};
                r.signatures[currentSignRole] = {
                    name: '{{ current_user.chinese_name or current_user.username }}',
                    img: img,
                    time: new Date().toLocaleString()
                };
                if (currentSignRole === '下流程簽收') r.status = '已核准';
            }
            renderFlowSteps(r);
            renderShipping();
            closePad();
            showToast('✅ 簽核完成');
        } else {
            showToast('簽核失敗', 'error');
        }
    }

<!-- 缺料挑選 Modal -->
<div id="pickerModal" class="modal-overlay" style="z-index:5000;">
    <div class="modal-box" style="max-width:900px;">
        <div class="modal-header">
            <h3>📋 從工單需求挑選項目</h3>
            <button class="modal-close" onclick="closePicker()">&times;</button>
        </div>
        <div class="modal-body">
            <div style="margin-bottom:1rem;">
                <input type="text" id="pickerSearch" placeholder="搜尋品號、說明、工單..." oninput="filterPicker()"
                    style="width:100%; padding:0.6rem 1rem; border:2px solid #e0e0e0; border-radius:10px;">
            </div>
            <div style="max-height:450px; overflow-y:auto; border-radius:8px; border:1px solid #eee;">
                <table class="delivery-table">
                    <thead style="position:sticky; top:0; z-index:10;">
                        <tr>
                            <th>類型</th>
                            <th>品號</th>
                            <th>說明</th>
                            <th>需求數</th>
                            <th>已領數</th>
                            <th>工單</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="pickerList"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- 手寫簽名板 Modal -->
<div id="padModal" class="pad-overlay">
    <div class="pad-box">
        <div class="pad-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <h3 id="padRoleLabel" class="pad-title" style="margin:0;">✍️ 手寫簽名</h3>
            <button class="modal-close" style="color:#666; background:none; border:none; font-size:1.5rem; cursor:pointer;" onclick="closePad()">×</button>
        </div>
        <div class="modal-body" style="padding:0;">
            <div style="margin-bottom:1.5rem;">
                <label style="display:block; margin-bottom:0.4rem; font-weight:600; color:#4b5563;">請在下方區域手寫簽名：</label>
                <canvas id="signatureCanvas"></canvas>
            </div>
            <div class="pad-actions">
                <button class="btn-clear" onclick="clearPad()">🗑️ 清除</button>
                <button class="btn-confirm-sign" onclick="confirmSign()">✅ 確認簽核</button>
            </div>
        </div>
    </div>
</div>

<!-- 簽核 Modal -->
<div id="signModal" class="modal-overlay">
    <div class="modal-box">
        <div class="modal-header">
            <h3>✍️ 出貨申請單簽核</h3>
            <button class="modal-close" onclick="closeSignModal()">×</button>
        </div>
        <div class="modal-body">
            <div class="flow-title">📋 申請資訊</div>
            <div class="info-grid" id="sm-info"></div>
            <div class="flow-title">🔖 簽核流程</div>
            <div class="flow-steps" id="sm-flow"></div>
        </div>
    </div>
</div>
</body>
</html>
