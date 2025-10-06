"""永豐金證券 Shioaji 交易系統模組

此模組提供永豐金證券 Shioaji API 的登入與管理功能。
"""

import shioaji as sj
from typing import Optional, List, Callable, Dict, Any
import time


class ShioajiTrader:
    """永豐金證券 Shioaji 交易管理類別
    
    此類別封裝 Shioaji API 的登入與管理功能，提供簡潔的介面供交易系統使用。
    
    Attributes:
        sj: Shioaji API 實例，登入成功後可用於後續交易操作
        contracts: 商品檔物件，提供證券、期貨、選擇權、指數等商品資訊
        _subscribed_contracts: 已訂閱的商品清單
        _quote_callback: 報價 callback 函數
        _order_callback: 委託回報 callback 函數
        
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
        self._subscribed_contracts: List = []  # 記錄已訂閱的商品
        self._quote_callback: Optional[Callable] = None  # 報價 callback
        self._order_callback: Optional[Callable] = None  # 委託 callback
    
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
    
    @property
    def contracts(self):
        """取得商品檔物件
        
        商品檔在登入時會自動下載，包含證券、期貨、選擇權、指數等商品資訊。
        商品檔會在特定時間更新：07:50, 08:00, 14:45, 17:15。
        
        Returns:
            商品檔物件，若未登入則回傳 None
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> # 取得所有證券商品
            >>> stocks = trader.contracts.Stocks
            >>> # 查詢台積電
            >>> tsmc = trader.contracts.Stocks["2330"]
            >>> print(tsmc)
        """
        if self.sj:
            return self.sj.Contracts
        return None
    
    def get_stock(self, code: str):
        """查詢證券商品
        
        根據股票代碼查詢證券商品資訊。
        
        Args:
            code: 股票代碼，例如 "2330" (台積電)
            
        Returns:
            證券商品物件，若查詢不到則回傳 None
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> tsmc = trader.get_stock("2330")
            >>> print(tsmc.name)  # 台積電
            >>> print(tsmc.exchange)  # TSE
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            return self.contracts.Stocks[code]
        except Exception as e:
            print(f"查詢股票 {code} 失敗：{str(e)}")
            return None
    
    def get_future(self, code: str):
        """查詢期貨商品
        
        根據期貨代碼查詢期貨商品資訊。
        
        Args:
            code: 期貨代碼，例如 "TXFR1" (台指期近月)
            
        Returns:
            期貨商品物件，若查詢不到則回傳 None
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> txf = trader.get_future("TXFR1")
            >>> print(txf.name)
            >>> print(txf.delivery_month)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            return self.contracts.Futures[code]
        except Exception as e:
            print(f"查詢期貨 {code} 失敗：{str(e)}")
            return None
    
    def get_option(self, code: str):
        """查詢選擇權商品
        
        根據選擇權代碼查詢選擇權商品資訊。
        
        Args:
            code: 選擇權代碼
            
        Returns:
            選擇權商品物件，若查詢不到則回傳 None
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> option = trader.get_option("TXO12000C1")
            >>> print(option.name)
            >>> print(option.strike_price)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            return self.contracts.Options[code]
        except Exception as e:
            print(f"查詢選擇權 {code} 失敗：{str(e)}")
            return None
    
    def search_contracts(self, keyword: str, category: str = "Stocks"):
        """搜尋商品
        
        根據關鍵字搜尋商品名稱或代碼。
        
        Args:
            keyword: 搜尋關鍵字，可以是商品名稱或代碼的一部分
            category: 商品類別，可選 "Stocks", "Futures", "Options", "Indexs"，
                     預設為 "Stocks"
            
        Returns:
            List: 符合條件的商品列表
            
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當商品類別無效時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> # 搜尋名稱包含「台積」的股票
            >>> results = trader.search_contracts("台積")
            >>> for contract in results:
            ...     print(f"{contract.code}: {contract.name}")
            >>> # 搜尋期貨
            >>> futures = trader.search_contracts("TX", category="Futures")
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        valid_categories = ["Stocks", "Futures", "Options", "Indexs"]
        if category not in valid_categories:
            raise ValueError(
                f"商品類別必須是以下其中之一：{', '.join(valid_categories)}"
            )
        
        try:
            # 取得指定類別的所有商品
            all_contracts = getattr(self.contracts, category)
            results = []
            
            # 遍歷所有商品，搜尋符合關鍵字的商品
            for exchange in dir(all_contracts):
                if exchange.startswith('_'):
                    continue
                
                exchange_obj = getattr(all_contracts, exchange)
                if hasattr(exchange_obj, '__iter__'):
                    for contract in exchange_obj:
                        # 檢查代碼或名稱是否包含關鍵字
                        if (keyword.lower() in contract.code.lower() or 
                            keyword in contract.name):
                            results.append(contract)
            
            return results
            
        except Exception as e:
            print(f"搜尋商品失敗：{str(e)}")
            return []
    
    def subscribe_quote(self, contract, quote_type: str = "tick") -> bool:
        """訂閱商品報價
        
        訂閱指定商品的即時報價資訊。報價資料將透過 callback 函數接收。
        需要先使用 set_quote_callback() 設定 callback 函數。
        
        Args:
            contract: 商品物件，可從 contracts 取得
            quote_type: 報價類型，可選 "tick" (逐筆) 或 "bidask" (五檔)，
                       預設為 "tick"
            
        Returns:
            bool: 訂閱是否成功
            
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當尚未設定 callback 函數時
            
        Examples:
            >>> trader = ShioajiTrader()
            >>> trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            >>> 
            >>> # 設定 callback
            >>> def my_callback(exchange, tick):
            ...     print(f"{tick.code}: 成交價={tick.close}, 量={tick.volume}")
            >>> 
            >>> trader.set_quote_callback(my_callback)
            >>> 
            >>> # 訂閱台積電報價
            >>> tsmc = trader.get_stock("2330")
            >>> trader.subscribe_quote(tsmc)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        if not self._quote_callback:
            raise ValueError("請先使用 set_quote_callback() 設定 callback 函數")
        
        try:
            # 訂閱報價
            self.sj.quote.subscribe(
                contract,
                quote_type=quote_type,
                version="v1"
            )
            
            # 記錄已訂閱的商品
            if contract not in self._subscribed_contracts:
                self._subscribed_contracts.append(contract)
            
            print(f"訂閱成功：{contract.code} - {contract.name}")
            return True
            
        except Exception as e:
            print(f"訂閱失敗：{str(e)}")
            return False
    
    def unsubscribe_quote(self, contract) -> bool:
        """取消訂閱商品報價
        
        取消訂閱指定商品的報價。
        
        Args:
            contract: 商品物件
            
        Returns:
            bool: 取消訂閱是否成功
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> trader.unsubscribe_quote(tsmc)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        try:
            self.sj.quote.unsubscribe(
                contract,
                quote_type="tick",
                version="v1"
            )
            
            if contract in self._subscribed_contracts:
                self._subscribed_contracts.remove(contract)
            
            print(f"取消訂閱成功：{contract.code} - {contract.name}")
            return True
            
        except Exception as e:
            print(f"取消訂閱失敗：{str(e)}")
            return False
    
    def set_quote_callback(self, callback: Callable) -> None:
        """設定報價 callback 函數
        
        設定用於接收報價資料的 callback 函數。
        callback 函數會接收兩個參數：(exchange, tick)。
        
        Args:
            callback: callback 函數，簽名為 callback(exchange, tick)
                     exchange: 交易所代碼
                     tick: 報價資料物件
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> def quote_callback(exchange, tick):
            ...     print(f"{tick.code}: 價={tick.close}, 量={tick.volume}")
            >>> 
            >>> trader.set_quote_callback(quote_callback)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        self._quote_callback = callback
        
        # 註冊 callback 到 Shioaji
        @self.sj.on_quote_stk_v1
        def inner_callback(exchange: str, tick: Dict[str, Any]):
            if self._quote_callback:
                self._quote_callback(exchange, tick)
        
        print("報價 callback 設定成功")
    
    def set_order_callback(self, callback: Callable) -> None:
        """設定委託回報 callback 函數
        
        設定用於接收委託回報與成交回報的 callback 函數。
        callback 函數會接收兩個參數：(stat, msg)。
        
        Args:
            callback: callback 函數，簽名為 callback(stat, msg)
                     stat: 委託狀態
                     msg: 委託或成交訊息
            
        Raises:
            RuntimeError: 當尚未登入時
            
        Examples:
            >>> def order_callback(stat, msg):
            ...     print(f"狀態: {stat}")
            ...     print(f"訊息: {msg}")
            >>> 
            >>> trader.set_order_callback(order_callback)
        """
        if not self.sj:
            raise RuntimeError("請先登入系統")
        
        self._order_callback = callback
        
        # 註冊 callback 到 Shioaji
        @self.sj.on_order_callback
        def inner_callback(stat, msg):
            if self._order_callback:
                self._order_callback(stat, msg)
        
        print("委託回報 callback 設定成功")
    
    def get_subscribed_contracts(self) -> List:
        """取得已訂閱的商品清單
        
        Returns:
            List: 已訂閱的商品清單
            
        Examples:
            >>> contracts = trader.get_subscribed_contracts()
            >>> for contract in contracts:
            ...     print(f"{contract.code}: {contract.name}")
        """
        return self._subscribed_contracts.copy()
