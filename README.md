# 永豐交易 API 專案

這是一個使用永豐證券 Shioaji API 進行程式交易的專案。本專案提供簡潔且直觀的配置管理系統，讓您能夠輕鬆地管理 API 登入憑證和設定。

## 功能特色

- ✅ 簡潔的 YAML 配置檔案管理
- ✅ 自動驗證必填欄位
- ✅ 永豐 API 登入管理
- ✅ 支援模擬環境和正式環境
- ✅ 完整的錯誤處理和提示
- ✅ 支援 Context Manager
- ✅ 100% 單元測試覆蓋（30 個測試案例）

## 安裝

### 1. Clone 專案

```bash
git clone <repository-url>
cd sample-trading
```

### 2. 建立虛擬環境（建議）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

## 快速開始

### 1. 建立配置檔案

複製範本檔案並填入您的帳號資訊：

```bash
cp config.yaml.example config.yaml
```

編輯 `config.yaml`，填入您的 API 金鑰和憑證：

```yaml
# 必填欄位
api_key: "YOUR_API_KEY"
secret_key: "YOUR_SECRET_KEY"
person_id: "YOUR_PERSON_ID"

# 選填欄位
simulation: false  # 設為 true 使用模擬環境
```

### 2. 使用配置與登入

#### 基本用法

```python
from src.config import Config
from src.login import Login

# 載入配置
config = Config("config.yaml")

# 建立登入物件
login = Login(config)

# 執行登入
try:
    login.login()
    print("✅ 登入成功！")
    
    # 這裡可以使用 login.api 進行交易操作
    # ...
    
    # 登出
    login.logout()
    print("✅ 已登出")
    
except Exception as e:
    print(f"❌ 錯誤: {e}")
```

#### 使用 Context Manager（推薦）

```python
from src.config import Config
from src.login import Login

# 使用 with 語句自動管理登入/登出
with Login(Config("config.yaml")) as login:
    print("✅ 自動登入成功")
    
    # 使用 login.api 進行交易
    # ...
    
# 離開 with 區塊時自動登出
print("✅ 自動登出完成")
```

## 配置說明

### 必填欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `api_key` | str | 永豐 API 金鑰 |
| `secret_key` | str | 永豐 API 密鑰 |
| `person_id` | str | 身分證字號 |

### 選填欄位

| 欄位 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `ca_path` | str | None | 憑證檔案路徑（.pfx 或 .p12） |
| `ca_passwd` | str | None | 憑證密碼 |
| `simulation` | bool | false | 是否使用模擬環境 |
| `contracts_timeout` | int | 0 | 合約下載逾時時間（秒），0 表示無限等待 |

## 取得 API 金鑰

請參考[永豐證券 Shioaji 官方文件](https://sinotrade.github.io/zh/tutor/login/)了解如何：

1. 開立證券帳戶
2. 申請 API 金鑰與憑證
3. 簽署 API 服務條款

## 開發

### 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_config.py -v  # Config 類別測試（13 個）
pytest tests/test_login.py -v   # Login 類別測試（17 個）

# 執行測試並顯示覆蓋率
pytest --cov=src tests/

# 執行測試並生成詳細報告
pytest -v --cov=src --cov-report=html tests/
```

### 專案結構

```
sample-trading/
├── src/
│   ├── __init__.py
│   ├── config.py          # Config 類別（配置管理）
│   └── login.py           # Login 類別（登入管理）
├── tests/
│   ├── __init__.py
│   ├── test_config.py     # Config 單元測試（13 個測試案例）
│   └── test_login.py      # Login 單元測試（17 個測試案例）
├── config.yaml.example    # 配置檔案範本
├── example.py             # 使用範例
├── requirements.txt       # 專案依賴
├── README.md             # 專案說明文件
├── DEVELOPMENT.md        # 開發文檔（含類別圖）
├── .gitignore            # Git 忽略檔案
└── LICENSE               # 授權條款
```

## 錯誤處理

### Config 錯誤

`Config` 類別會在以下情況拋出 `ConfigError` 異常：

- 配置檔案不存在
- YAML 格式錯誤
- 缺少必填欄位
- 必填欄位為空或只有空白字元

### Login 錯誤

`Login` 類別會在以下情況拋出 `LoginError` 異常：

- shioaji 套件未安裝
- 已經登入時重複登入
- 連線失敗
- 認證失敗（API 金鑰或密鑰錯誤）
- 憑證錯誤
- 連線逾時
- 尚未登入時呼叫登出

### 錯誤處理範例

```python
from src.config import Config, ConfigError
from src.login import Login, LoginError

try:
    # 載入配置
    config = Config("config.yaml")
    
    # 執行登入
    login = Login(config)
    login.login()
    
    # 進行交易...
    
except ConfigError as e:
    print(f"⚠️ 配置錯誤: {e}")
except LoginError as e:
    print(f"⚠️ 登入錯誤: {e}")
except Exception as e:
    print(f"❌ 未預期的錯誤: {e}")
```

## 安全性建議

⚠️ **重要：請勿將包含真實憑證的 `config.yaml` 提交到版本控制系統！**

建議在 `.gitignore` 中加入：

```
config.yaml
*.pfx
*.p12
```

## 授權

請參閱 [LICENSE](LICENSE) 檔案。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯絡資訊

如有問題或建議，請開啟 Issue 討論。

---

**注意：** 本專案僅供學習和研究使用。實際交易請謹慎評估風險。
