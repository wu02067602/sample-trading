"""
Shioaji 連線器模組

此模組提供與永豐證券 Shioaji API 的連線功能。
"""

import shioaji as sj
from typing import Optional, Any


class ShioajiConnector:
    """
    Shioaji 連線器類別，負責管理與永豐證券 API 的連線。
    
    此類別遵循單一職責原則，專注於處理 Shioaji 的登入與連線管理。
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        sj (Optional[sj.Shioaji]): Shioaji 連線實例
        contracts (Optional[Any]): 商品檔合約資料
    """
    
    def __init__(self, api_key: str, secret_key: str):
        """
        初始化 Shioaji 連線器。
        
        Args:
            api_key (str): 永豐證券提供的 API 金鑰
            secret_key (str): 永豐證券提供的密鑰
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空字串時
        """
        if not api_key:
            raise ValueError("api_key cannot be empty")
        if not secret_key:
            raise ValueError("secret_key cannot be empty")
        
        self.api_key = api_key
        self.secret_key = secret_key
        self.sj: Optional[sj.Shioaji] = None
        self.contracts: Optional[Any] = None
    
    def login(self) -> sj.Shioaji:
        """
        執行登入操作並建立 Shioaji 連線。
        
        Returns:
            sj.Shioaji: 登入成功後的 Shioaji 實例
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> api = connector.login()
            >>> print(api)
            <shioaji.Shioaji object>
        
        Raises:
            ConnectionError: 當無法連線到 Shioaji 伺服器時
            ValueError: 當 API 金鑰或密鑰無效時
        """
        # 創建 Shioaji 實例
        self.sj = sj.Shioaji()
        
        try:
            # 執行登入
            self.sj.login(
                api_key=self.api_key,
                secret_key=self.secret_key
            )
            
            return self.sj
        
        except ValueError as e:
            self.sj = None
            raise ValueError(f"Invalid API credentials: {e}")
        except ConnectionError as e:
            self.sj = None
            raise ConnectionError(f"Failed to connect to Shioaji server: {e}")
    
    def logout(self) -> None:
        """
        登出並關閉 Shioaji 連線。
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.logout()
        
        Raises:
            RuntimeError: 當尚未登入就嘗試登出時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first.")
        
        self.sj.logout()
        self.sj = None
    
    def is_connected(self) -> bool:
        """
        檢查是否已建立連線。
        
        Returns:
            bool: 如果已連線則返回 True，否則返回 False
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.is_connected()
            False
            >>> connector.login()
            >>> connector.is_connected()
            True
        """
        return self.sj is not None
    
    def fetch_contracts(self) -> Any:
        """
        取得所有商品檔合約資料。
        
        此方法會從 Shioaji API 取得所有可交易的商品合約資料，
        包括股票、期貨、選擇權等，並將結果保存在 contracts 屬性中。
        
        Returns:
            Any: 包含所有商品合約的 Contracts 物件
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> contracts = connector.fetch_contracts()
            >>> # 存取股票合約
            >>> stock_contract = contracts.Stocks["2330"]
            >>> # 存取期貨合約
            >>> futures_contract = contracts.Futures["TXFA4"]
        
        Raises:
            RuntimeError: 當尚未登入就嘗試取得商品檔時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before fetching contracts.")
        
        self.contracts = self.sj.Contracts
        return self.contracts
    
    def get_stock_contract(self, stock_code: str) -> Any:
        """
        取得指定股票代碼的合約資料。
        
        Args:
            stock_code (str): 股票代碼（例如："2330" 代表台積電）
        
        Returns:
            Any: 指定股票的合約物件
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> tsmc = connector.get_stock_contract("2330")
            >>> print(tsmc.code)
            2330
        
        Raises:
            RuntimeError: 當尚未取得商品檔就嘗試查詢合約時
            KeyError: 當找不到指定的股票代碼時
        """
        if self.contracts is None:
            raise RuntimeError("Contracts not fetched. Please call fetch_contracts() first.")
        
        try:
            return self.contracts.Stocks[stock_code]
        except KeyError as e:
            raise KeyError(f"Stock code '{stock_code}' not found: {e}")
    
    def get_futures_contract(self, futures_code: str) -> Any:
        """
        取得指定期貨代碼的合約資料。
        
        Args:
            futures_code (str): 期貨代碼（例如："TXFA4" 代表台指期近月）
        
        Returns:
            Any: 指定期貨的合約物件
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> tx = connector.get_futures_contract("TXFA4")
            >>> print(tx.code)
            TXFA4
        
        Raises:
            RuntimeError: 當尚未取得商品檔就嘗試查詢合約時
            KeyError: 當找不到指定的期貨代碼時
        """
        if self.contracts is None:
            raise RuntimeError("Contracts not fetched. Please call fetch_contracts() first.")
        
        try:
            return self.contracts.Futures[futures_code]
        except KeyError as e:
            raise KeyError(f"Futures code '{futures_code}' not found: {e}")
