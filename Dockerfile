FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir waitress

# 複製應用程式
COPY . .

# 創建日誌目錄
RUN mkdir -p logs

# 暴露端口
EXPOSE 5010

# 設置環境變數
ENV FLASK_ENV=production

# 啟動應用
CMD ["python", "start_production.py"]
