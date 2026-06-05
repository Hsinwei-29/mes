#!/bin/bash
# 自動備份 MES 系統資料
# 建議將此腳本加入 crontab，例如每天凌晨 2 點執行: 0 2 * * * /home/hsinwei/app/mes/backup_data.sh >> /home/hsinwei/app/mes/backups/backup.log 2>&1

# 設定目錄
APP_DIR="/home/hsinwei/app/mes"
DATA_DIR="$APP_DIR/app/data"
BACKUP_DIR="$APP_DIR/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/data_backup_$DATE.tar.gz"

# 確保備份目錄存在
mkdir -p "$BACKUP_DIR"

# 打包並壓縮資料目錄
tar -czf "$BACKUP_FILE" -C "$APP_DIR/app" data

# 刪除超過 30 天的舊備份，避免硬碟空間爆滿
find "$BACKUP_DIR" -name "data_backup_*.tar.gz" -type f -mtime +30 -delete

echo "[$DATE] 備份完成：$BACKUP_FILE"
