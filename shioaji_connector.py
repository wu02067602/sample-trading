"""
Shioaji 交易連線管理模組

此模組提供永豐金證券 Shioaji API 的連線管理功能，
包含登入、登出、連線狀態管理、商品檔查詢、即時報價訂閱、
事件回調處理、證券下單功能以及成交回報處理。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
from typing import Optional, Dict, Any, List, Union, Callable
from datetime import datetime
from collections import defaultdict

try:
    import shioaji as sj
except ImportError:
    sj = None
    logging.warning("Shioaji module not installed. Please install it using: pip install shioaji")


class ShioajiConnector:
    """
    Shioaji 交易連線管理類別
    
    此類別負責管理與永豐金證券 Shioaji API 的連線，包含登入、
    登出、憑證管理等功能。遵循單一職責原則(SRP)，專注於連線管理。
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        sj (shioaji.Shioaji): Shioaji API 實例，登入成功後可使用
        is_connected (bool): 連線狀態
        login_time (datetime): 登入時間
        contracts (object): 商品檔物件，包含所有可交易的商品資訊
        subscribed_contracts (Dict): 已訂閱的商品字典
        quote_callbacks (Dict): 報價回調函數字典
        
    Examples:
        >>> connector = ShioajiConnector(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET")
        >>> connector.login(person_id="A123456789", passwd="YOUR_PASSWORD")
        >>> if connector.is_connected:
        >>>     print("登入成功")
        >>>     # 使用 connector.sj 進行後續操作
        >>>     connector.logout()
        
    Note:
        - 使用前請確保已安裝 shioaji: pip install shioaji
        - API Key 和 Secret Key 需要從永豐金證券申請
        - 個人 ID 和密碼為證券帳戶的登入憑證
    """
    
    def __init__(self, api_key: str = "", secret_key: str = "", simulation: bool = False):
        """
        初始化 Shioaji 連線器
        
        Args:
            api_key (str, optional): API 金鑰。預設為空字串。
            secret_key (str, optional): 密鑰。預設為空字串。
            simulation (bool, optional): 是否使用模擬環境。預設為 False。
            
        Raises:
            ImportError: 當 shioaji 模組未安裝時拋出
            
        Examples:
            >>> # 正式環境
            >>> connector = ShioajiConnector(api_key="key123", secret_key="secret456")
            >>> 
            >>> # 模擬環境
            >>> connector = ShioajiConnector(simulation=True)
        """
        if sj is None:
            raise ImportError(
                "Shioaji module is not installed. "
                "Please install it using: pip install shioaji"
            )
        
        self.api_key: str = api_key
        self.secret_key: str = secret_key
        self.simulation: bool = simulation
        self.sj: Optional[sj.Shioaji] = None
        self.is_connected: bool = False
        self.login_time: Optional[datetime] = None
        self.contracts: Optional[Any] = None
        
        # 訂閱報價相關屬性
        self.subscribed_contracts: Dict[str, Any] = {}  # {code: contract}
        self.quote_callbacks: Dict[str, List[Callable]] = defaultdict(list)  # {event_type: [callbacks]}
        self.quote_data: Dict[str, Any] = {}  # {code: latest_quote}
        
        # 下單相關屬性
        self.order_callbacks: Dict[str, List[Callable]] = defaultdict(list)  # {event_type: [callbacks]}
        self.orders_history: List[Dict[str, Any]] = []  # 下單歷史記錄
        
        # 成交回報相關屬性
        self.deal_callbacks: List[Callable] = []  # 成交回調函數列表
        self.order_update_callbacks: List[Callable] = []  # 訂單狀態更新回調函數列表
        self.deals_history: List[Dict[str, Any]] = []  # 成交歷史記錄
        self.order_updates: List[Dict[str, Any]] = []  # 訂單更新記錄
        
        # 設置日誌
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 初始化 Shioaji API 實例
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """
        初始化 Shioaji API 實例
        
        此為私有方法，在建構子中調用，負責創建 Shioaji API 物件。
        
        Raises:
            Exception: 當 API 初始化失敗時拋出
        """
        try:
            self.sj = sj.Shioaji(simulation=self.simulation)
            self.logger.info(f"Shioaji API 初始化成功 (模擬環境: {self.simulation})")
        except Exception as e:
            self.logger.error(f"Shioaji API 初始化失敗: {str(e)}")
            raise
    
    def login(
        self,
        person_id: str,
        passwd: str,
        ca_path: Optional[str] = None,
        ca_passwd: Optional[str] = None,
        fetch_contract: bool = True
    ) -> bool:
        """
        登入永豐金證券 Shioaji API
        
        執行登入流程，包含帳號密碼驗證。若提供憑證路徑，
        則會同時進行憑證認證以啟用下單功能。
        
        Args:
            person_id (str): 使用者身分證字號或帳號
            passwd (str): 使用者密碼
            ca_path (str, optional): 憑證檔案路徑 (.pfx 檔案)。預設為 None。
            ca_passwd (str, optional): 憑證密碼。預設為 None。
            fetch_contract (bool, optional): 是否下載合約檔。預設為 True。
            
        Returns:
            bool: 登入成功返回 True，失敗返回 False
            
        Raises:
            ValueError: 當必要參數為空時拋出
            ConnectionError: 當連線失敗時拋出
            AuthenticationError: 當認證失敗時拋出
            
        Examples:
            >>> # 基本登入 (僅查詢功能)
            >>> connector = ShioajiConnector()
            >>> success = connector.login(
            >>>     person_id="A123456789",
            >>>     passwd="your_password"
            >>> )
            >>> 
            >>> # 完整登入 (包含下單功能)
            >>> success = connector.login(
            >>>     person_id="A123456789",
            >>>     passwd="your_password",
            >>>     ca_path="/path/to/cert.pfx",
            >>>     ca_passwd="cert_password"
            >>> )
            
        Note:
            - 僅使用帳號密碼登入只能進行查詢操作
            - 需要下單功能必須提供憑證
            - 憑證檔案(.pfx)需要從永豐金證券官網下載
        """
        if not person_id or not passwd:
            raise ValueError("person_id 和 passwd 不能為空")
        
        if self.sj is None:
            raise ConnectionError("Shioaji API 未初始化")
        
        try:
            # 執行登入
            self.logger.info(f"開始登入 Shioaji API (使用者: {person_id})")
            
            accounts = self.sj.login(
                api_key=self.api_key,
                secret_key=self.secret_key,
                person_id=person_id,
                passwd=passwd,
                fetch_contract=fetch_contract
            )
            
            self.is_connected = True
            self.login_time = datetime.now()
            self.logger.info(f"登入成功！帳戶資訊: {accounts}")
            
            # 若有下載合約檔，則儲存到 contracts 屬性
            if fetch_contract:
                self.contracts = self.sj.Contracts
                self.logger.info("商品檔已載入完成")
            
            # 如果提供憑證，則啟用下單功能
            if ca_path and ca_passwd:
                self._activate_ca(ca_path, ca_passwd)
            
            return True
            
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"登入失敗: {str(e)}")
            raise ConnectionError(f"Shioaji 登入失敗: {str(e)}")
    
    def _activate_ca(self, ca_path: str, ca_passwd: str) -> None:
        """
        啟用憑證認證
        
        啟用憑證以取得下單權限。此為私有方法，在 login 方法中調用。
        
        Args:
            ca_path (str): 憑證檔案路徑
            ca_passwd (str): 憑證密碼
            
        Raises:
            FileNotFoundError: 當憑證檔案不存在時拋出
            ValueError: 當憑證密碼錯誤時拋出
        """
        try:
            self.logger.info("開始啟用憑證...")
            self.sj.activate_ca(
                ca_path=ca_path,
                ca_passwd=ca_passwd,
                person_id=self.sj.person_id
            )
            self.logger.info("憑證啟用成功，已取得下單權限")
        except Exception as e:
            self.logger.error(f"憑證啟用失敗: {str(e)}")
            raise
    
    def logout(self) -> bool:
        """
        登出 Shioaji API
        
        結束與永豐金證券的連線，釋放資源。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> # ... 進行交易操作 ...
            >>> connector.logout()
            
        Note:
            - 登出後需要重新登入才能繼續使用
            - 建議在程式結束前呼叫此方法以正常釋放連線
        """
        if self.sj is None:
            self.logger.warning("API 未初始化，無需登出")
            return False
        
        if not self.is_connected:
            self.logger.warning("尚未登入，無需登出")
            return False
        
        try:
            self.logger.info("開始登出 Shioaji API...")
            self.sj.logout()
            self.is_connected = False
            self.logger.info("登出成功")
            return True
        except Exception as e:
            self.logger.error(f"登出失敗: {str(e)}")
            return False
    
    def get_contracts(self) -> Optional[Any]:
        """
        取得所有商品檔
        
        返回包含所有可交易商品的 Contracts 物件，包括股票、期貨、選擇權等。
        
        Returns:
            Optional[Any]: Contracts 物件，若尚未登入或未下載則返回 None
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> contracts = connector.get_contracts()
            >>> # 取得所有股票合約
            >>> stocks = contracts.Stocks
            >>> # 取得所有期貨合約
            >>> futures = contracts.Futures
            
        Note:
            - 需要先登入才能取得商品檔
            - 登入時需設定 fetch_contract=True (預設值)
            - Contracts 物件包含: Stocks, Futures, Options 等屬性
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if self.contracts is None:
            self.logger.warning("商品檔未載入，請在登入時設定 fetch_contract=True")
        
        return self.contracts
    
    def search_stock(self, keyword: str) -> List[Any]:
        """
        搜尋股票商品
        
        根據關鍵字搜尋股票商品，可使用股票代碼或名稱進行搜尋。
        
        Args:
            keyword (str): 搜尋關鍵字（股票代碼或名稱）
            
        Returns:
            List[Any]: 符合條件的股票合約列表
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當商品檔未載入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> # 使用股票代碼搜尋
            >>> result = connector.search_stock("2330")
            >>> print(result[0].code, result[0].name)  # 2330 台積電
            >>> 
            >>> # 使用股票名稱搜尋
            >>> result = connector.search_stock("台積電")
            
        Note:
            - 搜尋不區分大小寫
            - 支援部分匹配
            - 返回的是合約物件列表
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if self.contracts is None:
            raise ValueError("商品檔未載入，請確保登入時設定 fetch_contract=True")
        
        try:
            results = []
            stocks = self.contracts.Stocks
            
            # 搜尋股票代碼或名稱
            for stock in stocks:
                if keyword.upper() in stock.code.upper() or keyword in stock.name:
                    results.append(stock)
            
            self.logger.info(f"搜尋關鍵字 '{keyword}' 找到 {len(results)} 筆股票資料")
            return results
            
        except Exception as e:
            self.logger.error(f"搜尋股票失敗: {str(e)}")
            raise
    
    def get_stock_by_code(self, code: str) -> Optional[Any]:
        """
        根據股票代碼取得股票合約
        
        精確查詢特定股票代碼的合約資料。
        
        Args:
            code (str): 股票代碼（例如："2330"）
            
        Returns:
            Optional[Any]: 股票合約物件，若找不到則返回 None
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當商品檔未載入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> if stock:
            >>>     print(f"股票: {stock.code} {stock.name}")
            >>>     print(f"交易所: {stock.exchange}")
            
        Note:
            - 使用精確匹配
            - 股票代碼需要完整且正確
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if self.contracts is None:
            raise ValueError("商品檔未載入，請確保登入時設定 fetch_contract=True")
        
        try:
            stocks = self.contracts.Stocks
            
            # 使用字典查詢 (Shioaji 支援)
            if hasattr(stocks, code):
                stock = getattr(stocks, code)
                self.logger.info(f"找到股票: {code} {stock.name}")
                return stock
            
            # 如果使用屬性查詢失敗，嘗試遍歷
            for stock in stocks:
                if stock.code == code:
                    self.logger.info(f"找到股票: {code} {stock.name}")
                    return stock
            
            self.logger.warning(f"找不到股票代碼: {code}")
            return None
            
        except Exception as e:
            self.logger.error(f"取得股票失敗: {str(e)}")
            raise
    
    def search_futures(self, keyword: str) -> List[Any]:
        """
        搜尋期貨商品
        
        根據關鍵字搜尋期貨商品，可使用商品代碼或名稱進行搜尋。
        
        Args:
            keyword (str): 搜尋關鍵字（期貨代碼或名稱）
            
        Returns:
            List[Any]: 符合條件的期貨合約列表
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當商品檔未載入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> # 搜尋台指期
            >>> result = connector.search_futures("TX")
            >>> for contract in result:
            >>>     print(contract.code, contract.name)
            
        Note:
            - 期貨商品包含各種到期月份的合約
            - 搜尋結果可能包含多個不同月份的合約
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if self.contracts is None:
            raise ValueError("商品檔未載入，請確保登入時設定 fetch_contract=True")
        
        try:
            results = []
            futures = self.contracts.Futures
            
            # 搜尋期貨代碼或名稱
            for future in futures:
                if keyword.upper() in future.code.upper() or keyword in future.name:
                    results.append(future)
            
            self.logger.info(f"搜尋關鍵字 '{keyword}' 找到 {len(results)} 筆期貨資料")
            return results
            
        except Exception as e:
            self.logger.error(f"搜尋期貨失敗: {str(e)}")
            raise
    
    def get_contracts_summary(self) -> Dict[str, int]:
        """
        取得商品檔統計摘要
        
        統計各類商品的數量，提供商品檔的概覽資訊。
        
        Returns:
            Dict[str, int]: 包含各類商品數量的字典
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當商品檔未載入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> summary = connector.get_contracts_summary()
            >>> print(summary)
            {
                'stocks': 1800,
                'futures': 150,
                'options': 500
            }
            
        Note:
            - 數量會依市場狀況而變動
            - 包含所有上市、上櫃商品
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if self.contracts is None:
            raise ValueError("商品檔未載入，請確保登入時設定 fetch_contract=True")
        
        try:
            summary = {}
            
            # 計算股票數量
            if hasattr(self.contracts, 'Stocks'):
                summary['stocks'] = len(list(self.contracts.Stocks))
            
            # 計算期貨數量
            if hasattr(self.contracts, 'Futures'):
                summary['futures'] = len(list(self.contracts.Futures))
            
            # 計算選擇權數量
            if hasattr(self.contracts, 'Options'):
                summary['options'] = len(list(self.contracts.Options))
            
            self.logger.info(f"商品檔統計: {summary}")
            return summary
            
        except Exception as e:
            self.logger.error(f"取得商品檔統計失敗: {str(e)}")
            raise
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        取得連線狀態資訊
        
        Returns:
            Dict[str, Any]: 包含連線狀態的字典，包括:
                - is_connected (bool): 是否已連線
                - login_time (str): 登入時間
                - simulation (bool): 是否為模擬環境
                - api_initialized (bool): API 是否已初始化
                
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> status = connector.get_connection_status()
            >>> print(status)
            {
                'is_connected': True,
                'login_time': '2025-10-06 10:30:00',
                'simulation': False,
                'api_initialized': True
            }
        """
        return {
            'is_connected': self.is_connected,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S') if self.login_time else None,
            'simulation': self.simulation,
            'api_initialized': self.sj is not None,
            'contracts_loaded': self.contracts is not None,
            'subscribed_count': len(self.subscribed_contracts),
            'callback_count': sum(len(cbs) for cbs in self.quote_callbacks.values()),
            'orders_count': len(self.orders_history),
            'deals_count': len(self.deals_history),
            'order_updates_count': len(self.order_updates)
        }
    
    def __enter__(self):
        """
        支援 context manager (with 語句)
        
        Examples:
            >>> with ShioajiConnector() as connector:
            >>>     connector.login(person_id="A123456789", passwd="password")
            >>>     # 進行交易操作
            >>>     # 離開 with 區塊時自動登出
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出 context manager 時自動登出
        """
        if self.is_connected:
            self.logout()
        return False
    
    def subscribe_quote(self, contract: Any, quote_type: str = "tick") -> bool:
        """
        訂閱即時報價
        
        訂閱特定商品的即時報價，支援逐筆（tick）和快照（bidask）兩種類型。
        
        Args:
            contract (Any): 商品合約物件（從 contracts 取得）
            quote_type (str, optional): 報價類型，"tick" 或 "bidask"。預設為 "tick"。
            
        Returns:
            bool: 訂閱成功返回 True，失敗返回 False
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當報價類型不正確時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> 
            >>> # 訂閱逐筆報價
            >>> connector.subscribe_quote(stock, "tick")
            >>> 
            >>> # 訂閱五檔報價
            >>> connector.subscribe_quote(stock, "bidask")
            
        Note:
            - 需要先登入才能訂閱
            - tick: 逐筆成交報價
            - bidask: 五檔委買委賣報價
            - 訂閱後會自動呼叫已註冊的 callback 函數
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if quote_type not in ["tick", "bidask"]:
            raise ValueError("報價類型必須是 'tick' 或 'bidask'")
        
        try:
            # 訂閱報價
            if quote_type == "tick":
                self.sj.quote.subscribe(
                    contract,
                    quote_type=sj.constant.QuoteType.Tick,
                    version=sj.constant.QuoteVersion.v1
                )
            else:  # bidask
                self.sj.quote.subscribe(
                    contract,
                    quote_type=sj.constant.QuoteType.BidAsk,
                    version=sj.constant.QuoteVersion.v1
                )
            
            # 記錄已訂閱的商品
            self.subscribed_contracts[contract.code] = contract
            self.logger.info(f"訂閱報價成功: {contract.code} {contract.name} (類型: {quote_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"訂閱報價失敗: {str(e)}")
            return False
    
    def unsubscribe_quote(self, contract: Any) -> bool:
        """
        取消訂閱即時報價
        
        取消訂閱特定商品的即時報價。
        
        Args:
            contract (Any): 商品合約物件
            
        Returns:
            bool: 取消訂閱成功返回 True，失敗返回 False
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.subscribe_quote(stock)
            >>> # ... 接收報價 ...
            >>> connector.unsubscribe_quote(stock)
            
        Note:
            - 取消訂閱後將不再接收該商品的報價更新
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        try:
            self.sj.quote.unsubscribe(
                contract,
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            
            # 移除訂閱記錄
            if contract.code in self.subscribed_contracts:
                del self.subscribed_contracts[contract.code]
            
            self.logger.info(f"取消訂閱報價: {contract.code} {contract.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消訂閱報價失敗: {str(e)}")
            return False
    
    def set_quote_callback(self, callback: Callable, event_type: str = "tick") -> None:
        """
        設定報價回調函數
        
        註冊一個回調函數，當接收到報價更新時會被呼叫。
        支援多個 callback 函數同時註冊。
        
        Args:
            callback (Callable): 回調函數，接收兩個參數：
                - topic (str): 報價主題
                - quote (dict): 報價資料
            event_type (str, optional): 事件類型，"tick" 或 "bidask"。預設為 "tick"。
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當 callback 不是可呼叫的函數時拋出
            
        Examples:
            >>> def my_quote_handler(topic, quote):
            >>>     print(f"商品: {topic}")
            >>>     print(f"價格: {quote['close']}")
            >>>     print(f"成交量: {quote['volume']}")
            >>> 
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_quote_callback(my_quote_handler, "tick")
            >>> 
            >>> # 訂閱股票後，會自動呼叫 my_quote_handler
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.subscribe_quote(stock)
            
        Note:
            - callback 函數會在報價更新時被呼叫
            - 支援註冊多個 callback 函數
            - callback 應該快速執行，避免阻塞主程序
            - quote 資料結構依報價類型而異
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        # 註冊 callback
        self.quote_callbacks[event_type].append(callback)
        
        # 設定 Shioaji 的 callback
        if event_type == "tick":
            @self.sj.on_tick_stk_v1()
            def quote_callback(exchange, tick):
                """內部 tick 報價處理函數"""
                try:
                    # 更新最新報價資料
                    code = tick['code']
                    self.quote_data[code] = tick
                    
                    # 呼叫所有註冊的 callback
                    for cb in self.quote_callbacks['tick']:
                        try:
                            cb(f"{exchange}/{code}", tick)
                        except Exception as e:
                            self.logger.error(f"執行 callback 時發生錯誤: {str(e)}")
                except Exception as e:
                    self.logger.error(f"處理 tick 報價時發生錯誤: {str(e)}")
        
        elif event_type == "bidask":
            @self.sj.on_bidask_stk_v1()
            def bidask_callback(exchange, bidask):
                """內部 bidask 報價處理函數"""
                try:
                    # 更新最新報價資料
                    code = bidask['code']
                    self.quote_data[code] = bidask
                    
                    # 呼叫所有註冊的 callback
                    for cb in self.quote_callbacks['bidask']:
                        try:
                            cb(f"{exchange}/{code}", bidask)
                        except Exception as e:
                            self.logger.error(f"執行 callback 時發生錯誤: {str(e)}")
                except Exception as e:
                    self.logger.error(f"處理 bidask 報價時發生錯誤: {str(e)}")
        
        self.logger.info(f"已註冊 {event_type} 報價回調函數")
    
    def get_subscribed_contracts(self) -> Dict[str, Any]:
        """
        取得已訂閱的商品列表
        
        Returns:
            Dict[str, Any]: 已訂閱的商品字典 {code: contract}
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.subscribe_quote(stock)
            >>> 
            >>> subscribed = connector.get_subscribed_contracts()
            >>> print(f"已訂閱 {len(subscribed)} 個商品")
            >>> for code, contract in subscribed.items():
            >>>     print(f"{code}: {contract.name}")
        """
        return self.subscribed_contracts.copy()
    
    def get_latest_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """
        取得最新報價資料
        
        取得指定商品代碼的最新報價快照。
        
        Args:
            code (str): 商品代碼
            
        Returns:
            Optional[Dict[str, Any]]: 最新報價資料，若無資料則返回 None
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.subscribe_quote(stock)
            >>> 
            >>> # 等待接收報價...
            >>> import time
            >>> time.sleep(2)
            >>> 
            >>> quote = connector.get_latest_quote("2330")
            >>> if quote:
            >>>     print(f"最新價格: {quote['close']}")
            >>>     print(f"成交量: {quote['volume']}")
            
        Note:
            - 需要先訂閱該商品才能取得報價
            - 返回的是快照資料，不是即時串流
        """
        return self.quote_data.get(code)
    
    def clear_quote_callbacks(self, event_type: Optional[str] = None) -> None:
        """
        清除報價回調函數
        
        清除已註冊的回調函數。
        
        Args:
            event_type (str, optional): 要清除的事件類型，若為 None 則清除所有。
                預設為 None。
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_quote_callback(my_handler)
            >>> 
            >>> # 清除特定類型的 callback
            >>> connector.clear_quote_callbacks("tick")
            >>> 
            >>> # 清除所有 callback
            >>> connector.clear_quote_callbacks()
        """
        if event_type:
            self.quote_callbacks[event_type].clear()
            self.logger.info(f"已清除 {event_type} 類型的回調函數")
        else:
            self.quote_callbacks.clear()
            self.logger.info("已清除所有回調函數")
    
    def place_order(
        self,
        contract: Any,
        action: str,
        price: float,
        quantity: int,
        order_type: str = "ROD",
        price_type: str = "LMT",
        odd_lot: bool = False
    ) -> Optional[Any]:
        """
        下單買賣股票
        
        執行證券下單操作，支援整股和盤中零股下單。
        
        Args:
            contract (Any): 商品合約物件（從 contracts 取得）
            action (str): 買賣方向，"Buy" 或 "Sell"
            price (float): 委託價格（市價單請設為 0）
            quantity (int): 委託數量（股）
            order_type (str, optional): 委託類型，"ROD"、"IOC"、"FOK"。預設為 "ROD"。
            price_type (str, optional): 價格類型，"LMT"(限價)、"MKT"(市價)。預設為 "LMT"。
            odd_lot (bool, optional): 是否為零股交易。預設為 False。
            
        Returns:
            Optional[Any]: 下單結果物件，包含訂單資訊，若失敗則返回 None
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當參數不正確時拋出
            PermissionError: 當未啟用憑證時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(
            >>>     person_id="A123456789",
            >>>     passwd="password",
            >>>     ca_path="/path/to/cert.pfx",
            >>>     ca_passwd="cert_password"
            >>> )
            >>> 
            >>> # 買入整股（限價單）
            >>> stock = connector.get_stock_by_code("2330")
            >>> order = connector.place_order(
            >>>     contract=stock,
            >>>     action="Buy",
            >>>     price=600.0,
            >>>     quantity=1000,
            >>>     order_type="ROD",
            >>>     price_type="LMT"
            >>> )
            >>> 
            >>> # 買入零股
            >>> order = connector.place_order(
            >>>     contract=stock,
            >>>     action="Buy",
            >>>     price=600.0,
            >>>     quantity=100,
            >>>     odd_lot=True
            >>> )
            >>> 
            >>> # 市價買入
            >>> order = connector.place_order(
            >>>     contract=stock,
            >>>     action="Buy",
            >>>     price=0,
            >>>     quantity=1000,
            >>>     price_type="MKT"
            >>> )
            
        Note:
            - 需要先登入並啟用憑證才能下單
            - ROD: Rest of Day (整日有效)
            - IOC: Immediate or Cancel (立即成交否則取消)
            - FOK: Fill or Kill (全部成交否則取消)
            - LMT: Limit (限價)
            - MKT: Market (市價)
            - 整股交易數量必須為 1000 的倍數
            - 零股交易數量必須小於 1000
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        # 驗證參數
        if action not in ["Buy", "Sell"]:
            raise ValueError("action 必須是 'Buy' 或 'Sell'")
        
        if order_type not in ["ROD", "IOC", "FOK"]:
            raise ValueError("order_type 必須是 'ROD'、'IOC' 或 'FOK'")
        
        if price_type not in ["LMT", "MKT"]:
            raise ValueError("price_type 必須是 'LMT' 或 'MKT'")
        
        if quantity <= 0:
            raise ValueError("數量必須大於 0")
        
        # 檢查整股/零股數量
        if not odd_lot and quantity % 1000 != 0:
            raise ValueError("整股交易數量必須為 1000 的倍數")
        
        if odd_lot and quantity >= 1000:
            raise ValueError("零股交易數量必須小於 1000")
        
        try:
            # 建立訂單物件
            order = sj.Order(
                price=price,
                quantity=quantity,
                action=sj.constant.Action.Buy if action == "Buy" else sj.constant.Action.Sell,
                price_type=sj.constant.StockPriceType.LMT if price_type == "LMT" else sj.constant.StockPriceType.MKT,
                order_type=self._get_order_type(order_type),
                order_lot=sj.constant.StockOrderLot.IntradayOdd if odd_lot else sj.constant.TFTOrderLot.Common,
                account=self.sj.stock_account
            )
            
            # 執行下單
            trade = self.sj.place_order(contract, order)
            
            # 記錄下單歷史
            order_info = {
                'contract': contract,
                'action': action,
                'price': price,
                'quantity': quantity,
                'order_type': order_type,
                'price_type': price_type,
                'odd_lot': odd_lot,
                'trade': trade,
                'timestamp': datetime.now()
            }
            self.orders_history.append(order_info)
            
            self.logger.info(
                f"下單成功: {action} {contract.code} {contract.name}, "
                f"價格: {price}, 數量: {quantity}, "
                f"類型: {'零股' if odd_lot else '整股'}"
            )
            
            return trade
            
        except Exception as e:
            self.logger.error(f"下單失敗: {str(e)}")
            return None
    
    def _get_order_type(self, order_type: str) -> Any:
        """
        取得委託類型常數
        
        將字串型的委託類型轉換為 Shioaji 的常數。
        
        Args:
            order_type (str): 委託類型字串
            
        Returns:
            Any: Shioaji 委託類型常數
        """
        order_type_map = {
            "ROD": sj.constant.OrderType.ROD,
            "IOC": sj.constant.OrderType.IOC,
            "FOK": sj.constant.OrderType.FOK
        }
        return order_type_map.get(order_type, sj.constant.OrderType.ROD)
    
    def cancel_order(self, trade: Any) -> bool:
        """
        取消訂單
        
        取消已下的訂單。
        
        Args:
            trade (Any): 下單時返回的交易物件
            
        Returns:
            bool: 取消成功返回 True，失敗返回 False
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> trade = connector.place_order(stock, "Buy", 600.0, 1000)
            >>> 
            >>> # 取消訂單
            >>> success = connector.cancel_order(trade)
            >>> if success:
            >>>     print("訂單已取消")
            
        Note:
            - 只能取消尚未成交的訂單
            - 部分成交的訂單可以取消未成交部分
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        try:
            self.sj.cancel_order(trade)
            self.logger.info(f"取消訂單成功: {trade}")
            return True
        except Exception as e:
            self.logger.error(f"取消訂單失敗: {str(e)}")
            return False
    
    def update_order(self, trade: Any, price: float, quantity: int) -> Optional[Any]:
        """
        修改訂單
        
        修改已下訂單的價格和數量。
        
        Args:
            trade (Any): 下單時返回的交易物件
            price (float): 新的委託價格
            quantity (int): 新的委託數量
            
        Returns:
            Optional[Any]: 修改後的交易物件，失敗返回 None
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當參數不正確時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> trade = connector.place_order(stock, "Buy", 600.0, 1000)
            >>> 
            >>> # 修改訂單價格和數量
            >>> new_trade = connector.update_order(trade, 605.0, 2000)
            
        Note:
            - 只能修改尚未成交的訂單
            - 修改訂單相當於取消舊單再下新單
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if price <= 0 or quantity <= 0:
            raise ValueError("價格和數量必須大於 0")
        
        try:
            new_trade = self.sj.update_order(trade, price=price, qty=quantity)
            self.logger.info(f"修改訂單成功: 價格={price}, 數量={quantity}")
            return new_trade
        except Exception as e:
            self.logger.error(f"修改訂單失敗: {str(e)}")
            return None
    
    def get_account_balance(self) -> Optional[Any]:
        """
        取得帳戶餘額資訊
        
        查詢證券帳戶的餘額資訊，包含可用餘額、帳戶總額、已實現損益等。
        
        Returns:
            Optional[Any]: 帳戶餘額物件，包含以下屬性：
                - account_balance: 帳戶餘額
                - available_balance: 可用餘額
                - T_money: T日資金
                - T1_money: T+1日資金
                - T2_money: T+2日資金
                如果查詢失敗則返回 None
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> balance = connector.get_account_balance()
            >>> 
            >>> if balance:
            >>>     print(f"可用餘額: {balance.available_balance}")
            >>>     print(f"帳戶總額: {balance.account_balance}")
            
        Note:
            - 需要先登入才能查詢
            - 返回的餘額為即時資料
            - T日/T+1日/T+2日資金代表不同交割日的可用金額
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        try:
            balance = self.sj.account_balance()
            self.logger.info("查詢帳戶餘額成功")
            return balance
        except Exception as e:
            self.logger.error(f"查詢帳戶餘額失敗: {str(e)}")
            return None
    
    def get_account_balance_summary(self) -> Dict[str, Any]:
        """
        取得帳戶餘額摘要
        
        以字典格式返回帳戶餘額的關鍵資訊，便於顯示和處理。
        
        Returns:
            Dict[str, Any]: 帳戶餘額摘要字典
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> summary = connector.get_account_balance_summary()
            >>> 
            >>> print(f"可用餘額: {summary['available_balance']:,.0f} 元")
            >>> print(f"帳戶總額: {summary['account_balance']:,.0f} 元")
            >>> print(f"T日資金: {summary['T_money']:,.0f} 元")
            
        Note:
            - 所有金額單位為新台幣
            - 如果查詢失敗，各欄位值為 0
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        balance = self.get_account_balance()
        
        if balance is None:
            return {
                'account_balance': 0,
                'available_balance': 0,
                'T_money': 0,
                'T1_money': 0,
                'T2_money': 0,
                'query_time': datetime.now()
            }
        
        try:
            return {
                'account_balance': getattr(balance, 'account_balance', 0),
                'available_balance': getattr(balance, 'available_balance', 0),
                'T_money': getattr(balance, 'T_money', 0),
                'T1_money': getattr(balance, 'T1_money', 0),
                'T2_money': getattr(balance, 'T2_money', 0),
                'query_time': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"解析帳戶餘額失敗: {str(e)}")
            return {
                'account_balance': 0,
                'available_balance': 0,
                'T_money': 0,
                'T1_money': 0,
                'T2_money': 0,
                'query_time': datetime.now()
            }
    
    def list_positions(self, with_detail: bool = False) -> List[Any]:
        """
        查詢持股明細
        
        取得目前的持股明細，可選擇是否包含詳細資訊。
        
        Args:
            with_detail (bool, optional): 是否返回詳細資訊字典。預設為 False。
        
        Returns:
            List[Any]: 持股明細列表。如果 with_detail=True，返回字典列表
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> 
            >>> # 基本查詢
            >>> positions = connector.list_positions()
            >>> for pos in positions:
            >>>     print(f"商品: {pos.code}, 數量: {pos.quantity}")
            >>> 
            >>> # 詳細查詢
            >>> positions = connector.list_positions(with_detail=True)
            >>> for pos in positions:
            >>>     print(f"商品: {pos['code']}")
            >>>     print(f"數量: {pos['quantity']}")
            >>>     print(f"成本價: {pos['price']}")
            >>>     print(f"現價: {pos['last_price']}")
            >>>     print(f"損益: {pos['pnl']}")
            
        Note:
            - 需要先登入才能查詢
            - 返回的是即時持股資料
            - with_detail=True 時會將持股資訊轉換為易讀的字典格式
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        try:
            positions = self.sj.list_positions()
            self.logger.info(f"查詢持股明細成功，共 {len(positions)} 筆")
            
            if not with_detail:
                return positions
            
            # 轉換為詳細資訊字典
            detailed_positions = []
            for pos in positions:
                try:
                    detail = {
                        'code': getattr(pos, 'code', ''),
                        'quantity': getattr(pos, 'quantity', 0),
                        'price': getattr(pos, 'price', 0),
                        'last_price': getattr(pos, 'last_price', 0),
                        'pnl': getattr(pos, 'pnl', 0),
                        'yd_quantity': getattr(pos, 'yd_quantity', 0),
                        'cond': getattr(pos, 'cond', ''),
                        'direction': getattr(pos, 'direction', '')
                    }
                    detailed_positions.append(detail)
                except Exception as e:
                    self.logger.warning(f"解析持股資訊失敗: {str(e)}")
                    continue
            
            return detailed_positions
            
        except Exception as e:
            self.logger.error(f"查詢持股明細失敗: {str(e)}")
            return []
    
    def get_positions_summary(self) -> Dict[str, Any]:
        """
        取得持股摘要統計
        
        統計持股的總體資訊，包括持股數量、總市值、總損益等。
        
        Returns:
            Dict[str, Any]: 持股摘要字典
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> summary = connector.get_positions_summary()
            >>> 
            >>> print(f"持股檔數: {summary['total_stocks']} 檔")
            >>> print(f"總市值: {summary['total_value']:,.0f} 元")
            >>> print(f"總損益: {summary['total_pnl']:,.0f} 元")
            >>> print(f"報酬率: {summary['return_rate']:.2f}%")
            
        Note:
            - 總市值 = Σ(現價 × 數量)
            - 總損益 = Σ(現價 - 成本價) × 數量
            - 報酬率 = 總損益 / 總成本 × 100%
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        positions = self.list_positions(with_detail=True)
        
        if not positions:
            return {
                'total_stocks': 0,
                'total_quantity': 0,
                'total_cost': 0,
                'total_value': 0,
                'total_pnl': 0,
                'return_rate': 0,
                'query_time': datetime.now()
            }
        
        total_quantity = 0
        total_cost = 0
        total_value = 0
        total_pnl = 0
        
        for pos in positions:
            quantity = pos.get('quantity', 0)
            price = pos.get('price', 0)
            last_price = pos.get('last_price', 0)
            
            total_quantity += quantity
            total_cost += price * quantity
            total_value += last_price * quantity
            total_pnl += (last_price - price) * quantity
        
        return_rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_stocks': len(positions),
            'total_quantity': total_quantity,
            'total_cost': total_cost,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'return_rate': return_rate,
            'query_time': datetime.now()
        }
    
    def list_trades(self) -> List[Any]:
        """
        查詢今日委託明細
        
        取得今日所有的委託記錄。
        
        Returns:
            List[Any]: 委託明細列表
            
        Raises:
            ConnectionError: 當尚未登入時拋出
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> trades = connector.list_trades()
            >>> 
            >>> for trade in trades:
            >>>     print(f"訂單編號: {trade.order.id}")
            >>>     print(f"商品: {trade.contract.code}")
            >>>     print(f"狀態: {trade.status.status}")
            
        Note:
            - 需要先登入才能查詢
            - 只显示當日的委託記錄
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        try:
            trades = self.sj.list_trades()
            self.logger.info(f"查詢委託明細成功，共 {len(trades)} 筆")
            return trades
        except Exception as e:
            self.logger.error(f"查詢委託明細失敗: {str(e)}")
            return []
    
    def set_order_callback(self, callback: Callable) -> None:
        """
        設定訂單狀態更新回調函數
        
        註冊一個回調函數，當訂單狀態更新時會被呼叫。
        支援多個 callback 函數同時註冊。
        
        Args:
            callback (Callable): 回調函數，接收一個參數：
                - stat (OrderState): 訂單狀態物件
                
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當 callback 不是可呼叫的函數時拋出
            
        Examples:
            >>> def order_status_handler(stat):
            >>>     print(f"訂單狀態更新: {stat.status}")
            >>>     print(f"訂單編號: {stat.order_id}")
            >>>     print(f"委託價格: {stat.order.price}")
            >>>     print(f"委託數量: {stat.order.quantity}")
            >>>     print(f"已成交數量: {stat.deal_quantity}")
            >>> 
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_order_callback(order_status_handler)
            >>> 
            >>> # 下單後會自動觸發 callback
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.place_order(stock, "Buy", 600.0, 1000)
            
        Note:
            - 訂單狀態包括：已委託、部分成交、全部成交、已取消等
            - callback 會在訂單狀態改變時被呼叫
            - 支援註冊多個 callback 函數
            - callback 應該快速執行，避免阻塞主程序
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        # 註冊 callback
        self.order_update_callbacks.append(callback)
        
        # 設定 Shioaji 的 order callback
        @self.sj.on_order_status()
        def order_callback(stat):
            """內部訂單狀態處理函數"""
            try:
                # 記錄訂單更新
                update_info = {
                    'status': stat.status,
                    'order_id': stat.order_id,
                    'order': stat.order,
                    'deal_quantity': stat.deal_quantity,
                    'timestamp': datetime.now()
                }
                self.order_updates.append(update_info)
                
                # 呼叫所有註冊的 callback
                for cb in self.order_update_callbacks:
                    try:
                        cb(stat)
                    except Exception as e:
                        self.logger.error(f"執行 order callback 時發生錯誤: {str(e)}")
            except Exception as e:
                self.logger.error(f"處理訂單狀態時發生錯誤: {str(e)}")
        
        self.logger.info("已註冊訂單狀態更新回調函數")
    
    def set_deal_callback(self, callback: Callable) -> None:
        """
        設定成交回報回調函數
        
        註冊一個回調函數，當訂單成交時會被呼叫。
        支援多個 callback 函數同時註冊。
        
        Args:
            callback (Callable): 回調函數，接收一個參數：
                - deal (Deal): 成交回報物件
                
        Raises:
            ConnectionError: 當尚未登入時拋出
            ValueError: 當 callback 不是可呼叫的函數時拋出
            
        Examples:
            >>> def deal_handler(deal):
            >>>     print(f"成交通知: {deal.code}")
            >>>     print(f"成交價格: {deal.price}")
            >>>     print(f"成交數量: {deal.quantity}")
            >>>     print(f"成交時間: {deal.ts}")
            >>> 
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_deal_callback(deal_handler)
            >>> 
            >>> # 下單成交後會自動觸發 callback
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.place_order(stock, "Buy", 600.0, 1000)
            
        Note:
            - 成交回報會在訂單成交時觸發
            - 部分成交會觸發多次 callback
            - 支援註冊多個 callback 函數
            - callback 應該快速執行，避免阻塞主程序
        """
        if not self.is_connected:
            raise ConnectionError("尚未登入，請先執行 login()")
        
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        # 註冊 callback
        self.deal_callbacks.append(callback)
        
        # 設定 Shioaji 的 deal callback
        @self.sj.on_deal()
        def deal_callback(deal):
            """內部成交回報處理函數"""
            try:
                # 記錄成交資料
                deal_info = {
                    'code': deal.code,
                    'price': deal.price,
                    'quantity': deal.quantity,
                    'ts': deal.ts,
                    'order_id': deal.order_id,
                    'seqno': deal.seqno,
                    'timestamp': datetime.now()
                }
                self.deals_history.append(deal_info)
                
                # 呼叫所有註冊的 callback
                for cb in self.deal_callbacks:
                    try:
                        cb(deal)
                    except Exception as e:
                        self.logger.error(f"執行 deal callback 時發生錯誤: {str(e)}")
            except Exception as e:
                self.logger.error(f"處理成交回報時發生錯誤: {str(e)}")
        
        self.logger.info("已註冊成交回報回調函數")
    
    def get_deals_history(self) -> List[Dict[str, Any]]:
        """
        取得成交歷史記錄
        
        返回本次連線期間所有的成交記錄。
        
        Returns:
            List[Dict[str, Any]]: 成交歷史列表
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_deal_callback(lambda deal: None)
            >>> 
            >>> # 執行一些交易...
            >>> 
            >>> deals = connector.get_deals_history()
            >>> for deal in deals:
            >>>     print(f"商品: {deal['code']}")
            >>>     print(f"價格: {deal['price']}")
            >>>     print(f"數量: {deal['quantity']}")
            >>>     print(f"時間: {deal['ts']}")
            
        Note:
            - 只記錄本次連線期間的成交
            - 需要先註冊 deal callback 才會記錄
            - 登出後歷史記錄會被清除
        """
        return self.deals_history.copy()
    
    def get_order_updates(self) -> List[Dict[str, Any]]:
        """
        取得訂單更新記錄
        
        返回本次連線期間所有的訂單狀態更新記錄（委託回報）。
        
        Returns:
            List[Dict[str, Any]]: 訂單更新列表
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_order_callback(lambda stat: None)
            >>> 
            >>> # 執行一些交易...
            >>> 
            >>> updates = connector.get_order_updates()
            >>> for update in updates:
            >>>     print(f"訂單編號: {update['order_id']}")
            >>>     print(f"狀態: {update['status']}")
            >>>     print(f"已成交數量: {update['deal_quantity']}")
            
        Note:
            - 只記錄本次連線期間的更新
            - 需要先註冊 order callback 才會記錄
            - 登出後歷史記錄會被清除
        """
        return self.order_updates.copy()
    
    def get_order_update_by_id(self, order_id: str) -> List[Dict[str, Any]]:
        """
        根據訂單編號取得委託回報記錄
        
        查詢特定訂單的所有狀態更新記錄。
        
        Args:
            order_id (str): 訂單編號
            
        Returns:
            List[Dict[str, Any]]: 該訂單的所有更新記錄
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_order_callback(lambda stat: None)
            >>> 
            >>> # 下單
            >>> stock = connector.get_stock_by_code("2330")
            >>> trade = connector.place_order(stock, "Buy", 600.0, 1000)
            >>> 
            >>> # 查詢該訂單的所有狀態更新
            >>> updates = connector.get_order_update_by_id(trade.order.id)
            >>> for update in updates:
            >>>     print(f"時間: {update['timestamp']}")
            >>>     print(f"狀態: {update['status']}")
            
        Note:
            - 返回該訂單的所有歷史狀態變更
            - 按時間順序排列
        """
        return [
            update for update in self.order_updates 
            if update.get('order_id') == order_id
        ]
    
    def get_order_updates_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        根據狀態取得委託回報記錄
        
        查詢特定狀態的所有訂單更新記錄。
        
        Args:
            status (str): 訂單狀態，例如 "Filled", "Cancelled", "Submitted" 等
            
        Returns:
            List[Dict[str, Any]]: 符合狀態的更新記錄列表
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_order_callback(lambda stat: None)
            >>> 
            >>> # 執行一些交易...
            >>> 
            >>> # 查詢所有已成交的訂單
            >>> filled_orders = connector.get_order_updates_by_status("Filled")
            >>> print(f"已成交訂單: {len(filled_orders)} 筆")
            >>> 
            >>> # 查詢所有已取消的訂單
            >>> cancelled_orders = connector.get_order_updates_by_status("Cancelled")
            >>> print(f"已取消訂單: {len(cancelled_orders)} 筆")
            
        Note:
            - 常見狀態: Submitted (已委託), Filled (全部成交), 
              Filling (部分成交), Cancelled (已取消), Failed (失敗)
            - 狀態值區分大小寫
        """
        return [
            update for update in self.order_updates 
            if update.get('status') == status
        ]
    
    def get_order_updates_summary(self) -> Dict[str, int]:
        """
        取得委託回報統計摘要
        
        統計各種訂單狀態的數量。
        
        Returns:
            Dict[str, int]: 各狀態的訂單數量統計
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> connector.set_order_callback(lambda stat: None)
            >>> 
            >>> # 執行一些交易...
            >>> 
            >>> summary = connector.get_order_updates_summary()
            >>> print("訂單狀態統計:")
            >>> for status, count in summary.items():
            >>>     print(f"  {status}: {count} 筆")
            
        Note:
            - 統計所有接收到的委託回報
            - 同一訂單可能有多個狀態更新
        """
        from collections import Counter
        statuses = [update.get('status') for update in self.order_updates]
        return dict(Counter(statuses))
    
    def clear_order_update_callbacks(self) -> None:
        """
        清除所有委託回報回調函數
        
        移除所有已註冊的訂單狀態更新回調函數。
        
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> 
            >>> # 註冊回調
            >>> connector.set_order_callback(lambda stat: print("訂單更新"))
            >>> 
            >>> # 清除所有回調
            >>> connector.clear_order_update_callbacks()
            >>> print("✅ 已清除所有委託回報回調函數")
            
        Note:
            - 清除後將不再接收訂單狀態更新通知
            - 不影響已記錄的歷史資料
            - 可以重新註冊新的回調函數
        """
        self.order_update_callbacks.clear()
        self.logger.info("已清除所有委託回報回調函數")
    
    def get_orders_history(self) -> List[Dict[str, Any]]:
        """
        取得本次連線的下單歷史
        
        返回由此連線器執行的所有下單記錄。
        
        Returns:
            List[Dict[str, Any]]: 下單歷史列表
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> stock = connector.get_stock_by_code("2330")
            >>> connector.place_order(stock, "Buy", 600.0, 1000)
            >>> 
            >>> history = connector.get_orders_history()
            >>> for order in history:
            >>>     print(f"商品: {order['contract'].code}")
            >>>     print(f"動作: {order['action']}")
            >>>     print(f"價格: {order['price']}")
            >>>     print(f"數量: {order['quantity']}")
            
        Note:
            - 只記錄本次連線期間的下單
            - 登出後歷史記錄會被清除
        """
        return self.orders_history.copy()
    
    def __repr__(self) -> str:
        """
        物件的字串表示
        
        Returns:
            str: 物件的描述字串
        """
        status = "已連線" if self.is_connected else "未連線"
        env = "模擬" if self.simulation else "正式"
        return f"ShioajiConnector(狀態={status}, 環境={env})"


# 模組層級的便利函數
def create_connector(
    api_key: str = "",
    secret_key: str = "",
    simulation: bool = False
) -> ShioajiConnector:
    """
    建立 ShioajiConnector 實例的便利函數
    
    Args:
        api_key (str, optional): API 金鑰
        secret_key (str, optional): 密鑰
        simulation (bool, optional): 是否使用模擬環境
        
    Returns:
        ShioajiConnector: Shioaji 連線器實例
        
    Examples:
        >>> connector = create_connector(simulation=True)
        >>> connector.login(person_id="A123456789", passwd="password")
    """
    return ShioajiConnector(
        api_key=api_key,
        secret_key=secret_key,
        simulation=simulation
    )


if __name__ == "__main__":
    # 使用範例
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Shioaji 連線器使用範例")
    print("=" * 60)
    
    # 示範 1: 基本使用
    print("\n示範 1: 建立連線器實例")
    try:
        connector = ShioajiConnector(simulation=True)
        print(f"連線器已建立: {connector}")
        print(f"連線狀態: {connector.get_connection_status()}")
    except ImportError as e:
        print(f"錯誤: {e}")
        print("請先安裝 shioaji: pip install shioaji")
    
    # 示範 2: Context Manager 使用
    print("\n示範 2: 使用 Context Manager")
    print("with ShioajiConnector(simulation=True) as connector:")
    print("    # 在此進行登入和交易操作")
    print("    # 離開 with 區塊時自動登出")
    
    print("\n" + "=" * 60)
    print("請參考類別文件以了解完整功能")
    print("=" * 60)
