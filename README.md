# 交易系統 - 登入功能實作

這是一個使用 **Ports and Adapters** 架構模式實作的交易系統登入功能，專為永豐證券（Sinopac）交易系統設計。

## ✨ 特色

- 🏗️ **Ports and Adapters 架構**：清晰的關注點分離，易於測試和維護
- 📦 **DTO 模式**：穩定的資料模型，隔離外部依賴
- 🛡️ **完整的錯誤處理**：明確的例外類型，精確的錯誤處理
- ✅ **高測試覆蓋率**：16 個單元測試，100% mock，無外部依賴
- 📝 **完整的 Docstring**：所有函數都有詳細的文件註解
- 🔒 **安全性考量**：敏感資訊保護，遮蔽機制

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 配置設定

1. 複製範例配置檔案：
```bash
cp yaml_sample.yaml config.yaml
```

2. 編輯 `config.yaml`，填入你的永豐證券憑證：
```yaml
api_key: "your_api_key_here"
secret_key: "your_secret_key_here"
person_id: "your_person_id_here"
ca_password: "your_ca_password_here"
```

### 使用範例

```python
from config import Config
from login_dto import LoginRequestDTO
from sinopac_login_adapter import SinopacLoginAdapter

# 載入配置
config = Config("config.yaml")

# 建立登入請求
request = LoginRequestDTO(
    api_key=config.api_key,
    secret_key=config.secret_key,
    person_id=config.person_id,
    ca_password=config.ca_password
)

# 初始化 Adapter 並登入
adapter = SinopacLoginAdapter()
response = adapter.login(request)

# 使用回應資料
print(f"登入成功！Token: {response.token}")
print(f"Session ID: {response.session_id}")
```

完整使用範例請參考 `example_usage.py`。

## 🧪 執行測試

```bash
# 執行所有測試
python3 -m pytest -v

# 執行特定測試
python3 -m pytest test_sinopac_login_adapter.py -v

# 查看詳細測試輸出
python3 -m pytest -v --tb=short
```

### 測試覆蓋率

```
✅ Config 類別測試：7 個測試
✅ SinopacLoginAdapter 測試：9 個測試
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
總計：16 個測試，全部通過
```

## 📁 專案結構

```
.
├── config.py                       # 配置管理類別
├── config.yaml                     # 配置檔案（請勿提交）
├── yaml_sample.yaml                # 配置範例
├── login_port.py                   # Port 介面定義
├── login_dto.py                    # DTO 資料模型
├── login_exceptions.py             # 自訂例外
├── sinopac_login_adapter.py        # 永豐 Adapter 實作
├── test_config.py                  # Config 測試
├── test_sinopac_login_adapter.py   # Adapter 測試
├── example_usage.py                # 使用範例
├── ARCHITECTURE.md                 # 架構詳細文件
├── requirements.txt                # Python 依賴
└── README.md                       # 本文件
```

## 📚 架構設計

本專案採用 **Ports and Adapters**（六角架構）設計模式：

```
應用層
   ↓
LoginPort (介面)
   ↓
SinopacLoginAdapter (實作)
   ↓
永豐 API / SDK
```

詳細架構說明請參考 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 🛡️ 例外處理

所有例外都繼承自 `LoginException`：

- **`AuthenticationError`**：認證失敗（帳號密碼錯誤）
- **`ConnectionError`**：連線失敗或逾時
- **`DataFormatError`**：回應資料格式錯誤
- **`ParameterError`**：輸入參數錯誤
- **`ServerError`**：伺服器錯誤（HTTP 4xx, 5xx）

```python
from login_exceptions import AuthenticationError, ConnectionError

try:
    response = adapter.login(request)
except AuthenticationError:
    print("認證失敗，請檢查帳號密碼")
except ConnectionError:
    print("連線失敗，請檢查網路")
```

## 🔧 開發原則

- ✅ **簡潔優於複雜**：避免過度設計
- ✅ **SOLID 原則**：單一職責、開放封閉、依賴反轉等
- ✅ **完整的文件**：所有函數都有 docstring
- ✅ **測試驅動**：使用 mock 進行單元測試
- ✅ **型別提示**：使用 Python type hints

## 📝 程式碼風格

所有 Python 函數都包含完整的 docstring，包括：

- 函數描述
- 參數說明
- 返回值說明
- 可能的例外
- 使用範例

範例：

```python
def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
    """Perform login operation with Sinopac API.
    
    Args:
        request: LoginRequestDTO containing login credentials
    
    Returns:
        LoginResponseDTO containing authentication token and session info
    
    Raises:
        AuthenticationError: When credentials are invalid
        ConnectionError: When connection to server fails
    
    Examples:
        >>> adapter = SinopacLoginAdapter()
        >>> request = LoginRequestDTO(...)
        >>> response = adapter.login(request)
    """
```

## 🔒 安全性

- ❌ **不要提交** `config.yaml` 到版本控制
- ✅ `config.yaml` 已加入 `.gitignore`
- ✅ 敏感資訊在日誌中會被遮蔽
- ✅ 所有 API 通訊使用 HTTPS

## 📊 測試案例

### Config 類別測試
1. ✅ 檔案不存在時拋出例外
2. ✅ 成功讀取 YAML 檔案
3. ✅ 驗證 YAML 格式
4. ✅ 屬性正確儲存
5. ✅ 驗證失敗時拋出例外
6. ✅ 讀取失敗時拋出例外
7. ✅ 字串表示遮蔽敏感資訊

### SinopacLoginAdapter 測試
1. ✅ 成功登入返回正確 DTO
2. ✅ 認證失敗拋出 AuthenticationError
3. ✅ 連線失敗拋出 ConnectionError
4. ✅ 資料格式錯誤拋出 DataFormatError
5. ✅ 參數錯誤拋出 ParameterError
6. ✅ HTTP 錯誤拋出 ServerError
7. ✅ 正確呼叫 HTTP 客戶端
8. ✅ 自訂參數初始化
9. ✅ 處理選擇性欄位

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

請參考 LICENSE 檔案。

## 👨‍💻 作者

Trading System Team

---

**版本：** 1.0.0  
**最後更新：** 2025-10-06