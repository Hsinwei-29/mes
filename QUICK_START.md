# MES 系統內網部署 - 快速開始

## 🎯 目標
將 MES 系統部署到專用內網伺服器，實現 24/7 穩定運行

---

## 📋 方案選擇

### ✅ 方案 A：Windows 內網伺服器（推薦）
**優點**：
- 簡單易懂，不需要 Docker 知識
- 與現有 Windows 環境兼容
- 支援 Windows 服務自動啟動

**適用於**：有閒置的 Windows 電腦或 Windows Server

### ⚙️ 方案 B：Docker 容器化
**優點**：
- 環境隔離，更安全
- 易於遷移和更新
- 資源使用更高效

**適用於**：熟悉 Docker 或有 Linux 伺服器

---

## 🚀 方案 A：快速部署步驟

### 第一步：準備伺服器
1. 找一台可以 24 小時開機的 Windows 電腦
2. 設置固定內網 IP（例如：192.168.20.100）
   - 控制台 → 網路 → 變更介面卡設定 → 內容 → IPv4 → 手動設定 IP

### 第二步：複製檔案到伺服器
1. 將整個 `d:\app\mes` 資料夾複製到伺服器
2. 建議路徑：`C:\MES_Server`

### 第三步：安裝環境
在伺服器上執行：
```batch
cd C:\MES_Server
prepare_deployment.bat
```

### 第四步：測試運行
執行試運行：
```batch
python start_production.py
```
訪問測試：http://伺服器IP:5010

### 第五步：設置為服務（開機自動啟動）

#### 方法 1：使用 NSSM（推薦）
1. 下載 NSSM: https://nssm.cc/download
2. 解壓到 `C:\nssm`
3. 以管理員身份執行命令提示字元：
```batch
C:\nssm\nssm.exe install MES_System "C:\Python39\python.exe" "C:\MES_Server\start_production.py"
C:\nssm\nssm.exe set MES_System AppDirectory C:\MES_Server
C:\nssm\nssm.exe start MES_System
```

#### 方法 2：使用任務排程器（簡易）
1. 打開「工作排程器」(taskschd.msc)
2. 建立基本工作 → 名稱：MES_System
3. 觸發程序：當電腦啟動時
4. 動作：啟動程式
   - 程式：`C:\Python39\python.exe`
   - 新增引數：`C:\MES_Server\start_production.py`
   - 開始位置：`C:\MES_Server`

### 第六步：設置防火牆
以管理員身份執行：
```batch
cd C:\MES_Server
setup_firewall.bat
```

---

## 🔧 日常維護

### 備份數據
定期執行（建議每週）：
```batch
cd C:\MES_Server
backup_data.bat
```

### 查看運行狀態
1. 檢查服務：`services.msc` → 找到 MES_System
2. 查看日誌：`C:\MES_Server\logs\mes_system.log`

### 更新 Excel 檔案
將新的 Excel 檔案複製到 `C:\MES_Server\`，系統會自動檢測並重新載入

---

## 🌐 訪問地址

部署完成後，內網所有設備都可以訪問：

- **庫存看板**：http://伺服器IP:5010/
- **工單需求**：http://伺服器IP:5010/orders
- **缺料分析**：http://伺服器IP:5010/shortage
- **鑄件詳情**：http://伺服器IP:5010/casting/工作台

---

## ❓ 常見問題

### Q: 其他電腦無法訪問？
A: 
1. 確認伺服器防火牆已開放端口 5010
2. 確認其他電腦與伺服器在同一網段
3. 嘗試 ping 伺服器 IP

### Q: 服務無法啟動？
A:
1. 檢查 Python 路徑是否正確
2. 查看日誌檔案：`logs\mes_system.log`
3. 手動執行測試：`python start_production.py`

### Q: 如何停止服務？
A:
- NSSM: `C:\nssm\nssm.exe stop MES_System`
- 任務排程器：右鍵 → 停用

### Q: 如何更新系統？
A:
1. 停止服務
2. 備份數據：`backup_data.bat`
3. 複製新版本檔案
4. 啟動服務

---

## 📞 技術支援

如有問題，請提供：
1. 錯誤訊息截圖
2. 日誌檔案：`logs\mes_system.log`
3. 伺服器環境資訊：`systeminfo`
