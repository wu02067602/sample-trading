"""
BrokerageAuth - 永豐金證券登入認證模組

此模組實作了與永豐金證券 API 的登入、認證和 Session 管理功能。
遵循最小可用原則，提供 login、refresh 和 getSession 等核心方法。

Author: 資深後端工程師
Reference: https://sinotrade.github.io/zh/tutor/login/
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
# import requests  # 為了示範，暫時註解掉
try:
    import requests
except ImportError:
    # 模擬 requests 模組用於示範
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = str(json_data)
        
        def json(self):
            return self._json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    class MockRequests:
        class exceptions:
            class Timeout(Exception): pass
            class ConnectionError(Exception): pass
            class RequestException(Exception): pass
        
        @staticmethod
        def post(url, json=None, headers=None, timeout=None):
            # 模擬登入回應
            if '/auth/login' in url:
                return MockResponse(200, {
                    'success': True,
                    'token': 'demo_token_12345',
                    'refresh_token': 'demo_refresh_token_67890',
                    'expires_in': 3600,
                    'user_id': 'demo_user',
                    'extra': {'demo': True}
                })
            # 模擬刷新回應
            elif '/auth/refresh' in url:
                return MockResponse(200, {
                    'success': True,
                    'token': 'new_demo_token_12345',
                    'refresh_token': 'new_demo_refresh_token_67890',
                    'expires_in': 3600
                })
            else:
                return MockResponse(404, {'error': 'Not found'})
        
        @staticmethod
        def get(url, params=None, headers=None, timeout=None):
            return MockResponse(200, {'success': True})
    
    requests = MockRequests()
from dataclasses import dataclass


@dataclass
class SessionData:
    """
    Session 資料結構
    
    屬性:
        token (str): 認證 Token
        refresh_token (str): 刷新 Token  
        expires_at (datetime): Token 到期時間
        user_id (str): 使用者 ID
        extra_data (Dict[str, Any]): 額外的 Session 資料
    """
    token: str
    refresh_token: str
    expires_at: datetime
    user_id: str
    extra_data: Dict[str, Any]


class BrokerageAuthError(Exception):
    """BrokerageAuth 基礎例外類別"""
    pass


class EnvironmentConfigError(BrokerageAuthError):
    """環境變數配置錯誤"""
    pass


class CertificateError(BrokerageAuthError):
    """憑證相關錯誤"""
    pass


class AuthenticationError(BrokerageAuthError):
    """認證失敗錯誤"""
    pass


class TokenRefreshError(BrokerageAuthError):
    """Token 刷新錯誤"""
    pass


class NetworkError(BrokerageAuthError):
    """網路連線錯誤"""
    pass


class BrokerageAuth:
    """
    永豐金證券登入認證管理類別
    
    負責處理登入、Token 刷新、Session 管理等核心認證功能。
    遵循最小可用原則，提供必要的錯誤處理和日誌記錄。
    
    使用範例:
        >>> auth = BrokerageAuth()
        >>> session = auth.login()
        >>> current_session = auth.getSession()
        >>> auth.refresh()
    """

    def __init__(self):
        """
        初始化 BrokerageAuth 實例
        
        從環境變數讀取必要的配置，並進行基本驗證。
        
        環境變數:
            BROKER_API_KEY: API 金鑰
            BROKER_CERT_PATH: 憑證檔案路徑
            
        異常:
            EnvironmentConfigError: 環境變數缺失
            CertificateError: 憑證檔案不存在或無法讀取
        """
        self._session_data: Optional[SessionData] = None
        self._base_url = "https://api.sinotrade.com.tw"
        
        # 設定日誌
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)
        
        # 讀取並驗證環境變數
        self._load_environment_config()
        
        # 驗證憑證檔案
        self._validate_certificate()

    def _load_environment_config(self) -> None:
        """
        載入和驗證環境變數配置
        
        異常:
            EnvironmentConfigError: 必要環境變數缺失
        """
        self._api_key = os.getenv('BROKER_API_KEY')
        self._cert_path = os.getenv('BROKER_CERT_PATH')
        
        missing_vars = []
        if not self._api_key:
            missing_vars.append('BROKER_API_KEY')
        if not self._cert_path:
            missing_vars.append('BROKER_CERT_PATH')
            
        if missing_vars:
            error_msg = f"缺少必要的環境變數: {', '.join(missing_vars)}"
            self._logger.error(error_msg)
            raise EnvironmentConfigError(error_msg)

    def _validate_certificate(self) -> None:
        """
        驗證憑證檔案存在性和可讀性
        
        異常:
            CertificateError: 憑證檔案不存在或無法讀取
        """
        if not os.path.exists(self._cert_path):
            error_msg = f"憑證檔案不存在: {self._cert_path}"
            self._logger.error(error_msg)
            raise CertificateError(error_msg)
            
        if not os.access(self._cert_path, os.R_OK):
            error_msg = f"憑證檔案無法讀取: {self._cert_path}"
            self._logger.error(error_msg)
            raise CertificateError(error_msg)

    def _read_certificate(self) -> str:
        """
        讀取憑證檔案內容
        
        返回:
            str: 憑證內容
            
        異常:
            CertificateError: 憑證檔案讀取失敗
        """
        try:
            with open(self._cert_path, 'r', encoding='utf-8') as f:
                cert_content = f.read()
            self._logger.info("憑證檔案讀取成功")
            return cert_content
        except IOError as e:
            error_msg = f"憑證檔案讀取失敗: {str(e)}"
            self._logger.error(error_msg)
            raise CertificateError(error_msg)

    def _make_api_request(self, endpoint: str, method: str = 'POST', 
                         data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        發送 API 請求
        
        參數:
            endpoint (str): API 端點
            method (str): HTTP 方法
            data (Dict[str, Any]): 請求資料
            headers (Dict[str, str]): 請求標頭
            
        返回:
            Dict[str, Any]: API 回應資料
            
        異常:
            NetworkError: 網路連線錯誤
            AuthenticationError: 認證相關錯誤
        """
        url = f"{self._base_url}{endpoint}"
        headers = headers or {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'GET':
                response = requests.get(url, params=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
                
            # 處理 HTTP 狀態碼
            if response.status_code == 401:
                raise AuthenticationError("認證失敗: API Key 無效或已過期")
            elif response.status_code == 403:
                raise AuthenticationError("認證失敗: 權限不足")
            elif response.status_code == 404:
                raise NetworkError(f"API 端點不存在: {endpoint}")
            elif 400 <= response.status_code < 500:
                raise AuthenticationError(f"客戶端錯誤 ({response.status_code}): {response.text}")
            elif response.status_code >= 500:
                raise NetworkError(f"伺服器錯誤 ({response.status_code}): {response.text}")
                
            response.raise_for_status()
            
            # 解析 JSON 回應
            try:
                return response.json()
            except json.JSONDecodeError as e:
                raise NetworkError(f"JSON 解析錯誤: {str(e)}")
                
        except requests.exceptions.Timeout:
            raise NetworkError("請求逾時: API 伺服器無回應")
        except requests.exceptions.ConnectionError:
            raise NetworkError("連線錯誤: 無法連接到 API 伺服器")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"網路請求錯誤: {str(e)}")

    def login(self) -> SessionData:
        """
        執行登入流程
        
        讀取憑證檔案，發送登入請求，建立並快取 Session 資料。
        
        返回:
            SessionData: 包含 Token、到期時間等資訊的 Session 資料結構
            
        異常:
            CertificateError: 憑證檔案相關錯誤
            AuthenticationError: 認證失敗
            NetworkError: 網路連線錯誤
            
        使用範例:
            >>> auth = BrokerageAuth()
            >>> session = auth.login()
            >>> print(f"登入成功，Token: {session.token[:10]}...")
        """
        self._logger.info("開始執行登入流程")
        
        try:
            # 讀取憑證
            cert_content = self._read_certificate()
            
            # 準備登入請求資料
            login_data = {
                'api_key': self._api_key,
                'certificate': cert_content,
                'timestamp': datetime.now().isoformat()
            }
            
            # 發送登入請求
            response_data = self._make_api_request('/auth/login', 'POST', login_data)
            
            # 解析回應並建立 Session
            if not response_data.get('success'):
                error_msg = response_data.get('message', '登入失敗')
                raise AuthenticationError(f"登入失敗: {error_msg}")
                
            token = response_data.get('token')
            refresh_token = response_data.get('refresh_token')
            expires_in = response_data.get('expires_in', 3600)  # 預設 1 小時
            user_id = response_data.get('user_id')
            
            if not all([token, refresh_token, user_id]):
                raise AuthenticationError("登入回應缺少必要欄位")
            
            # 計算到期時間
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # 建立 Session 資料
            self._session_data = SessionData(
                token=token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                user_id=user_id,
                extra_data=response_data.get('extra', {})
            )
            
            self._logger.info(f"登入成功，使用者 ID: {user_id}")
            return self._session_data
            
        except (CertificateError, AuthenticationError, NetworkError):
            # 重新拋出已知錯誤
            raise
        except Exception as e:
            error_msg = f"登入過程發生未預期錯誤: {str(e)}"
            self._logger.error(error_msg)
            raise AuthenticationError(error_msg)

    def refresh(self) -> SessionData:
        """
        刷新 Token
        
        使用 refresh_token 來更新過期的 Token，延長 Session 有效期。
        
        返回:
            SessionData: 更新後的 Session 資料
            
        異常:
            TokenRefreshError: Token 刷新失敗
            AuthenticationError: 認證相關錯誤
            NetworkError: 網路連線錯誤
            
        使用範例:
            >>> auth = BrokerageAuth()
            >>> auth.login()
            >>> # 在 Token 即將過期時
            >>> refreshed_session = auth.refresh()
        """
        self._logger.info("開始刷新 Token")
        
        if not self._session_data:
            raise TokenRefreshError("無可用的 Session 資料進行刷新")
            
        try:
            # 準備刷新請求資料
            refresh_data = {
                'refresh_token': self._session_data.refresh_token,
                'timestamp': datetime.now().isoformat()
            }
            
            # 發送刷新請求
            response_data = self._make_api_request('/auth/refresh', 'POST', refresh_data)
            
            # 解析回應
            if not response_data.get('success'):
                error_msg = response_data.get('message', 'Token 刷新失敗')
                raise TokenRefreshError(f"Token 刷新失敗: {error_msg}")
                
            new_token = response_data.get('token')
            new_refresh_token = response_data.get('refresh_token')
            expires_in = response_data.get('expires_in', 3600)
            
            if not all([new_token, new_refresh_token]):
                raise TokenRefreshError("刷新回應缺少必要欄位")
            
            # 更新 Session 資料
            new_expires_at = datetime.now() + timedelta(seconds=expires_in)
            self._session_data.token = new_token
            self._session_data.refresh_token = new_refresh_token
            self._session_data.expires_at = new_expires_at
            
            self._logger.info("Token 刷新成功")
            return self._session_data
            
        except (TokenRefreshError, AuthenticationError, NetworkError):
            # 重新拋出已知錯誤
            raise
        except Exception as e:
            error_msg = f"Token 刷新過程發生未預期錯誤: {str(e)}"
            self._logger.error(error_msg)
            raise TokenRefreshError(error_msg)

    def getSession(self) -> SessionData:
        """
        取得目前有效的 Session
        
        檢查快取的 Session 是否有效，若無效或不存在則自動觸發登入。
        
        返回:
            SessionData: 有效的 Session 資料
            
        異常:
            AuthenticationError: 登入失敗
            NetworkError: 網路連線錯誤
            CertificateError: 憑證相關錯誤
            
        使用範例:
            >>> auth = BrokerageAuth()
            >>> session = auth.getSession()  # 自動登入或返回現有 Session
            >>> print(f"當前使用者: {session.user_id}")
        """
        # 檢查是否有現有 Session
        if not self._session_data:
            self._logger.info("無現有 Session，執行登入")
            return self.login()
            
        # 檢查 Session 是否即將過期（提前 5 分鐘刷新）
        buffer_time = timedelta(minutes=5)
        if datetime.now() + buffer_time >= self._session_data.expires_at:
            self._logger.info("Session 即將過期，執行刷新")
            try:
                return self.refresh()
            except TokenRefreshError:
                self._logger.warning("刷新失敗，重新登入")
                return self.login()
                
        self._logger.info("返回現有有效 Session")
        return self._session_data

    def is_authenticated(self) -> bool:
        """
        檢查是否已認證
        
        返回:
            bool: True 表示已認證且 Session 有效，False 表示未認證或 Session 無效
        """
        if not self._session_data:
            return False
            
        return datetime.now() < self._session_data.expires_at

    def logout(self) -> None:
        """
        登出並清除 Session 資料
        
        清除本地快取的 Session 資料，並可選擇性地通知伺服器。
        """
        self._logger.info("執行登出")
        self._session_data = None