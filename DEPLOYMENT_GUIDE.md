# MES 系統內網部署指南

## 方案一：部署到 Windows Server（推薦）

### 1. 準備工作
- 一台 Windows Server 或 Windows 10/11 電腦（24小時開機）
- 固定內網 IP 地址（如 192.168.20.100）
- Python 3.9+ 環境

### 2. 部署步驟

#### 步驟 1：複製專案到伺服器
```bash
# 將整個 d:\app\mes 資料夾複製到伺服器
# 例如：複製到 C:\MES_Server
```

#### 步驟 2：安裝依賴
```bash
cd C:\MES_Server
pip install -r requirements.txt
pip install waitress  # 生產級 WSGI 伺服器
```

#### 步驟 3：修改配置
編輯 `config.py`，設置為生產環境：
```python
DEBUG = False
SECRET_KEY = '設置一個安全的密鑰'
```

#### 步驟 4：創建生產環境啟動腳本
創建 `start_production.py`（見下方文件）

#### 步驟 5：設置為 Windows 服務
使用 NSSM（Non-Sucking Service Manager）：
1. 下載 NSSM: https://nssm.cc/download
2. 解壓到 C:\nssm
3. 以管理員身份運行：
```bash
C:\nssm\nssm.exe install MES_System "C:\Python39\python.exe" "C:\MES_Server\start_production.py"
C:\nssm\nssm.exe set MES_System AppDirectory C:\MES_Server
C:\nssm\nssm.exe start MES_System
```

---

## 方案二：使用 Docker（進階）

### 1. 安裝 Docker Desktop
下載並安裝 Docker Desktop for Windows

### 2. 創建 Dockerfile
（見下方 Dockerfile）

### 3. 構建並運行
```bash
cd d:\app\mes
docker build -t mes-system .
docker run -d -p 5010:5010 --name mes --restart always mes-system
```

---

## 方案三：簡易背景執行（臨時方案）

### 使用 Windows 任務排程器
1. 打開「任務排程器」
2. 創建基本任務
3. 觸發程序：「當電腦啟動時」
4. 動作：啟動程序
   - 程序：`C:\Python39\python.exe`
   - 參數：`C:\MES_Server\start_production.py`

---

## 建議配置

### 內網伺服器要求
- **作業系統**：Windows Server 2016+ 或 Windows 10/11 Pro
- **記憶體**：4GB+ RAM
- **儲存空間**：20GB+ 可用空間
- **網路**：固定內網 IP（建議設置 DHCP 保留）

### 安全建議
1. 設置防火牆僅允許內網訪問
2. 定期備份 Excel 數據檔案
3. 設置強密碼保護管理員帳號

### 維護建議
1. 設置自動備份腳本（每日備份 Excel 檔案）
2. 設置日誌輪替（避免日誌檔案過大）
3. 監控伺服器運行狀態

---

## 故障排除

### 服務無法啟動
```bash
# 檢查服務狀態
C:\nssm\nssm.exe status MES_System

# 查看日誌
type C:\MES_Server\logs\error.log
```

### 無法連線
1. 檢查防火牆規則
2. 確認伺服器 IP 地址
3. 測試端口是否開啟：`telnet 192.168.20.100 5010`

---

## 下一步

1. 選擇合適的部署方案
2. 準備內網伺服器
3. 跟隨上述步驟進行部署
4. 測試訪問：`http://伺服器IP:5010`
