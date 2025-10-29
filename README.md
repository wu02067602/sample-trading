# 永豐金證券股票回測系統

## 專案簡介

本專案提供永豐金證券 (Sinotrade) API 的 Python 整合介面，用於股票交易和回測系統的開發。透過封裝 Shioaji API，提供更簡潔、易用的操作介面。

## 系統架構

本系統採用模組化設計，遵循 SOLID 設計原則，主要包含以下模組：

### 核心模組

#### 認證模組
- **AuthenticationService（認證服務）**：負責帳號登入、登出和認證狀態管理
- **SinotradeClient（客戶端）**：提供 API 操作的主要介面
- **LoginCredentials（登入憑證）**：封裝登入所需的憑證資訊

#### 市場資料模組
- **MarketDataFetcher（市場資料抓取器）**：從永豐金證券抓取歷史交易資料
- **DateRange（日期區間）**：封裝日期範圍資訊

#### 資料儲存模組
- **BigQueryStorage（BigQuery 儲存服務）**：管理 BigQuery 資料存取
- **DataValidator（資料驗證器）**：驗證資料完整性和品質

詳細的類別結構請參考 [類別圖.md](./類別圖.md) 和 [元件圖.md](./元件圖.md)

## 功能特色

### 認證與帳號管理
- ✅ 安全的帳號認證機制
- ✅ 支援模擬和實盤環境
- ✅ 證券和期貨帳號管理

### 市場資料抓取
- ✅ 支援全市場股票資料抓取
- ✅ 批量處理多支股票
- ✅ 自動錯誤處理和重試機制
- ✅ 資料格式自動轉換為 DataFrame

### 資料儲存與管理
- ✅ 整合 Google BigQuery 雲端資料倉儲
- ✅ 自動建立和管理資料表
- ✅ 支援資料表分區和叢集優化
- ✅ 完整的資料驗證機制

### 程式品質
- ✅ 遵循 SOLID 設計原則
- ✅ 完整的 docstring 文件
- ✅ 完整的錯誤處理和日誌記錄
- ✅ 模組化設計，易於擴展

## 安裝方式

### 環境需求

- Python 3.8 或以上版本
- pip 套件管理工具

### 安裝步驟

1. 複製專案到本地

```bash
git clone <repository_url>
cd <project_directory>
```

2. 安裝相依套件

```bash
pip install -r requirements.txt
```

## 使用方式

### 基本使用範例

```python
from src.client import SinotradeClient

# 建立客戶端（模擬環境）
client = SinotradeClient(simulation=True)

# 登入
success = client.login(
    person_id="您的身份證字號",
    passwd="您的密碼"
)

if success:
    print("登入成功！")
    
    # 取得帳號列表
    accounts = client.list_accounts()
    print(f"帳號數量: {len(accounts)}")
    
    # 取得證券帳號
    stock_acc = client.stock_account
    print(f"證券帳號: {stock_acc.account_id}")
    
    # 登出
    client.logout()
```

### 進階使用

```python
from src.client import SinotradeClient
from src.authentication import LoginCredentials

# 建立客戶端（實盤環境）
client = SinotradeClient(simulation=False, log_level="DEBUG")

# 準備登入憑證
credentials = LoginCredentials(
    person_id="您的身份證字號",
    passwd="您的密碼"
)

# 登入
client.login(
    person_id=credentials.person_id,
    passwd=credentials.passwd,
    subscribe_trade=True,
    contracts_timeout=30000
)

# 取得所有帳號
accounts = client.list_accounts()

# 設定預設帳號
if len(accounts) > 0:
    client.set_default_account(accounts[0])
    print(f"預設帳號已設定為: {accounts[0].account_id}")

# 檢查登入狀態
if client.is_logged_in:
    print("目前已登入")
```

### 抓取市場資料

```python
from src.client import SinotradeClient
from src.market_data import MarketDataFetcher, DateRange

# 登入
client = SinotradeClient(simulation=True)
client.login("your_id", "your_password")

# 建立資料抓取器
fetcher = MarketDataFetcher(client.api)

# 定義日期範圍
date_range = DateRange(
    start_date="2023-01-01",
    end_date="2023-01-31"
)

# 抓取單一股票資料
df_2330 = fetcher.fetch_stock_kbars("2330", date_range)
print(f"台積電資料筆數: {len(df_2330)}")

# 抓取多支股票資料
stocks = ["2330", "2317", "2454"]
df_multiple = fetcher.fetch_multiple_stocks_kbars(stocks, date_range)
print(f"多支股票資料筆數: {len(df_multiple)}")

# 抓取全市場資料（較耗時）
df_all = fetcher.fetch_all_market_kbars(date_range)
print(f"全市場資料筆數: {len(df_all)}")
```

### 儲存資料到 BigQuery

```python
from src.bigquery_storage import BigQueryStorage

# 建立 BigQuery 儲存服務
storage = BigQueryStorage(
    project_id="your-gcp-project",
    dataset_id="stock_data",
    table_id="daily_kbars",
    credentials_path="/path/to/credentials.json"  # 選用
)

# 上傳資料
count = storage.insert_dataframe(df_all)
print(f"成功上傳 {count} 筆資料")

# 查詢資料
query = """
    SELECT stock_code, AVG(Close) as avg_close
    FROM `your-gcp-project.stock_data.daily_kbars`
    WHERE DATE(ts) BETWEEN '2023-01-01' AND '2023-01-31'
    GROUP BY stock_code
    ORDER BY avg_close DESC
    LIMIT 10
"""
result_df = storage.query_data(query)
print(result_df)
```

### 驗證資料完整性

```python
from src.bigquery_storage import DataValidator

# 建立驗證器
validator = DataValidator(storage)

# 檢查資料是否存在
exists = validator.check_data_exists(
    stock_code="2330",
    start_date="2023-01-01",
    end_date="2023-01-31"
)
print(f"資料存在: {exists}")

# 驗證資料品質
quality_report = validator.validate_data_quality("2330")
print(f"資料品質報告: {quality_report}")

# 取得資料摘要
summary = validator.get_data_summary()
print(f"總筆數: {summary['total_records']}")
print(f"股票數: {summary['unique_stocks']}")
print(f"日期範圍: {summary['earliest_date']} ~ {summary['latest_date']}")

# 檢查缺失的日期
trading_days = ["2023-01-03", "2023-01-04", "2023-01-05"]
missing_dates = validator.get_missing_dates(
    stock_code="2330",
    start_date="2023-01-03",
    end_date="2023-01-05",
    expected_trading_days=trading_days
)
if missing_dates:
    print(f"缺失日期: {missing_dates}")
```

## 錯誤處理

系統提供完整的錯誤處理機制：

```python
from src.client import SinotradeClient

client = SinotradeClient()

try:
    client.login("INVALID_ID", "INVALID_PASS")
except ValueError as e:
    print(f"參數錯誤: {e}")
except ConnectionError as e:
    print(f"連線錯誤: {e}")
except RuntimeError as e:
    print(f"執行錯誤: {e}")
```

## 設計原則

本專案嚴格遵循 SOLID 設計原則：

- **單一職責原則 (SRP)**：每個類別只負責單一功能
- **開放封閉原則 (OCP)**：對擴展開放，對修改封閉
- **里氏替換原則 (LSP)**：子類別可以替換父類別
- **介面隔離原則 (ISP)**：使用專門的介面
- **依賴反轉原則 (DIP)**：依賴抽象而非具體實作

## 開發規範

### Docstring 規範

所有函數都必須包含完整的 docstring，包括：
- 函數說明
- 參數 (Args)
- 返回值 (Returns)
- 使用範例 (Examples)
- 可能的錯誤 (Raises)

### 錯誤處理規範

- 禁止使用籠統的錯誤捕捉（`except:` 或 `except Exception:`）
- 必須明確指定要捕捉的錯誤類型
- 每個錯誤都要有明確的處理邏輯

### Git Commit 規範

使用 Conventional Commits 規範：
- `feat:` - 新功能
- `fix:` - 錯誤修復
- `docs:` - 文件更新
- `test:` - 測試相關
- `refactor:` - 重構

## 專案結構

```
.
├── src/
│   ├── __init__.py           # 套件初始化
│   ├── authentication.py     # 認證服務模組
│   ├── client.py            # 客戶端模組
│   ├── market_data.py       # 市場資料抓取模組
│   └── bigquery_storage.py  # BigQuery 儲存與驗證模組
├── requirements.txt          # 專案相依套件
├── 類別圖.md                 # 系統類別圖
├── 元件圖.md                 # 系統元件圖
├── README.md                 # 專案說明文件
└── LICENSE                   # 授權條款
```

## 注意事項

### 安全性
1. **憑證管理**：請勿將帳號密碼寫死在程式碼中，建議使用環境變數或設定檔
2. **GCP 認證**：BigQuery 需要 GCP 服務帳號認證，請妥善保管金鑰檔案
3. **IAM 權限**：確保服務帳號有足夠的 BigQuery 操作權限

### API 使用
1. **連線限制**：永豐金證券有連線數限制，不使用時請記得登出
2. **模擬環境**：開發測試時建議使用模擬環境 (`simulation=True`)
3. **速率限制**：注意 API 呼叫頻率，避免超過限制

### 資料處理
1. **記憶體管理**：全市場資料抓取會產生大量資料，注意記憶體使用
2. **批次處理**：建議分批抓取資料，避免一次處理過多股票
3. **錯誤處理**：使用 `skip_errors=True` 參數，避免單一股票錯誤中斷整個流程

### BigQuery
1. **成本控制**：BigQuery 按查詢資料量計費，注意查詢優化
2. **資料分區**：系統已自動設定按日期分區，查詢時善用分區條件
3. **配額限制**：注意 BigQuery 的每日上傳和查詢配額

## 版本資訊

- 當前版本：0.2.0
- Python 版本要求：>= 3.8
- 主要相依套件：
  - shioaji >= 1.0.0
  - google-cloud-bigquery >= 3.0.0
  - pandas >= 1.5.0
  - db-dtypes >= 1.1.0

## 授權條款

請參考 [LICENSE](./LICENSE) 文件

## 參考資源

### Shioaji API
- [Shioaji 官方文件](https://sinotrade.github.io/)
- [永豐金證券 API 登入教學](https://sinotrade.github.io/zh/tutor/login/)
- [歷史行情資料教學](https://sinotrade.github.io/zh/tutor/market_data/historical/)
- [商品檔使用說明](https://sinotrade.github.io/zh/tutor/contract/)

### Google BigQuery
- [BigQuery 官方文件](https://cloud.google.com/bigquery/docs)
- [Python Client 文件](https://cloud.google.com/python/docs/reference/bigquery/latest)

## 開發狀態

- ✅ 基礎認證功能
- ✅ 帳號管理功能
- ✅ 市場資料抓取功能
- ✅ BigQuery 資料儲存功能
- ✅ 資料完整性驗證功能
- ⏳ 交易功能（計畫中）
- ⏳ 回測系統（計畫中）
- ⏳ 策略回測框架（計畫中）

## 版本歷程

### v0.2.0 (2025-10-29)
- 新增市場資料抓取功能
- 新增 BigQuery 整合
- 新增資料驗證機制
- 更新系統架構文件

### v0.1.0 (2025-10-29)
- 初始版本
- 基礎認證功能
- 帳號管理功能

## 聯絡方式

如有任何問題或建議，歡迎提出 Issue 或 Pull Request。