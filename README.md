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
    # 取得帳戶資訊
    accounts = client.get_accounts()
    print(accounts)
    # 登出
    client.logout()
else:
    print(f"登入失敗: {result['error']}")
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