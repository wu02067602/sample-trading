"""
永豐金證券帳號認證模組

此模組負責處理永豐金證券帳號的登入、登出和認證相關功能。
"""

from typing import Optional, Callable
import shioaji as sj
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LoginCredentials:
    """
    登入憑證資料類別
    
    Attributes:
        person_id (str): 使用者身份證字號
        passwd (str): 使用者密碼
    """
    person_id: str
    passwd: str
    
    def __post_init__(self) -> None:
        """驗證登入憑證的有效性"""
        if not self.person_id or not isinstance(self.person_id, str):
            raise ValueError("person_id 必須為非空字串")
        if not self.passwd or not isinstance(self.passwd, str):
            raise ValueError("passwd 必須為非空字串")


class AuthenticationService:
    """
    永豐金證券帳號認證服務
    
    此類別負責處理永豐金證券帳號的登入和登出功能，
    確保使用者身份驗證的安全性和正確性。
    
    職責：
    - 管理使用者登入狀態
    - 執行登入和登出操作
    - 驗證登入憑證的有效性
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化認證服務
        
        Args:
            api (sj.Shioaji): Shioaji API 實例
            
        Raises:
            TypeError: 當 api 不是 Shioaji 實例時
        """
        if not isinstance(api, sj.Shioaji):
            raise TypeError("api 必須是 Shioaji 實例")
        
        self._api = api
        self._is_logged_in = False
        logger.info("認證服務已初始化")
    
    def login(
        self,
        credentials: LoginCredentials,
        contracts_cb: Optional[Callable] = None,
        subscribe_trade: bool = True,
        contracts_timeout: int = 30000
    ) -> bool:
        """
        執行登入操作
        
        Args:
            credentials (LoginCredentials): 登入憑證資料
            contracts_cb (Optional[Callable]): 契約回調函數
            subscribe_trade (bool): 是否訂閱交易資訊，預設為 True
            contracts_timeout (int): 契約超時時間（毫秒），預設為 30000
            
        Returns:
            bool: 登入成功返回 True，失敗返回 False
            
        Examples:
            >>> credentials = LoginCredentials(person_id="A123456789", passwd="password")
            >>> auth_service = AuthenticationService(api)
            >>> auth_service.login(credentials)
            True
            
        Raises:
            ValueError: 當 credentials 無效時
            ConnectionError: 當無法連接到永豐金證券伺服器時
            RuntimeError: 當登入過程發生錯誤時
        """
        if not isinstance(credentials, LoginCredentials):
            raise ValueError("credentials 必須是 LoginCredentials 實例")
        
        if contracts_timeout <= 0:
            raise ValueError("contracts_timeout 必須為正整數")
        
        try:
            logger.info(f"嘗試登入，使用者: {credentials.person_id}")
            
            self._api.login(
                person_id=credentials.person_id,
                passwd=credentials.passwd,
                contracts_cb=contracts_cb,
                subscribe_trade=subscribe_trade,
                contracts_timeout=contracts_timeout
            )
            
            self._is_logged_in = True
            logger.info("登入成功")
            return True
            
        except ConnectionError as e:
            logger.error(f"連線失敗: {e}")
            raise ConnectionError(f"無法連接到永豐金證券伺服器: {e}")
        except RuntimeError as e:
            logger.error(f"登入失敗: {e}")
            raise RuntimeError(f"登入過程發生錯誤: {e}")
    
    def logout(self) -> bool:
        """
        執行登出操作
        
        登出功能將關閉客戶端及服務端之間的連接。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
            
        Examples:
            >>> auth_service.logout()
            True
            
        Raises:
            RuntimeError: 當登出過程發生錯誤時
        """
        if not self._is_logged_in:
            logger.warning("尚未登入，無需登出")
            return True
        
        try:
            logger.info("執行登出操作")
            self._api.logout()
            self._is_logged_in = False
            logger.info("登出成功")
            return True
            
        except RuntimeError as e:
            logger.error(f"登出失敗: {e}")
            raise RuntimeError(f"登出過程發生錯誤: {e}")
    
    @property
    def is_logged_in(self) -> bool:
        """
        檢查是否已登入
        
        Returns:
            bool: 已登入返回 True，未登入返回 False
        """
        return self._is_logged_in
