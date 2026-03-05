#!/bin/bash
# =============================================================
# 工單總表自動更新腳本
# 每天自動從 EIP 下載最新工單總表並更新 MES 系統
# =============================================================

# 設定路徑
MES_DIR="/home/hsinwei/app/mes"
TARGET_FILE="$MES_DIR/工單總表2026.xls"
BACKUP_DIR="$MES_DIR/workorder_backup"
LOG_FILE="$MES_DIR/logs/workorder_update.log"
DOWNLOAD_URL="http://eip.hartford.com.tw/DocLib1/%E5%B7%A5%E5%96%AE%E7%B8%BD%E8%A1%A82026.xls"
TEMP_FILE="/tmp/workorder_temp_$$.xls"

# 確保目錄存在
mkdir -p "$BACKUP_DIR"
mkdir -p "$MES_DIR/logs"

# 時間戳記
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE_TAG=$(date '+%Y%m%d_%H%M%S')

echo "======================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] 開始更新工單總表..." >> "$LOG_FILE"

# --- 1. 下載最新工單總表 ---
echo "[$TIMESTAMP] 從 EIP 下載中: $DOWNLOAD_URL" >> "$LOG_FILE"

HTTP_CODE=$(curl -s -o "$TEMP_FILE" \
    -w "%{http_code}" \
    --connect-timeout 30 \
    --max-time 120 \
    "$DOWNLOAD_URL")

if [ "$HTTP_CODE" != "200" ]; then
    echo "[$TIMESTAMP] ❌ 下載失敗！HTTP 狀態碼: $HTTP_CODE" >> "$LOG_FILE"
    rm -f "$TEMP_FILE"
    exit 1
fi

# 確認下載的是 Excel 檔案（不是 HTML 登入頁）
FILE_TYPE=$(file "$TEMP_FILE" | grep -i "excel\|OLE\|Composite\|CDFV2\|Microsoft")
FILE_SIZE=$(stat -c%s "$TEMP_FILE" 2>/dev/null || echo 0)

if [ -z "$FILE_TYPE" ] || [ "$FILE_SIZE" -lt 50000 ]; then
    echo "[$TIMESTAMP] ❌ 下載內容不是有效的 Excel 檔案 (大小: ${FILE_SIZE} bytes, 類型: $(file $TEMP_FILE))" >> "$LOG_FILE"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo "[$TIMESTAMP] ✅ 下載成功 (大小: $((FILE_SIZE / 1024)) KB)" >> "$LOG_FILE"

# --- 2. 備份舊版工單總表 ---
if [ -f "$TARGET_FILE" ]; then
    BACKUP_FILE="$BACKUP_DIR/工單總表2026_${DATE_TAG}.xls"
    cp "$TARGET_FILE" "$BACKUP_FILE"
    echo "[$TIMESTAMP] 📦 已備份舊檔案至: $BACKUP_FILE" >> "$LOG_FILE"

    # 只保留最近 30 天的備份
    find "$BACKUP_DIR" -name "*.xls" -mtime +30 -delete
    echo "[$TIMESTAMP] 🗑️  已清除 30 天前的舊備份" >> "$LOG_FILE"
fi

# --- 3. 取代新檔案 ---
mv "$TEMP_FILE" "$TARGET_FILE"
echo "[$TIMESTAMP] ✅ 工單總表已更新: $TARGET_FILE" >> "$LOG_FILE"

# --- 4. 通知 MES Flask 伺服器重新載入資料（觸發重新讀取）---
# 修改檔案的時間戳記，讓應用程式能偵測到更新
touch "$TARGET_FILE"
echo "[$TIMESTAMP] 🔄 已觸發 MES 系統重新載入工單資料" >> "$LOG_FILE"

echo "[$TIMESTAMP] ✅ 所有步驟完成！" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

exit 0
