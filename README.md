# 量化交易系統 (Quantitative Trading System)

基於永豐金證券 Shioaji API 的量化交易系統開發專案。

## 📋 專案簡介

本專案實作了一個完整的量化交易系統連線管理模組，提供與永豐金證券 Shioaji API 的整合功能，包含：

- ✅ 安全的登入/登出管理
- ✅ 憑證認證與下單權限管理
- ✅ 連線狀態監控
- ✅ **商品檔管理與查詢（v2.0）**
- ✅ **股票、期貨商品搜尋功能（v2.0）**
- ✅ **即時報價訂閱功能（v3.0）**
- ✅ **Callback 事件處理機制（v3.0）**
- ✅ **證券下單與交易功能（v4.0）**
- ✅ **訂單管理與持股查詢（v4.0）**
- ✅ **委託回報與成交回報監控（v4.1）**
- ✅ **帳戶餘額查詢與持股分析（v4.2 新增）**
- ✅ 完整的錯誤處理與日誌記錄
- ✅ 符合 SOLID 原則的物件導向設計

## 🏗️ 專案結構

```
sample-trading/
├── shioaji_connector.py       # Shioaji 連線管理核心模組
├── example_usage.py           # 基本使用範例程式
├── contract_example.py        # 商品檔查詢範例程式（v2.0）
├── quote_streaming_example.py # 即時報價訂閱範例（v3.0）
├── order_trading_example.py   # 證券下單交易範例（v4.0）
├── deal_event_example.py      # 成交回報監控範例（v4.1）
├── order_event_example.py     # 委託回報查詢範例（v4.1）
├── account_info_example.py    # 帳戶資訊查詢範例（v4.2 新增）
├── requirements.txt           # 專案依賴套件
├── 類別圖.md                 # 系統架構與類別圖文件
├── README.md                 # 專案說明文件
└── LICENSE                   # 授權條款
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

**商品檔查詢（v2.0）：**
- `get_contracts()` - 取得所有商品檔物件
- `search_stock(keyword)` - 搜尋股票（關鍵字）
- `get_stock_by_code(code)` - 精確查詢股票（代碼）
- `search_futures(keyword)` - 搜尋期貨（關鍵字）
- `get_contracts_summary()` - 取得商品統計摘要

**即時報價訂閱（v3.0）：**
- `subscribe_quote(contract, quote_type)` - 訂閱即時報價
- `unsubscribe_quote(contract)` - 取消訂閱報價
- `set_quote_callback(callback, event_type)` - 設定報價回調函數
- `get_subscribed_contracts()` - 取得已訂閱商品列表
- `get_latest_quote(code)` - 取得最新報價快照
- `clear_quote_callbacks(event_type)` - 清除回調函數

**證券下單與交易（v4.0）：**
- `place_order(contract, action, price, quantity, ...)` - 下單買賣股票
- `cancel_order(trade)` - 取消訂單
- `update_order(trade, price, quantity)` - 修改訂單
- `list_positions()` - 查詢持股明細
- `list_trades()` - 查詢今日委託明細
- `get_orders_history()` - 取得下單歷史記錄

**委託回報（Order Event）（v4.1 新增）：**
- `set_order_callback(callback)` - 設定委託回報回調函數
- `get_order_updates()` - 取得所有委託更新記錄
- `get_order_update_by_id(order_id)` - 按訂單編號查詢委託記錄
- `get_order_updates_by_status(status)` - 按狀態篩選委託記錄
- `get_order_updates_summary()` - 統計各狀態的委託數量
- `clear_order_update_callbacks()` - 清除委託回報回調

**成交回報（Deal Event）（v4.1）：**
- `set_deal_callback(callback)` - 設定成交回報回調函數
- `get_deals_history()` - 取得成交歷史記錄

**帳戶資訊查詢（v4.2 新增）：**
- `get_account_balance()` - 取得帳戶餘額資訊
- `get_account_balance_summary()` - 取得帳戶餘額摘要
- `list_positions(with_detail)` - 查詢持股明細（增強版）
- `get_positions_summary()` - 取得持股摘要統計

**主要屬性：**

- `sj` - Shioaji API 實例 (登入後可用)
- `is_connected` - 連線狀態
- `login_time` - 登入時間
- `contracts` - 商品檔物件 (v2.0)
- `subscribed_contracts` - 已訂閱商品字典 (v3.0)
- `quote_callbacks` - 報價回調函數字典 (v3.0)
- `quote_data` - 最新報價資料 (v3.0)
- `order_callbacks` - 下單回調函數字典 (v4.0)
- `orders_history` - 下單歷史記錄 (v4.0)
- `deal_callbacks` - 成交回調函數列表 (v4.1)
- `order_update_callbacks` - 委託回調函數列表 (v4.1)
- `deals_history` - 成交歷史記錄 (v4.1)
- `order_updates` - 委託更新記錄 (v4.1)

詳細的參數說明、返回值、異常處理請參考程式碼中的 docstring。

## 🔍 商品檔查詢功能（v2.0）

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
#     'contracts_loaded': True,
#     'subscribed_count': 2,
#     'callback_count': 1,
#     'orders_count': 5,
#     'deals_count': 3,  # v4.1 新增
#     'order_updates_count': 8  # v4.1 新增
# }
```

## 📡 即時報價訂閱功能（v3.0 新增）

### 基本報價訂閱

```python
from shioaji_connector import ShioajiConnector

connector = ShioajiConnector(simulation=True)
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD"
)

# 取得股票合約
stock = connector.get_stock_by_code("2330")

# 訂閱逐筆報價
connector.subscribe_quote(stock, "tick")

print("開始接收報價...")
# 報價會透過 callback 自動推送

# 取消訂閱
connector.unsubscribe_quote(stock)
```

### 使用 Callback 處理報價

```python
import time
from shioaji_connector import ShioajiConnector

# 定義報價處理函數
def quote_handler(topic, quote):
    """"處理即時報價"""
    print(f"商品: {topic}")
    print(f"價格: {quote['close']}")
    print(f"成交量: {quote['volume']}")
    print(f"時間: {quote['datetime']}")
    print("-" * 40)

connector = ShioajiConnector(simulation=True)
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD"
)

# 註冊 callback
connector.set_quote_callback(quote_handler, "tick")

# 訂閱股票
stock = connector.get_stock_by_code("2330")
connector.subscribe_quote(stock, "tick")

# 持續接收報價
time.sleep(10)

# 清理
connector.unsubscribe_quote(stock)
connector.logout()
```

### 訂閱多個股票

```python
# 訂閱多個股票
stock_codes = ["2330", "2317", "2454"]

for code in stock_codes:
    stock = connector.get_stock_by_code(code)
    if stock:
        connector.subscribe_quote(stock, "tick")
        print(f"✅ 已訂閱 {stock.code} {stock.name}")

# 查看已訂閱的商品
subscribed = connector.get_subscribed_contracts()
print(f"目前訂閱 {len(subscribed)} 個商品")
```

### 取得最新報價快照

```python
# 訂閱後可以隨時取得最新報價
quote = connector.get_latest_quote("2330")

if quote:
    print(f"最新價格: {quote['close']}")
    print(f"成交量: {quote['volume']}")
    print(f"時間: {quote['datetime']}")
```

### 多個 Callback 處理

```python
# 可以註冊多個 callback 來處理不同的邂輯

def logger_callback(topic, quote):
    """記錄日誌"""
    print(f"[LOG] {quote['code']}: {quote['close']}")

def alert_callback(topic, quote):
    """價格警示"""
    if quote['close'] > 600:
        print(f"⚠️  [警告] 價格突破 600: {quote['close']}")

# 註冊多個 callback
connector.set_quote_callback(logger_callback, "tick")
connector.set_quote_callback(alert_callback, "tick")

# 訂閱後，兩個 callback 都會被呼叫
stock = connector.get_stock_by_code("2330")
connector.subscribe_quote(stock, "tick")
```

## 💰 證券下單與交易功能（v4.0 新增）

### 基本下單操作

⚠️ **重要提醒：下單功能需要啟用憑證！**

```python
from shioaji_connector import ShioajiConnector

connector = ShioajiConnector(simulation=True)

# 登入並啟用憑證（下單必須）
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    ca_path="/path/to/cert.pfx",  # 憑證檔案
    ca_passwd="CERT_PASSWORD"       # 憑證密碼
)

# 取得股票合約
stock = connector.get_stock_by_code("2330")

# 限價買入 1000 股
trade = connector.place_order(
    contract=stock,
    action="Buy",
    price=600.0,
    quantity=1000,
    order_type="ROD",    # 當日有效單
    price_type="LMT"     # 限價單
)

if trade:
    print(f"✅ 下單成功！訂單編號: {trade.order.id}")
else:
    print("❌ 下單失敗")
```

### 市價單與零股交易

```python
# 市價買入
trade = connector.place_order(
    contract=stock,
    action="Buy",
    price=0,  # 市價單價格設 0
    quantity=1000,
    price_type="MKT"
)

# 盤中零股交易（數量 < 1000）
trade = connector.place_order(
    contract=stock,
    action="Buy",
    price=600.0,
    quantity=100,  # 零股數量
    odd_lot=True   # 標記為零股
)
```

### 訂單管理

```python
# 取消訂單
connector.cancel_order(trade)

# 修改訂單（價格和數量）
new_trade = connector.update_order(
    trade=trade,
    price=605.0,
    quantity=2000
)
```

### 查詢持股與委託

```python
# 查詢持股明細
positions = connector.list_positions()
for pos in positions:
    print(f"{pos.code}: {pos.quantity} 股, 成本: {pos.price}")

# 查詢今日委託
trades = connector.list_trades()
for trade in trades:
    print(f"{trade.contract.code}: {trade.order.action} {trade.order.quantity}")

# 查詢本次連線的下單歷史
history = connector.get_orders_history()
for order in history:
    print(f"{order['contract'].code}: {order['action']} {order['quantity']}")
```

### 委託類型說明

| 類型 | 說明 | 適用場景 |
|------|------|----------|
| **ROD** | Rest of Day 當日有效單 | 一般交易，未成交部分當日有效 |
| **IOC** | Immediate or Cancel 立即成交否則取消 | 需要快速成交，不在意部分成交 |
| **FOK** | Fill or Kill 全部成交否則取消 | 必須全部成交，不接受部分成交 |

| 價格類型 | 說明 |
|----------|------|
| **LMT** | 限價單，指定價格下單 |
| **MKT** | 市價單，以市場價格成交 |

## 📢 委託回報與成交回報（v4.1 新增）

### 重要概念說明

**委託回報（Order Event）：** 訂單狀態變更的通知
- 觸發時機：訂單提交、委託成功、部分成交、全部成交、取消等
- 資訊內容：訂單狀態、訂單編號、已成交數量
- 使用場景：追蹤訂單進度、確認委託是否成功

**成交回報（Deal Event）：** 實際成交的通知  
- 觸發時機：每次實際成交時
- 資訊內容：成交價格、成交數量、成交時間
- 使用場景：計算交易成本、更新持倉、記帳

### 委託回報監控（Order Event）

```python
from shioaji_connector import ShioajiConnector

connector = ShioajiConnector(simulation=True)
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    ca_path="/path/to/cert.pfx",
    ca_passwd="CERT_PASSWORD"
)

# 定義訂單狀態處理函數
def order_status_handler(stat):
    print(f"訂單狀態: {stat.status}")
    print(f"訂單編號: {stat.order_id}")
    print(f"已成交數量: {stat.deal_quantity}")

# 註冊回調
connector.set_order_callback(order_status_handler)

# 下單，狀態變化會自動觸發 callback
stock = connector.get_stock_by_code("2330")
connector.place_order(stock, "Buy", 600.0, 1000)
```

### 委託回報進階查詢

```python
# 按訂單編號查詢該訂單的所有狀態變更
updates = connector.get_order_update_by_id("ORDER123")
for update in updates:
    print(f"時間: {update['timestamp']}")
    print(f"狀態: {update['status']}")
    print(f"已成交: {update['deal_quantity']} 股")

# 按狀態查詢所有訂單
filled_orders = connector.get_order_updates_by_status("Filled")
print(f"已成交訂單: {len(filled_orders)} 筆")

cancelled_orders = connector.get_order_updates_by_status("Cancelled")
print(f"已取消訂單: {len(cancelled_orders)} 筆")

# 取得委託狀態統計
summary = connector.get_order_updates_summary()
print("委託狀態統計:")
for status, count in summary.items():
    print(f"  {status}: {count} 筆")
```

### 成交回報通知

```python
# 定義成交處理函數
def deal_handler(deal):
    print(f"成交通知: {deal.code}")
    print(f"成交價格: {deal.price}")
    print(f"成交數量: {deal.quantity}")
    print(f"成交時間: {deal.ts}")

# 註冊成交回調
connector.set_deal_callback(deal_handler)

# 下單成交後會自動觸發 callback
connector.place_order(stock, "Buy", 0, 1000, price_type="MKT")

# 查詢成交歷史
deals = connector.get_deals_history()
for deal in deals:
    print(f"{deal['code']}: {deal['price']} x {deal['quantity']}")
```

### 同時監控訂單和成交

```python
# 同時註冊兩種 callback
connector.set_order_callback(order_status_handler)
connector.set_deal_callback(deal_handler)

# 下單後會同時接收訂單狀態和成交回報
connector.place_order(stock, "Buy", 600.0, 1000)
```

### 查詢歷史記錄

```python
# 查詢成交歷史
deals = connector.get_deals_history()
for deal in deals:
    print(f"{deal['code']}: {deal['price']} x {deal['quantity']}")

# 查詢訂單更新歷史
updates = connector.get_order_updates()
for update in updates:
    print(f"{update['order_id']}: {update['status']}")
```

### 多個 Callback 處理

```python
# 可以為同一事件註冊多個 callback

def logger(deal):
    print(f"[LOG] 成交: {deal.code}")

def notifier(deal):
    print(f"[NOTIFY] 📢 {deal.code} 已成交")

def calculator(deal):
    cost = deal.price * deal.quantity
    print(f"[COST] 成本: {cost:,.0f} 元")

# 註冊多個 callback
connector.set_deal_callback(logger)
connector.set_deal_callback(notifier)
connector.set_deal_callback(calculator)

# 成交時所有 callback 都會被呼叫
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

### 帳戶資訊查詢範例（v4.2 新增）

```bash
python account_info_example.py
```

範例包含：
1. 查詢帳戶餘額
2. 查詢帳戶餘額摘要
3. 查詢持股明細
4. 查詢持股明細（詳細版）
5. 查詢持股摘要統計
6. 帳戶總覽
7. 持股分析
8. 檢查購買力

### 委託回報查詢範例（v4.1）

```bash
python order_event_example.py
```

範例包含：
1. 委託回報追蹤
2. 按訂單編號查詢委託記錄
3. 按狀態查詢委託記錄
4. 委託狀態統計
5. 訂單生命週期追蹤
6. 委託回報回調管理
7. 綜合委託回報追蹤

### 成交回報監控範例（v4.1）

```bash
python deal_event_example.py
```

範例包含：
1. 訂單狀態回報
2. 成交回報
3. 同時監控訂單和成交
4. 查詢成交歷史
5. 查詢訂單更新歷史
6. 註冊多個 Callback
7. 檢查連線狀態（含成交資訊）

### 證券下單交易範例（v4.0）

```bash
python order_trading_example.py
```

範例包含：
1. 基本股票下單
2. 市價下單
3. 盤中零股下單
4. IOC 委託
5. 取消訂單
6. 修改訂單
7. 查詢持股明細
8. 查詢今日委託
9. 查詢下單歷史
10. 批量下單

### 商品檔查詢範例（v2.0）

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

### 即時報價訂閱範例（v3.0 新增）

```bash
python quote_streaming_example.py
```

範例包含：
1. 基本報價訂閱
2. 使用 Callback 處理報價
3. 訂閱多個股票
4. 訂閱五檔報價
5. 取得最新報價快照
6. 註冊多個 Callback
7. 檢查連線狀態（含訂閱資訊）

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

## 🏦 帳戶資訊查詢（v4.2 新增）

### 查詢帳戶餘額

```python
from shioaji_connector import ShioajiConnector

connector = ShioajiConnector(simulation=True)
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD"
)

# 查詢帳戶餘額
balance = connector.get_account_balance()
print(f"可用餘額: {balance.available_balance:,.0f} 元")
print(f"帳戶總額: {balance.account_balance:,.0f} 元")
print(f"T日資金: {balance.T_money:,.0f} 元")

# 查詢餘額摘要（字典格式）
summary = connector.get_account_balance_summary()
print(f"可用餘額: {summary['available_balance']:,.0f} 元")
print(f"T+1日資金: {summary['T1_money']:,.0f} 元")
```

### 查詢持股資訊

```python
# 基本持股查詢
positions = connector.list_positions()
for pos in positions:
    print(f"{pos.code}: {pos.quantity} 股")

# 詳細持股查詢（字典格式）
positions = connector.list_positions(with_detail=True)
for pos in positions:
    return_rate = (pos['last_price'] - pos['price']) / pos['price'] * 100
    print(f"{pos['code']}: {return_rate:+.2f}%")

# 持股摘要統計
summary = connector.get_positions_summary()
print(f"持股檔數: {summary['total_stocks']} 檔")
print(f"總市值: {summary['total_value']:,.0f} 元")
print(f"總損益: {summary['total_pnl']:,.0f} 元")
print(f"報酬率: {summary['return_rate']:+.2f}%")
```

### 帳戶總覽

```python
# 綜合查詢
balance = connector.get_account_balance_summary()
positions = connector.get_positions_summary()

print("=== 帳戶總覽 ===")
print(f"現金: {balance['available_balance']:,.0f} 元")
print(f"股票: {positions['total_value']:,.0f} 元")
print(f"總資產: {balance['available_balance'] + positions['total_value']:,.0f} 元")
print(f"持股損益: {positions['total_pnl']:,.0f} 元 ({positions['return_rate']:+.2f}%)")
```

---

## 📝 版本記錄

### v4.2.0 (2025-10-06) - 帳戶資訊查詢與持股分析

**帳戶餘額查詢功能：**
- ✅ 實作 `get_account_balance()` 查詢帳戶餘額
- ✅ 實作 `get_account_balance_summary()` 取得餘額摘要
- ✅ 支援查詢 T/T+1/T+2 日可用資金

**持股查詢與分析功能：**
- ✅ 增強 `list_positions(with_detail)` 支援詳細資訊
- ✅ 實作 `get_positions_summary()` 持股統計
- ✅ 自動計算總市值、總損益、報酬率

**其他改進：**
- ✅ 提供原始物件和字典兩種格式
- ✅ 完整的錯誤處理與預設值
- ✅ 新增 `account_info_example.py` 範例程式
- ✅ 更新類別圖和文檔

### v4.1.0 (2025-10-06) - 委託回報與成交回報監控

**委託回報（Order Event）功能：**
- ✅ 新增 `order_update_callbacks` 屬性管理委託回調函數
- ✅ 新增 `order_updates` 屬性記錄委託更新
- ✅ 實作 `set_order_callback()` 委託狀態監控
- ✅ 實作 `get_order_updates()` 查詢所有委託記錄
- ✅ 實作 `get_order_update_by_id()` 按訂單編號查詢
- ✅ 實作 `get_order_updates_by_status()` 按狀態篩選
- ✅ 實作 `get_order_updates_summary()` 統計委託狀態
- ✅ 實作 `clear_order_update_callbacks()` 清除回調函數

**成交回報（Deal Event）功能：**
- ✅ 新增 `deal_callbacks` 屬性管理成交回調函數
- ✅ 新增 `deals_history` 屬性記錄成交歷史
- ✅ 實作 `set_deal_callback()` 成交回報監控
- ✅ 實作 `get_deals_history()` 查詢成交歷史

**其他改進：**
- ✅ 支援多個 callback 同時註冊
- ✅ 自動記錄所有成交和狀態更新
- ✅ 完整的錯誤處理與日誌
- ✅ 更新類別圖加入完整回報架構
- ✅ 新增 `deal_event_example.py` 成交回報範例
- ✅ 新增 `order_event_example.py` 委託回報範例

### v4.0.0 (2025-10-06) - 證券下單與交易

- ✅ 新增 `order_callbacks` 屬性管理下單回調
- ✅ 新增 `orders_history` 屬性記錄下單歷史
- ✅ 實作 `place_order()` 下單買賣股票
- ✅ 實作 `cancel_order()` 取消訂單
- ✅ 實作 `update_order()` 修改訂單
- ✅ 實作 `list_positions()` 查詢持股明細
- ✅ 實作 `list_trades()` 查詢委託明細
- ✅ 實作 `get_orders_history()` 查詢下單歷史
- ✅ 支援整股、盤中零股交易
- ✅ 支援限價、市價下單
- ✅ 支援 ROD、IOC、FOK 委託類型
- ✅ 完整的參數驗證與錯誤處理
- ✅ 更新類別圖加入下單架構
- ✅ 新增 `order_trading_example.py` 下單範例

### v3.0.0 (2025-10-06) - 即時報價訂閱與 Callback

- ✅ 新增 `subscribed_contracts` 屬性儲存已訂閱商品
- ✅ 新增 `quote_callbacks` 屬性管理回調函數
- ✅ 新增 `quote_data` 屬性儲存最新報價
- ✅ 實作 `subscribe_quote()` 訂閱即時報價
- ✅ 實作 `unsubscribe_quote()` 取消訂閱
- ✅ 實作 `set_quote_callback()` 設定報價回調函數
- ✅ 實作 `get_subscribed_contracts()` 查詢已訂閱商品
- ✅ 實作 `get_latest_quote()` 取得最新報價快照
- ✅ 實作 `clear_quote_callbacks()` 清除回調函數
- ✅ 支援 tick 和 bidask 兩種報價類型
- ✅ 支援多個 callback 同時註冊
- ✅ 更新類別圖加入報價訂閱架構
- ✅ 新增 `quote_streaming_example.py` 報價訂閱範例
- ✅ 完整的 callback 錯誤處理與日誌

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
**版本：** 4.2.0 (帳戶資訊查詢與持股分析)  
**作者：** Trading System Team
