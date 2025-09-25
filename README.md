# BrokerageAuth - 永豐金證券 API 認證模組

## 概述

`BrokerageAuth` 是一個專為永豐金證券 API (Shioaji) 設計的認證管理模組，提供完整的登入、Token 刷新和 Session 管理功能。此模組遵循最小可用結構原則，專注於核心認證功能，並提供精確的錯誤處理機制。

## 功能特色

- ✅ **自動登入管理**：支援自動登入和 Session 快取
- ✅ **Token 自動刷新**：在 Token 過期前自動刷新，確保連線穩定
- ✅ **精確錯誤處理**：針對不同錯誤類型提供具體錯誤訊息
- ✅ **安全性保護**：不記錄敏感資訊，保護 API Key 和憑證安全
- ✅ **狀態監控**：提供詳細的認證狀態查詢功能
- ✅ **完整文件**：包含詳細的 API 文件和使用範例

## 安裝需求

### 系統需求
- Python 3.7+
- 永豐金證券 API 帳戶
- 有效的 API Key 和憑證檔案

### 依賴套件安裝
```bash
pip install -r requirements.txt
```

### 主要依賴
- `shioaji>=1.1.0` - 永豐金證券官方 Python SDK
- `requests>=2.25.0` - HTTP 請求處理
- `typing>=3.7.0` - 型別提示支援（Python < 3.9）

## 環境設定

使用前請設定以下環境變數：

```bash
# 永豐金證券 API Key
export BROKER_API_KEY="your_api_key_here"

# 憑證檔案路徑
export BROKER_CERT_PATH="/path/to/your/certificate.pem"
```

### 環境變數說明

| 變數名稱 | 必要性 | 說明 |
|---------|--------|------|
| `BROKER_API_KEY` | 必要 | 永豐金證券提供的 API Key |
| `BROKER_CERT_PATH` | 必要 | 憑證檔案的完整路徑 |

## 快速開始

### 基本使用範例

```python
from brokerage_auth import BrokerageAuth

# 初始化認證物件
auth = BrokerageAuth()

# 方法一：直接登入
login_result = auth.login()
print(f"登入狀態: {login_result['status']}")

# 方法二：自動管理 Session（推薦）
session = auth.get_session()  # 自動處理登入和刷新
contracts = session.Contracts.Stocks  # 使用 Session 進行 API 調用
```

### 完整使用範例

```python
import logging
from brokerage_auth import (
    BrokerageAuth, 
    AuthenticationError, 
    EnvironmentError,
    CertificateError
)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # 初始化認證管理器
        auth = BrokerageAuth()
        logger.info("認證管理器初始化成功")
        
        # 檢查初始狀態
        status = auth.get_status()
        logger.info(f"初始狀態: {status}")
        
        # 獲取 Session（自動登入）
        session = auth.get_session()
        logger.info("成功獲取 Session")
        
        # 使用 Session 進行 API 操作
        # 例如：獲取股票合約
        stocks = session.Contracts.Stocks
        logger.info(f"成功獲取股票合約，數量: {len(stocks)}")
        
        # 檢查登入狀態
        if auth.is_logged_in():
            logger.info("確認處於登入狀態")
        
        # 手動刷新 Token（通常不需要，get_session 會自動處理）
        refresh_result = auth.refresh()
        logger.info(f"Token 刷新成功: {refresh_result['status']}")
        
        # 獲取最新狀態
        final_status = auth.get_status()
        logger.info(f"最終狀態: {final_status}")
        
    except EnvironmentError as e:
        logger.error(f"環境配置錯誤: {e}")
    except CertificateError as e:
        logger.error(f"憑證錯誤: {e}")
    except AuthenticationError as e:
        logger.error(f"認證錯誤: {e}")
    except Exception as e:
        logger.error(f"未預期錯誤: {e}")
    finally:
        # 清理資源
        if 'auth' in locals():
            logout_result = auth.logout()
            logger.info(f"登出結果: {logout_result['message']}")

if __name__ == "__main__":
    main()
```

## API 文件

### 類別：BrokerageAuth

永豐金證券 API 認證管理類別，負責處理登入、Token 刷新和 Session 管理。

#### 建構函式

```python
def __init__(self, token_lifetime_hours: int = 23) -> None
```

**參數：**
- `token_lifetime_hours` (int, 可選): Token 有效期限（小時），預設 23 小時

**引發：**
- `EnvironmentError`: 當環境變數缺失時
- `CertificateError`: 當憑證檔案不存在或無法讀取時

#### 方法：login()

```python
def login(self) -> Dict[str, Any]
```

執行登入操作，獲取並快取 Session。

**返回：**
```python
{
    'status': 'success',
    'login_time': '2025-09-25 10:30:00',
    'session_id': 'session_identifier',
    'message': '登入成功'
}
```

**引發：**
- `AuthenticationError`: 當登入失敗時

#### 方法：refresh()

```python
def refresh(self) -> Dict[str, Any]
```

在 Token 逾期前安全刷新 Session。

**返回：**
```python
{
    'status': 'success',
    'refresh_time': '2025-09-25 15:30:00',
    'previous_login_time': '2025-09-25 10:30:00',
    'new_session_id': 'new_session_identifier',
    'message': 'Token 刷新成功'
}
```

**引發：**
- `SessionError`: 當沒有有效 Session 可供刷新時
- `AuthenticationError`: 當刷新過程中發生認證錯誤時

#### 方法：get_session()

```python
def get_session(self) -> sj.Shioaji
```

取得目前有效的 Session，若無則自動執行登入或刷新。

**返回：**
- `sj.Shioaji`: 有效的 Shioaji API Session 實例

**引發：**
- `AuthenticationError`: 當無法獲取有效 Session 時

#### 方法：is_logged_in()

```python
def is_logged_in(self) -> bool
```

檢查是否已登入且 Session 有效。

**返回：**
- `bool`: True 如果已登入且 Session 有效，False 否則

#### 方法：logout()

```python
def logout(self) -> Dict[str, Any]
```

登出並清理 Session。

**返回：**
```python
{
    'status': 'success',
    'logout_time': '2025-09-25 18:00:00',
    'message': '登出成功'
}
```

#### 方法：get_status()

```python
def get_status(self) -> Dict[str, Any]
```

獲取當前認證狀態的詳細資訊。

**返回：**
```python
{
    'logged_in': True,
    'session_exists': True,
    'login_time': '2025-09-25 10:30:00',
    'token_expired': False,
    'next_refresh_time': '2025-09-26 08:30:00'
}
```

## 錯誤處理

### 錯誤類型階層

```
BrokerageAuthError (基類)
├── EnvironmentError (環境變數相關)
├── CertificateError (憑證相關)
├── AuthenticationError (認證相關)
└── SessionError (Session 相關)
```

### 錯誤處理範例

```python
from brokerage_auth import (
    BrokerageAuth,
    EnvironmentError,
    CertificateError,
    AuthenticationError,
    SessionError
)

try:
    auth = BrokerageAuth()
    session = auth.get_session()
except EnvironmentError as e:
    print(f"環境設定錯誤: {e}")
    # 檢查 BROKER_API_KEY 和 BROKER_CERT_PATH
except CertificateError as e:
    print(f"憑證問題: {e}")
    # 檢查憑證檔案路徑和權限
except AuthenticationError as e:
    print(f"認證失敗: {e}")
    # 檢查 API Key 是否正確或網路連線
except SessionError as e:
    print(f"Session 錯誤: {e}")
    # 重新登入或聯繫技術支援
```

## 測試與驗證

### 執行示範程式

```bash
# 設定環境變數後執行示範程式
python demo.py
```

示範程式包含：
- 環境變數驗證測試
- 基本認證功能測試
- Session 管理測試
- 錯誤情境測試
- 互動式示範

### 驗收準則檢查

執行示範程式將自動驗證以下準則：

1. ✅ `login()` 缺環境變數應精準報錯
2. ✅ 憑證路徑不存在時回傳明確錯誤
3. ✅ 成功登入可取得並快取 Session
4. ✅ `refresh()` 可正常刷新 Token
5. ✅ `get_session()` 在無有效 Session 時自動登入

## 最佳實踐

### 1. 使用 get_session() 方法（推薦）

```python
# 推薦：讓 BrokerageAuth 自動管理登入和刷新
auth = BrokerageAuth()
session = auth.get_session()  # 自動處理一切
```

### 2. 適當的錯誤處理

```python
try:
    auth = BrokerageAuth()
    session = auth.get_session()
    # 使用 session 進行 API 操作
except BrokerageAuthError as e:
    logger.error(f"認證相關錯誤: {e}")
    # 根據具體錯誤類型進行處理
```

### 3. 狀態監控

```python
# 定期檢查認證狀態
status = auth.get_status()
if not status['logged_in']:
    logger.warning("認證狀態異常，需要重新登入")
```

### 4. 資源清理

```python
try:
    # 執行交易邏輯
    pass
finally:
    # 程式結束前清理資源
    auth.logout()
```

## 安全注意事項

1. **環境變數保護**：永遠不要將 API Key 硬編碼在程式中
2. **憑證檔案權限**：確保憑證檔案只有必要的使用者可以讀取
3. **日誌安全**：模組不會記錄任何敏感資訊（API Key、憑證內容）
4. **網路安全**：建議在安全的網路環境中使用

## 故障排除

### 常見問題

**Q: 初始化時出現 EnvironmentError**
```
A: 檢查環境變數是否正確設定：
   echo $BROKER_API_KEY
   echo $BROKER_CERT_PATH
```

**Q: 出現 CertificateError**
```
A: 檢查憑證檔案：
   ls -la $BROKER_CERT_PATH
   # 確保檔案存在且有讀取權限
```

**Q: 登入時出現 AuthenticationError**
```
A: 可能的原因：
   1. API Key 錯誤或過期
   2. 憑證檔案損壞
   3. 網路連線問題
   4. 永豐金 API 服務異常
```

**Q: Token 自動刷新失敗**
```
A: 檢查：
   1. 網路連線穩定性
   2. API Key 是否仍然有效
   3. 查看詳細錯誤日誌
```

## 技術支援

如有技術問題，請：
1. 檢查日誌檔案 (`demo.log`)
2. 確認環境變數和憑證設定
3. 執行示範程式進行診斷
4. 參考永豐金證券 API 官方文件

## 授權

此模組遵循專案授權條款。使用前請確保遵守永豐金證券 API 的使用條款和條件。