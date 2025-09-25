# BrokerageAuth - 永豐金證券登入認證模組

## 概述

`BrokerageAuth` 是一個專為永豐金證券 API 設計的登入認證模組，實作了完整的認證流程、Token 管理和 Session 快取功能。

### 特色

- ✅ **最小可用設計**: 遵循 KISS 原則，提供核心必要功能
- ✅ **完整錯誤處理**: 針對不同錯誤類型提供專門的例外類別
- ✅ **安全性**: 不將敏感資訊寫入日誌
- ✅ **自動化管理**: 自動處理 Token 刷新和 Session 維護
- ✅ **完整文檔**: 每個方法都有詳細的文檔和使用範例

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
export BROKER_API_KEY="your_api_key"
export BROKER_CERT_PATH="/path/to/your/certificate.pem"
```

### 3. 基本使用

```python
from brokerage_auth import BrokerageAuth

# 初始化認證物件
auth = BrokerageAuth()

# 自動登入或取得現有 Session
session = auth.getSession()

print(f"登入成功，使用者: {session.user_id}")
```

## API 文檔

### BrokerageAuth 類別

主要的認證管理類別，負責處理登入、Token 刷新、Session 管理等功能。

#### 初始化

```python
auth = BrokerageAuth()
```

**說明**: 從環境變數讀取配置並驗證憑證檔案

**環境變數**:
- `BROKER_API_KEY`: API 金鑰
- `BROKER_CERT_PATH`: 憑證檔案路徑

**異常**:
- `EnvironmentConfigError`: 環境變數缺失
- `CertificateError`: 憑證檔案不存在或無法讀取

#### login() 方法

```python
session = auth.login()
```

**說明**: 執行登入流程，建立並快取 Session 資料

**返回**: `SessionData` - 包含 Token、到期時間等資訊的 Session 資料結構

**異常**:
- `CertificateError`: 憑證檔案相關錯誤
- `AuthenticationError`: 認證失敗
- `NetworkError`: 網路連線錯誤

#### refresh() 方法

```python
refreshed_session = auth.refresh()
```

**說明**: 使用 refresh_token 來更新過期的 Token

**返回**: `SessionData` - 更新後的 Session 資料

**異常**:
- `TokenRefreshError`: Token 刷新失敗
- `AuthenticationError`: 認證相關錯誤
- `NetworkError`: 網路連線錯誤

#### getSession() 方法

```python
session = auth.getSession()
```

**說明**: 取得目前有效的 Session，自動處理登入和刷新

**返回**: `SessionData` - 有效的 Session 資料

**異常**:
- `AuthenticationError`: 登入失敗
- `NetworkError`: 網路連線錯誤
- `CertificateError`: 憑證相關錯誤

#### is_authenticated() 方法

```python
is_valid = auth.is_authenticated()
```

**說明**: 檢查是否已認證且 Session 有效

**返回**: `bool` - True 表示已認證，False 表示未認證

#### logout() 方法

```python
auth.logout()
```

**說明**: 登出並清除 Session 資料

### SessionData 資料結構

```python
@dataclass
class SessionData:
    token: str              # 認證 Token
    refresh_token: str      # 刷新 Token
    expires_at: datetime    # Token 到期時間
    user_id: str           # 使用者 ID
    extra_data: Dict[str, Any]  # 額外的 Session 資料
```

### 例外類別

| 例外類別 | 說明 | 使用情境 |
|---------|------|----------|
| `BrokerageAuthError` | 基礎例外類別 | 所有模組相關錯誤的父類別 |
| `EnvironmentConfigError` | 環境變數配置錯誤 | 缺少必要環境變數 |
| `CertificateError` | 憑證相關錯誤 | 憑證檔案不存在或無法讀取 |
| `AuthenticationError` | 認證失敗錯誤 | API Key 無效、權限不足 |
| `TokenRefreshError` | Token 刷新錯誤 | Refresh Token 無效或過期 |
| `NetworkError` | 網路連線錯誤 | HTTP 錯誤、連線逾時 |

## 使用範例

### 完整使用流程

```python
from brokerage_auth import (
    BrokerageAuth, 
    EnvironmentConfigError, 
    AuthenticationError, 
    NetworkError
)

try:
    # 初始化認證物件
    auth = BrokerageAuth()
    
    # 方式 1: 手動登入
    session = auth.login()
    print(f"登入成功，Token 到期時間: {session.expires_at}")
    
    # 方式 2: 自動管理（推薦）
    session = auth.getSession()  # 自動登入或返回現有 Session
    
    # 檢查認證狀態
    if auth.is_authenticated():
        print("目前已認證，可以進行 API 呼叫")
    
    # 手動刷新 Token（通常不需要）
    auth.refresh()
    
    # 登出
    auth.logout()
    
except EnvironmentConfigError as e:
    print(f"環境配置錯誤: {e}")
except AuthenticationError as e:
    print(f"認證失敗: {e}")
except NetworkError as e:
    print(f"網路錯誤: {e}")
```

### 在應用程式中整合

```python
class TradingService:
    def __init__(self):
        self.auth = BrokerageAuth()
    
    def make_authenticated_request(self, endpoint, data):
        # 自動取得有效 Session
        session = self.auth.getSession()
        
        headers = {
            'Authorization': f'Bearer {session.token}',
            'Content-Type': 'application/json'
        }
        
        # 進行 API 呼叫
        response = requests.post(
            f"https://api.sinotrade.com.tw{endpoint}",
            json=data,
            headers=headers
        )
        
        return response.json()
```

## 驗收準則

以下是所有驗收準則的實作狀態：

- ✅ `login()` 缺環境變數時精準報錯
- ✅ 憑證路徑不存在時回傳明確錯誤
- ✅ 成功登入可取得並快取 Session
- ✅ `refresh()` 可正常刷新 Token
- ✅ `getSession()` 自動處理登入和刷新
- ✅ 針對不同錯誤類型提供專門的例外處理
- ✅ 不將敏感資訊寫入日誌
- ✅ 提供完整的方法和類別文檔

## 執行示範程式

```bash
python demo.py
```

示範程式會執行以下測試：
1. 環境變數驗證
2. 憑證檔案檢查
3. 認證流程測試
4. 錯誤處理驗證

## 安全注意事項

1. **環境變數**: 請確保 `BROKER_API_KEY` 和憑證檔案的安全性
2. **日誌安全**: 模組不會將 API Key 或憑證內容寫入日誌
3. **檔案權限**: 確保憑證檔案有適當的讀取權限
4. **Token 管理**: Token 會自動刷新，無需手動處理

## 故障排除

### 常見錯誤

1. **EnvironmentConfigError**: 檢查環境變數是否正確設定
2. **CertificateError**: 檢查憑證檔案路徑和權限
3. **AuthenticationError**: 檢查 API Key 是否有效
4. **NetworkError**: 檢查網路連線和 API 伺服器狀態

### 除錯模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

auth = BrokerageAuth()
```

## 技術規格

- **Python 版本**: 3.6+
- **依賴套件**: requests, dataclasses (Python < 3.7)
- **API 端點**: https://api.sinotrade.com.tw
- **Token 有效期**: 預設 1 小時（可配置）
- **自動刷新**: Token 到期前 5 分鐘自動刷新

## 授權

此模組遵循最小可用原則實作，專為永豐金證券 API 設計。