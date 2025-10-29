# 永豐金證券股票回測系統

## 專案簡介

本專案提供永豐金證券 (Sinotrade) API 的 Python 整合介面，用於股票交易和回測系統的開發。透過封裝 Shioaji API，提供更簡潔、易用的操作介面。

## 系統架構

本系統採用模組化設計，遵循 SOLID 設計原則，主要包含以下模組：

### 核心模組

- **AuthenticationService（認證服務）**：負責帳號登入、登出和認證狀態管理
- **SinotradeClient（客戶端）**：提供 API 操作的主要介面
- **LoginCredentials（登入憑證）**：封裝登入所需的憑證資訊

詳細的類別結構請參考 [類別圖.md](./類別圖.md)

## 功能特色

- ✅ 安全的帳號認證機制
- ✅ 完整的錯誤處理和日誌記錄
- ✅ 支援模擬和實盤環境
- ✅ 證券和期貨帳號管理
- ✅ 遵循 SOLID 設計原則
- ✅ 完整的 docstring 文件

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
│   └── client.py            # 客戶端模組
├── requirements.txt          # 專案相依套件
├── 類別圖.md                 # 系統類別圖
├── README.md                 # 專案說明文件
└── LICENSE                   # 授權條款
```

## 注意事項

1. **安全性**：請勿將帳號密碼寫死在程式碼中，建議使用環境變數或設定檔
2. **連線限制**：永豐金證券有連線數限制，不使用時請記得登出
3. **模擬環境**：開發測試時建議使用模擬環境 (`simulation=True`)
4. **錯誤處理**：務必妥善處理各種可能的錯誤情況

## 版本資訊

- 當前版本：0.1.0
- Python 版本要求：>= 3.8
- Shioaji 版本要求：>= 1.0.0

## 授權條款

請參考 [LICENSE](./LICENSE) 文件

## 參考資源

- [Shioaji 官方文件](https://sinotrade.github.io/)
- [永豐金證券 API 登入教學](https://sinotrade.github.io/zh/tutor/login/)

## 開發狀態

- ✅ 基礎認證功能
- ✅ 帳號管理功能
- ⏳ 交易功能（開發中）
- ⏳ 回測系統（計畫中）

## 聯絡方式

如有任何問題或建議，歡迎提出 Issue 或 Pull Request。