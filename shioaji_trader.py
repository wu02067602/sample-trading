"""永豐金證券 Shioaji 交易系統模組

此模組提供永豐金證券 Shioaji API 的登入與管理功能。
"""

import shioaji as sj
from typing import Optional, List


class ShioajiTrader:
    """永豐金證券 Shioaji 交易管理類別
    
    此類別封裝 Shioaji API 的登入與管理功能，提供簡潔的介面供交易系統使用。
    
    Attributes:
        sj: Shioaji API 實例，登入成功後可用於後續交易操作
        
    Examples:
        使用 API Key 登入：
        >>> trader = ShioajiTrader()
        >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
        >>> print(trader.sj.stock_account)
        
        使用帳號密碼登入：
        >>> trader = ShioajiTrader()
        >>> trader.login(person_id="YOUR_PERSON_ID", passwd="YOUR_PASSWORD")
        >>> accounts = trader.list_accounts()
        
        登出：
        >>> trader.logout()
    """
    
    def __init__(self):
        """初始化 ShioajiTrader 實例
        
        建立 Shioaji API 物件並儲存於 self.sj 屬性中。
        """
        self.sj: Optional[sj.Shioaji] = sj.Shioaji()
    
    def login(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        person_id: Optional[str] = None,
        passwd: Optional[str] = None,
        contracts_timeout: int = 30000
    ) -> bool:
        """登入永豐金證券 Shioaji 系統
        
        支援兩種登入方式：
        1. 使用 API Key 與 Secret Key (推薦)
        2. 使用身分證字號與密碼
        
        Args:
            api_key: API 金鑰，與 secret_key 配對使用
            secret_key: API 密鑰，與 api_key 配對使用
            person_id: 身分證字號，與 passwd 配對使用
            passwd: 登入密碼，與 person_id 配對使用
            contracts_timeout: 合約下載逾時時間(毫秒)，預設 30000
            
        Returns:
            bool: 登入是否成功，成功回傳 True，失敗回傳 False
            
        Raises:
            ValueError: 當未提供任何登入憑證或提供的憑證組合不正確時
            ConnectionError: 當無法連線至伺服器時
            AuthenticationError: 當認證失敗時
            
        Examples:
            使用 API Key 登入：
            >>> trader = ShioajiTrader()
            >>> success = trader.login(
            ...     api_key="YOUR_API_KEY",
            ...     secret_key="YOUR_SECRET_KEY"
            ... )
            >>> if success:
            ...     print("登入成功")
            
            使用帳號密碼登入：
            >>> trader = ShioajiTrader()
            >>> success = trader.login(
            ...     person_id="A123456789",
            ...     passwd="YOUR_PASSWORD"
            ... )
        """
        try:
            # 檢查登入憑證
            if api_key and secret_key:
                # 使用 API Key 登入
                result = self.sj.login(
                    api_key=api_key,
                    secret_key=secret_key,
                    contracts_timeout=contracts_timeout
                )
            elif person_id and passwd:
                # 使用身分證字號與密碼登入
                result = self.sj.login(
                    person_id=person_id,
                    passwd=passwd,
                    contracts_timeout=contracts_timeout
                )
            else:
                raise ValueError(
                    "請提供有效的登入憑證：\n"
                    "1. api_key 與 secret_key 或\n"
                    "2. person_id 與 passwd"
                )
            
            return True
            
        except Exception as e:
            print(f"登入失敗：{str(e)}")
            return False
    
    def logout(self) -> bool:
        """登出永豐金證券 Shioaji 系統
        
        關閉客戶端與伺服器之間的連線。為了提供優質的服務，
        永豐金證券限制同時連線數，建議不使用時主動登出。
        
        Returns:
            bool: 登出是否成功
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> trader.logout()
            True
        """
        try:
            if self.sj:
                result = self.sj.logout()
                return result
            return False
        except Exception as e:
            print(f"登出失敗：{str(e)}")
            return False
    
    def list_accounts(self) -> List:
        """列出所有可用帳戶
        
        取得登入後可使用的所有證券與期貨帳戶列表。
        
        Returns:
            List: 帳戶列表，包含證券帳戶與期貨帳戶
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> accounts = trader.list_accounts()
            >>> for account in accounts:
            ...     print(account)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            return self.sj.list_accounts()
        except Exception as e:
            print(f"取得帳戶列表失敗：{str(e)}")
            return []
    
    def set_default_account(self, account) -> None:
        """設定預設帳戶
        
        設定預設的證券或期貨帳戶，用於後續下單操作。
        
        Args:
            account: 帳戶物件，可從 list_accounts() 取得
            
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當提供的帳戶無效時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> accounts = trader.list_accounts()
            >>> trader.set_default_account(accounts[0])
            >>> print(trader.sj.futopt_account)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            self.sj.set_default_account(account)
        except Exception as e:
            raise ValueError(f"設定預設帳戶失敗：{str(e)}")
    
    @property
    def stock_account(self):
        """取得預設證券帳戶
        
        Returns:
            證券帳戶物件，若未登入則回傳 None
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> print(trader.stock_account)
        """
        if self.sj:
            return self.sj.stock_account
        return None
    
    @property
    def futopt_account(self):
        """取得預設期貨帳戶
        
        Returns:
            期貨帳戶物件，若未登入則回傳 None
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> print(trader.futopt_account)
        """
        if self.sj:
            return self.sj.futopt_account
        return None
