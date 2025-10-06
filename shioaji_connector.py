"""
Shioaji 連線器模組

此模組提供與永豐證券 Shioaji API 的連線功能。
"""

import shioaji as sj
from typing import Optional, Any, Callable, Dict, List


class ShioajiConnector:
    """
    Shioaji 連線器類別，負責管理與永豐證券 API 的連線。
    
    此類別遵循單一職責原則，專注於處理 Shioaji 的登入與連線管理。
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        sj (Optional[sj.Shioaji]): Shioaji 連線實例
        contracts (Optional[Any]): 商品檔合約資料
        subscribed_contracts (List[Any]): 已訂閱的合約列表
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
        self.subscribed_contracts: List[Any] = []
    
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
    
    def subscribe_quote(self, contract: Any) -> None:
        """
        訂閱指定合約的即時報價。
        
        此方法會向 Shioaji API 訂閱指定商品的即時報價資料。
        訂閱後，當有新的報價資料時，會觸發已註冊的 callback 函數。
        
        Args:
            contract (Any): 要訂閱的合約物件（可透過 get_stock_contract 或 get_futures_contract 取得）
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> connector.subscribe_quote(contract)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試訂閱報價時
            ValueError: 當傳入的合約物件無效時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before subscribing.")
        
        if contract is None:
            raise ValueError("Contract cannot be None")
        
        try:
            self.sj.quote.subscribe(
                self.sj.Contracts.Stocks[contract.code]
                if hasattr(contract, 'code')
                else contract
            )
            self.subscribed_contracts.append(contract)
        except AttributeError as e:
            raise ValueError(f"Invalid contract object: {e}")
    
    def unsubscribe_quote(self, contract: Any) -> None:
        """
        取消訂閱指定合約的即時報價。
        
        Args:
            contract (Any): 要取消訂閱的合約物件
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> connector.subscribe_quote(contract)
            >>> connector.unsubscribe_quote(contract)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試取消訂閱時
            ValueError: 當傳入的合約物件無效時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first.")
        
        if contract is None:
            raise ValueError("Contract cannot be None")
        
        try:
            self.sj.quote.unsubscribe(
                self.sj.Contracts.Stocks[contract.code]
                if hasattr(contract, 'code')
                else contract
            )
            if contract in self.subscribed_contracts:
                self.subscribed_contracts.remove(contract)
        except AttributeError as e:
            raise ValueError(f"Invalid contract object: {e}")
    
    def set_quote_callback(self, callback: Callable[[Any, Any], None]) -> None:
        """
        設定即時報價的 callback 函數。
        
        當訂閱的商品有新報價資料時，會自動呼叫此 callback 函數。
        Callback 函數應該接受兩個參數：(topic, quote_data)
        
        Args:
            callback (Callable[[Any, Any], None]): 
                Callback 函數，接收兩個參數：
                - topic: 報價主題（包含交易所和商品代碼資訊）
                - quote_data: 報價資料物件（包含成交價、量、買賣價等）
        
        Examples:
            >>> def my_quote_handler(topic, quote):
            ...     print(f"代碼: {topic}, 成交價: {quote.close}")
            >>> 
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.set_quote_callback(my_quote_handler)
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> connector.subscribe_quote(contract)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試設定 callback 時
            TypeError: 當傳入的不是可呼叫物件時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before setting callback.")
        
        if not callable(callback):
            raise TypeError("Callback must be a callable function")
        
        # 使用裝飾器方式註冊 callback
        @self.sj.on_quote_stk_v1()
        def quote_callback(topic: str, quote: Any) -> None:
            callback(topic, quote)
    
    def get_subscribed_contracts(self) -> List[Any]:
        """
        取得目前已訂閱的合約列表。
        
        Returns:
            List[Any]: 已訂閱的合約物件列表
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> connector.subscribe_quote(contract)
            >>> subscribed = connector.get_subscribed_contracts()
            >>> print(len(subscribed))
            1
        """
        return self.subscribed_contracts.copy()
