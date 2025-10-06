# 交易系統登入功能架構設計

## 架構概述

本專案採用 **Ports and Adapters**（六角架構 / Hexagonal Architecture）設計模式，實現了永豐證券交易系統的登入功能。這種架構模式將核心業務邏輯與外部依賴（如 SDK、資料庫、API）分離，提供了以下優勢：

- ✅ **可測試性**：可以輕鬆使用 mock 進行單元測試
- ✅ **可維護性**：業務邏輯與實作細節分離
- ✅ **可擴展性**：容易替換或新增不同的 Adapter
- ✅ **鬆耦合**：降低各模組之間的依賴關係

## 架構圖

```
┌─────────────────────────────────────────────────────────┐
│                      應用層                              │
│                 (Application Layer)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 依賴於介面（Port）
                     │
┌────────────────────▼────────────────────────────────────┐
│                 LoginPort (介面)                         │
│                   - login()                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 實作介面
                     │
┌────────────────────▼────────────────────────────────────┐
│          SinopacLoginAdapter (Adapter)                  │
│         實作 LoginPort 介面                              │
│         對接永豐 SDK / API                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 使用
                     │
┌────────────────────▼────────────────────────────────────┐
│                  外部服務                                │
│            (Sinopac API / SDK)                          │
└─────────────────────────────────────────────────────────┘
```

## 模組說明

### 1. DTOs (Data Transfer Objects) - 資料傳輸物件

**檔案：** `login_dto.py`

提供穩定的資料模型，隔離應用程式與 SDK 實作細節。

#### LoginRequestDTO
- **用途**：封裝登入請求所需的所有參數
- **屬性**：
  - `api_key`: API 金鑰
  - `secret_key`: 密鑰
  - `person_id`: 身份證字號
  - `ca_password`: 憑證密碼

#### LoginResponseDTO
- **用途**：封裝登入成功後的回應資訊
- **屬性**：
  - `success`: 是否成功
  - `token`: 認證 token
  - `session_id`: 會話 ID
  - `user_id`: 使用者 ID
  - `login_time`: 登入時間
  - `message`: 訊息

### 2. Port (介面) - 領域邊界

**檔案：** `login_port.py`

定義登入功能的抽象介面，遵循依賴反轉原則（DIP）。

#### LoginPort
- **用途**：定義登入操作的契約
- **方法**：
  - `login(request: LoginRequestDTO) -> LoginResponseDTO`

### 3. Adapter (適配器) - 外部整合

**檔案：** `sinopac_login_adapter.py`

實作 LoginPort 介面，負責與永豐 API 通訊。

#### SinopacLoginAdapter
- **用途**：將永豐 SDK/API 適配到 LoginPort 介面
- **特性**：
  - HTTP 客戶端可注入（便於測試）
  - 完整的錯誤處理
  - 回應資料驗證
  - 參數驗證

### 4. Exceptions (例外處理) - 錯誤類型

**檔案：** `login_exceptions.py`

定義清晰的例外階層，提供精確的錯誤處理。

#### 例外類別階層
```
LoginException (基礎例外)
├── AuthenticationError (認證失敗)
├── ConnectionError (連線失敗)
├── DataFormatError (資料格式錯誤)
├── ParameterError (參數錯誤)
└── ServerError (伺服器錯誤)
```

### 5. Configuration (配置管理)

**檔案：** `config.py`, `config.yaml`

提供配置管理功能，使用 YAML 格式儲存敏感資訊。

## 使用範例

### 基本使用

```python
from config import Config
from login_dto import LoginRequestDTO
from sinopac_login_adapter import SinopacLoginAdapter

# 1. 載入配置
config = Config("config.yaml")

# 2. 建立登入請求
request = LoginRequestDTO(
    api_key=config.api_key,
    secret_key=config.secret_key,
    person_id=config.person_id,
    ca_password=config.ca_password
)

# 3. 初始化 Adapter
adapter = SinopacLoginAdapter()

# 4. 執行登入
response = adapter.login(request)

# 5. 使用回應資料
print(f"Token: {response.token}")
print(f"Session ID: {response.session_id}")
```

### 測試使用 (使用 Mock)

```python
from unittest.mock import Mock
from sinopac_login_adapter import SinopacLoginAdapter

# 建立 mock HTTP 客戶端
mock_http_client = Mock()
mock_response = Mock()
mock_response.status_code = 200
mock_response.json.return_value = {
    "token": "test_token",
    "session_id": "test_session",
    "user_id": "A123456789",
    "login_time": "2025-10-06T10:00:00"
}
mock_http_client.post.return_value = mock_response

# 注入 mock 客戶端
adapter = SinopacLoginAdapter(http_client=mock_http_client)

# 執行測試
response = adapter.login(request)
```

## 錯誤處理

所有錯誤都會拋出特定的例外類型，便於精確處理：

```python
try:
    response = adapter.login(request)
except AuthenticationError:
    # 處理認證失敗（帳號密碼錯誤）
except ConnectionError:
    # 處理連線失敗或逾時
except DataFormatError:
    # 處理資料格式錯誤
except ParameterError:
    # 處理參數錯誤
except ServerError as e:
    # 處理伺服器錯誤（HTTP 4xx, 5xx）
    print(f"Status code: {e.status_code}")
```

## 測試策略

### 單元測試覆蓋率

- ✅ 成功登入情境
- ✅ 認證失敗（401, 403）
- ✅ 連線失敗與逾時
- ✅ 資料格式錯誤
- ✅ 參數驗證
- ✅ HTTP 錯誤狀態碼（500, 503, 400）
- ✅ HTTP 客戶端呼叫驗證
- ✅ 選擇性欄位處理

### 測試執行

```bash
# 執行所有測試
python3 -m pytest -v

# 執行特定測試
python3 -m pytest test_sinopac_login_adapter.py -v

# 檢視測試覆蓋率
python3 -m pytest --cov=. --cov-report=html
```

## 設計原則

本專案遵循以下設計原則：

1. **SOLID 原則**
   - Single Responsibility: 每個類別只有一個責任
   - Open/Closed: 開放擴展，封閉修改
   - Liskov Substitution: 可替換性
   - Interface Segregation: 介面隔離
   - Dependency Inversion: 依賴反轉

2. **簡潔原則**
   - 避免過度設計
   - 程式碼直觀易懂
   - 清晰的命名

3. **測試驅動**
   - 完整的單元測試
   - 使用 mock 隔離外部依賴
   - 高測試覆蓋率

## 擴展性

### 新增其他券商 Adapter

```python
from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO

class AnotherBrokerAdapter(LoginPort):
    """另一個券商的 Adapter 實作"""
    
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        # 實作其他券商的登入邏輯
        pass
```

### 新增其他認證方式

只需實作 LoginPort 介面，不需修改現有程式碼：

```python
class OAuthLoginAdapter(LoginPort):
    """OAuth 登入 Adapter"""
    
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        # 實作 OAuth 認證邏輯
        pass
```

## 檔案結構

```
.
├── config.py                       # 配置管理
├── config.yaml                     # 配置檔案（敏感資訊）
├── yaml_sample.yaml                # 配置檔案範例
├── login_port.py                   # Port 介面定義
├── login_dto.py                    # DTO 定義
├── login_exceptions.py             # 例外定義
├── sinopac_login_adapter.py        # 永豐 Adapter 實作
├── test_config.py                  # Config 測試
├── test_sinopac_login_adapter.py   # Adapter 測試
├── example_usage.py                # 使用範例
├── requirements.txt                # Python 依賴
├── ARCHITECTURE.md                 # 架構文件（本文件）
└── .gitignore                      # Git 忽略檔案
```

## 安全性考量

1. **敏感資訊保護**
   - `config.yaml` 已加入 `.gitignore`
   - 不要將真實憑證提交到版本控制

2. **錯誤訊息**
   - 不在錯誤訊息中洩漏敏感資訊
   - `__repr__` 方法會遮蔽敏感資料

3. **HTTPS**
   - 所有 API 通訊使用 HTTPS
   - 驗證伺服器憑證

## 效能考量

1. **逾時設定**
   - 預設 30 秒逾時
   - 可自訂逾時時間

2. **連線重用**
   - 考慮使用 session 物件重用連線
   - 減少 TCP 握手開銷

3. **錯誤重試**
   - 可在應用層實作重試邏輯
   - 指數退避策略

## 未來改進方向

1. **非同步支援**
   - 實作 async/await 版本的 Adapter
   - 提升並發處理能力

2. **快取機制**
   - Token 快取
   - 減少重複登入

3. **日誌記錄**
   - 結構化日誌
   - 請求追蹤

4. **監控指標**
   - 登入成功率
   - 回應時間
   - 錯誤率

---

**版本：** 1.0.0  
**最後更新：** 2025-10-06  
**維護者：** Trading System Team
