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
    
    def place_stock_order(
        self,
        contract: Any,
        action: str,
        price: float,
        quantity: int
    ) -> Any:
        """
        下一般股票委託單。
        
        此方法用於下達一般股票（整股）的委託單。
        支援現股買進和賣出。
        
        Args:
            contract (Any): 股票合約物件（透過 get_stock_contract 取得）
            action (str): 委託動作，"Buy" 為買進，"Sell" 為賣出
            price (float): 委託價格（元），0 表示市價單
            quantity (int): 委託數量（股），必須為 1000 的倍數
        
        Returns:
            Any: 委託回報物件，包含委託書號、狀態等資訊
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> # 以 600 元買進 1000 股台積電
            >>> trade = connector.place_stock_order(contract, "Buy", 600, 1000)
            >>> print(trade.status.status)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試下單時
            ValueError: 當動作、價格或數量參數無效時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before placing order.")
        
        if action not in ["Buy", "Sell"]:
            raise ValueError(f"Invalid action '{action}'. Must be 'Buy' or 'Sell'.")
        
        if price < 0:
            raise ValueError(f"Price must be non-negative, got {price}")
        
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {quantity}")
        
        if quantity % 1000 != 0:
            raise ValueError(f"Quantity must be multiple of 1000 for regular stock, got {quantity}")
        
        # 建立訂單物件
        order = self.sj.Order(
            price=price,
            quantity=quantity,
            action=action,
            price_type="LMT" if price > 0 else "MKT",
            order_type="ROD",
            order_cond="Cash",
            account=self.sj.stock_account
        )
        
        # 執行下單
        trade = self.sj.place_order(contract, order)
        return trade
    
    def place_odd_lot_order(
        self,
        contract: Any,
        action: str,
        price: float,
        quantity: int
    ) -> Any:
        """
        下盤中零股委託單。
        
        此方法用於下達盤中零股（小於 1000 股）的委託單。
        支援零股買進和賣出。
        
        Args:
            contract (Any): 股票合約物件（透過 get_stock_contract 取得）
            action (str): 委託動作，"Buy" 為買進，"Sell" 為賣出
            price (float): 委託價格（元），0 表示市價單
            quantity (int): 委託數量（股），必須小於 1000
        
        Returns:
            Any: 委託回報物件，包含委託書號、狀態等資訊
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.fetch_contracts()
            >>> contract = connector.get_stock_contract("2330")
            >>> # 以 600 元買進 100 股台積電零股
            >>> trade = connector.place_odd_lot_order(contract, "Buy", 600, 100)
            >>> print(trade.status.status)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試下單時
            ValueError: 當動作、價格或數量參數無效時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before placing order.")
        
        if action not in ["Buy", "Sell"]:
            raise ValueError(f"Invalid action '{action}'. Must be 'Buy' or 'Sell'.")
        
        if price < 0:
            raise ValueError(f"Price must be non-negative, got {price}")
        
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {quantity}")
        
        if quantity >= 1000:
            raise ValueError(f"Quantity must be less than 1000 for odd lot, got {quantity}")
        
        # 建立零股訂單物件
        order = self.sj.Order(
            price=price,
            quantity=quantity,
            action=action,
            price_type="LMT" if price > 0 else "MKT",
            order_type="ROD",
            order_cond="Cash",
            daytrade_short=False,
            account=self.sj.stock_account
        )
        
        # 執行下單
        trade = self.sj.place_order(contract, order, odd_lot=True)
        return trade
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        取得帳戶餘額資訊。
        
        Returns:
            Dict[str, Any]: 帳戶餘額資訊，包含可用資金、庫存等
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> balance = connector.get_account_balance()
            >>> print(balance)
        
        Raises:
            RuntimeError: 當尚未登入就嘗試查詢餘額時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before getting account balance.")
        
        return self.sj.account_balance()
    
    def set_order_callback(self, callback: Callable[[Any], None]) -> None:
        """
        設定訂單狀態回報的 callback 函數。
        
        當下單後訂單狀態發生變更時（如委託中、已成交、已取消等），
        會自動呼叫此 callback 函數。Callback 函數應該接受一個參數：order_status
        
        Args:
            callback (Callable[[Any], None]): 
                Callback 函數，接收一個參數：
                - order_status: 訂單狀態物件，包含訂單編號、狀態、價格、數量等資訊
        
        Examples:
            >>> def my_order_handler(order_status):
            ...     print(f"訂單編號: {order_status.order.id}")
            ...     print(f"訂單狀態: {order_status.status}")
            >>> 
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.set_order_callback(my_order_handler)
            >>> # 之後下單時，訂單狀態變更會自動觸發 callback
        
        Raises:
            RuntimeError: 當尚未登入就嘗試設定 callback 時
            TypeError: 當傳入的不是可呼叫物件時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before setting callback.")
        
        if not callable(callback):
            raise TypeError("Callback must be a callable function")
        
        # 使用裝飾器方式註冊訂單狀態 callback
        @self.sj.on_order_status()
        def order_callback(order_status: Any) -> None:
            callback(order_status)
    
    def set_deal_callback(self, callback: Callable[[Any], None]) -> None:
        """
        設定成交回報的 callback 函數。
        
        當訂單成交時（全部成交或部分成交），會自動呼叫此 callback 函數。
        Callback 函數應該接受一個參數：deal_status
        
        Args:
            callback (Callable[[Any], None]): 
                Callback 函數，接收一個參數：
                - deal_status: 成交回報物件，包含成交價格、成交數量、成交時間等資訊
        
        Examples:
            >>> def my_deal_handler(deal_status):
            ...     print(f"成交價格: {deal_status.price}")
            ...     print(f"成交數量: {deal_status.quantity}")
            >>> 
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.set_deal_callback(my_deal_handler)
            >>> # 之後下單成交時，會自動觸發 callback
        
        Raises:
            RuntimeError: 當尚未登入就嘗試設定 callback 時
            TypeError: 當傳入的不是可呼叫物件時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first before setting callback.")
        
        if not callable(callback):
            raise TypeError("Callback must be a callable function")
        
        # 使用裝飾器方式註冊成交回報 callback
        @self.sj.on_deal()
        def deal_callback(deal_status: Any) -> None:
            callback(deal_status)
