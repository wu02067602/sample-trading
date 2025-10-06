"""
Shioaji 交易客戶端模組

此模組提供與永豐 Shioaji API 交互的客戶端類別。
"""

import shioaji as sj
from typing import Optional, Any


class ShioajiClient:
    """
    Shioaji 交易客戶端類別
    
    此類別負責處理與永豐 Shioaji API 的連線和認證。
    
    Attributes:
        sj (Optional[sj.Shioaji]): Shioaji API 實例，登入成功後可用
        contracts (Optional[Any]): 商品檔物件，登入成功後自動載入
    """
    
    def __init__(self):
        """初始化 ShioajiClient 實例。"""
        self.sj: Optional[sj.Shioaji] = None
        self.contracts: Optional[Any] = None
    
    def login(
        self,
        api_key: str,
        secret_key: str,
        contracts_timeout: int = 30000
    ) -> bool:
        """
        使用 API Key 和 Secret Key 登入永豐 Shioaji。
        
        Args:
            api_key (str): 永豐提供的 API Key
            secret_key (str): 永豐提供的 Secret Key
            contracts_timeout (int): 合約下載逾時時間（毫秒），預設 30000
        
        Returns:
            bool: 登入成功返回 True，失敗返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.sj.stock_account
            Account(...)
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空字串時
            ConnectionError: 當無法連線到 Shioaji 伺服器時
            AuthenticationError: 當認證失敗時（無效的 API Key 或 Secret Key）
        """
        if not api_key or not api_key.strip():
            raise ValueError("API Key 不可為空")
        
        if not secret_key or not secret_key.strip():
            raise ValueError("Secret Key 不可為空")
        
        try:
            # 建立 Shioaji 實例
            self.sj = sj.Shioaji()
            
            # 執行登入
            result = self.sj.login(
                api_key=api_key,
                secret_key=secret_key,
                contracts_timeout=contracts_timeout
            )
            
            if result:
                # 登入成功後，載入商品檔
                self.contracts = self.sj.Contracts
                return True
            else:
                self.sj = None
                self.contracts = None
                raise AuthenticationError("登入失敗：認證未通過")
                
        except ConnectionError as e:
            self.sj = None
            self.contracts = None
            raise ConnectionError(f"無法連線到 Shioaji 伺服器: {e}")
        except AuthenticationError:
            # 重新拋出已處理的認證錯誤
            self.contracts = None
            raise
        except (ValueError, TypeError) as e:
            # 處理參數相關錯誤
            self.sj = None
            self.contracts = None
            raise ValueError(f"登入參數錯誤: {e}")
        except OSError as e:
            # 處理網路相關錯誤
            self.sj = None
            self.contracts = None
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def logout(self) -> bool:
        """
        登出 Shioaji 連線。
        
        Returns:
            bool: 登出成功返回 True
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.logout()
            True
        
        Raises:
            RuntimeError: 當尚未登入時嘗試登出
        """
        if self.sj is None:
            raise RuntimeError("尚未登入，無法執行登出操作")
        
        try:
            result = self.sj.logout()
            self.sj = None
            self.contracts = None
            return result
        except (ConnectionError, OSError) as e:
            # 即使登出失敗，也清理本地狀態
            self.sj = None
            self.contracts = None
            raise RuntimeError(f"登出時發生網路錯誤: {e}")
        except AttributeError as e:
            # Shioaji 物件可能已損壞
            self.sj = None
            self.contracts = None
            raise RuntimeError(f"登出時發生錯誤，API 物件狀態異常: {e}")
    
    def is_logged_in(self) -> bool:
        """
        檢查是否已登入。
        
        Returns:
            bool: 已登入返回 True，否則返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.is_logged_in()
            False
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.is_logged_in()
            True
        
        Raises:
            None
        """
        return self.sj is not None
    
    def get_stock_contract(self, symbol: str) -> Any:
        """
        取得指定的股票商品檔。
        
        Args:
            symbol (str): 股票代碼（例如：'2330' 或 'TSE2330'）
        
        Returns:
            Any: 股票商品檔物件
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> contract = client.get_stock_contract("2330")
            >>> contract.symbol
            'TSE2330'
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當找不到指定商品時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法取得商品檔")
        
        try:
            # 先嘗試從 TSE（上市）查找
            if hasattr(self.contracts.Stocks, 'TSE'):
                contract = self.contracts.Stocks.TSE.get(symbol)
                if contract:
                    return contract
            
            # 再嘗試從 OTC（上櫃）查找
            if hasattr(self.contracts.Stocks, 'OTC'):
                contract = self.contracts.Stocks.OTC.get(symbol)
                if contract:
                    return contract
            
            raise ValueError(f"找不到股票代碼: {symbol}")
        except AttributeError as e:
            raise RuntimeError(f"商品檔結構異常: {e}")
    
    def get_future_contract(self, symbol: str) -> Any:
        """
        取得指定的期貨商品檔。
        
        Args:
            symbol (str): 期貨商品代碼（例如：'TXFR1'）
        
        Returns:
            Any: 期貨商品檔物件
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> contract = client.get_future_contract("TXFR1")
            >>> contract.symbol
            'TXFR1'
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當找不到指定商品時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法取得商品檔")
        
        try:
            futures = list(self.contracts.Futures)
            for future in futures:
                if future.symbol == symbol or future.code == symbol:
                    return future
            
            raise ValueError(f"找不到期貨商品: {symbol}")
        except AttributeError as e:
            raise RuntimeError(f"商品檔結構異常: {e}")
    
    def get_option_contract(self, symbol: str) -> Any:
        """
        取得指定的選擇權商品檔。
        
        Args:
            symbol (str): 選擇權商品代碼
        
        Returns:
            Any: 選擇權商品檔物件
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> contract = client.get_option_contract("TXO")
            >>> contract.symbol
            'TXO'
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當找不到指定商品時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法取得商品檔")
        
        try:
            options = list(self.contracts.Options)
            for option in options:
                if option.symbol == symbol or option.code == symbol:
                    return option
            
            raise ValueError(f"找不到選擇權商品: {symbol}")
        except AttributeError as e:
            raise RuntimeError(f"商品檔結構異常: {e}")


class AuthenticationError(Exception):
    """
    認證錯誤異常
    
    當 Shioaji 認證失敗時拋出此異常。
    """
    pass
