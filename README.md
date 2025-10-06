# Shioaji 量化交易系統

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![SOLID Principles](https://img.shields.io/badge/SOLID-Compliant-green)](https://en.wikipedia.org/wiki/SOLID)
[![Code Style](https://img.shields.io/badge/code%20style-documented-brightgreen)](https://peps.python.org/pep-0257/)

專業的量化交易系統，整合永豐金證券 Shioaji API，完全遵循 SOLID 設計原則。

## 專案特色

✅ **完全符合 SOLID 原則**: 高品質、可維護、可擴展的程式碼架構  
✅ **完整的文檔**: 所有函數都有詳細的 docstring，包含參數、返回值、範例、異常說明  
✅ **抽象介面設計**: 支援依賴注入，便於測試和擴展  
✅ **單元測試**: 使用 Mock 物件進行測試，無需真實 API 連線  
✅ **類型標註**: 完整的 Type Hints，提升程式碼可讀性  
✅ **錯誤處理**: 完善的異常處理和日誌記錄  
✅ **Context Manager**: 支援 `with` 語句，自動管理資源

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from shioaji_client import ShioajiClient, LoginConfig

# 建立登入配置
config = LoginConfig(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD",
    simulation=True  # 使用模擬環境
)

# 登入並使用
client = ShioajiClient()
client.login(config)

# 取得帳戶資訊
accounts = client.get_accounts()
print(f"股票帳戶: {accounts['stock_account']}")
print(f"期貨帳戶: {accounts['futopt_account']}")

# 取得商品檔
contracts = client.get_contracts()
tsmc = contracts.Stocks["2330"]
print(f"台積電: {tsmc.name}, 參考價: {tsmc.reference}")

# 搜尋商品
results = client.search_contracts("台積")
for contract in results:
    print(f"{contract.code} - {contract.name}")

# 登出
client.logout()
```

### 使用 Context Manager（推薦）

```python
with ShioajiClient() as client:
    config = LoginConfig(
        person_id="YOUR_ID",
        passwd="YOUR_PASSWORD"
    )
    client.login(config)
    
    # 執行交易操作
    accounts = client.get_accounts()
    
# 自動登出，無需手動呼叫 logout()
```

### CA 憑證登入

```python
config = LoginConfig(
    person_id="YOUR_ID",
    passwd="YOUR_PASSWORD",
    ca_path="/path/to/cert.pfx",
    ca_passwd="CERT_PASSWORD"
)

client = ShioajiClient()
client.login(config)
```

## 專案結構

```
/workspace/
├── trading_interface.py       # 抽象介面定義 (ITradingClient, IConfigValidator)
├── shioaji_client.py          # Shioaji 客戶端實作
├── test_shioaji_client.py     # 單元測試
├── example_usage.py           # 登入使用範例
├── example_contracts.py       # 商品檔使用範例
├── requirements.txt           # 專案依賴
├── 類別圖.md                   # Mermaid 類別圖文檔
├── REFACTORING_SUMMARY.md     # 重構總結報告
├── SOLID_REVIEW.md            # SOLID 原則檢查報告
└── README.md                  # 本文件
```

## 架構設計

### 類別圖

詳細的類別圖請參考 [類別圖.md](類別圖.md)

### SOLID 原則實踐

| 原則 | 實踐方式 |
|------|---------|
| **單一職責原則 (SRP)** | 每個類別只有一個職責：`LoginConfig` 負責配置、`ShioajiClient` 負責 API 管理 |
| **開放封閉原則 (OCP)** | 通過抽象介面擴展功能，無需修改現有程式碼 |
| **里氏替換原則 (LSP)** | 所有實作 `ITradingClient` 的類別都可互相替換 |
| **介面隔離原則 (ISP)** | 介面精簡專注，只包含必要方法 |
| **依賴反轉原則 (DIP)** | 高層模組依賴抽象介面，而非具體實作 |

詳細說明請參考 [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)

## API 文檔

### LoginConfig

登入配置資料類別，實作 `IConfigValidator` 介面。

**屬性**:
- `person_id` (str): 使用者身分證字號或統一編號
- `passwd` (str): 使用者密碼
- `ca_path` (Optional[str]): CA 憑證路徑
- `ca_passwd` (Optional[str]): CA 憑證密碼
- `simulation` (bool): 是否使用模擬環境，預設為 False

**方法**:
- `validate()`: 驗證配置參數的有效性

### ShioajiClient

Shioaji 交易客戶端，實作 `ITradingClient` 介面。

**屬性**:
- `sj` (Optional[Shioaji]): Shioaji API 實例
- `is_logged_in` (bool): 登入狀態標記
- `config` (Optional[LoginConfig]): 登入配置資訊
- `contracts` (Optional[Any]): 商品檔物件（登入後自動載入）

**方法**:
- `connect(config: LoginConfig) -> bool`: 連接到交易系統
- `disconnect() -> bool`: 斷開連線
- `login(config: LoginConfig) -> bool`: 執行登入操作
- `logout() -> bool`: 執行登出操作
- `get_accounts() -> Dict[str, Any]`: 取得帳戶資訊
- `is_connected() -> bool`: 檢查連線狀態
- `get_contracts() -> Any`: 取得商品檔資訊
- `search_contracts(keyword: str) -> list`: 搜尋商品檔
- `get_stock(code: str) -> Any`: 取得特定股票商品

### ITradingClient (介面)

交易客戶端抽象介面，定義了所有交易客戶端必須實作的方法。

**方法**:
- `connect(config: Any) -> bool`: 連接到交易系統
- `disconnect() -> bool`: 斷開連線
- `get_accounts() -> Dict[str, Any]`: 取得帳戶資訊
- `is_connected() -> bool`: 檢查連線狀態

## 測試

### 執行單元測試

```bash
python3 test_shioaji_client.py
```

### 測試覆蓋範圍

- ✅ 配置驗證測試
- ✅ 登入/登出流程測試
- ✅ CA 憑證登入測試
- ✅ 帳戶查詢測試
- ✅ 商品檔取得測試
- ✅ 商品檔搜尋測試
- ✅ 股票查詢測試
- ✅ Context Manager 測試
- ✅ 錯誤處理測試

## 設計模式

本專案應用了以下設計模式：

1. **Facade Pattern (外觀模式)**: `ShioajiClient` 提供簡化的介面封裝 Shioaji SDK
2. **Adapter Pattern (適配器模式)**: 將 Shioaji SDK 適配到 `ITradingClient` 介面
3. **Strategy Pattern (策略模式)**: 通過介面實現可替換的交易策略
4. **Context Manager Pattern**: 支援 `with` 語句的資源管理

## 擴展性

### 添加新的交易平台

通過實作 `ITradingClient` 介面，可以輕鬆添加其他交易平台：

```python
class FutuTradingClient(ITradingClient):
    """富途證券客戶端"""
    
    def connect(self, config: Any) -> bool:
        # 實作富途的登入邏輯
        pass
    
    def disconnect(self) -> bool:
        # 實作登出邏輯
        pass
    
    def get_accounts(self) -> Dict[str, Any]:
        # 實作取得帳戶邏輯
        pass
    
    def is_connected(self) -> bool:
        # 實作檢查連線邏輯
        pass
```

## 程式碼品質

- ✅ 完整的 Type Hints
- ✅ 詳細的 Docstring（遵循 Google/NumPy 風格）
- ✅ 完善的錯誤處理
- ✅ 日誌記錄
- ✅ 單元測試
- ✅ 符合 SOLID 原則

## 參考資料

- [Shioaji 官方文檔](https://sinotrade.github.io/)
- [Shioaji 登入教學](https://sinotrade.github.io/zh/tutor/login/)
- [SOLID 設計原則](https://en.wikipedia.org/wiki/SOLID)

## 授權

本專案遵循 MIT 授權。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 作者

專業的 Python 工程師團隊，遵循 SOLID 原則和最佳實踐。

---

**注意**: 本專案為教學和示範用途，請在正式環境使用前進行充分測試。