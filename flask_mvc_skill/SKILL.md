---
name: Flask MVC 生成器
description: 協助建立具有 MVC 架構和模組化 HTML 模板的穩健 Flask Web 應用程式結構的技能。
---

# Flask MVC 生成器技能

此技能協助建立一個符合模型-視圖-控制器 (MVC) 模式的生產級 Flask 應用程式結構。它強調模組化、可擴展性和乾淨的程式碼實踐。

## 功能

- **專案結構**：為 Flask 應用程式設置標準目錄佈局。
- **MVC 架構**：將關注點分離為模型 (Models)、控制器 (Controllers/Blueprints) 和視圖 (Views/Templates)。
- **應用程式工廠模式**：使用 `__init__.py` 建立應用程式實例，便於測試和配置。
- **模組化模板**：包含具有 Jinja2 區塊的基礎模板，以及模組化組件 (頁眉/頁腳) 和巨集 (Macros) 的範例。
- **支援 SQLAlchemy**：包含 SQLAlchemy 的基礎設置。
- **響應式設計**：包含基本的 CSS 重置和響應式佈局啟動器。

## 使用方法

要在當前目錄 (或指定目標目錄) 中生成新的 Flask MVC 專案，請運行包含的生成腳本。

### 1. 運行生成腳本

您可以使用提供的 Python 腳本來搭建專案。

```bash
python3 scripts/generate_skeleton.py --name my_flask_app
```

*參數：*
- `--name`: (可選) 要建立的專案目錄名稱。如果未提供，預設使用 `flask_mvc_app`。
- `--force`: (可選) 如果目錄存在則覆蓋。

### 2. 安裝依賴

生成後，進入專案目錄並安裝需求。

```bash
cd my_flask_app
pip install -r requirements.txt
```

### 3. 運行應用程式

```bash
python3 run.py
```

## 結構總覽

```
project_root/
|-- app/
|   |-- __init__.py          # 應用程式工廠 (App Factory)
|   |-- models/             # 資料庫模型
|   |-- controllers/        # 路由處理 (Blueprints)
|   |-- views/              # UI 層
|       |-- static/         # CSS, JS, 圖片
|       |-- templates/      # Jinja2 模板
|           |-- base.html   # 基礎佈局
|           |-- components/ # 局部組件 (導航欄, 頁腳)
|           |-- macros/     # 可重用邏輯
|           |-- main/       # 特定頁面模板
|-- config.py               # 設定檔
|-- run.py                  # 進入點
|-- requirements.txt        # 依賴列表
```

## 自定義

- **新增模型**：在 `app/models/` 中建立繼承自 `db.Model` 的新類別。
- **新增控制器**：在 `app/controllers/` 中建立新的 blueprint 並在 `app/__init__.py` 中註冊它們。
- **修改樣式**：編輯 `app/views/static/css/style.css` 或新增新的 CSS 文件。
