# 永豐 Shioaji 量化交易系統

## 專案簡介

本專案是一個基於永豐證券 Shioaji SDK 的量化交易系統，採用 SOLID 原則設計，提供簡潔、可擴展的交易 API 封裝。

## 特色

- ✅ **遵循 SOLID 原則**：完整實踐所有五大物件導向設計原則
- ✅ **依賴注入支援**：靈活的配置驗證器注入機制
- ✅ **介面導向設計**：易於擴展支援其他券商
- ✅ **完整的 Docstring**：所有函數都包含詳細的文件說明
- ✅ **錯誤處理**：統一的錯誤處理模式
- ✅ **類型提示**：完整的 Python 類型註解

## 專案結構

```
.
├── README.md                      # 專案說明文件
├── 類別圖.md                      # 系統架構與 SOLID 原則說明
├── requirements.txt               # Python 依賴套件
├── trading_client_interface.py   # 交易客戶端抽象介面
├── config_validator.py            # 配置驗證器實作
├── quote_callback_handler.py     # 報價與委託成交回調處理器
├── order_manager.py               # 訂單管理與驗證模組
└── shioaji_client.py             # 永豐 Shioaji 客戶端實作
```

## 安裝

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 確保已安裝 Python 3.8 或以上版本

## 使用方法

### 基本登入

```python
from shioaji_client import ShioajiClient
from trading_client_interface import LoginConfig

# 建立登入配置
config = LoginConfig(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    person_id="A123456789",
    simulation=True
)

# 建立客戶端並登入
client = ShioajiClient()
result = client.login(config)

if result["success"]:
    print("登入成功")
    
    # 取得商品檔
    contract_result = client.fetch_contracts()
    if contract_result["success"]:
        # 取得股票商品
        stocks = client.get_contracts("Stocks")
        print(f"股票商品數量: {len(stocks)}")
        
        # 訂閱台積電報價
        tsmc = stocks["2330"]
        subscribe_result = client.subscribe_quote([tsmc])
        if subscribe_result["success"]:
            print("訂閱報價成功")
    
    # 取得帳戶資訊
    accounts = client.get_accounts()
    print(accounts)
    # 登出
    client.logout()
else:
    print(f"登入失敗: {result['error']}")
```

### 取得商品檔

```python
# 先登入
client = ShioajiClient()
client.login(config)

# 取得商品檔
contract_result = client.fetch_contracts()
if contract_result["success"]:
    print("商品檔載入成功")
    
    # 取得所有商品
    all_contracts = client.get_contracts()
    
    # 取得股票商品
    stocks = client.get_contracts("Stocks")
    
    # 取得期貨商品
    futures = client.get_contracts("Futures")
    
    # 取得選擇權商品
    options = client.get_contracts("Options")
```

### 訂閱報價與回調處理

```python
from quote_callback_handler import QuoteCallbackHandler

# 自訂報價處理函數
def my_quote_handler(topic, quote):
    print(f"商品: {topic}, 成交價: {quote.close}, 成交量: {quote.volume}")

# 建立自訂報價處理器
quote_handler = QuoteCallbackHandler(custom_handler=my_quote_handler)

# 建立客戶端並注入回調處理器
client = ShioajiClient(quote_callback=quote_handler)
client.login(config)
client.fetch_contracts()

# 訂閱報價
stocks = client.get_contracts("Stocks")
tsmc = stocks["2330"]
result = client.subscribe_quote([tsmc])

# 報價會透過 my_quote_handler 處理
# 也可以直接取得報價資料
import time
time.sleep(5)  # 等待接收報價
latest_quote = quote_handler.get_latest_quote("2330")
print(f"最新報價: {latest_quote}")

# 取消訂閱
client.unsubscribe_quote([tsmc])
```

### 下單功能

```python
from order_manager import OrderConfig, OrderAction, OrderPriceType, IntradayOddOrderConfig

# 先登入並啟用憑證
client = ShioajiClient()
client.login(config)
ca_result = client.activate_ca("YOUR_CA_PASSWORD")

if ca_result["success"]:
    # 設置委託成交回調
    client.set_order_callback()
    
    # 取得商品
    client.fetch_contracts()
    stocks = client.get_contracts("Stocks")
    tsmc = stocks["2330"]
    
    # 下一般股票訂單（1000股的倍數）
    order_config = OrderConfig(
        contract=tsmc,
        action=OrderAction.BUY,
        price=100.0,
        quantity=1000,
        price_type=OrderPriceType.LIMIT
    )
    result = client.place_order(order_config)
    if result["success"]:
        print(f"下單成功：{result['order']}")
    
    # 下盤中零股訂單（小於1000股）
    odd_config = IntradayOddOrderConfig(
        contract=tsmc,
        action=OrderAction.BUY,
        price=100.0,
        quantity=100
    )
    odd_result = client.place_intraday_odd_order(odd_config)
    if odd_result["success"]:
        print("零股下單成功")
```

### 取得成交回報

```python
# 先設置委託成交回調
client.set_order_callback()

# ... 下單後 ...

# 取得所有成交記錄
report = client.get_deal_report()
print(f"總成交數量: {report['total_quantity']}")
print(f"平均成交價: {report['average_price']}")
for deal in report['deals']:
    print(f"成交時間: {deal['timestamp']}")
    print(f"成交價格: {deal.get('price')}")
    print(f"成交數量: {deal.get('quantity')}")

# 取得特定訂單的成交記錄
order_report = client.get_deal_report("ORDER_ID_123")
print(f"訂單 ORDER_ID_123 成交數量: {order_report['total_quantity']}")

# 取得最新成交
latest = client.get_latest_deal_report()
if latest["success"] and latest["deal"]:
    print(f"最新成交價: {latest['deal'].get('price')}")

# 直接透過 callback handler 取得詳細資訊
all_deals = client.order_deal_callback.get_deals()
avg_price = client.order_deal_callback.get_average_deal_price()
total_qty = client.order_deal_callback.get_total_deal_quantity()
```

### 取得委託回報

```python
# 先設置委託成交回調
client.set_order_callback()

# ... 下單後 ...

# 取得所有委託記錄
report = client.get_order_report()
print(f"總委託數: {report['statistics']['total']}")
print(f"已成交: {report['statistics']['filled']}")
print(f"已取消: {report['statistics']['cancelled']}")
print(f"待送出: {report['statistics']['pending']}")

for order in report['orders']:
    print(f"委託時間: {order['timestamp']}")
    print(f"委託狀態: {order.get('status')}")
    print(f"委託價格: {order.get('price')}")
    print(f"委託數量: {order.get('quantity')}")

# 取得特定訂單的委託記錄
order_report = client.get_order_report("ORDER_ID_123")
if order_report["orders"]:
    order = order_report["orders"][0]
    print(f"訂單狀態: {order.get('status')}")

# 取得最新委託
latest = client.get_latest_order_report()
if latest["success"] and latest["order"]:
    print(f"最新委託狀態: {latest['order'].get('status')}")

# 根據狀態查詢委託
filled_orders = client.get_orders_by_status("Filled")
print(f"已成交委託: {filled_orders['count']} 筆")

pending_orders = client.get_orders_by_status("PendingSubmit")
print(f"待送出委託: {pending_orders['count']} 筆")

# 直接透過 callback handler 取得詳細資訊
all_orders = client.order_deal_callback.get_orders()
statistics = client.order_deal_callback.get_order_statistics()
order_by_id = client.order_deal_callback.get_order_by_id("ORDER_123")
```

### 取得帳戶餘額

```python
# 查詢帳戶餘額
result = client.get_account_balance()
if result["success"]:
    balance = result["balance"]
    print(f"可用餘額: {balance.available_balance}")
    print(f"帳戶餘額: {balance.acc_balance}")
    print(f"已實現損益: {balance.realized_profit_loss}")
    print(f"未實現損益: {balance.unrealized_profit_loss}")
```

### 取得持倉資訊

```python
# 查詢所有持倉（使用預設帳戶）
result = client.list_positions()
if result["success"]:
    print(f"持倉數量: {result['count']}")
    for position in result["positions"]:
        print(f"代碼: {position.code}")
        print(f"數量: {position.quantity}")
        print(f"損益: {position.pnl}")
        print(f"平均成本: {position.price}")

# 指定帳戶查詢持倉
accounts = client.get_accounts()
if accounts["success"] and accounts["accounts"]:
    account = accounts["accounts"][0]
    result = client.list_positions(account)
```

### 啟用憑證（用於下單）

```python
# 先登入
client = ShioajiClient()
client.login(config)

# 啟用憑證
ca_result = client.activate_ca("YOUR_CA_PASSWORD")
if ca_result["success"]:
    print("憑證啟用成功")
```

### 依賴注入使用

```python
from shioaji_client import ShioajiClient
from config_validator import LoginConfigValidator

# 建立自訂驗證器
custom_validator = LoginConfigValidator()

# 注入驗證器
client = ShioajiClient(validator=custom_validator)
```

## 架構設計

本專案採用以下設計模式和原則：

### SOLID 原則

- **單一職責原則 (SRP)**：每個類別只負責一項職責
- **開放封閉原則 (OCP)**：對擴展開放，對修改封閉
- **里氏替換原則 (LSP)**：子類別可替換父類別
- **介面隔離原則 (ISP)**：精簡的介面設計
- **依賴反轉原則 (DIP)**：依賴抽象而非具體實作

詳細的架構說明請參考 [類別圖.md](類別圖.md)

### 設計模式

- **外觀模式 (Facade Pattern)**：簡化複雜 API 的使用
- **資料傳輸物件 (DTO Pattern)**：封裝資料傳遞
- **策略模式 (Strategy Pattern)**：可抽換的驗證策略
- **依賴注入 (Dependency Injection)**：提高可測試性與彈性

## API 文件

### LoginConfig

登入配置資料類別

**參數**：
- `api_key` (str): API 金鑰
- `secret_key` (str): 密鑰
- `person_id` (str): 身分證字號或統一編號
- `ca_password` (Optional[str]): 憑證密碼
- `simulation` (bool): 是否使用模擬交易環境

### ShioajiClient

永豐 Shioaji 交易客戶端

**方法**：
- `login(config: LoginConfig) -> Dict[str, Any]`: 執行登入
- `logout() -> Dict[str, Any]`: 執行登出
- `activate_ca(ca_password: str) -> Dict[str, Any]`: 啟用憑證
- `get_accounts() -> Optional[Any]`: 取得帳戶資訊
- `fetch_contracts() -> Dict[str, Any]`: 取得商品檔
- `get_contracts(contract_type: Optional[str]) -> Optional[Any]`: 取得已載入的商品檔資料
- `subscribe_quote(contracts: List[Any]) -> Dict[str, Any]`: 訂閱報價
- `unsubscribe_quote(contracts: List[Any]) -> Dict[str, Any]`: 取消訂閱報價
- `set_order_callback() -> Dict[str, Any]`: 設置委託成交回調
- `place_order(order_config: OrderConfig) -> Dict[str, Any]`: 下一般股票訂單
- `place_intraday_odd_order(order_config: IntradayOddOrderConfig) -> Dict[str, Any]`: 下盤中零股訂單
- `cancel_order(order_id: str) -> Dict[str, Any]`: 取消訂單
- `update_order(order_id: str, price: float, quantity: int) -> Dict[str, Any]`: 修改訂單
- `get_deal_report(order_id: Optional[str]) -> Dict[str, Any]`: 取得成交回報
- `get_latest_deal_report() -> Dict[str, Any]`: 取得最新成交回報
- `get_order_report(order_id: Optional[str]) -> Dict[str, Any]`: 取得委託回報
- `get_latest_order_report() -> Dict[str, Any]`: 取得最新委託回報
- `get_orders_by_status(status: str) -> Dict[str, Any]`: 根據狀態取得委託回報
- `get_account_balance() -> Dict[str, Any]`: 取得帳戶餘額
- `list_positions(account: Optional[Any]) -> Dict[str, Any]`: 取得持倉資訊

### OrderConfig

訂單配置資料類別

**屬性**：
- `contract`: 商品合約物件
- `action`: 買賣方向（OrderAction.BUY/SELL）
- `price`: 價格
- `quantity`: 數量（必須為1000股的倍數）
- `price_type`: 價格類型（OrderPriceType.LIMIT/MARKET）
- `order_type`: 訂單類型（OrderType.ROD/IOC/FOK）
- `account`: 交易帳戶（可選）

### IntradayOddOrderConfig

盤中零股訂單配置資料類別

**屬性**：
- `contract`: 商品合約物件
- `action`: 買賣方向
- `price`: 價格
- `quantity`: 數量（必須小於1000股）
- `account`: 交易帳戶（可選）

### QuoteCallbackHandler

報價回調處理器

**方法**：
- `on_quote(topic: str, quote: Any)`: 處理報價回調
- `get_latest_quote(topic: str) -> Optional[Dict]`: 取得最新報價
- `get_all_quotes(topic: str) -> List[Dict]`: 取得所有報價歷史
- `clear_quotes(topic: Optional[str])`: 清除報價資料

### OrderDealCallbackHandler

委託成交回調處理器

**方法**：
- `on_order(order: Any)`: 處理委託回調
- `on_deal(deal: Any)`: 處理成交回調
- `get_orders() -> List[Dict]`: 取得所有委託記錄
- `get_deals() -> List[Dict]`: 取得所有成交記錄
- `get_latest_deal() -> Optional[Dict]`: 取得最新成交記錄
- `get_deals_by_order_id(order_id: str) -> List[Dict]`: 根據訂單 ID 取得成交記錄
- `get_total_deal_quantity(order_id: Optional[str]) -> int`: 取得成交總數量
- `get_average_deal_price(order_id: Optional[str]) -> float`: 取得平均成交價格
- `clear_deals(order_id: Optional[str])`: 清除成交記錄
- `clear_orders(order_id: Optional[str])`: 清除委託記錄
- `get_latest_order() -> Optional[Dict]`: 取得最新委託記錄
- `get_orders_by_status(status: str) -> List[Dict]`: 根據狀態取得委託記錄
- `get_order_by_id(order_id: str) -> Optional[Dict]`: 根據訂單 ID 取得委託記錄
- `get_order_statistics() -> Dict[str, Any]`: 取得委託統計資訊

## 錯誤處理

所有方法都返回統一格式的字典：

```python
{
    "success": bool,      # 操作是否成功
    "message": str,       # 結果訊息
    "error": Optional[str]  # 錯誤訊息（如果失敗）
}
```

## 開發指南

### 擴展支援其他券商

1. 實作 `ITradingClient` 介面
2. 建立對應的客戶端類別
3. 實作必要的方法

```python
from trading_client_interface import ITradingClient, LoginConfig

class AnotherBrokerClient(ITradingClient):
    def login(self, config: LoginConfig) -> Dict[str, Any]:
        # 實作登入邏輯
        pass
    
    def logout(self) -> Dict[str, Any]:
        # 實作登出邏輯
        pass
    
    def get_accounts(self) -> Optional[Any]:
        # 實作取得帳戶邏輯
        pass
```

### 自訂驗證器

1. 實作 `IConfigValidator` 介面
2. 在建構 `ShioajiClient` 時注入

```python
from trading_client_interface import IConfigValidator, LoginConfig

class CustomValidator(IConfigValidator):
    def validate(self, config: LoginConfig) -> None:
        # 自訂驗證邏輯
        pass
```

## 授權

本專案採用 MIT 授權，詳見 LICENSE 檔案。

## 參考資源

- [永豐 Shioaji SDK 文件](https://sinotrade.github.io/zh/tutor/login/)
- [SOLID 原則說明](https://en.wikipedia.org/wiki/SOLID)

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 聯絡方式

如有任何問題，歡迎透過 Issue 討論。