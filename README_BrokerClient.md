# BrokerClient - 永豐金證券交易客戶端

## 概述

`BrokerClient` 是一個聚合 `BrokerageAuth` 的最小可用交易客戶端，提供完整的證券交易功能包括即時報價訂閱、市場掃描、訂單管理、帳戶查詢等。

### 特色

- ✅ **聚合認證**: 自動整合 `BrokerageAuth` 處理登入和 Token 管理
- ✅ **自動簽章**: 自動處理 API 請求的簽章和標頭設定
- ✅ **即時資料**: 支援股票報價訂閱和事件回調
- ✅ **訂單管理**: 完整的下單、查詢、狀態追蹤功能
- ✅ **錯誤分類**: 針對不同錯誤類型提供專門處理
- ✅ **事件驅動**: 支援多種回調函數處理即時事件
- ✅ **資源管理**: 支援 Context Manager 自動清理資源

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
export BROKER_API_KEY="your_api_key"
export BROKER_CERT_PATH="/path/to/your/certificate.pem"
```

### 3. 基本使用

```python
from broker_client import BrokerClient, Order, OrderSide, OrderType

# 使用 Context Manager（推薦）
with BrokerClient() as client:
    # 查詢帳戶餘額
    balance = client.getAccountBalance()
    print(f"可用資金: ${balance.buying_power:,.2f}")
    
    # 訂閱即時報價
    def on_tick(tick):
        print(f"{tick.symbol}: {tick.price}")
    
    client.onTick(on_tick)
    client.subscribeTick("2330")
    
    # 下單
    order = Order("2330", OrderSide.BUY, OrderType.LIMIT, 1000, 500.0)
    order_id = client.placeOrder(order)
    print(f"訂單已提交: {order_id}")
```

## API 文檔

### BrokerClient 類別

主要的交易客戶端類別，聚合 `BrokerageAuth` 提供完整交易功能。

#### 初始化

```python
client = BrokerClient()
```

**說明**: 自動建立 `BrokerageAuth` 實例進行認證管理

**異常**: 所有 `BrokerageAuth` 相關例外

### 即時報價功能

#### subscribeTick(symbol, oddlot=False)

```python
client.subscribeTick("2330", False)
```

**說明**: 訂閱股票即時報價

**參數**:
- `symbol` (str): 股票代號（例如 "2330"）
- `oddlot` (bool): 是否包含零股交易，預設 False

**異常**:
- `SubscriptionError`: 訂閱失敗
- `NetworkError`: 網路連線錯誤
- `UnauthorizedError`: 認證失敗

#### onTick(callback)

```python
def handle_tick(tick):
    print(f"{tick.symbol}: {tick.price}")

client.onTick(handle_tick)
```

**說明**: 註冊即時報價回調函數

**參數**:
- `callback` (Callable[[TickData], None]): 接收 `TickData` 物件的回調函數

#### unsubscribeTick(symbol)

```python
client.unsubscribeTick("2330")
```

**說明**: 取消訂閱股票報價

**參數**:
- `symbol` (str): 股票代號

### 市場掃描功能

#### scanTopGainers(limit=100)

```python
gainers = client.scanTopGainers(50)
```

**說明**: 掃描漲幅排行榜

**參數**:
- `limit` (int): 回傳筆數限制，預設 100

**返回**: `List[TopGainer]` - 漲幅排行清單，依漲幅由高到低排序

**異常**:
- `NetworkError`: 網路連線錯誤
- `DataFormatError`: 資料格式錯誤
- `UnauthorizedError`: 認證失敗

### 訂單管理功能

#### placeOrder(order)

```python
from broker_client import Order, OrderSide, OrderType

order = Order(
    symbol="2330",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity=1000,
    price=500.0
)
order_id = client.placeOrder(order)
```

**說明**: 提交訂單

**參數**:
- `order` (Order): 訂單物件

**返回**: `str` - 訂單 ID

**異常**:
- `OrderError`: 訂單相關錯誤
- `NetworkError`: 網路連線錯誤
- `UnauthorizedError`: 認證失敗

#### queryOrderStatus(order_id)

```python
status = client.queryOrderStatus(order_id)
print(f"訂單狀態: {status.status.value}")
```

**說明**: 查詢訂單狀態

**參數**:
- `order_id` (str): 訂單 ID

**返回**: `OrderStatusInfo` - 訂單狀態資訊

**異常**:
- `OrderError`: 訂單不存在或查詢失敗
- `NetworkError`: 網路連線錯誤
- `UnauthorizedError`: 認證失敗

#### onOrderCallback(callback)

```python
def handle_order_update(status):
    print(f"訂單 {status.order_id}: {status.status.value}")

client.onOrderCallback(handle_order_update)
```

**說明**: 註冊訂單狀態更新回調函數

**參數**:
- `callback` (Callable[[OrderStatusInfo], None]): 接收 `OrderStatusInfo` 的回調函數

#### onDealCallback(callback)

```python
def handle_deal(deal):
    print(f"成交: {deal['symbol']} {deal['quantity']}股")

client.onDealCallback(handle_deal)
```

**說明**: 註冊成交回調函數

**參數**:
- `callback` (Callable[[Dict[str, Any]], None]): 接收成交資訊的回調函數

### 帳戶查詢功能

#### getAccountBalance()

```python
balance = client.getAccountBalance()
print(f"現金餘額: ${balance.cash_balance:,.2f}")
print(f"總資產: ${balance.total_value:,.2f}")
```

**說明**: 取得帳戶餘額資訊

**返回**: `AccountBalance` - 帳戶餘額和資產資訊

**異常**:
- `NetworkError`: 網路連線錯誤
- `UnauthorizedError`: 認證失敗
- `DataFormatError`: 資料格式錯誤

### 輔助方法

#### getSubscribedSymbols()

```python
symbols = client.getSubscribedSymbols()
print(f"已訂閱: {symbols}")
```

**說明**: 取得已訂閱的股票代號清單

**返回**: `List[str]` - 已訂閱的股票代號清單

#### close()

```python
client.close()
```

**說明**: 關閉客戶端，清理資源

## 資料結構

### Order - 訂單資料

```python
@dataclass
class Order:
    symbol: str                    # 股票代號
    side: OrderSide               # 買賣方向 (BUY/SELL)
    order_type: OrderType         # 訂單類型 (MARKET/LIMIT/STOP/STOP_LIMIT)
    quantity: int                 # 數量
    price: Optional[float]        # 價格（市價單可為 None）
    stop_price: Optional[float]   # 停損價格
    time_in_force: str = "DAY"    # 有效期限
    order_id: Optional[str]       # 訂單 ID（系統生成）
```

### TickData - 即時報價

```python
@dataclass
class TickData:
    symbol: str           # 股票代號
    price: float          # 現價
    volume: int           # 成交量
    bid_price: float      # 買價
    ask_price: float      # 賣價
    bid_volume: int       # 買量
    ask_volume: int       # 賣量
    timestamp: datetime   # 時間戳
    change: float         # 漲跌
    change_percent: float # 漲跌幅
```

### OrderStatusInfo - 訂單狀態

```python
@dataclass
class OrderStatusInfo:
    order_id: str              # 訂單 ID
    status: OrderStatus        # 訂單狀態
    filled_quantity: int       # 已成交數量
    remaining_quantity: int    # 剩餘數量
    avg_price: float          # 平均成交價格
    last_update: datetime     # 最後更新時間
    message: str = ""         # 狀態訊息
```

### TopGainer - 漲幅排行

```python
@dataclass
class TopGainer:
    symbol: str           # 股票代號
    name: str            # 股票名稱
    price: float         # 現價
    change: float        # 漲跌
    change_percent: float # 漲跌幅
    volume: int          # 成交量
    market_cap: float    # 市值
```

### AccountBalance - 帳戶餘額

```python
@dataclass
class AccountBalance:
    cash_balance: float      # 現金餘額
    buying_power: float      # 可用資金
    total_value: float       # 總資產價值
    unrealized_pnl: float    # 未實現損益
    realized_pnl: float      # 已實現損益
    margin_used: float       # 已使用保證金
    margin_available: float  # 可用保證金
```

## 枚舉類型

### OrderSide - 買賣方向

```python
class OrderSide(Enum):
    BUY = "Buy"
    SELL = "Sell"
```

### OrderType - 訂單類型

```python
class OrderType(Enum):
    MARKET = "Market"        # 市價單
    LIMIT = "Limit"          # 限價單
    STOP = "Stop"            # 停損單
    STOP_LIMIT = "StopLimit" # 停損限價單
```

### OrderStatus - 訂單狀態

```python
class OrderStatus(Enum):
    PENDING = "Pending"              # 待處理
    SUBMITTED = "Submitted"          # 已提交
    PARTIAL_FILLED = "PartialFilled" # 部分成交
    FILLED = "Filled"                # 完全成交
    CANCELLED = "Cancelled"          # 已取消
    REJECTED = "Rejected"            # 已拒絕
```

## 例外處理

### 例外類別階層

```
BrokerClientError
├── DataFormatError      # 資料格式錯誤
├── UnauthorizedError    # 未授權錯誤 (401)
├── ForbiddenError       # 權限不足錯誤 (403)
├── OrderError           # 訂單相關錯誤
└── SubscriptionError    # 訂閱相關錯誤
```

### 錯誤處理範例

```python
from broker_client import (
    BrokerClient, UnauthorizedError, NetworkError, 
    OrderError, SubscriptionError, DataFormatError
)

try:
    client = BrokerClient()
    
    # 各種操作...
    balance = client.getAccountBalance()
    client.subscribeTick("2330")
    
except UnauthorizedError as e:
    print(f"認證失敗: {e}")
except NetworkError as e:
    print(f"網路錯誤: {e}")
except OrderError as e:
    print(f"訂單錯誤: {e}")
except SubscriptionError as e:
    print(f"訂閱錯誤: {e}")
except DataFormatError as e:
    print(f"資料格式錯誤: {e}")
```

## 使用範例

### 完整交易流程

```python
from broker_client import (
    BrokerClient, Order, OrderSide, OrderType,
    OrderStatus
)

def main():
    with BrokerClient() as client:
        # 1. 查詢帳戶資訊
        balance = client.getAccountBalance()
        print(f"可用資金: ${balance.buying_power:,.2f}")
        
        # 2. 掃描市場機會
        gainers = client.scanTopGainers(10)
        print("今日漲幅排行:")
        for gainer in gainers[:5]:
            print(f"  {gainer.symbol}: +{gainer.change_percent:.2f}%")
        
        # 3. 設定事件回調
        def on_tick(tick):
            print(f"報價更新: {tick.symbol} = {tick.price}")
        
        def on_order_update(status):
            print(f"訂單更新: {status.order_id} -> {status.status.value}")
            if status.status == OrderStatus.FILLED:
                print(f"完全成交！平均價格: {status.avg_price}")
        
        client.onTick(on_tick)
        client.onOrderCallback(on_order_update)
        
        # 4. 訂閱目標股票
        target_symbol = "2330"
        client.subscribeTick(target_symbol)
        
        # 5. 下單
        order = Order(
            symbol=target_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=1000,
            price=500.0
        )
        
        order_id = client.placeOrder(order)
        print(f"訂單已提交: {order_id}")
        
        # 6. 監控訂單狀態
        import time
        time.sleep(5)  # 等待狀態更新
        
        status = client.queryOrderStatus(order_id)
        print(f"最新狀態: {status.status.value}")

if __name__ == "__main__":
    main()
```

### 批量訂單管理

```python
def batch_order_example():
    with BrokerClient() as client:
        # 準備多筆訂單
        orders = [
            Order("2330", OrderSide.BUY, OrderType.LIMIT, 1000, 500.0),
            Order("2317", OrderSide.BUY, OrderType.LIMIT, 2000, 100.0),
            Order("2454", OrderSide.SELL, OrderType.LIMIT, 500, 800.0),
        ]
        
        # 批量提交
        order_ids = []
        for order in orders:
            try:
                order_id = client.placeOrder(order)
                order_ids.append(order_id)
                print(f"訂單提交: {order.symbol} -> {order_id}")
            except OrderError as e:
                print(f"訂單失敗: {order.symbol} - {e}")
        
        # 批量查詢狀態
        for order_id in order_ids:
            status = client.queryOrderStatus(order_id)
            print(f"{order_id}: {status.status.value}")
```

### 即時監控系統

```python
import threading
import time

def real_time_monitor():
    with BrokerClient() as client:
        # 監控多檔股票
        symbols = ["2330", "2317", "2454", "0050"]
        
        # 設定報價回調
        def price_alert(tick):
            if abs(tick.change_percent) > 3.0:  # 漲跌幅超過 3%
                print(f"⚠️  價格警報: {tick.symbol} {tick.change_percent:+.2f}%")
        
        client.onTick(price_alert)
        
        # 訂閱所有股票
        for symbol in symbols:
            client.subscribeTick(symbol)
            print(f"開始監控: {symbol}")
        
        # 定期查詢帳戶狀態
        def account_monitor():
            while True:
                balance = client.getAccountBalance()
                print(f"帳戶總值: ${balance.total_value:,.2f}")
                time.sleep(60)  # 每分鐘查詢一次
        
        # 背景執行帳戶監控
        monitor_thread = threading.Thread(target=account_monitor, daemon=True)
        monitor_thread.start()
        
        # 主程式保持運行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("停止監控")
```

## 執行示範程式

```bash
python broker_client_demo.py
```

示範程式會執行以下測試：
1. 即時報價訂閱功能
2. 市場掃描功能
3. 訂單管理功能
4. 帳戶查詢功能
5. 錯誤處理驗證
6. Context Manager 功能
7. 完整功能展示

## 實作狀態

### 已實作功能 ✅

- 聚合 `BrokerageAuth` 完成認證管理
- 自動處理簽章/標頭和 Token 刷新
- `subscribeTick`、`onTick`（含模擬器）
- `scanTopGainers`（含假資料）
- `placeOrder`、`queryOrderStatus`（含模擬）
- `onOrderCallback`、`onDealCallback` 事件掛勾
- `getAccountBalance`（含模擬資料）
- 針對網路錯誤、401/403、資料格式錯誤分類處理
- 完整的方法文件和使用範例
- 內部使用 `BrokerageAuth.getSession()` 取得授權

### TODO 項目（後續擴展）

- 連接真實 API 端點
- WebSocket 即時連線
- 更多訂單類型支援
- 技術指標計算
- 歷史資料查詢
- 風險管理功能

## 安全注意事項

1. **認證管理**: 所有 API 請求自動附加認證標頭
2. **Token 刷新**: 自動檢測 Token 過期並刷新
3. **錯誤恢復**: 401 錯誤時自動重新認證
4. **資源清理**: 使用 Context Manager 確保資源正確釋放
5. **執行緒安全**: 回調函數在獨立執行緒中執行

## 技術規格

- **Python 版本**: 3.6+
- **依賴套件**: requests, dataclasses (Python < 3.7)
- **認證模組**: BrokerageAuth
- **API 端點**: https://api.sinotrade.com.tw
- **支援功能**: 即時報價、訂單管理、帳戶查詢、市場掃描

BrokerClient 提供了完整的證券交易功能，是構建交易系統的理想基礎模組。