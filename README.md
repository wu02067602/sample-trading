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

#### 基本使用（推薦）

```python
from client import Client

# 建立 Client 並登入
client = Client("config.yaml")
client.login()

# 使用 session (sj 屬性)
print(f"登入成功！")
print(f"Token: {client.sj.token}")
print(f"Session ID: {client.sj.session_id}")
print(f"User ID: {client.sj.user_id}")
print(f"Is logged in: {client.is_logged_in}")

# 登出
client.logout()
```

#### 使用 Context Manager（自動登出）

```python
from client import Client

# 使用 with 語句，自動處理登出
with Client("config.yaml") as client:
    client.login()
    # 進行交易操作...
    print(f"Session ID: {client.sj.session_id}")
# 離開 with 區塊後自動登出
```

#### 錯誤處理

```python
from client import Client
from login_exceptions import AuthenticationError, ConnectionError

try:
    client = Client("config.yaml")
    client.login()
    print("登入成功！")
except AuthenticationError:
    print("認證失敗，請檢查帳號密碼")
except ConnectionError:
    print("連線失敗，請檢查網路")
```

完整使用範例請參考 `example_client_usage.py` 和 `example_usage.py`。

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
✅ Client 單元測試：14 個測試
✅ Client 整合測試：9 個測試
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
總計：39 個測試，全部通過
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
├── client.py                       # Client 類別（主要使用介面）
├── test_config.py                  # Config 測試
├── test_sinopac_login_adapter.py   # Adapter 測試
├── test_client.py                  # Client 單元測試
├── test_client_integration.py      # Client 整合測試
├── example_usage.py                # Adapter 使用範例
├── example_client_usage.py         # Client 使用範例
├── ARCHITECTURE.md                 # 架構詳細文件
├── requirements.txt                # Python 依賴
└── README.md                       # 本文件
```

## 📚 架構設計

本專案採用 **Ports and Adapters**（六角架構）設計模式：

```
Client (應用程式入口)
   ↓
   ├─ Config (配置管理)
   └─ LoginPort (介面)
         ↓
      SinopacLoginAdapter (實作)
         ↓
      永豐 API / SDK
```

**使用流程：**
1. `Client` 讀取 `Config` 獲取登入憑證
2. `Client` 調用 `LoginAdapter` 執行登入
3. `LoginAdapter` 與永豐 API 通訊
4. 登入結果儲存在 `Client.sj` 屬性中

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

### Config 類別測試（7 個）
1. ✅ 檔案不存在時拋出例外
2. ✅ 成功讀取 YAML 檔案
3. ✅ 驗證 YAML 格式
4. ✅ 屬性正確儲存
5. ✅ 驗證失敗時拋出例外
6. ✅ 讀取失敗時拋出例外
7. ✅ 字串表示遮蔽敏感資訊

### SinopacLoginAdapter 測試（9 個）
1. ✅ 成功登入返回正確 DTO
2. ✅ 認證失敗拋出 AuthenticationError
3. ✅ 連線失敗拋出 ConnectionError
4. ✅ 資料格式錯誤拋出 DataFormatError
5. ✅ 參數錯誤拋出 ParameterError
6. ✅ HTTP 錯誤拋出 ServerError
7. ✅ 正確呼叫 HTTP 客戶端
8. ✅ 自訂參數初始化
9. ✅ 處理選擇性欄位

### Client 單元測試（14 個）
1. ✅ 使用 Config 物件初始化
2. ✅ 使用配置檔案路徑初始化
3. ✅ 無效配置類型拋出錯誤
4. ✅ 登入調用 Adapter
5. ✅ 登入失敗拋出例外
6. ✅ 連線錯誤拋出例外
7. ✅ 登入成功儲存結果到 sj
8. ✅ 未預期錯誤包裝處理
9. ✅ 登出清除 session
10. ✅ 登入前字串表示
11. ✅ 登入後字串表示
12. ✅ Context Manager 功能
13. ✅ 多次登入更新 sj
14. ✅ 預設 Adapter

### Client 整合測試（9 個）
1. ✅ 真實 Config 調用 Adapter
2. ✅ 認證失敗拋出例外
3. ✅ 連線錯誤拋出例外
4. ✅ 伺服器錯誤拋出例外
5. ✅ 成功登入儲存 sj
6. ✅ 使用 yaml_sample.yaml
7. ✅ Context Manager 整合
8. ✅ 多次登入整合
9. ✅ 登出整合測試

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

請參考 LICENSE 檔案。

## 👨‍💻 作者

Trading System Team

---

**版本：** 1.0.0  
**最後更新：** 2025-10-06