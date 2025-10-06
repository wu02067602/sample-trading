# 量化交易系統 - 系統概覽

## 📋 系統簡介

本系統是一個基於永豐金證券 Shioaji API 的完整量化交易系統，提供從連線管理、商品查詢、即時報價、到下單交易的一站式解決方案。

## 🎯 核心功能總覽

### v1.0 - 連線管理基礎
- ✅ 登入/登出管理
- ✅ 憑證認證
- ✅ 連線狀態監控
- ✅ Context Manager 支援

### v2.0 - 商品檔管理
- ✅ 商品檔自動載入
- ✅ 股票搜尋（關鍵字、代碼）
- ✅ 期貨搜尋
- ✅ 商品統計查詢

### v3.0 - 即時報價訂閱
- ✅ Tick（逐筆）報價訂閱
- ✅ BidAsk（五檔）報價訂閱
- ✅ 報價 Callback 處理
- ✅ 最新報價快照查詢

### v4.0 - 證券下單交易
- ✅ 整股交易（1000的倍數）
- ✅ 盤中零股交易（<1000股）
- ✅ 限價單（LMT）
- ✅ 市價單（MKT）
- ✅ ROD、IOC、FOK 委託類型
- ✅ 取消訂單
- ✅ 修改訂單
- ✅ 查詢持股
- ✅ 查詢委託

### v4.1 - 委託與成交回報
- ✅ 委託回報（訂單狀態變更）
- ✅ 成交回報（實際成交通知）
- ✅ 按訂單編號查詢
- ✅ 按狀態篩選查詢
- ✅ 統計摘要
- ✅ 回調管理

## 📊 系統架構

```
┌─────────────────────────────────────────────────┐
│          ShioajiConnector 連線管理器             │
├─────────────────────────────────────────────────┤
│                                                 │
│  [連線管理] → 登入、登出、憑證認證                │
│  [商品管理] → 商品檔查詢、搜尋                    │
│  [報價管理] → 訂閱報價、Callback 處理             │
│  [交易管理] → 下單、取消、修改                    │
│  [回報管理] → 委託回報、成交回報                  │
│                                                 │
└─────────────────────────────────────────────────┘
                      ↓
         ┌────────────────────────┐
         │   Shioaji API (永豐)   │
         └────────────────────────┘
```

## 🔧 主要類別與方法

### ShioajiConnector 類別

**核心屬性：**
```python
sj                      # Shioaji API 實例
contracts               # 商品檔物件
subscribed_contracts    # 已訂閱商品
quote_data             # 最新報價快照
orders_history         # 下單歷史
deals_history          # 成交歷史
order_updates          # 委託更新記錄
```

**核心方法分類：**

#### 1. 連線管理（v1.0）
```python
login()                 # 登入
logout()                # 登出
get_connection_status() # 連線狀態
```

#### 2. 商品查詢（v2.0）
```python
get_contracts()         # 取得商品檔
search_stock()          # 搜尋股票
get_stock_by_code()     # 精確查詢
search_futures()        # 搜尋期貨
get_contracts_summary() # 商品統計
```

#### 3. 報價訂閱（v3.0）
```python
subscribe_quote()       # 訂閱報價
unsubscribe_quote()     # 取消訂閱
set_quote_callback()    # 設定報價回調
get_latest_quote()      # 最新報價
```

#### 4. 下單交易（v4.0）
```python
place_order()           # 下單
cancel_order()          # 取消訂單
update_order()          # 修改訂單
list_positions()        # 查詢持股
list_trades()           # 查詢委託
```

#### 5. 委託回報（v4.1）
```python
set_order_callback()              # 設定委託回報回調
get_order_updates()               # 取得所有委託記錄
get_order_update_by_id()          # 按ID查詢
get_order_updates_by_status()     # 按狀態查詢
get_order_updates_summary()       # 統計摘要
clear_order_update_callbacks()    # 清除回調
```

#### 6. 成交回報（v4.1）
```python
set_deal_callback()     # 設定成交回報回調
get_deals_history()     # 取得成交歷史
```

## 📝 完整使用流程

### 步驟 1: 初始化與登入

```python
from shioaji_connector import ShioajiConnector

# 建立連線器
connector = ShioajiConnector(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    simulation=True
)

# 登入並啟用憑證
connector.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    ca_path="/path/to/cert.pfx",
    ca_passwd="CERT_PASSWORD",
    fetch_contract=True  # 自動載入商品檔
)
```

### 步驟 2: 查詢商品

```python
# 搜尋台積電
stocks = connector.search_stock("2330")

# 精確查詢
tsmc = connector.get_stock_by_code("2330")
print(f"{tsmc.code} {tsmc.name}")  # 2330 台積電
```

### 步驟 3: 訂閱即時報價

```python
# 定義報價處理函數
def quote_handler(topic, quote):
    print(f"價格: {quote['close']}, 量: {quote['volume']}")

# 註冊回調並訂閱
connector.set_quote_callback(quote_handler, "tick")
connector.subscribe_quote(tsmc, "tick")
```

### 步驟 4: 設定委託與成交回報

```python
# 委託回報（訂單狀態變更）
def order_handler(stat):
    print(f"委託狀態: {stat.status}")
    print(f"已成交: {stat.deal_quantity} 股")

connector.set_order_callback(order_handler)

# 成交回報（實際成交）
def deal_handler(deal):
    print(f"成交: {deal.price} x {deal.quantity}")

connector.set_deal_callback(deal_handler)
```

### 步驟 5: 執行交易

```python
# 下單
trade = connector.place_order(
    contract=tsmc,
    action="Buy",
    price=600.0,
    quantity=1000,
    order_type="ROD",
    price_type="LMT"
)

# 回調會自動被觸發...
```

### 步驟 6: 查詢與分析

```python
# 查詢委託回報
updates = connector.get_order_updates()
filled = connector.get_order_updates_by_status("Filled")
summary = connector.get_order_updates_summary()

# 查詢成交回報
deals = connector.get_deals_history()

# 查詢持股
positions = connector.list_positions()

# 查詢委託
trades = connector.list_trades()
```

### 步驟 7: 清理與登出

```python
# 取消訂閱
connector.unsubscribe_quote(tsmc)

# 登出
connector.logout()
```

## 🎨 設計原則

### SOLID 原則體現

1. **單一職責（SRP）**
   - ShioajiConnector 專注於連線與交易管理
   - 每個方法職責單一、明確

2. **開放封閉（OCP）**
   - 可透過繼承擴展功能
   - 核心功能無需修改

3. **里氏替換（LSP）**
   - 子類別可以替換父類別使用

4. **介面隔離（ISP）**
   - 方法介面精簡、職責明確
   - 不強迫使用者依賴不需要的功能

5. **依賴反轉（DIP）**
   - 依賴 Shioaji 抽象介面
   - 不依賴具體實作細節

### 適當設計，不過度設計

- ✅ 功能完整但不複雜
- ✅ 介面清晰易用
- ✅ 擴展性良好
- ✅ 文檔完整詳細
- ✅ 錯誤處理完善

## 📈 使用統計

通過 `get_connection_status()` 可以查看系統使用統計：

```python
status = connector.get_connection_status()
# 輸出：
# {
#     'is_connected': True,
#     'login_time': '2025-10-06 10:30:00',
#     'simulation': True,
#     'api_initialized': True,
#     'contracts_loaded': True,
#     'subscribed_count': 5,        # 已訂閱商品數
#     'callback_count': 3,           # 報價回調數
#     'orders_count': 10,            # 下單次數
#     'deals_count': 8,              # 成交次數
#     'order_updates_count': 25      # 委託回報次數
# }
```

## 🔐 安全性建議

1. **不要將帳號密碼寫死在程式碼中**
2. **使用環境變數管理敏感資訊**
3. **先在模擬環境測試**
4. **下單前仔細檢查參數**
5. **定期檢查憑證有效期**

## 🚀 快速開始指南

### 最簡單的使用方式

```python
from shioaji_connector import ShioajiConnector

# 使用 Context Manager 自動管理連線
with ShioajiConnector(simulation=True) as connector:
    # 登入
    connector.login(
        person_id="YOUR_ID",
        passwd="YOUR_PASSWORD"
    )
    
    # 查詢商品
    stock = connector.get_stock_by_code("2330")
    
    # 訂閱報價
    connector.set_quote_callback(
        lambda topic, quote: print(f"價格: {quote['close']}")
    )
    connector.subscribe_quote(stock)
    
    # 執行你的交易策略...
    
# 離開 with 區塊時自動登出
```

## 📚 範例程式總覽

| 範例檔案 | 功能 | 版本 |
|---------|------|------|
| `example_usage.py` | 基本使用 | v1.0 |
| `contract_example.py` | 商品查詢 | v2.0 |
| `quote_streaming_example.py` | 即時報價 | v3.0 |
| `order_trading_example.py` | 證券下單 | v4.0 |
| `deal_event_example.py` | 成交回報 | v4.1 |
| `order_event_example.py` | 委託回報 | v4.1 |

## 🎓 學習路徑建議

### 初學者
1. 閱讀 `README.md`
2. 執行 `example_usage.py`
3. 執行 `contract_example.py`
4. 查看 `類別圖.md` 了解架構

### 進階使用者
1. 執行 `quote_streaming_example.py` 學習報價訂閱
2. 執行 `order_trading_example.py` 學習下單
3. 執行 `order_event_example.py` 學習委託回報
4. 執行 `deal_event_example.py` 學習成交回報

### 開發者
1. 研究 `shioaji_connector.py` 源碼
2. 查看 `類別圖.md` 了解完整架構
3. 根據需求擴展功能

## 💡 最佳實踐

### 1. 使用 Callback 處理異步事件

```python
# ✅ 好的做法
def quote_handler(topic, quote):
    # 快速處理，不阻塞
    price = quote['close']
    process_price(price)

connector.set_quote_callback(quote_handler)

# ❌ 不好的做法
def slow_handler(topic, quote):
    time.sleep(10)  # 阻塞太久
    # ...
```

### 2. 完整的錯誤處理

```python
# ✅ 好的做法
try:
    trade = connector.place_order(stock, "Buy", 600.0, 1000)
    if trade:
        print("下單成功")
    else:
        print("下單失敗")
except Exception as e:
    logger.error(f"錯誤: {e}")

# ❌ 不好的做法
trade = connector.place_order(stock, "Buy", 600.0, 1000)
# 沒有錯誤處理
```

### 3. 資源管理

```python
# ✅ 好的做法 - 使用 Context Manager
with ShioajiConnector() as connector:
    connector.login(...)
    # 進行交易
# 自動登出

# ✅ 也可以手動管理
connector = ShioajiConnector()
try:
    connector.login(...)
    # 進行交易
finally:
    connector.logout()
```

## 🎯 典型使用場景

### 場景 1: 盤中監控與自動交易

```python
# 監控台積電價格，突破600自動買入
def price_monitor(topic, quote):
    if quote['close'] > 600:
        stock = connector.get_stock_by_code("2330")
        connector.place_order(stock, "Buy", 0, 1000, price_type="MKT")

connector.set_quote_callback(price_monitor)
connector.subscribe_quote(tsmc)
```

### 場景 2: 批量下單與監控

```python
# 批量下單
stock_list = ["2330", "2317", "2454"]
for code in stock_list:
    stock = connector.get_stock_by_code(code)
    connector.place_order(stock, "Buy", price, 1000)

# 監控成交
def deal_tracker(deal):
    print(f"✅ {deal.code} 成交 {deal.quantity} 股")

connector.set_deal_callback(deal_tracker)
```

### 場景 3: 訂單追蹤與分析

```python
# 下單
trade = connector.place_order(stock, "Buy", 600.0, 1000)

# 追蹤該訂單的所有狀態變更
updates = connector.get_order_update_by_id(trade.order.id)
for update in updates:
    print(f"{update['timestamp']}: {update['status']}")

# 統計分析
summary = connector.get_order_updates_summary()
print(f"成功率: {summary.get('Filled', 0) / len(updates) * 100}%")
```

## 📊 功能對照表

| 功能 | 方法 | Callback | 查詢 |
|------|------|----------|------|
| **商品查詢** | `search_stock()` | - | `get_contracts()` |
| **報價訂閱** | `subscribe_quote()` | `set_quote_callback()` | `get_latest_quote()` |
| **證券下單** | `place_order()` | - | `list_trades()` |
| **委託回報** | - | `set_order_callback()` | `get_order_updates()` |
| **成交回報** | - | `set_deal_callback()` | `get_deals_history()` |

## 🔮 系統特色

### 1. 完整的功能覆蓋
從連線、查詢、報價、下單到回報，一站式解決方案

### 2. 事件驅動架構
使用 Callback 機制處理異步事件，響應及時

### 3. 靈活的查詢能力
支援按 ID、狀態、時間等多維度查詢

### 4. 完整的歷史記錄
自動記錄所有操作，便於回測和分析

### 5. 優秀的文檔
每個方法都有詳細的 docstring 和使用範例

### 6. 安全可靠
完整的錯誤處理和日誌記錄

## 📈 下一步發展

### 規劃中的功能
- [ ] 策略執行引擎
- [ ] 回測框架
- [ ] 風險管理模組
- [ ] 績效分析工具
- [ ] 資料庫整合
- [ ] Web 管理介面

### 可擴展方向
- [ ] 期貨/選擇權交易支援
- [ ] 技術指標計算
- [ ] 自動化策略執行
- [ ] 多帳戶管理
- [ ] 告警系統

## 🆘 常見問題

### Q1: 為什麼下單失敗？
A: 檢查是否已啟用憑證 (ca_path 和 ca_passwd)

### Q2: 為什麼收不到報價？
A: 檢查是否在交易時間，且是否已訂閱商品

### Q3: 如何區分委託回報和成交回報？
A: 委託回報 = 訂單狀態變更，成交回報 = 實際成交通知

### Q4: Callback 沒有被觸發？
A: 確認已註冊 callback 且訂單有狀態變化

### Q5: 如何查看系統狀態？
A: 使用 `get_connection_status()` 查看完整狀態

## 📞 技術支援

- 官方文檔：https://sinotrade.github.io/
- GitHub: https://github.com/Sinotrade/Shioaji
- 本專案文檔：`類別圖.md` 和 `README.md`

---

**文件版本：** 4.1  
**建立日期：** 2025-10-06  
**最後更新：** 2025-10-06  
**作者：** Trading System Team

**系統版本歷程：**
- v1.0: 連線管理基礎
- v2.0: 商品檔管理
- v3.0: 即時報價訂閱
- v4.0: 證券下單交易
- v4.1: 委託與成交回報
