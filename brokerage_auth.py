"""
永豐金證券 API 認證模組

此模組提供 BrokerageAuth 類別，負責處理與永豐金證券 API 的認證流程，
包括登入、刷新 Token 以及管理 Session。

Author: Senior Backend Engineer
Date: 2025-09-25
"""

import os
import shioaji as sj
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from shioaji.error import ShioajiError


class BrokerageAuthError(Exception):
    """BrokerageAuth 相關錯誤的基類"""
    pass


class EnvironmentError(BrokerageAuthError):
    """環境變數相關錯誤"""
    pass


class CertificateError(BrokerageAuthError):
    """憑證相關錯誤"""
    pass


class AuthenticationError(BrokerageAuthError):
    """認證相關錯誤"""
    pass


class SessionError(BrokerageAuthError):
    """Session 相關錯誤"""
    pass


class BrokerageAuth:
    """
    永豐金證券 API 認證管理類別
    
    此類別負責處理與永豐金證券 API 的認證流程，包含登入、刷新 Token 
    以及管理 Session。支援自動登入和 Token 刷新機制。
    
    屬性：
        api (sj.Shioaji): Shioaji API 實例
        session (Optional[sj.Shioaji]): 已登入的 Session 實例
        login_time (Optional[datetime]): 登入時間
        token_lifetime (timedelta): Token 有效期限（預設 23 小時）
    """
    
    def __init__(self, token_lifetime_hours: int = 23):
        """
        初始化 BrokerageAuth 實例
        
        從環境變數讀取必要的認證資訊並進行驗證。
        
        參數：
            token_lifetime_hours (int): Token 有效期限（小時），預設 23 小時
            
        引發：
            EnvironmentError: 當環境變數缺失時
            CertificateError: 當憑證檔案不存在時
        """
        # 設定日誌（但不記錄敏感資訊）
        self.logger = logging.getLogger(__name__)
        
        # 初始化屬性
        self.api = sj.Shioaji()
        self.session: Optional[sj.Shioaji] = None
        self.login_time: Optional[datetime] = None
        self.token_lifetime = timedelta(hours=token_lifetime_hours)
        
        # 從環境變數讀取認證資訊
        self.api_key = os.getenv('BROKER_API_KEY')
        self.cert_path = os.getenv('BROKER_CERT_PATH')
        
        # 驗證環境變數
        self._validate_environment()
        
        self.logger.info("BrokerageAuth 初始化完成")
    
    def _validate_environment(self) -> None:
        """
        驗證環境變數和憑證檔案
        
        引發：
            EnvironmentError: 當環境變數缺失時
            CertificateError: 當憑證檔案不存在時
        """
        if not self.api_key:
            raise EnvironmentError("環境變數 'BROKER_API_KEY' 缺失")
        
        if not self.cert_path:
            raise EnvironmentError("環境變數 'BROKER_CERT_PATH' 缺失")
        
        if not os.path.exists(self.cert_path):
            raise CertificateError(f"憑證檔案不存在於路徑：{self.cert_path}")
        
        # 檢查憑證檔案權限
        if not os.access(self.cert_path, os.R_OK):
            raise CertificateError(f"憑證檔案無法讀取：{self.cert_path}")
    
    def _is_token_expired(self) -> bool:
        """
        檢查 Token 是否已過期
        
        返回：
            bool: True 如果 Token 已過期或接近過期，False 否則
        """
        if not self.login_time:
            return True
        
        # 提前 1 小時判斷過期，確保安全邊際
        expiry_time = self.login_time + self.token_lifetime - timedelta(hours=1)
        return datetime.now() >= expiry_time
    
    def login(self) -> Dict[str, Any]:
        """
        執行登入操作，獲取並快取 Session
        
        此方法會使用環境變數中的 API Key 和憑證檔案進行認證，
        成功後將 Session 快取於物件中供後續使用。
        
        返回：
            Dict[str, Any]: 包含登入狀態和基本資訊的字典
            {
                'status': 'success',
                'login_time': '2025-09-25 10:30:00',
                'session_id': 'session_identifier',
                'message': '登入成功'
            }
            
        引發：
            AuthenticationError: 當登入失敗時
            
        使用範例：
            auth = BrokerageAuth()
            result = auth.login()
            print(f"登入狀態: {result['status']}")
        """
        try:
            self.logger.info("開始執行登入流程")
            
            # 執行登入
            self.session = self.api.login(
                api_key=self.api_key,
                secret_key=self.api_key,  # 永豐 API 使用相同的 key
                ca_path=self.cert_path
            )
            
            # 記錄登入時間
            self.login_time = datetime.now()
            
            # 構建返回結果
            result = {
                'status': 'success',
                'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                'session_id': id(self.session),  # 使用物件 ID 作為識別
                'message': '登入成功'
            }
            
            self.logger.info("登入成功")
            return result
            
        except ShioajiError as e:
            error_msg = f"Shioaji API 登入錯誤: {str(e)}"
            self.logger.error(error_msg)
            raise AuthenticationError(error_msg)
        
        except Exception as e:
            error_msg = f"登入過程發生未預期錯誤: {str(e)}"
            self.logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def refresh(self) -> Dict[str, Any]:
        """
        在 Token 逾期前安全刷新 Session
        
        此方法會先登出當前 Session，然後重新登入以獲取新的 Token。
        如果當前沒有有效的 Session，會拋出錯誤。
        
        返回：
            Dict[str, Any]: 包含刷新狀態和新登入資訊的字典
            {
                'status': 'success',
                'refresh_time': '2025-09-25 15:30:00',
                'previous_login_time': '2025-09-25 10:30:00',
                'new_session_id': 'new_session_identifier',
                'message': 'Token 刷新成功'
            }
            
        引發：
            SessionError: 當沒有有效 Session 可供刷新時
            AuthenticationError: 當刷新過程中發生認證錯誤時
            
        使用範例：
            auth = BrokerageAuth()
            auth.login()
            # ... 一段時間後 ...
            result = auth.refresh()
            print(f"刷新狀態: {result['status']}")
        """
        if not self.session:
            raise SessionError("無法刷新 Token，因為目前沒有有效的 Session")
        
        try:
            self.logger.info("開始刷新 Token")
            
            # 記錄舊的登入時間
            previous_login_time = self.login_time
            
            # 先登出當前 Session
            try:
                self.session.logout()
                self.logger.info("已登出舊 Session")
            except Exception as e:
                self.logger.warning(f"登出舊 Session 時發生錯誤: {e}")
            
            # 清除舊 Session
            self.session = None
            self.login_time = None
            
            # 重新登入
            login_result = self.login()
            
            # 構建返回結果
            result = {
                'status': 'success',
                'refresh_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'previous_login_time': previous_login_time.strftime('%Y-%m-%d %H:%M:%S') if previous_login_time else None,
                'new_session_id': login_result['session_id'],
                'message': 'Token 刷新成功'
            }
            
            self.logger.info("Token 刷新成功")
            return result
            
        except AuthenticationError:
            # 重新拋出認證錯誤
            raise
        
        except Exception as e:
            error_msg = f"刷新 Token 過程發生未預期錯誤: {str(e)}"
            self.logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def get_session(self) -> sj.Shioaji:
        """
        取得目前有效的 Session
        
        此方法會檢查當前 Session 的有效性，如果沒有有效的 Session 
        或 Token 即將過期，會自動執行登入或刷新操作。
        
        返回：
            sj.Shioaji: 有效的 Shioaji API Session 實例
            
        引發：
            AuthenticationError: 當無法獲取有效 Session 時
            
        使用範例：
            auth = BrokerageAuth()
            session = auth.get_session()  # 自動處理登入
            contracts = session.Contracts.Stocks  # 使用 Session 進行 API 調用
        """
        try:
            # 如果沒有 Session，執行登入
            if not self.session:
                self.logger.info("沒有有效 Session，執行登入")
                self.login()
                return self.session
            
            # 如果 Token 即將過期，執行刷新
            if self._is_token_expired():
                self.logger.info("Token 即將過期，執行刷新")
                self.refresh()
                return self.session
            
            # 返回當前有效的 Session
            self.logger.debug("返回當前有效 Session")
            return self.session
            
        except (AuthenticationError, SessionError):
            # 重新拋出已知錯誤
            raise
        
        except Exception as e:
            error_msg = f"獲取 Session 過程發生未預期錯誤: {str(e)}"
            self.logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def is_logged_in(self) -> bool:
        """
        檢查是否已登入且 Session 有效
        
        返回：
            bool: True 如果已登入且 Session 有效，False 否則
        """
        return self.session is not None and not self._is_token_expired()
    
    def logout(self) -> Dict[str, Any]:
        """
        登出並清理 Session
        
        返回：
            Dict[str, Any]: 包含登出狀態的字典
        """
        try:
            if self.session:
                self.session.logout()
                self.logger.info("已登出 Session")
            
            # 清理狀態
            self.session = None
            self.login_time = None
            
            return {
                'status': 'success',
                'logout_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'message': '登出成功'
            }
            
        except Exception as e:
            self.logger.error(f"登出時發生錯誤: {e}")
            # 即使登出失敗，也清理本地狀態
            self.session = None
            self.login_time = None
            
            return {
                'status': 'warning',
                'logout_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'message': f'登出時發生錯誤，但已清理本地狀態: {e}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取當前認證狀態
        
        返回：
            Dict[str, Any]: 包含詳細狀態資訊的字典
        """
        return {
            'logged_in': self.is_logged_in(),
            'session_exists': self.session is not None,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S') if self.login_time else None,
            'token_expired': self._is_token_expired(),
            'next_refresh_time': (self.login_time + self.token_lifetime - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S') if self.login_time else None
        }