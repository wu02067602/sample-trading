"""
Shioaji 交易客戶端模組

此模組提供與永豐金證券 Shioaji API 的整合介面，用於量化交易系統。
"""

import shioaji as sj
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
import logging

from trading_interface import ITradingClient, IConfigValidator
from quote_callback import IQuoteCallback, IOrderCallback, DefaultQuoteCallback, DefaultOrderCallback


@dataclass
class LoginConfig(IConfigValidator):
    """
    登入配置資料類別
    
    Attributes:
        person_id: 使用者身分證字號或統一編號
        passwd: 使用者密碼
        ca_path: CA 憑證路徑（可選）
        ca_passwd: CA 憑證密碼（可選）
        simulation: 是否使用模擬環境，預設為 False
    
    Examples:
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password"
        ... )
    """
    person_id: str
    passwd: str
    ca_path: Optional[str] = None
    ca_passwd: Optional[str] = None
    simulation: bool = False
    
    def validate(self) -> None:
        """
        驗證配置參數的有效性
        
        Raises:
            ValueError: 當必要的參數缺失或無效時
        
        Examples:
            >>> config = LoginConfig(person_id="", passwd="password")
            >>> config.validate()  # 會拋出 ValueError
        """
        if not self.person_id or not self.person_id.strip():
            raise ValueError("person_id 不可為空")
        if not self.passwd or not self.passwd.strip():
            raise ValueError("passwd 不可為空")
        if self.ca_path and not self.ca_passwd:
            raise ValueError("提供 ca_path 時必須同時提供 ca_passwd")
        if self.ca_passwd and not self.ca_path:
            raise ValueError("提供 ca_passwd 時必須同時提供 ca_path")


class ShioajiClient(ITradingClient):
    """
    Shioaji 交易客戶端
    
    此類別封裝了 Shioaji API 的登入、登出等基本功能，
    並提供統一的介面供量化交易系統使用。
    
    Attributes:
        sj: Shioaji API 實例，登入成功後可用於後續交易操作
        is_logged_in: 登入狀態標記
        config: 登入配置資訊
        contracts: 商品檔物件，包含所有可交易的商品資訊
    
    Examples:
        基本登入範例：
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password"
        ... )
        >>> client = ShioajiClient()
        >>> client.login(config)
        >>> # 使用 client.sj 進行後續操作
        >>> client.logout()
        
        使用 CA 憑證登入：
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password",
        ...     ca_path="/path/to/cert.pfx",
        ...     ca_passwd="cert_password"
        ... )
        >>> client = ShioajiClient()
        >>> client.login(config)
    
    Raises:
        ValueError: 當登入參數不正確時
        ConnectionError: 當連線失敗時
        RuntimeError: 當登入過程發生錯誤時
    """
    
    def __init__(self):
        """
        初始化 Shioaji 客戶端
        
        建立 Shioaji API 實例並設定日誌記錄器。
        
        Examples:
            >>> client = ShioajiClient()
        """
        self.sj: Optional[sj.Shioaji] = None
        self.is_logged_in: bool = False
        self.config: Optional[LoginConfig] = None
        self.contracts: Optional[Any] = None
        self.logger = logging.getLogger(__name__)
        
        # Callback 處理器
        self.quote_callback: Optional[IQuoteCallback] = None
        self.order_callback: Optional[IOrderCallback] = None
        
        # 訂閱列表
        self.subscribed_quotes: List[str] = []
        
    def connect(self, config: LoginConfig) -> bool:
        """
        連接到 Shioaji 交易系統（實作 ITradingClient.connect）
        
        此方法為 login 的別名，遵循介面定義。
        
        Args:
            config: LoginConfig 登入配置物件
        
        Returns:
            bool: 連線成功返回 True，失敗返回 False
        
        Raises:
            ValueError: 當配置參數無效時
            ConnectionError: 當連線失敗時
            RuntimeError: 當發生其他錯誤時
        
        Examples:
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client = ShioajiClient()
            >>> client.connect(config)
        """
        return self.login(config)
    
    def login(self, config: LoginConfig) -> bool:
        """
        執行登入操作
        
        根據提供的配置進行登入。如果提供了 CA 憑證資訊，
        將使用憑證登入；否則使用基本帳號密碼登入。
        
        Args:
            config: LoginConfig 登入配置物件
        
        Returns:
            bool: 登入成功返回 True，失敗返回 False
        
        Raises:
            ValueError: 當必要的登入參數缺失時
            ConnectionError: 當無法連接到 Shioaji 伺服器時
            RuntimeError: 當登入過程發生其他錯誤時
        
        Examples:
            基本登入：
            >>> config = LoginConfig(
            ...     person_id="A123456789",
            ...     passwd="your_password"
            ... )
            >>> client = ShioajiClient()
            >>> success = client.login(config)
            >>> print(f"登入狀態: {success}")
            
            CA 憑證登入：
            >>> config = LoginConfig(
            ...     person_id="A123456789",
            ...     passwd="your_password",
            ...     ca_path="/path/to/cert.pfx",
            ...     ca_passwd="cert_password"
            ... )
            >>> success = client.login(config)
        """
        try:
            # 驗證配置參數
            config.validate()
            
            # 建立 Shioaji 實例
            self.sj = sj.Shioaji(simulation=config.simulation)
            self.logger.info(f"開始登入 Shioaji API (模擬模式: {config.simulation})")
            
            # 執行登入
            accounts = self.sj.login(
                person_id=config.person_id,
                passwd=config.passwd
            )
            
            self.logger.info(f"登入成功，取得 {len(accounts)} 個帳戶")
            
            # 如果提供了 CA 憑證，進行憑證啟用
            if config.ca_path and config.ca_passwd:
                self.logger.info("開始啟用 CA 憑證")
                self.sj.activate_ca(
                    ca_path=config.ca_path,
                    ca_passwd=config.ca_passwd,
                    person_id=config.person_id
                )
                self.logger.info("CA 憑證啟用成功")
            
            # 更新狀態
            self.is_logged_in = True
            self.config = config
            
            # 獲取商品檔（登入後自動下載）
            self.contracts = self.sj.Contracts
            self.logger.info("商品檔載入成功")
            
            return True
            
        except ValueError as e:
            self.logger.error(f"登入參數錯誤: {e}")
            raise
        except ConnectionError as e:
            self.logger.error(f"連線失敗: {e}")
            raise
        except Exception as e:
            self.logger.error(f"登入過程發生錯誤: {e}")
            raise RuntimeError(f"登入失敗: {e}") from e
    
    def disconnect(self) -> bool:
        """
        斷開與 Shioaji 交易系統的連線（實作 ITradingClient.disconnect）
        
        此方法為 logout 的別名，遵循介面定義。
        
        Returns:
            bool: 斷線成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未連線或斷線過程發生錯誤時
        
        Examples:
            >>> client.disconnect()
        """
        return self.logout()
    
    def logout(self) -> bool:
        """
        執行登出操作
        
        關閉與 Shioaji 伺服器的連線。為了維持良好的服務品質，
        建議在不使用時主動登出。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未登入或登出過程發生錯誤時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> # 執行交易操作...
            >>> client.logout()
            >>> print(f"登出狀態: {not client.is_logged_in}")
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，無法執行登出操作")
            
            self.logger.info("開始登出 Shioaji API")
            result = self.sj.logout()
            
            # 重置狀態
            self.is_logged_in = False
            self.sj = None
            self.contracts = None
            self.subscribed_quotes = []
            
            self.logger.info("登出成功")
            return result
            
        except Exception as e:
            self.logger.error(f"登出過程發生錯誤: {e}")
            raise RuntimeError(f"登出失敗: {e}") from e
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        取得帳戶資訊
        
        Returns:
            Dict[str, Any]: 包含股票帳戶和期貨帳戶的字典
        
        Raises:
            RuntimeError: 當尚未登入時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> accounts = client.get_accounts()
            >>> print(accounts['stock_account'])
            >>> print(accounts['futopt_account'])
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法取得帳戶資訊")
        
        return {
            'stock_account': self.sj.stock_account,
            'futopt_account': self.sj.futopt_account
        }
    
    def __enter__(self):
        """
        支援 context manager 的進入方法
        
        Returns:
            ShioajiClient: 客戶端實例本身
        
        Examples:
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> with ShioajiClient() as client:
            ...     client.login(config)
            ...     # 執行交易操作
            ...     # 自動登出
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支援 context manager 的退出方法，自動登出
        
        Args:
            exc_type: 例外類型
            exc_val: 例外值
            exc_tb: 例外追蹤資訊
        """
        if self.is_logged_in:
            try:
                self.logout()
            except Exception as e:
                self.logger.error(f"自動登出時發生錯誤: {e}")
    
    def is_connected(self) -> bool:
        """
        檢查是否已連線到 Shioaji 系統（實作 ITradingClient.is_connected）
        
        Returns:
            bool: 已連線返回 True，未連線返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> print(client.is_connected())  # False
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> print(client.is_connected())  # True
        """
        return self.is_logged_in and self.sj is not None
    
    def get_contracts(self) -> Any:
        """
        取得商品檔資訊（實作 ITradingClient.get_contracts）
        
        商品檔包含所有可交易的商品資訊，包括股票、期貨、選擇權、指數等。
        登入後會自動下載商品檔，可透過此方法取得。
        
        Returns:
            Any: 商品檔物件，包含以下屬性：
                - Stocks: 股票商品
                - Futures: 期貨商品
                - Options: 選擇權商品
                - Indexs: 指數商品
        
        Raises:
            RuntimeError: 當尚未登入時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> contracts = client.get_contracts()
            >>> 
            >>> # 取得台積電股票
            >>> tsmc = contracts.Stocks["2330"]
            >>> print(tsmc.name)  # 台積電
            >>> 
            >>> # 取得台指期
            >>> tx = contracts.Futures.TXF.TXFR1
            >>> print(tx.name)  # 台指期
            >>> 
            >>> # 取得加權指數
            >>> tse = contracts.Indexs.TSE.TSE001
            >>> print(tse.name)  # 加權指數
        """
        if not self.is_logged_in or self.contracts is None:
            raise RuntimeError("尚未登入，無法取得商品檔")
        
        return self.contracts
    
    def search_contracts(self, keyword: str) -> list:
        """
        搜尋商品檔
        
        根據關鍵字搜尋商品，支援商品代碼和商品名稱搜尋。
        
        Args:
            keyword: 搜尋關鍵字（商品代碼或名稱）
        
        Returns:
            list: 符合條件的商品列表
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當關鍵字為空時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> 
            >>> # 搜尋台積電
            >>> results = client.search_contracts("2330")
            >>> for contract in results:
            ...     print(f"{contract.code} - {contract.name}")
            >>> 
            >>> # 搜尋包含「台積」的商品
            >>> results = client.search_contracts("台積")
            >>> for contract in results:
            ...     print(f"{contract.code} - {contract.name}")
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法搜尋商品檔")
        
        if not keyword or not keyword.strip():
            raise ValueError("搜尋關鍵字不可為空")
        
        try:
            results = self.sj.Contracts.search(keyword.strip())
            self.logger.info(f"搜尋商品檔 '{keyword}'，找到 {len(results)} 個結果")
            return results
        except Exception as e:
            self.logger.error(f"搜尋商品檔時發生錯誤: {e}")
            raise RuntimeError(f"搜尋商品檔失敗: {e}") from e
    
    def get_stock(self, code: str) -> Any:
        """
        取得特定股票商品
        
        Args:
            code: 股票代碼（如 "2330"）
        
        Returns:
            Any: 股票商品物件
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當股票代碼無效時
            KeyError: 當找不到指定的股票時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> 
            >>> # 取得台積電
            >>> tsmc = client.get_stock("2330")
            >>> print(f"{tsmc.code} - {tsmc.name}")
            >>> print(f"漲停價: {tsmc.limit_up}, 跌停價: {tsmc.limit_down}")
        """
        if not self.is_logged_in or self.contracts is None:
            raise RuntimeError("尚未登入，無法取得股票資訊")
        
        if not code or not code.strip():
            raise ValueError("股票代碼不可為空")
        
        try:
            stock = self.contracts.Stocks[code.strip()]
            self.logger.info(f"取得股票 {code}: {stock.name}")
            return stock
        except KeyError:
            raise KeyError(f"找不到股票代碼: {code}")
        except Exception as e:
            self.logger.error(f"取得股票時發生錯誤: {e}")
            raise RuntimeError(f"取得股票失敗: {e}") from e
    
    def set_quote_callback(self, callback: IQuoteCallback) -> None:
        """
        設定報價 Callback 處理器
        
        Args:
            callback: 實作 IQuoteCallback 介面的回調處理器
        
        Examples:
            >>> from quote_callback import DefaultQuoteCallback
            >>> client = ShioajiClient()
            >>> client.login(config)
            >>> callback = DefaultQuoteCallback()
            >>> client.set_quote_callback(callback)
        """
        self.quote_callback = callback
        self.logger.info("已設定報價 Callback 處理器")
    
    def set_order_callback(self, callback: IOrderCallback) -> None:
        """
        設定訂單 Callback 處理器
        
        Args:
            callback: 實作 IOrderCallback 介面的回調處理器
        
        Examples:
            >>> from quote_callback import DefaultOrderCallback
            >>> client = ShioajiClient()
            >>> client.login(config)
            >>> callback = DefaultOrderCallback()
            >>> client.set_order_callback(callback)
        """
        self.order_callback = callback
        self.logger.info("已設定訂單 Callback 處理器")
    
    def subscribe_quote(self, contract: Any) -> bool:
        """
        訂閱報價
        
        訂閱指定商品的即時報價，需要先設定 Callback 處理器。
        
        Args:
            contract: 商品物件（從 Contracts 取得）
        
        Returns:
            bool: 訂閱成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未登入或未設定 Callback 時
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(config)
            >>> 
            >>> # 設定並註冊 callback
            >>> callback = DefaultQuoteCallback()
            >>> client.set_quote_callback(callback)
            >>> client.register_quote_callback()  # 註冊 callback
            >>> 
            >>> # 訂閱台積電報價
            >>> tsmc = client.get_stock("2330")
            >>> client.subscribe_quote(tsmc)
            >>> 
            >>> # 或直接使用 contracts
            >>> client.subscribe_quote(client.contracts.Stocks["2330"])
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法訂閱報價")
        
        if not self.quote_callback:
            raise RuntimeError("尚未設定報價 Callback，請先調用 set_quote_callback()")
        
        try:
            # 執行訂閱
            self.sj.quote.subscribe(
                self.sj.Contracts.Stocks[contract.code],
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            
            # 記錄訂閱
            if contract.code not in self.subscribed_quotes:
                self.subscribed_quotes.append(contract.code)
            
            self.logger.info(f"訂閱報價成功: {contract.code} - {contract.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"訂閱報價時發生錯誤: {e}")
            raise RuntimeError(f"訂閱報價失敗: {e}") from e
    
    def unsubscribe_quote(self, contract: Any) -> bool:
        """
        取消訂閱報價
        
        Args:
            contract: 商品物件
        
        Returns:
            bool: 取消訂閱成功返回 True
        
        Raises:
            RuntimeError: 當尚未登入時
        
        Examples:
            >>> tsmc = client.get_stock("2330")
            >>> client.unsubscribe_quote(tsmc)
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法取消訂閱")
        
        try:
            self.sj.quote.unsubscribe(
                self.sj.Contracts.Stocks[contract.code],
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            
            # 移除訂閱記錄
            if contract.code in self.subscribed_quotes:
                self.subscribed_quotes.remove(contract.code)
            
            self.logger.info(f"取消訂閱成功: {contract.code}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消訂閱時發生錯誤: {e}")
            raise RuntimeError(f"取消訂閱失敗: {e}") from e
    
    def register_quote_callback(self) -> bool:
        """
        註冊報價回調
        
        註冊報價 callback，必須在訂閱報價之前調用。
        
        Returns:
            bool: 註冊成功返回 True
        
        Raises:
            RuntimeError: 當尚未登入或未設定 Callback 時
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(config)
            >>> 
            >>> # 設定 callback
            >>> callback = DefaultQuoteCallback()
            >>> client.set_quote_callback(callback)
            >>> 
            >>> # 註冊回調
            >>> client.register_quote_callback()
            >>> 
            >>> # 現在可以訂閱報價
            >>> tsmc = client.get_stock("2330")
            >>> client.subscribe_quote(tsmc)
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法註冊報價回調")
        
        if not self.quote_callback:
            raise RuntimeError("尚未設定報價 Callback，請先調用 set_quote_callback()")
        
        try:
            # 註冊報價回調
            @self.sj.on_quote_stk_v1()
            def quote_callback_wrapper(topic: str, quote: Any):
                """內部報價回調包裝函數"""
                if self.quote_callback:
                    self.quote_callback.on_quote(topic, quote)
            
            self.logger.info("報價回調註冊成功")
            return True
            
        except Exception as e:
            self.logger.error(f"註冊報價回調時發生錯誤: {e}")
            raise RuntimeError(f"註冊報價回調失敗: {e}") from e
    
    def register_order_callback(self) -> bool:
        """
        註冊訂單回調
        
        註冊訂單狀態和成交事件的回調處理，需要先設定 Callback 處理器。
        
        Returns:
            bool: 註冊成功返回 True
        
        Raises:
            RuntimeError: 當尚未登入或未設定 Callback 時
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(config)
            >>> 
            >>> # 設定 callback
            >>> callback = DefaultOrderCallback()
            >>> client.set_order_callback(callback)
            >>> 
            >>> # 註冊回調
            >>> client.register_order_callback()
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法註冊訂單回調")
        
        if not self.order_callback:
            raise RuntimeError("尚未設定訂單 Callback，請先調用 set_order_callback()")
        
        try:
            # 註冊訂單狀態回調
            @self.sj.on_order()
            def order_callback_wrapper(stat: str, order: Any):
                """內部訂單回調包裝函數"""
                if self.order_callback:
                    self.order_callback.on_order(stat, order)
            
            # 註冊成交回調
            @self.sj.on_deal()
            def deal_callback_wrapper(stat: str, deal: Any):
                """內部成交回調包裝函數"""
                if self.order_callback:
                    self.order_callback.on_deal(stat, deal)
            
            self.logger.info("訂單回調註冊成功")
            return True
            
        except Exception as e:
            self.logger.error(f"註冊訂單回調時發生錯誤: {e}")
            raise RuntimeError(f"註冊訂單回調失敗: {e}") from e
    
    def get_subscribed_quotes(self) -> List[str]:
        """
        取得已訂閱的商品列表
        
        Returns:
            List[str]: 已訂閱的商品代碼列表
        
        Examples:
            >>> client.subscribe_quote(tsmc)
            >>> client.subscribe_quote(hon_hai)
            >>> subscribed = client.get_subscribed_quotes()
            >>> print(subscribed)  # ['2330', '2317']
        """
        return self.subscribed_quotes.copy()
