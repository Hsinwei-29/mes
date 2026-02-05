import pandas as pd
from flask import current_app
from datetime import datetime
import json
import os

# 清除快取的腳本
print("清除庫存快取...")

# 這個腳本需要在 Flask app context 中執行
# 所以我們直接刪除可能存在的快取檔案或重啟伺服器

print("請重啟伺服器以清除記憶體快取")
print("建議：關閉當前伺服器並重新執行 python run.py")
