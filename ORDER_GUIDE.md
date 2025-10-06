# Shioaji 下單功能指南

## 功能概覽

ShioajiTrader 提供簡潔的股票下單介面，支援整股與零股交易。

## 下單方法

### 1. place_order() - 通用下單

完整的下單方法，支援所有參數自訂。

```python
trade = trader.place_order(
    contract=contract,      # 商品物件
    action="Buy",          # "Buy" 或 "Sell"
    price=500.0,           # 委託價格
    quantity=1000,         # 委託數量
    price_type="LMT",      # "LMT" 或 "MKT"
    order_type="ROD",      # "ROD", "IOC", "FOK"
    order_lot="Common"     # "Common" 或 "IntradayOdd"
)
```

### 2. buy_stock() - 買進整股

簡化的買進整股方法。

```python
# 買進 1 張台積電（1000 股）
trade = trader.buy_stock("2330", price=500.0, quantity=1000)

# 買進 2 張台積電
trade = trader.buy_stock("2330", price=500.0, quantity=2000)

# 使用市價買進
trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="MKT")

# 使用 IOC 委託
trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="IOC")
```

### 3. sell_stock() - 賣出整股

簡化的賣出整股方法。

```python
# 賣出 1 張台積電
trade = trader.sell_stock("2330", price=510.0, quantity=1000)

# 賣出 2 張台積電
trade = trader.sell_stock("2330", price=510.0, quantity=2000)
```

### 4. buy_odd_lot() - 買進零股

買進盤中零股（1-999 股）。

```python
# 買進 100 股台積電零股
trade = trader.buy_odd_lot("2330", price=500.0, quantity=100)

# 買進 1 股台積電零股
trade = trader.buy_odd_lot("2330", price=500.0, quantity=1)
```

### 5. sell_odd_lot() - 賣出零股

賣出盤中零股（1-999 股）。

```python
# 賣出 100 股台積電零股
trade = trader.sell_odd_lot("2330", price=510.0, quantity=100)

# 賣出 50 股台積電零股
trade = trader.sell_odd_lot("2330", price=510.0, quantity=50)
```

## 參數說明

### 買賣方向 (action)
- `Buy` - 買進
- `Sell` - 賣出

### 價格類型 (price_type)
- `LMT` (限價) - 指定價格，只在該價格或更好的價格成交
- `MKT` (市價) - 以市場當前最佳價格立即成交

### 委託類型 (order_type)
- `ROD` - 當日有效，委託單在當日收盤前有效
- `IOC` - 立即成交否則取消，未成交部分立即取消
- `FOK` - 全部成交否則取消，必須全部立即成交

### 交易單位 (order_lot)
- `Common` - 整股，數量必須是 1000 的倍數
- `IntradayOdd` - 盤中零股，數量可以是 1-999 股

## 重要事項

### 整股交易
1. **最小單位**：1000 股（1 張）
2. **數量要求**：必須是 1000 的倍數
3. **委託類型**：支援 ROD、IOC、FOK
4. **交易時間**：09:00-13:30

### 零股交易
1. **數量範圍**：1-999 股
2. **委託類型**：只能使用 ROD
3. **價格類型**：支援限價與市價
4. **交易時間**：09:00-13:30

### 交易前注意
1. ✅ 確認帳戶餘額充足
2. ✅ 確認價格合理（避免離當前價格太遠）
3. ✅ 注意交易時間（盤中 09:00-13:30）
4. ✅ 市價單可能會有較大價差
5. ✅ 建議先使用模擬帳號測試

## 完整範例

```python
from shioaji_trader import ShioajiTrader

# 初始化
trader = ShioajiTrader()

# 登入
trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")

# 設定委託回報 callback
def order_callback(stat, msg):
    print(f"委託狀態: {stat}")
    print(f"委託訊息: {msg}")

trader.set_order_callback(order_callback)

# ========== 整股交易 ==========

# 買進 1 張台積電
trade = trader.buy_stock("2330", price=500.0, quantity=1000)
print(f"下單成功: {trade}")

# 賣出 1 張台積電
trade = trader.sell_stock("2330", price=510.0, quantity=1000)

# ========== 零股交易 ==========

# 買進 100 股台積電零股
trade = trader.buy_odd_lot("2330", price=500.0, quantity=100)

# 賣出 100 股台積電零股
trade = trader.sell_odd_lot("2330", price=510.0, quantity=100)

# ========== 不同價格類型 ==========

# 限價單
trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="LMT")

# 市價單
trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="MKT")

# ========== 不同委託類型 ==========

# ROD (當日有效)
trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="ROD")

# IOC (立即成交否則取消)
trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="IOC")

# FOK (全部成交否則取消)
trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="FOK")

# 登出
trader.logout()
```

## 錯誤處理

```python
try:
    trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    print(f"下單成功: {trade}")
except RuntimeError as e:
    print(f"系統錯誤: {e}")
except ValueError as e:
    print(f"參數錯誤: {e}")
except Exception as e:
    print(f"下單失敗: {e}")
```

## Trade 物件

下單成功後會回傳 Trade 物件，包含以下資訊：
- `contract` - 商品資訊
- `order` - 委託單資訊
- `status` - 委託狀態

```python
trade = trader.buy_stock("2330", price=500.0, quantity=1000)

print(f"商品代碼: {trade.contract.code}")
print(f"商品名稱: {trade.contract.name}")
print(f"委託價格: {trade.order.price}")
print(f"委託數量: {trade.order.quantity}")
print(f"委託狀態: {trade.status.status}")
```

## 常見問題

### Q: 如何查詢委託是否成交？
A: 透過 `set_order_callback()` 設定 callback 函數，當委託狀態改變時會自動通知。

### Q: 零股可以使用 IOC 或 FOK 嗎？
A: 不可以，零股只能使用 ROD 委託類型。

### Q: 市價單會在什麼價格成交？
A: 市價單會以當時市場最佳價格成交，可能會有價差。

### Q: 如何取消委託？
A: 需要使用 `api.cancel_order()` 方法（目前 ShioajiTrader 尚未實作此功能）。

### Q: 可以同時下多筆訂單嗎？
A: 可以，每次呼叫下單方法都會產生一筆新的委託。

## 安全提示

⚠️ **重要警告**

1. 下單是真實的交易操作，會影響您的帳戶
2. 建議先使用永豐金證券的模擬帳號測試
3. 確認所有參數正確後再執行
4. 注意價格是否合理（避免誤下錯價格）
5. 確認帳戶有足夠餘額
6. 了解各種委託類型的特性

## 測試建議

1. **使用模擬帳號**
   - 先在模擬環境測試所有功能
   - 確認理解各種參數的效果
   
2. **小額測試**
   - 實際使用時先以小額測試
   - 確認系統運作正常
   
3. **監控委託**
   - 設定 callback 監控委託狀態
   - 確認委託是否按預期執行

## 參考資料

- [Shioaji 官方文件](https://sinotrade.github.io/)
- [證券下單教學](https://sinotrade.github.io/zh/tutor/order/Stock/)
- [零股下單教學](https://sinotrade.github.io/zh/tutor/order/IntradayOdd/)
