
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
