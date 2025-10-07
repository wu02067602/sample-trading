# 量化交易系統 (Quantitative Trading System)

基於永豐 Shioaji API 的 Python 量化交易系統，實現動能交易策略的自動化執行。

## 📋 專案簡介

本系統是一個完整的量化交易系統，整合了市場數據獲取、策略執行、自動下單、訂單監控與帳戶管理等功能。系統採用模組化設計，符合 SOLID 原則，具有良好的可擴展性與維護性。

### 核心特色

- 🔐 **安全登入**：支援 API Key 驗證方式
- 📊 **市場掃描**：定期獲取市場交易狀況排行
- 📈 **即時報價**：訂閱並監控股票即時報價
- 🤖 **自動交易**：基於動能策略自動產生交易訊號
- 💰 **訂單管理**：支援股票整股、盤中零股交易
- 📝 **交易監控**：即時監控委託與成交狀態
- 📑 **報表產生**：自動產生當日交易摘要報表

## 🏗️ 系統架構

系統採用模組化設計，各模組職責明確：

```
TradingSystem (主程式)
├── Login (登入模組)
├── ContractManager (商品檔管理)
├── QuoteSubscriber (報價訂閱)
├── QuoteCallback (報價回調處理)
├── MarketScanner (市場掃描)
├── StrategyDataPreparer (策略數據準備)
├── MomentumStrategy (動能交易策略)
├── OrderExecutor (下單執行)
├── TradeMonitor (交易監控)
└── AccountManager (帳戶管理)
```

## 🚀 快速開始

### 環境需求

- Python 3.8+
- 永豐證券 Shioaji API 帳號

### 安裝

1. 克隆專案：
```bash
git clone https://github.com/yourusername/sample-trading.git
cd sample-trading
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

### 基本使用

```python
from trading_system import TradingSystem

# 1. 初始化系統
system = TradingSystem()
system.initialize(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY"
)

# 2. 啟動策略數據準備（每 10 分鐘更新）
system.start_data_preparation(interval_seconds=600, count=100)

# 3. 訂閱漲幅 > 4% 的股票
system.subscribe_stocks_by_change_percent(threshold=4.0, count=100)

# 4. 註冊訊號處理器（自動下單）
system.register_signal_handler()

# 5. 等待交易訊號並自動執行...
# 系統會自動監控報價、產生訊號、執行下單、監控成交

# 6. 當日交易結束後，產生報表
system.print_daily_report()

# 7. 關閉系統
system.shutdown()
```

## 📦 模組說明

### 核心模組

#### 1. Login (登入模組)
- 職責：使用者驗證與身份認證
- 主要方法：
  - `login(api_key, secret_key)`: 執行登入
  - `is_logged_in()`: 檢查登入狀態
  - `logout()`: 登出

#### 2. ContractManager (商品檔管理)
- 職責：獲取可交易的商品資訊
- 主要方法：
  - `fetch_contracts()`: 獲取商品檔
  - `get_stock(code)`: 取得指定股票合約
  - `get_all_stocks()`: 取得所有股票合約

#### 3. MarketScanner (市場掃描)
- 職責：提供市場交易狀況排行
- 主要方法：
  - `get_change_percent_rank()`: 取得漲跌幅排行
  - `get_volume_rank()`: 取得成交量排行
  - `get_amount_rank()`: 取得成交金額排行

#### 4. QuoteSubscriber (報價訂閱)
- 職責：訂閱即時市場報價
- 主要方法：
  - `subscribe(contract)`: 訂閱報價
  - `unsubscribe(contract)`: 取消訂閱
  - `get_subscribed_contracts()`: 取得已訂閱列表

#### 5. QuoteCallback (報價回調處理)
- 職責：處理接收到的報價資料
- 主要方法：
  - `set_quote_callback(callback)`: 設定報價回調函數
  - `get_latest_quote(code)`: 取得最新報價

#### 6. StrategyDataPreparer (策略數據準備)
- 職責：定期獲取市場數據
- 主要方法：
  - `start_auto_update()`: 啟動自動更新
  - `update_market_data()`: 更新市場數據
  - `get_top_gainers()`: 取得漲幅最大股票

#### 7. MomentumStrategy (動能交易策略)
- 職責：基於漲幅和成交量產生交易訊號
- 訊號條件：
  - 漲幅 > 6%（可調整）
  - 成交量 > 1000 張（可調整）
- 主要方法：
  - `set_change_percent_threshold()`: 設定漲幅閾值
  - `set_volume_threshold()`: 設定成交量閾值
  - `get_signals()`: 取得所有訊號

#### 8. OrderExecutor (下單執行)
- 職責：執行交易訂單
- 主要方法：
  - `place_stock_order()`: 下股票委託單
  - `update_order()`: 修改訂單
  - `cancel_order()`: 取消訂單

#### 9. TradeMonitor (交易監控)
- 職責：監控委託與成交狀態
- 主要方法：
  - `list_trades()`: 列出所有交易
  - `update_status()`: 更新訂單狀態
  - `get_deals()`: 取得成交明細

#### 10. AccountManager (帳戶管理)
- 職責：管理帳戶餘額與持倉
- 主要方法：
  - `list_positions()`: 列出所有持倉
  - `get_total_unrealized_pnl()`: 計算未實現損益
  - `get_position_summary()`: 取得持倉摘要

#### 11. TradingSystem (交易系統主程式)
- 職責：協調所有模組，控制交易流程
- 主要方法：
  - `initialize()`: 初始化系統
  - `get_market_ranking()`: 取得市場排行
  - `subscribe_stocks_by_change_percent()`: 訂閱符合條件的股票
  - `register_signal_handler()`: 註冊訊號處理器
  - `generate_daily_report()`: 產生交易報表
  - `shutdown()`: 關閉系統

## 🎯 交易策略說明

### 動能交易策略 (Momentum Strategy)

系統實現了基於價格動能的交易策略：

1. **市場掃描階段**
   - 每 10 分鐘掃描市場交易狀況排行
   - 找出漲幅 > 4% 的股票

2. **報價訂閱階段**
   - 自動訂閱符合條件的股票即時報價
   - 持續監控價格與成交量變化

3. **訊號產生階段**
   - 當股票漲幅 > 6% 且成交量 > 1000 張時
   - 自動產生買入訊號

4. **訂單執行階段**
   - 收到訊號後自動執行下單
   - 使用限價單（可調整）

5. **訂單監控階段**
   - 監控委託回報直到委託成功
   - 監控成交回報直到成交完成

6. **報表產生階段**
   - 當日交易結束後產生摘要報表
   - 包含訊號統計、交易明細、持倉狀況

## 📊 交易報表範例

```
================================================================================
交易摘要報表 - 2025-10-07
================================================================================

【摘要統計】
  交易訊號數: 5
  執行交易數: 3
  訂閱股票數: 15
  當前持倉數: 2
  未實現損益: 1250.00

【交易訊號】
  1. 2330 Buy @ 500.0
     原因: 漲幅 6.50% > 6.0%, 成交量 1500 張 > 1000 張
     時間: 2025-10-07 10:30:00

【執行交易】
  1. 訂單 12345: 2330 Buy @ 500.0 x 1 (Filled)

【當前持倉】
  1. 2330: 1 張 @ 500.00 (損益: 1250.00)

================================================================================
```

## 🔧 進階配置

### 自訂策略閾值

```python
from strategy import MomentumStrategy
from quote_callback import QuoteCallback

# 初始化
callback = QuoteCallback(api)
strategy = MomentumStrategy(callback)

# 調整閾值
strategy.set_change_percent_threshold(8.0)   # 漲幅 > 8%
strategy.set_volume_threshold(2000)          # 成交量 > 2000 張
```

### 自訂訊號處理器

```python
def custom_signal_handler(signal):
    print(f"收到訊號: {signal.code} {signal.action}")
    # 自訂處理邏輯
    # 例如：風險控制、倉位管理等

system.register_signal_handler(custom_signal_handler)
```

### 調整數據更新頻率

```python
# 每 5 分鐘更新一次市場數據
system.start_data_preparation(interval_seconds=300, count=50)
```

## 📋 系統需求

- Python 3.8 或更高版本
- 穩定的網路連線
- 永豐證券 Shioaji API 帳號
- 足夠的交易權限與資金

## ⚠️ 注意事項

1. **風險警告**
   - 本系統僅供學習與研究使用
   - 實際交易前請充分測試並評估風險
   - 過去績效不代表未來表現

2. **API 限制**
   - 注意永豐 API 的呼叫頻率限制
   - 避免過於頻繁的訂單操作

3. **資金管理**
   - 建議設定單筆交易金額上限
   - 控制總體風險暴露

4. **系統監控**
   - 建議搭配日誌監控系統運行狀況
   - 定期檢查訂單執行結果

5. **網路穩定性**
   - 確保網路連線穩定
   - 建議在交易時段使用有線網路

## 🛠️ 開發指南

### 專案結構

```
sample-trading/
├── login.py                    # 登入模組
├── contract.py                 # 商品檔管理模組
├── quote_subscriber.py         # 報價訂閱模組
├── quote_callback.py           # 報價回調處理模組
├── market_scanner.py           # 市場掃描模組
├── order_executor.py           # 下單執行模組
├── trade_monitor.py            # 交易監控模組
├── account_manager.py          # 帳戶管理模組
├── strategy_data_preparer.py   # 策略數據準備模組
├── strategy.py                 # 交易策略模組
├── trading_system.py           # 交易系統主程式
├── requirements.txt            # 依賴清單
├── README.md                   # 專案說明
└── 類別圖.md                   # 系統架構圖
```

### 設計原則

本專案遵循以下設計原則：

- **SOLID 原則**：每個模組職責單一、易於擴展
- **依賴注入**：模組間透過建構子注入依賴
- **錯誤處理**：使用具體錯誤類型，避免籠統的 Exception
- **完整文檔**：所有函數包含完整的 docstring
- **型別標註**：使用 Python type hints 提升程式碼可讀性

### 程式碼規範

- 遵循 PEP 8 編碼風格
- 使用繁體中文撰寫註釋與文檔
- 所有函數包含 Args、Returns、Examples、Raises 說明
- Commit 訊息遵循 Conventional Commits 規範

## 📚 參考資源

- [永豐 Shioaji API 文檔](https://sinotrade.github.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [SOLID 設計原則](https://en.wikipedia.org/wiki/SOLID)

## 📄 授權

請參閱 [LICENSE](LICENSE) 文件。

## 🤝 貢獻

歡迎提出 Issue 或 Pull Request！

## 📧 聯絡方式

如有問題或建議，歡迎透過 Issue 與我們聯繫。

---

**免責聲明**：本系統僅供教育與研究目的使用。使用者需自行承擔交易風險，開發者不對任何交易損失負責。
