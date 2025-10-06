"""
Shioaji 交易客戶端模組

此模組提供與永豐 Shioaji API 交互的客戶端類別。
"""

import shioaji as sj
from typing import Optional, Any, Callable
from quote_callback import QuoteCallback, OrderCallback, DefaultQuoteCallback, DefaultOrderCallback


class ShioajiClient:
    """
    Shioaji 交易客戶端類別
    
    此類別負責處理與永豐 Shioaji API 的連線和認證。
    
    Attributes:
        sj (Optional[sj.Shioaji]): Shioaji API 實例，登入成功後可用
        contracts (Optional[Any]): 商品檔物件，登入成功後自動載入
        quote_callback (Optional[QuoteCallback]): 報價回調處理器
        order_callback (Optional[OrderCallback]): 訂單回調處理器
    """
    
    def __init__(self):
        """初始化 ShioajiClient 實例。"""
        self.sj: Optional[sj.Shioaji] = None
        self.contracts: Optional[Any] = None
        self.quote_callback: Optional[QuoteCallback] = None
        self.order_callback: Optional[OrderCallback] = None
    
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
            self.quote_callback = None
            self.order_callback = None
            return result
        except (ConnectionError, OSError) as e:
            # 即使登出失敗，也清理本地狀態
            self.sj = None
            self.contracts = None
            self.quote_callback = None
            self.order_callback = None
            raise RuntimeError(f"登出時發生網路錯誤: {e}")
        except AttributeError as e:
            # Shioaji 物件可能已損壞
            self.sj = None
            self.contracts = None
            self.quote_callback = None
            self.order_callback = None
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
    
    def set_quote_callback(
        self,
        callback: Optional[QuoteCallback] = None,
        callback_func: Optional[Callable] = None
    ) -> None:
        """
        設定報價回調處理器。
        
        Args:
            callback (Optional[QuoteCallback]): 自訂的報價回調處理器
            callback_func (Optional[Callable]): 簡單的回調函數，
                                                 如果未提供 callback 則使用此函數建立預設處理器
        
        Returns:
            None
        
        Examples:
            >>> client = ShioajiClient()
            >>> def my_callback(topic, data):
            ...     print(f"收到 {topic} 報價")
            >>> client.set_quote_callback(callback_func=my_callback)
        
        Raises:
            ValueError: 當同時提供 callback 和 callback_func 時
        """
        if callback is not None and callback_func is not None:
            raise ValueError("不可同時設定 callback 和 callback_func")
        
        if callback is not None:
            self.quote_callback = callback
        else:
            self.quote_callback = DefaultQuoteCallback(callback_func)
    
    def set_order_callback(
        self,
        callback: Optional[OrderCallback] = None,
        callback_func: Optional[Callable] = None
    ) -> None:
        """
        設定訂單回調處理器。
        
        Args:
            callback (Optional[OrderCallback]): 自訂的訂單回調處理器
            callback_func (Optional[Callable]): 簡單的回調函數，
                                                 如果未提供 callback 則使用此函數建立預設處理器
        
        Returns:
            None
        
        Examples:
            >>> client = ShioajiClient()
            >>> def my_callback(state, data):
            ...     print(f"訂單狀態: {state}")
            >>> client.set_order_callback(callback_func=my_callback)
        
        Raises:
            ValueError: 當同時提供 callback 和 callback_func 時
        """
        if callback is not None and callback_func is not None:
            raise ValueError("不可同時設定 callback 和 callback_func")
        
        if callback is not None:
            self.order_callback = callback
        else:
            self.order_callback = DefaultOrderCallback(callback_func)
    
    def subscribe_quote(self, contract: Any) -> None:
        """
        訂閱商品報價。
        
        Args:
            contract (Any): 商品檔物件（透過 get_stock_contract 等方法取得）
        
        Returns:
            None
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.set_quote_callback(callback_func=lambda t, d: print(f"報價: {t}"))
            >>> contract = client.get_stock_contract("2330")
            >>> client.subscribe_quote(contract)
        
        Raises:
            RuntimeError: 當尚未登入時
            RuntimeError: 當尚未設定報價回調處理器時
            ValueError: 當商品檔物件無效時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法訂閱報價")
        
        if self.quote_callback is None:
            raise RuntimeError("尚未設定報價回調處理器，請先呼叫 set_quote_callback()")
        
        if not hasattr(contract, 'symbol'):
            raise ValueError("無效的商品檔物件")
        
        try:
            # 設定報價回調
            @self.sj.on_quote
            def quote_handler(topic: str, data: Any) -> None:
                if self.quote_callback:
                    self.quote_callback.on_quote(topic, data)
            
            # 訂閱報價
            self.sj.quote.subscribe(contract)
        except AttributeError as e:
            raise RuntimeError(f"訂閱報價時發生錯誤: {e}")
    
    def unsubscribe_quote(self, contract: Any) -> None:
        """
        取消訂閱商品報價。
        
        Args:
            contract (Any): 商品檔物件
        
        Returns:
            None
        
        Examples:
            >>> client = ShioajiClient()
            >>> contract = client.get_stock_contract("2330")
            >>> client.unsubscribe_quote(contract)
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當商品檔物件無效時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法取消訂閱報價")
        
        if not hasattr(contract, 'symbol'):
            raise ValueError("無效的商品檔物件")
        
        try:
            self.sj.quote.unsubscribe(contract)
        except AttributeError as e:
            raise RuntimeError(f"取消訂閱報價時發生錯誤: {e}")
    
    def activate_order_callback(self) -> None:
        """
        啟用訂單回調監控。
        
        Returns:
            None
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.set_order_callback(callback_func=lambda s, d: print(f"訂單: {s}"))
            >>> client.activate_order_callback()
        
        Raises:
            RuntimeError: 當尚未登入時
            RuntimeError: 當尚未設定訂單回調處理器時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法啟用訂單回調")
        
        if self.order_callback is None:
            raise RuntimeError("尚未設定訂單回調處理器，請先呼叫 set_order_callback()")
        
        try:
            @self.sj.on_order_callback
            def order_handler(state: str, data: dict) -> None:
                if self.order_callback:
                    self.order_callback.on_order(state, data)
        except AttributeError as e:
            raise RuntimeError(f"啟用訂單回調時發生錯誤: {e}")


class AuthenticationError(Exception):
    """
    認證錯誤異常
    
    當 Shioaji 認證失敗時拋出此異常。
    """
    pass
