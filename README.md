# 永豐金證券 Shioaji 交易系統

這是一個基於永豐金證券 Shioaji API 的交易系統實作。

## 功能特色

- ✅ 簡潔直觀的登入介面
- ✅ 支援 API Key 與帳號密碼兩種登入方式
- ✅ 完整的 docstring 註解
- ✅ 類別屬性 `sj` 供後續交易使用
- ✅ 類別屬性 `contracts` 供查詢商品檔
- ✅ 帳戶管理功能
- ✅ 商品檔查詢與搜尋功能
- ✅ 即時報價訂閱功能
- ✅ Callback 監控機制（報價與委託回報）
- ✅ 股票下單功能（整股與零股）
- ✅ 成交回報查詢功能
- ✅ 持倉與損益查詢功能
- ✅ 委託回報記錄與管理功能

## 安裝

```bash
pip install -r requirements.txt
```

## 快速開始

### 使用 API Key 登入（推薦）

```python
from shioaji_trader import ShioajiTrader

# 建立交易器實例
trader = ShioajiTrader()

# 登入
trader.login(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY"
)

# 使用 trader.sj 進行後續操作
print(trader.sj.stock_account)
print(trader.sj.futopt_account)

# 登出
trader.logout()
```

### 使用帳號密碼登入

```python
from shioaji_trader import ShioajiTrader

trader = ShioajiTrader()

trader.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD"
)
```

## 主要功能

### 1. 登入系統

```python
# 使用 API Key
success = trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")

# 使用帳號密碼
success = trader.login(person_id="YOUR_PERSON_ID", passwd="YOUR_PASSWORD")
```

### 2. 查看帳戶

```python
# 列出所有帳戶
accounts = trader.list_accounts()

# 查看預設證券帳戶
print(trader.stock_account)

# 查看預設期貨帳戶
print(trader.futopt_account)
```

### 3. 設定預設帳戶

```python
accounts = trader.list_accounts()
trader.set_default_account(accounts[0])
```

### 4. 查詢商品檔

商品檔在登入時會自動下載，包含證券、期貨、選擇權、指數等商品資訊。

```python
# 方法 1：使用 contracts 屬性直接訪問
tsmc = trader.contracts.Stocks["2330"]
print(f"{tsmc.code}: {tsmc.name}")

# 查詢期貨
txf = trader.contracts.Futures.TXF["TXFR1"]

# 查詢指數
tse001 = trader.contracts.Indexs.TSE["001"]
```

```python
# 方法 2：使用輔助方法查詢
stock = trader.get_stock("2330")
future = trader.get_future("TXFR1")
option = trader.get_option("TXO12000C1")
```

```python
# 方法 3：搜尋商品
results = trader.search_contracts("台積")
for contract in results:
    print(f"{contract.code}: {contract.name}")
```

### 5. 訂閱即時報價

```python
# 定義 callback 函數
def quote_callback(exchange, tick):
    print(f"{tick['code']}: 價={tick['close']}, 量={tick['volume']}")

# 設定 callback
trader.set_quote_callback(quote_callback)

# 訂閱台積電報價
tsmc = trader.get_stock("2330")
trader.subscribe_quote(tsmc)

# 取消訂閱
trader.unsubscribe_quote(tsmc)
```

### 6. 設定委託回報 Callback

```python
# 定義委託回報 callback
def order_callback(stat, msg):
    print(f"狀態: {stat}")
    print(f"訊息: {msg}")

# 設定 callback
trader.set_order_callback(order_callback)
```

### 7. 股票下單

```python
# 買進整股（1 張 = 1000 股）
trade = trader.buy_stock("2330", price=500.0, quantity=1000)

# 賣出整股
trade = trader.sell_stock("2330", price=510.0, quantity=1000)

# 買進零股（1-999 股）
trade = trader.buy_odd_lot("2330", price=500.0, quantity=100)

# 賣出零股
trade = trader.sell_odd_lot("2330", price=510.0, quantity=100)

# 使用市價單
trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="MKT")

# 使用 IOC 委託
trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="IOC")
```

### 8. 查詢委託與成交

```python
# 列出所有委託單
trades = trader.list_trades()

# 更新委託狀態
trader.update_status()

# 查詢特定委託狀態
status = trader.get_trade_status(trade)
print(f"委託狀態: {status['status']}")
print(f"成交數量: {status['deal_quantity']}")

# 查詢持倉
positions = trader.list_positions()

# 查詢損益
pnl = trader.list_profit_loss()

# 查詢帳戶額度
margin = trader.get_account_margin()
```

### 9. 委託回報記錄

```python
# 啟用委託回報記錄功能
trader.enable_order_report_recording()

# 取得委託回報記錄
order_reports = trader.get_order_reports()
deal_reports = trader.get_deal_reports()

# 取得最新幾筆回報
recent_orders = trader.get_order_reports(limit=10)
recent_deals = trader.get_deal_reports(limit=5)

# 取得回報摘要
summary = trader.get_report_summary()
print(f"委託回報數: {summary['order_count']}")
print(f"成交回報數: {summary['deal_count']}")

# 清除歷史記錄
trader.clear_report_history()
```

### 10. 登出系統

```python
trader.logout()
```

## 類別屬性

- `sj`: Shioaji API 實例，登入成功後可用於所有交易操作
- `contracts`: 商品檔物件，提供證券、期貨、選擇權、指數等商品資訊

## 參考資料

- [Shioaji 官方文件](https://sinotrade.github.io/)
- [Shioaji 登入教學](https://sinotrade.github.io/zh/tutor/login/)
- [Shioaji 商品檔教學](https://sinotrade.github.io/zh/tutor/contract/)
- [Shioaji 報價訂閱教學](https://sinotrade.github.io/zh/tutor/market_data/streaming/stocks/)
- [Shioaji Callback 教學](https://sinotrade.github.io/zh/tutor/callback/orderdeal_event/)
- [Shioaji 證券下單教學](https://sinotrade.github.io/zh/tutor/order/Stock/)
- [Shioaji 零股下單教學](https://sinotrade.github.io/zh/tutor/order/IntradayOdd/)
- [Shioaji 委託回報教學](https://sinotrade.github.io/zh/tutor/order/order_deal_event/stocks/)

## 範例程式

- `example_usage.py` - 基本使用範例（含登入、帳戶管理、商品查詢）
- `example_contracts.py` - 商品檔查詢範例（詳細示範各種查詢方法）
- `example_quote_callback.py` - 報價訂閱與 Callback 監控範例
- `example_order.py` - 股票下單範例（整股與零股下單）
- `example_trade_status.py` - 成交回報查詢範例（委託狀態、持倉、損益查詢）
- `example_order_report.py` - 委託回報記錄範例（即時記錄與管理委託回報）
- `example_complete.py` - 完整功能示範（整合所有功能的交易機器人範例）

## 授權

請參考 LICENSE 文件