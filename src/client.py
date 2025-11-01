"""
永豐金證券 API 客戶端模組

此模組提供永豐金證券 API 的主要操作介面，
包含帳號管理、合約查詢等功能。
"""

from typing import List, Optional
import shioaji as sj
from shioaji.account import Account, StockAccount, FutureAccount
import logging

from .authentication import AuthenticationService, LoginCredentials

logger = logging.getLogger(__name__)


class SinotradeClient:
    """
    永豐金證券 API 客戶端
    
    此類別提供永豐金證券 API 的主要操作介面，
    整合認證服務和各項交易功能。
    
    職責：
    - 管理 API 連線
    - 提供帳號資訊查詢
    - 管理預設帳號
    - 提供合約查詢功能
    """
    
    def __init__(
        self,
        simulation: bool = False,
        log_level: str = "INFO"
    ) -> None:
        """
        初始化永豐金證券客戶端
        
        Args:
            simulation (bool): 是否使用模擬環境，預設為 False
            log_level (str): 日誌等級，預設為 "INFO"
            
        Examples:
            >>> client = SinotradeClient(simulation=True)
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            
        Raises:
            ValueError: 當 log_level 無效時
        """
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            raise ValueError(f"log_level 必須是 {valid_log_levels} 之一")
        
        # 初始化 Shioaji API
        self._api = sj.Shioaji(simulation=simulation)
        
        # 初始化認證服務
        self._auth_service = AuthenticationService(self._api)
        
        # 設定日誌等級
        logging.basicConfig(level=getattr(logging, log_level))
        logger.info(f"客戶端已初始化 (模擬環境: {simulation})")
    
    def login(
        self,
        api_key: str,
        secret_key: str,
        subscribe_trade: bool = True,
        contracts_timeout: int = 0,
        receive_window: int = 30000,
        fetch_contract: bool = True
    ) -> bool:
        """
        登入永豐金證券帳號
        
        Args:
            api_key (str): API 金鑰
            secret_key (str): 密鑰
            subscribe_trade (bool): 是否訂閱委託/成交回報，預設為 True
            contracts_timeout (int): 獲取商品檔 timeout（毫秒），預設為 0
            receive_window (int): 登入動作有效執行時間（毫秒），預設為 30000
            fetch_contract (bool): 是否從快取中讀取商品檔或從伺服器下載商品檔，預設為 True
            
        Returns:
            bool: 登入成功返回 True，失敗返回 False
            
        Examples:
            >>> client = SinotradeClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            
        Raises:
            ValueError: 當登入參數無效時
            ConnectionError: 當無法連接到永豐金證券伺服器時
            RuntimeError: 當登入過程發生錯誤時
        """
        credentials = LoginCredentials(api_key=api_key, secret_key=secret_key)
        return self._auth_service.login(
            credentials=credentials,
            subscribe_trade=subscribe_trade,
            contracts_timeout=contracts_timeout,
            receive_window=receive_window,
            fetch_contract=fetch_contract
        )
    
    def logout(self) -> bool:
        """
        登出永豐金證券帳號
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
            
        Examples:
            >>> client.logout()
            True
            
        Raises:
            RuntimeError: 當登出過程發生錯誤時
        """
        return self._auth_service.logout()
    
    def list_accounts(self) -> List[Account]:
        """
        取得所有帳號列表
        
        Returns:
            List[Account]: 帳號列表，包含證券和期貨帳號
            
        Examples:
            >>> accounts = client.list_accounts()
            >>> for account in accounts:
            ...     print(account.account_id)
            
        Raises:
            RuntimeError: 當尚未登入時
        """
        if not self._auth_service.is_logged_in:
            raise RuntimeError("尚未登入，無法取得帳號列表")
        
        try:
            accounts = self._api.list_accounts()
            logger.info(f"取得 {len(accounts)} 個帳號")
            return accounts
        except RuntimeError as e:
            logger.error(f"取得帳號列表失敗: {e}")
            raise RuntimeError(f"取得帳號列表失敗: {e}")
    
    @property
    def stock_account(self) -> Optional[StockAccount]:
        """
        取得預設證券帳號
        
        Returns:
            Optional[StockAccount]: 證券帳號，若無則返回 None
            
        Examples:
            >>> account = client.stock_account
            >>> print(account.account_id)
            
        Raises:
            RuntimeError: 當尚未登入時
        """
        if not self._auth_service.is_logged_in:
            raise RuntimeError("尚未登入，無法取得證券帳號")
        
        return self._api.stock_account
    
    @property
    def futopt_account(self) -> Optional[FutureAccount]:
        """
        取得預設期貨帳號
        
        Returns:
            Optional[FutureAccount]: 期貨帳號，若無則返回 None
            
        Examples:
            >>> account = client.futopt_account
            >>> print(account.account_id)
            
        Raises:
            RuntimeError: 當尚未登入時
        """
        if not self._auth_service.is_logged_in:
            raise RuntimeError("尚未登入，無法取得期貨帳號")
        
        return self._api.futopt_account
    
    def set_default_account(self, account: Account) -> None:
        """
        設定預設帳號
        
        Args:
            account (Account): 要設定為預設的帳號
            
        Examples:
            >>> accounts = client.list_accounts()
            >>> client.set_default_account(accounts[0])
            
        Raises:
            ValueError: 當 account 無效時
            RuntimeError: 當尚未登入時
        """
        if not self._auth_service.is_logged_in:
            raise RuntimeError("尚未登入，無法設定預設帳號")
        
        if not isinstance(account, Account):
            raise ValueError("account 必須是 Account 實例")
        
        try:
            self._api.set_default_account(account)
            logger.info(f"已設定預設帳號: {account.account_id}")
        except ValueError as e:
            logger.error(f"設定預設帳號失敗: {e}")
            raise ValueError(f"設定預設帳號失敗: {e}")
    
    @property
    def is_logged_in(self) -> bool:
        """
        檢查是否已登入
        
        Returns:
            bool: 已登入返回 True，未登入返回 False
        """
        return self._auth_service.is_logged_in
    
    @property
    def api(self) -> sj.Shioaji:
        """
        取得底層 Shioaji API 實例
        
        Returns:
            sj.Shioaji: Shioaji API 實例
        """
        return self._api
