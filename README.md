# LLM Pydantic Agent

> 一個基於 Pydantic AI 和 MCP 協議的智能聊天機器人

## 🌟 專案簡介

這是一個現代化的 AI 聊天機器人系統，結合了 **Pydantic AI**、**MCP (Model Context Protocol)** 和 **Gradio** 技術。支援即時串流回應、工具整合，並提供友善的繁體中文介面。

## ✨ 功能特色

- 🚀 **即時串流回應** - 逐步顯示 AI 回覆，提升使用體驗
- 🛠️ **工具整合** - 支援 MCP 協議，可擴展各種外部工具
- 🌏 **繁體中文支援** - 預設使用繁體中文回應
- 📱 **現代化介面** - 基於 Gradio 的美觀 Web 介面
- 🔧 **模組化設計** - 易於擴展和維護
- 📋 **歷史記錄** - 自動儲存對話紀錄

## 🏗️ 技術架構

- **AI 框架**: Pydantic AI
- **協議支援**: MCP (Model Context Protocol)
- **Web 介面**: Gradio
- **套件管理**: uv
- **日誌系統**: Loguru + Logfire

## 📋 環境需求

- Python 3.10+
- UV [Python 套件管理工具](https://github.com/astral-sh/uv)

## 🚀 安裝設定

### 1. 複製專案

```bash
git clone <your-repo-url>
cd llm-pydanitc-agent
```

### 2. 安裝依賴

```bash
uv sync
```

### 3. 設定環境變數

**重要：請務必設定 `.env` 檔案**

在專案根目錄建立 `.env` 檔案：

```env
# OpenAI API 金鑰
OPENAI_API_KEY=your_openai_api_key_here

# 其他可選設定
# LOGFIRE_TOKEN=your_logfire_token (可選)
```

## 🎯 使用方法

### 啟動聊天機器人

```bash
python main.py
```

啟動後，瀏覽器會自動開啟 Gradio 介面，您就可以開始與 AI 對話了！

## 📁 專案結構

```
llm-pydanitc-agent/
├── main.py                    # 主程式入口
├── pyproject.toml             # 專案配置
├── mcp_servers.json           # MCP 伺服器配置
├── .env                       # 環境變數 (需自行建立)
├── prompt/
│   └── system_prompt.txt      # 系統提示詞
├── src/
│   ├── mcp_server/           # MCP 伺服器管理
│   │   ├── server_registry.py # 伺服器註冊管理
│   │   ├── types.py          # 型別定義
│   │   ├── servers/          # 自訂伺服器
│   │   └── utils/            # 工具函數
│   └── utils/
│       └── messages.py       # 訊息處理工具
└── static/                   # 靜態資源
    └── kitty.png           # 聊天機器人頭像
```

## 🔧 MCP 伺服器管理

### 目前支援的伺服器

專案預設整合了以下 MCP 伺服器：

1. **時間伺服器** (`time`)
   - 提供當前時間查詢功能
   - 時區：Asia/Taipei

2. **網路搜尋** (`ddg-search`)
   - 使用 DuckDuckGo 進行網路搜尋

3. **示範伺服器** (`demo`)
   - 自訂的示範功能伺服器

### 新增 MCP 伺服器

#### 方法一：新增外部伺服器

1. 編輯 `mcp_servers.json` 檔案：

```json
{
    "mcp_servers": {
        "your_server_name": {
            "command": "uvx",
            "args": [
                "your-mcp-package-name"
            ]
        }
    }
}
```

2. 重新啟動應用程式

#### 方法二：建立自訂伺服器

1. 在 `src/mcp_server/servers/` 目錄建立新的 Python 檔案
2. 實作 MCP 伺服器邏輯
3. 在 `mcp_servers.json` 中註冊：

```json
{
    "mcp_servers": {
        "your_custom_server": {
            "command": "python",
            "args": [
                "src/mcp_server/servers/your_server.py"
            ]
        }
    }
}
```

## ⚙️ 自訂設定

### 修改系統提示詞

編輯 `prompt/system_prompt.txt` 檔案來自訂 AI 的行為模式。

### 更換 AI 模型

在 `main.py` 中修改 `MODEL_NAME` 變數：

```python
MODEL_NAME = "openai:gpt-4o"  # 或其他支援的模型
```

### 自訂介面

Gradio 介面設定在 `main.py` 的 `main()` 函數中，您可以：
- 修改主題 (`theme="soft"`)
- 更換頭像圖片
- 調整介面佈局

## 🔍 疑難排解

### 常見問題

1. **MCP 伺服器無法啟動**
   - 檢查是否已安裝所需的執行環境 (uvx, npx, node)
   - 確認伺服器路徑是否正確
   - 若上面仍舊無法連接，請在 global 使用 pip install mcp

2. **API 金鑰錯誤**
   - 確認 `.env` 檔案中的 `OPENAI_API_KEY` 設定正確

3. **套件相依性問題**
   - 執行 `uv sync` 重新安裝依賴
