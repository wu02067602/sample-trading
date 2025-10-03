# 開發文檔

## 專案架構

```
sample-trading/
├── src/                    # 原始碼目錄
│   ├── __init__.py        # 套件初始化
│   ├── config.py          # Config 類別實作
│   ├── login.py           # Login 類別實作
│   └── controller.py      # Controller 類別實作 ✨
├── tests/                  # 測試目錄
│   ├── __init__.py        
│   ├── test_config.py     # Config 單元測試（13個測試案例）
│   ├── test_login.py      # Login 單元測試（17個測試案例）
│   └── test_controller.py # Controller 整合測試（23個測試案例）✨
├── config.yaml.example     # 配置檔案範本
├── example.py             # 使用範例
├── example_login.py       # Login 使用範例
├── requirements.txt       # 專案依賴
├── README.md             # 專案說明
├── DEVELOPMENT.md        # 開發文檔
├── PROJECT_SUMMARY.md    # 專案總結
├── .gitignore            # Git 忽略檔案
└── LICENSE               # 授權條款
```

## Config 類別設計

### 類別圖

```
┌─────────────────────────────────────────┐
│            Config                       │
├─────────────────────────────────────────┤
│ 類別屬性：                               │
│ + REQUIRED_FIELDS: list                 │
│ + OPTIONAL_FIELDS: dict                 │
├─────────────────────────────────────────┤
│ 實例屬性：                               │
│ + api_key: str                          │
│ + secret_key: str                       │
│ + person_id: str                        │
│ + ca_path: Optional[str]                │
│ + ca_passwd: Optional[str]              │
│ + simulation: bool                      │
│ + contracts_timeout: int                │
│ + config_path: Path                     │
│ - _config_data: dict                    │
├─────────────────────────────────────────┤
│ 方法：                                   │
│ + __init__(config_path)                 │
│ + to_dict() -> dict                     │
│ + __repr__() -> str                     │
│ - _load_config() -> None                │
│ - _validate_config() -> None            │
│ - _set_attributes() -> None             │
└─────────────────────────────────────────┘
```

### 設計原則

1. **簡潔優於複雜**：直接使用 PyYAML，不引入過度依賴
2. **明確的職責分離**：
   - `_load_config()`: 負責檔案讀取
   - `_validate_config()`: 負責資料驗證
   - `_set_attributes()`: 負責屬性設定
3. **完整的錯誤處理**：所有錯誤都拋出 `ConfigError` 並提供清楚的訊息
4. **類型提示**：使用 Python type hints 提升程式碼可讀性

### 方法說明

#### `__init__(config_path: Union[str, Path])`
初始化配置物件，自動執行載入、驗證和屬性設定流程。

**參數：**
- `config_path`: 配置檔案路徑，可以是字串或 Path 物件

**異常：**
- `ConfigError`: 檔案不存在、格式錯誤或驗證失敗

#### `_load_config() -> None`
從 YAML 檔案讀取配置資料。

**異常：**
- `ConfigError`: 檔案不存在或 YAML 格式錯誤

#### `_validate_config() -> None`
驗證必填欄位是否存在且不為空。

**驗證規則：**
- 檢查所有 `REQUIRED_FIELDS` 是否存在
- 檢查必填欄位是否為空字串或只有空白字元

**異常：**
- `ConfigError`: 缺少必填欄位或必填欄位為空

#### `_set_attributes() -> None`
將配置資料設定為物件屬性。

**行為：**
- 設定所有必填欄位
- 設定所有選填欄位（使用預設值）

#### `to_dict() -> dict`
將配置轉換為字典格式。

**回傳：**
- 包含所有配置參數的字典

#### `__repr__() -> str`
返回配置物件的字串表示。

**回傳：**
- 包含關鍵資訊的字串（API key 會被截斷保護隱私）

## Login 類別設計

### 類別圖

```
┌─────────────────────────────────────────┐
│            Login                        │
├─────────────────────────────────────────┤
│ 實例屬性：                               │
│ + config: Config                        │
│ + api: Optional[Shioaji]                │
│ + is_logged_in: bool                    │
├─────────────────────────────────────────┤
│ 方法：                                   │
│ + __init__(config: Config)              │
│ + login() -> bool                       │
│ + logout() -> bool                      │
│ + __repr__() -> str                     │
│ + __enter__()                           │
│ + __exit__(...)                         │
└─────────────────────────────────────────┘
          │
          │ 依賴
          ▼
┌─────────────────────────────────────────┐
│            Config                       │
└─────────────────────────────────────────┘
```

### 設計原則

1. **依賴注入**：接收 Config 物件而非直接讀取配置
2. **狀態管理**：清楚追蹤登入狀態，避免重複登入
3. **延遲導入**：動態導入 shioaji 模組，支援測試環境
4. **錯誤分類**：將不同類型的錯誤轉換為有意義的訊息
5. **Context Manager**：支援 with 語句自動管理登入/登出

### 方法說明

#### `__init__(config: Config)`
初始化登入物件。

**參數：**
- `config`: Config 配置物件

**異常：**
- `TypeError`: 當 config 不是 Config 類型時

#### `login() -> bool`
執行登入操作，連線到永豐 Shioaji API。

**回傳：**
- `bool`: 登入成功返回 True

**異常：**
- `LoginError`: 已經登入時重複呼叫
- `LoginError`: shioaji 套件未安裝
- `LoginError`: 連線失敗
- `LoginError`: 認證失敗（API 金鑰錯誤）
- `LoginError`: 憑證錯誤
- `LoginError`: 連線逾時
- `LoginError`: 其他登入錯誤

#### `logout() -> bool`
執行登出操作。

**回傳：**
- `bool`: 登出成功返回 True

**異常：**
- `LoginError`: 尚未登入時呼叫
- `LoginError`: 登出失敗

#### `__enter__()` 和 `__exit__(...)`
支援 context manager 模式，自動管理登入和登出。

**範例：**
```python
with Login(config) as login:
    # 自動登入
    print("已登入")
# 自動登出
```

## Controller 類別設計

### 類別圖

```
┌─────────────────────────────────────────┐
│          Controller                     │
├─────────────────────────────────────────┤
│ 實例屬性：                               │
│ + config: Config                        │
│ + login: Login                          │
│ + sj: Optional[Shioaji]                 │
├─────────────────────────────────────────┤
│ 方法：                                   │
│ + __init__(config)                      │
│ + connect() -> bool                     │
│ + disconnect() -> bool                  │
│ + is_connected() -> bool                │
│ + get_status() -> dict                  │
│ + __repr__() -> str                     │
│ + __enter__()                           │
│ + __exit__(...)                         │
└─────────────────────────────────────────┘
```

### 設計原則

1. **整合介面**：整合 Config 和 Login，提供高層次 API
2. **簡化使用**：使用者只需要與 Controller 互動
3. **狀態管理**：清楚管理連線狀態和 Shioaji 實例
4. **彈性初始化**：支援多種初始化方式（路徑或 Config 物件）
5. **Context Manager**：支援自動資源管理

### 方法說明

#### `__init__(config: Union[str, Path, Config])`
初始化控制器，支援多種輸入類型。

**參數：**
- `config`: 配置檔案路徑或 Config 物件

**異常：**
- `TypeError`: 當 config 類型不正確時
- `ConfigError`: 當配置載入失敗時

#### `connect() -> bool`
連線到永豐 API，執行登入並儲存 Shioaji 實例到 `self.sj`。

**回傳：**
- `bool`: 連線成功返回 True

**異常：**
- `ControllerError`: 已經連線時重複呼叫
- `LoginError`: 登入失敗

#### `disconnect() -> bool`
中斷連線，執行登出並清除 Shioaji 實例。

**回傳：**
- `bool`: 中斷連線成功返回 True

**異常：**
- `ControllerError`: 尚未連線時呼叫
- `LoginError`: 登出失敗

#### `is_connected() -> bool`
檢查是否已連線。

**回傳：**
- `bool`: 已連線返回 True

#### `get_status() -> dict`
取得控制器狀態資訊。

**回傳：**
- `dict`: 包含 connected, person_id, simulation, has_certificate

## 類別關係圖

```
┌─────────────┐
│   Config    │  配置管理
└─────────────┘
       │
       │ 包含
       │
       ▼
┌─────────────┐
│ Controller  │  高層次控制介面 ✨
└─────────────┘
       │
       │ 包含
       │
       ▼
┌─────────────┐
│    Login    │  登入管理
└─────────────┘
       │
       │ 使用
       │
       ▼
┌─────────────┐
│  Shioaji    │  永豐 API
└─────────────┘
```

## 配置 Schema

### 必填欄位（REQUIRED_FIELDS）

| 欄位 | 類型 | 說明 | 驗證規則 |
|------|------|------|----------|
| `api_key` | str | API 金鑰 | 不可為空 |
| `secret_key` | str | API 密鑰 | 不可為空 |
| `person_id` | str | 身分證字號 | 不可為空 |

### 選填欄位（OPTIONAL_FIELDS）

| 欄位 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `ca_path` | str | None | 憑證檔案路徑 |
| `ca_passwd` | str | None | 憑證密碼 |
| `simulation` | bool | False | 是否為模擬環境 |
| `contracts_timeout` | int | 0 | 合約下載逾時時間（秒） |

## 測試覆蓋

### Config 類別測試（13 個測試案例）

✅ **正常情境測試（3 個）**
1. `test_load_valid_config` - 載入有效配置
2. `test_load_full_config` - 載入完整配置（含選填欄位）
3. `test_default_values` - 驗證預設值

✅ **錯誤處理測試（6 個）**
4. `test_missing_required_field` - 缺少必填欄位
5. `test_empty_required_field` - 必填欄位為空字串
6. `test_whitespace_required_field` - 必填欄位只有空白
7. `test_file_not_exists` - 檔案不存在
8. `test_invalid_yaml_format` - YAML 格式錯誤
9. `test_empty_yaml_file` - 空的 YAML 檔案

✅ **功能測試（4 個）**
10. `test_to_dict` - to_dict() 方法
11. `test_repr` - __repr__() 方法
12. `test_config_with_path_object` - 使用 Path 物件
13. `test_config_with_string_path` - 使用字串路徑

### Login 類別測試（17 個測試案例）

✅ **初始化測試（2 個）**
1. `test_init_with_valid_config` - 使用有效 Config 初始化
2. `test_init_with_invalid_config` - 使用無效 Config 初始化

✅ **登入成功測試（3 個）**
3. `test_login_success` - 登入成功
4. `test_login_with_certificate` - 使用憑證登入
5. `test_login_already_logged_in` - 重複登入（應失敗）

✅ **登入錯誤測試（5 個）**
6. `test_login_shioaji_not_installed` - shioaji 未安裝
7. `test_login_connection_error` - 連線失敗
8. `test_login_authentication_error` - 認證失敗
9. `test_login_certificate_error` - 憑證錯誤
10. `test_login_timeout_error` - 連線逾時
11. `test_login_generic_error` - 一般錯誤

✅ **登出測試（3 個）**
12. `test_logout_success` - 登出成功
13. `test_logout_not_logged_in` - 未登入時登出
14. `test_logout_error` - 登出失敗

✅ **功能測試（4 個）**
15. `test_repr` - __repr__() 方法
16. `test_context_manager` - Context manager 正常流程
17. `test_context_manager_with_exception` - Context manager 異常處理

### Controller 類別測試（23 個測試案例）

✅ **初始化測試（5 個）**
1. `test_init_with_config_object` - 使用 Config 物件初始化
2. `test_init_with_config_path_string` - 使用字串路徑初始化
3. `test_init_with_config_path_object` - 使用 Path 物件初始化
4. `test_init_with_invalid_type` - 使用無效類型初始化
5. `test_init_with_invalid_config_file` - 使用不存在的配置檔案

✅ **連線測試（3 個）**
6. `test_connect_success` - 連線成功
7. `test_connect_already_connected` - 重複連線（應失敗）
8. `test_connect_login_failure` - 連線失敗

✅ **中斷連線測試（3 個）**
9. `test_disconnect_success` - 中斷連線成功
10. `test_disconnect_not_connected` - 未連線時中斷連線
11. `test_disconnect_logout_failure` - 登出失敗

✅ **連線狀態測試（3 個）**
12. `test_is_connected_before_connect` - 連線前的狀態
13. `test_is_connected_after_connect` - 連線後的狀態
14. `test_is_connected_after_disconnect` - 中斷連線後的狀態

✅ **狀態資訊測試（3 個）**
15. `test_get_status_not_connected` - 取得未連線狀態
16. `test_get_status_connected` - 取得已連線狀態
17. `test_get_status_with_certificate` - 有憑證的狀態

✅ **功能測試（4 個）**
18. `test_repr_not_connected` - 未連線的字串表示
19. `test_repr_connected` - 已連線的字串表示
20. `test_context_manager` - Context manager 正常流程
21. `test_context_manager_with_exception` - Context manager 異常處理

✅ **整合測試（2 個）**
22. `test_full_lifecycle` - 完整的生命週期測試
23. `test_integration_with_real_config_file` - 與真實配置檔案的整合

### 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_config.py -v      # Config 類別測試（13 個）
pytest tests/test_login.py -v       # Login 類別測試（17 個）
pytest tests/test_controller.py -v  # Controller 類別測試（23 個）✨

# 執行測試並查看覆蓋率
pytest tests/ --cov=src --cov-report=term-missing

# 執行測試並生成 HTML 報告
pytest tests/ --cov=src --cov-report=html
```

### 測試統計

- **總測試案例數**：53 個 ✅
- **測試通過率**：100% ✅
- **測試覆蓋率**：完整覆蓋所有核心功能 ✅

## API 參數來源

根據[永豐 Shioaji 官方文件](https://sinotrade.github.io/zh/tutor/login/)，登入 API 所需的參數包括：

**必填參數：**
- `api_key`: 從永豐證券申請的 API 金鑰
- `secret_key`: 對應的 API 密鑰
- `person_id`: 身分證字號

**選填參數：**
- `ca_path`: 憑證檔案路徑（使用憑證登入時需要）
- `ca_passwd`: 憑證密碼
- `simulation`: 是否使用模擬環境（測試用）
- `contracts_timeout`: 下載合約資料的逾時時間

## 依賴套件

### 核心依賴
- **PyYAML** (>=6.0.1): YAML 檔案解析

### 開發依賴
- **pytest** (>=7.4.0): 單元測試框架
- **pytest-cov** (>=4.1.0): 測試覆蓋率報告

### 可選依賴
- **shioaji** (>=1.1.0): 永豐交易 API（實際使用時需要）

## 開發指南

### 程式碼風格

- 遵循 PEP 8 規範
- 使用 type hints 標註類型
- 撰寫完整的 docstrings
- 簡潔且直觀的命名

### 添加新功能

1. 在 `src/config.py` 中實作功能
2. 在 `tests/test_config.py` 中添加測試
3. 執行測試確保通過
4. 更新相關文檔

### 提交前檢查

```bash
# 1. 執行所有測試
pytest tests/

# 2. 檢查程式碼格式（可選）
# black src/ tests/
# flake8 src/ tests/

# 3. 驗證範例程式
python example.py
```

## 安全性考量

⚠️ **重要安全提醒：**

1. **永不提交敏感資訊**
   - `config.yaml` 包含真實憑證，已加入 `.gitignore`
   - 憑證檔案（`.pfx`, `.p12`）已加入 `.gitignore`

2. **保護 API 金鑰**
   - 使用環境變數或安全的密鑰管理系統
   - 定期輪換 API 金鑰

3. **檔案權限**
   ```bash
   chmod 600 config.yaml  # 僅所有者可讀寫
   chmod 600 *.pfx        # 保護憑證檔案
   ```

## 未來改進方向

- [ ] 支援環境變數覆蓋配置
- [ ] 支援加密的配置檔案
- [ ] 添加配置檔案遷移工具
- [ ] 支援多環境配置（開發、測試、生產）
- [ ] 添加配置驗證 CLI 工具

## 聯絡方式

如有問題或建議，請開啟 Issue 討論。

---

**文件更新日期：** 2025-10-03
