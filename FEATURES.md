# ShioajiTrader 功能說明

## 核心類別: ShioajiTrader

### 主要屬性
- `sj` - Shioaji API 實例
- `contracts` - 商品檔物件
- `stock_account` - 預設證券帳戶
- `futopt_account` - 預設期貨帳戶

### 功能模組

#### 1. 帳戶管理
- ✅ `login()` - 登入系統（支援 API Key 與帳號密碼）
- ✅ `logout()` - 登出系統
- ✅ `list_accounts()` - 列出所有帳戶
- ✅ `set_default_account()` - 設定預設帳戶

#### 2. 商品查詢
- ✅ `get_stock()` - 查詢證券商品
- ✅ `get_future()` - 查詢期貨商品
- ✅ `get_option()` - 查詢選擇權商品
- ✅ `search_contracts()` - 搜尋商品

#### 3. 報價訂閱
- ✅ `subscribe_quote()` - 訂閱即時報價
- ✅ `unsubscribe_quote()` - 取消訂閱報價
- ✅ `set_quote_callback()` - 設定報價 callback
- ✅ `get_subscribed_contracts()` - 取得已訂閱商品清單

#### 4. 委託監控
- ✅ `set_order_callback()` - 設定委託回報 callback

## 實作特色

### 程式碼風格
- ✅ 簡潔直觀，避免過度設計
- ✅ 所有函數都有完整 docstring
- ✅ 包含參數說明、返回值、使用範例、錯誤型別
- ✅ 符合 Python coding style 規範

### 錯誤處理
- ✅ 完善的異常處理
- ✅ 清晰的錯誤訊息
- ✅ 適當的狀態檢查

### 使用便利性
- ✅ 類別屬性直接訪問
- ✅ 輔助方法簡化操作
- ✅ Callback 機制靈活
- ✅ 狀態追蹤完整

## 程式碼統計

- **主檔案**: shioaji_trader.py (578 行)
- **函數數量**: 22 個
- **範例程式**: 4 個
- **文件檔案**: 2 個

## 使用流程

```
1. 初始化 → 2. 登入 → 3. 設定 Callback → 4. 訂閱報價 → 5. 接收資料 → 6. 登出
```

## 完整功能列表

| 功能類別 | 方法名稱 | 說明 |
|---------|---------|------|
| 登入管理 | `login()` | 登入系統 |
| 登入管理 | `logout()` | 登出系統 |
| 帳戶管理 | `list_accounts()` | 列出帳戶 |
| 帳戶管理 | `set_default_account()` | 設定預設帳戶 |
| 帳戶管理 | `stock_account` | 證券帳戶屬性 |
| 帳戶管理 | `futopt_account` | 期貨帳戶屬性 |
| 商品檔 | `contracts` | 商品檔屬性 |
| 商品檔 | `get_stock()` | 查詢證券 |
| 商品檔 | `get_future()` | 查詢期貨 |
| 商品檔 | `get_option()` | 查詢選擇權 |
| 商品檔 | `search_contracts()` | 搜尋商品 |
| 報價 | `subscribe_quote()` | 訂閱報價 |
| 報價 | `unsubscribe_quote()` | 取消訂閱 |
| 報價 | `set_quote_callback()` | 設定報價 callback |
| 報價 | `get_subscribed_contracts()` | 已訂閱清單 |
| 委託 | `set_order_callback()` | 設定委託 callback |

## 範例程式

### 1. example_usage.py
基本使用範例，涵蓋登入、帳戶管理、商品查詢等基礎功能。

### 2. example_contracts.py
商品檔查詢範例，詳細展示各種商品查詢方法。

### 3. example_quote_callback.py
報價訂閱與 Callback 監控範例，展示即時報價接收。

### 4. example_complete.py
完整功能示範，整合所有功能的交易機器人範例。

## 技術亮點

1. **簡潔設計**: 避免過度設計，保持程式碼簡潔直觀
2. **完整註解**: 所有函數都有詳細的 docstring
3. **錯誤處理**: 完善的異常處理機制
4. **狀態管理**: 清晰的狀態追蹤與管理
5. **易於擴展**: 模組化設計，方便後續擴展
