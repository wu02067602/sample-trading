# 量化交易系統 (Quantitative Trading System)

基於永豐金證券 Shioaji API 的量化交易系統開發專案。

## 📋 專案簡介

本專案實作了一個完整的量化交易系統連線管理模組，提供與永豐金證券 Shioaji API 的整合功能，包含：

- ✅ 安全的登入/登出管理
- ✅ 憑證認證與下單權限管理
- ✅ 連線狀態監控
- ✅ **商品檔管理與查詢（v2.0 新增）**
- ✅ **股票、期貨商品搜尋功能（v2.0 新增）**
- ✅ 完整的錯誤處理與日誌記錄
- ✅ 符合 SOLID 原則的物件導向設計

## 🏗️ 專案結構

```
sample-trading/
├── shioaji_connector.py   # Shioaji 連線管理核心模組
├── example_usage.py       # 基本使用範例程式
├── contract_example.py    # 商品檔查詢範例程式（v2.0 新增）
├── requirements.txt       # 專案依賴套件
├── 類別圖.md             # 系統架構與類別圖文件
├── README.md             # 專案說明文件
└── LICENSE               # 授權條款
```

## 🚀 快速開始

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 基本使用

```python
from shioaji_connector import ShioajiConnector

# 建立連線器 (模擬環境)
connector = ShioajiConnector(simulation=True)

# 登入
connector.login(
    person_id="YOUR_PERSON_ID",  # 您的身分證字號
    passwd="YOUR_PASSWORD"        # 您的密碼
)

# 使用 connector.sj 進行後續操作
if connector.is_connected:
    print("登入成功！")
    # 在這裡執行您的交易策略
    
# 登出
connector.logout()
```

### 3. 使用 Context Manager

```python
from shioaji_connector import ShioajiConnector

# 使用 with 語句自動管理連線
with ShioajiConnector(simulation=True) as connector:
    connector.login(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD"
    )
    # 進行交易操作
    # 離開 with 區塊時自動登出
```

## 📚 詳細文件

### 類別圖與架構設計

完整的系統架構、類別關係圖、時序圖請參考：[類別圖.md](類別圖.md)

### API 文件

#### ShioajiConnector 類別

主要的連線管理類別，負責與永豐金證券 API 的互動。

**主要方法：**

**連線管理：**
- `__init__(api_key, secret_key, simulation)` - 初始化連線器
- `login(person_id, passwd, ca_path, ca_passwd, fetch_contract)` - 登入
- `logout()` - 登出
- `get_connection_status()` - 取得連線狀態
- `__enter__()` / `__exit__()` - Context Manager 支援

**商品檔查詢（v2.0 新增）：**
- `get_contracts()` - 取得所有商品檔物件
- `search_stock(keyword)` - 搜尋股票（關鍵字）
- `get_stock_by_code(code)` - 精確查詢股票（代碼）
- `search_futures(keyword)` - 搜尋期貨（關鍵字）
- `get_contracts_summary()` - 取得商品統計摘要

**主要屬性：**

- `sj` - Shioaji API 實例 (登入後可用)
- `is_connected` - 連線狀態
- `login_time` - 登入時間
- `contracts` - 商品檔物件 (v2.0 新增)

詳細的參數說明、返回值、異常處理請參考程式碼中的 docstring。

## 🔍 商品檔查詢功能（v2.0 新增）

### 基本商品查詢

```python
from shioaji_connector import ShioajiConnector

connector = ShioajiConnector(simulation=True)
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    fetch_contract=True  # 自動下載商品檔
)

# 搜尋股票（使用代碼或名稱）
stocks = connector.search_stock("2330")
for stock in stocks:
    print(f"{stock.code} {stock.name}")

# 精確查詢特定股票
stock = connector.get_stock_by_code("2330")
if stock:
    print(f"股票: {stock.code} {stock.name}")
    print(f"交易所: {stock.exchange}")

# 搜尋期貨
futures = connector.search_futures("TX")
print(f"找到 {len(futures)} 個台指期合約")

# 查看商品統計
summary = connector.get_contracts_summary()
print(f"股票總數: {summary['stocks']}")
print(f"期貨總數: {summary['futures']}")
```

### 直接訪問 contracts 屬性

```python
# 取得所有商品檔物件
contracts = connector.get_contracts()

# 或直接使用屬性
all_stocks = list(connector.contracts.Stocks)
all_futures = list(connector.contracts.Futures)
all_options = list(connector.contracts.Options)

# 進行自訂操作
for stock in all_stocks[:10]:
    print(f"{stock.code} - {stock.name}")
```

## 🔧 進階功能

### 使用憑證啟用下單功能

```python
connector = ShioajiConnector(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    simulation=False  # 正式環境
)

connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    ca_path="/path/to/certificate.pfx",  # 憑證路徑
    ca_passwd="CERT_PASSWORD"             # 憑證密碼
)

# 現在可以進行下單操作
```

### 連線狀態監控

```python
status = connector.get_connection_status()
print(status)
# 輸出：
# {
#     'is_connected': True,
#     'login_time': '2025-10-06 10:30:00',
#     'simulation': True,
#     'api_initialized': True,
#     'contracts_loaded': True  # v2.0 新增
# }
```

## 📖 使用範例

### 基本功能範例

```bash
python example_usage.py
```

範例包含：
1. 基本使用方式
2. Context Manager 使用
3. 憑證登入
4. 便利函數使用
5. 錯誤處理

### 商品檔查詢範例（v2.0 新增）

```bash
python contract_example.py
```

範例包含：
1. 取得所有商品檔
2. 搜尋股票（關鍵字搜尋）
3. 精確查詢股票（代碼查詢）
4. 搜尋期貨
5. 直接訪問 contracts 屬性
6. 檢查連線狀態（包含商品檔狀態）

## 🎯 設計原則

本專案遵循 SOLID 設計原則：

- **S (Single Responsibility)**: 單一職責，專注連線管理
- **O (Open/Closed)**: 開放擴展，封閉修改
- **L (Liskov Substitution)**: 可被子類別替換
- **I (Interface Segregation)**: 介面精簡，方法職責明確
- **D (Dependency Inversion)**: 依賴抽象而非具體實作

## 🔒 安全性注意事項

⚠️ **重要提醒：**

1. **不要將帳號密碼寫死在程式碼中**
2. **不要將 API Key 和 Secret Key 提交到版本控制**
3. **建議使用環境變數或配置檔案管理敏感資訊**
4. **先在模擬環境測試，確認無誤後再使用正式環境**

推薦做法：

```python
import os

connector = ShioajiConnector(
    api_key=os.getenv("SHIOAJI_API_KEY"),
    secret_key=os.getenv("SHIOAJI_SECRET_KEY"),
    simulation=True
)
```

## 🧪 測試

建議在模擬環境中進行測試：

```python
# 使用模擬環境
connector = ShioajiConnector(simulation=True)
```

## 🛠️ 開發環境

- Python 3.8+
- Shioaji 1.1.0+

## 📝 版本記錄

### v2.0.0 (2025-10-06) - 商品檔管理功能

- ✅ 新增 `contracts` 屬性儲存商品檔資料
- ✅ 實作 `get_contracts()` 取得商品檔物件
- ✅ 實作 `search_stock()` 股票搜尋功能
- ✅ 實作 `get_stock_by_code()` 精確股票查詢
- ✅ 實作 `search_futures()` 期貨搜尋功能
- ✅ 實作 `get_contracts_summary()` 商品統計功能
- ✅ 更新類別圖加入新功能架構
- ✅ 新增 `contract_example.py` 商品檔使用範例
- ✅ 完整的商品檔錯誤處理與日誌

### v1.0.0 (2025-10-06) - 初始版本

- ✅ 實作 ShioajiConnector 核心功能
- ✅ 登入/登出管理
- ✅ 憑證認證支援
- ✅ Context Manager 支援
- ✅ 完整的錯誤處理與日誌記錄
- ✅ 詳細的程式碼文件
- ✅ 系統架構與類別圖

## 🔮 未來規劃

- [ ] 訂單管理器 (OrderManager)
- [ ] 帳戶管理器 (AccountManager)
- [ ] 市場資料管理器 (MarketDataManager)
- [ ] 策略執行器 (StrategyExecutor)
- [ ] 回測引擎 (Backtesting Engine)
- [ ] 風險管理模組 (Risk Management)

## 📞 技術支援

- [永豐金證券 Shioaji 官方文件](https://sinotrade.github.io/)
- [永豐金證券 Shioaji GitHub](https://github.com/Sinotrade/Shioaji)

## 👥 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

請參考 [LICENSE](LICENSE) 檔案。

---

**建立日期：** 2025-10-06  
**版本：** 2.0.0 (商品檔管理功能)  
**作者：** Trading System Team
