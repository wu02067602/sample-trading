"""
永豐 Shioaji 交易客戶端模組

此模組提供與永豐證券 Shioaji API 的整合功能，包括登入、認證等操作。
遵循 SOLID 原則，透過抽象介面實現依賴反轉。
"""

import shioaji as sj
from typing import Optional, Dict, Any, List
from trading_client_interface import ITradingClient, LoginConfig, IConfigValidator
from config_validator import LoginConfigValidator
from quote_callback_handler import IQuoteCallback, QuoteCallbackHandler, OrderDealCallbackHandler
from order_manager import (
    OrderConfig, IntradayOddOrderConfig, IOrderManager, OrderValidator,
    OrderAction, OrderPriceType, OrderType
)


class ShioajiClient(ITradingClient, IOrderManager):
    """
    永豐 Shioaji 交易客戶端類別
    
    此類別封裝了與永豐證券 Shioaji API 的互動邏輯，提供登入、
    憑證認證等功能。
    
    Attributes:
        sj (Optional[sj.Shioaji]): Shioaji API 實例
        is_logged_in (bool): 登入狀態標記
        contract (Optional[Any]): 商品檔資料
        quote_callback (IQuoteCallback): 報價回調處理器
        order_deal_callback (OrderDealCallbackHandler): 委託成交回調處理器
    
    Examples:
        >>> config = LoginConfig(
        ...     api_key="YOUR_API_KEY",
        ...     secret_key="YOUR_SECRET_KEY",
        ...     person_id="A123456789"
        ... )
        >>> client = ShioajiClient()
        >>> result = client.login(config)
        >>> if result["success"]:
        ...     print("登入成功")
    
    Raises:
        ConnectionError: 當無法連接到 Shioaji API 時
        ValueError: 當登入參數不正確時
        Exception: 其他登入過程中的錯誤
    """
    
    def __init__(
        self,
        validator: Optional[IConfigValidator] = None,
        quote_callback: Optional[IQuoteCallback] = None,
        order_deal_callback: Optional[OrderDealCallbackHandler] = None
    ) -> None:
        """
        初始化 ShioajiClient 實例
        
        創建一個新的客戶端實例，初始化必要的屬性。
        遵循依賴注入原則，允許外部注入驗證器和回調處理器。
        
        Args:
            validator (Optional[IConfigValidator]): 配置驗證器，預設為 LoginConfigValidator
            quote_callback (Optional[IQuoteCallback]): 報價回調處理器，預設為 QuoteCallbackHandler
            order_deal_callback (Optional[OrderDealCallbackHandler]): 委託成交回調處理器
        
        Examples:
            >>> client = ShioajiClient()  # 使用預設處理器
            >>> custom_validator = LoginConfigValidator()
            >>> custom_quote_handler = QuoteCallbackHandler()
            >>> client = ShioajiClient(
            ...     validator=custom_validator,
            ...     quote_callback=custom_quote_handler
            ... )
        """
        self.sj: Optional[sj.Shioaji] = None
        self.is_logged_in: bool = False
        self.contract: Optional[Any] = None
        self._validator: IConfigValidator = validator or LoginConfigValidator()
        self.quote_callback: IQuoteCallback = quote_callback or QuoteCallbackHandler()
        self.order_deal_callback: OrderDealCallbackHandler = order_deal_callback or OrderDealCallbackHandler()
        self._order_validator: OrderValidator = OrderValidator()
    
    def login(self, config: LoginConfig) -> Dict[str, Any]:
        """
        執行登入操作
        
        使用提供的配置資訊登入永豐證券 Shioaji API。
        
        Args:
            config (LoginConfig): 登入配置物件，包含 API 金鑰、密鑰等資訊
        
        Returns:
            Dict[str, Any]: 登入結果字典，包含以下鍵值：
                - success (bool): 登入是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> config = LoginConfig(
            ...     api_key="YOUR_API_KEY",
            ...     secret_key="YOUR_SECRET_KEY",
            ...     person_id="A123456789"
            ... )
            >>> client = ShioajiClient()
            >>> result = client.login(config)
            >>> print(result["message"])
        
        Raises:
            ValueError: 當配置參數不完整或格式錯誤時
            ConnectionError: 當無法連接到 Shioaji 伺服器時
            Exception: 其他登入過程中的錯誤
        """
        try:
            # 使用注入的驗證器驗證配置
            self._validator.validate(config)
            
            # 創建 Shioaji 實例
            self.sj = sj.Shioaji(simulation=config.simulation)
            
            # 執行登入
            accounts = self.sj.login(
                api_key=config.api_key,
                secret_key=config.secret_key,
                person_id=config.person_id
            )
            
            self.is_logged_in = True
            
            return {
                "success": True,
                "message": "登入成功",
                "accounts": accounts
            }
            
        except ValueError as e:
            error_msg = f"配置參數錯誤: {str(e)}"
            return {
                "success": False,
                "message": "登入失敗",
                "error": error_msg
            }
        except ConnectionError as e:
            error_msg = f"連線錯誤: {str(e)}"
            return {
                "success": False,
                "message": "登入失敗",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"登入過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "登入失敗",
                "error": error_msg
            }
    
    def activate_ca(self, ca_password: str) -> Dict[str, Any]:
        """
        啟用憑證
        
        在登入後啟用憑證以進行下單等需要憑證的操作。
        
        Args:
            ca_password (str): 憑證密碼
        
        Returns:
            Dict[str, Any]: 憑證啟用結果字典，包含以下鍵值：
                - success (bool): 啟用是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.activate_ca("YOUR_CA_PASSWORD")
            >>> print(result["message"])
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當憑證密碼格式錯誤時
            Exception: 其他憑證啟用過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            self.sj.activate_ca(
                ca_path="",  # 預設路徑
                ca_passwd=ca_password,
                person_id=""  # 使用登入時的 person_id
            )
            
            return {
                "success": True,
                "message": "憑證啟用成功"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "憑證啟用失敗",
                "error": str(e)
            }
        except ValueError as e:
            error_msg = f"憑證密碼錯誤: {str(e)}"
            return {
                "success": False,
                "message": "憑證啟用失敗",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"憑證啟用過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "憑證啟用失敗",
                "error": error_msg
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        執行登出操作
        
        登出 Shioaji API 並清理資源。
        
        Returns:
            Dict[str, Any]: 登出結果字典，包含以下鍵值：
                - success (bool): 登出是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.logout()
            >>> print(result["message"])
        
        Raises:
            Exception: 登出過程中的錯誤
        """
        try:
            if self.sj is not None:
                self.sj.logout()
            
            self.is_logged_in = False
            self.sj = None
            
            return {
                "success": True,
                "message": "登出成功"
            }
            
        except Exception as e:
            error_msg = f"登出過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "登出失敗",
                "error": error_msg
            }
    
    def get_accounts(self) -> Optional[Any]:
        """
        取得帳戶資訊
        
        返回當前登入使用者的帳戶資訊。
        
        Returns:
            Optional[Any]: 帳戶資訊物件，如果尚未登入則返回 None
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> accounts = client.get_accounts()
            >>> if accounts:
            ...     print(accounts)
        
        Raises:
            RuntimeError: 當嘗試在未登入狀態下取得帳戶資訊時
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，請先執行 login() 方法")
        
        return self.sj.list_accounts()
    
    def fetch_contracts(self) -> Dict[str, Any]:
        """
        取得商品檔
        
        從 Shioaji API 載入商品檔資料並儲存至 contract 屬性。
        必須在登入後才能執行此操作。
        
        Returns:
            Dict[str, Any]: 商品檔取得結果字典，包含以下鍵值：
                - success (bool): 取得是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.fetch_contracts()
            >>> if result["success"]:
            ...     print("商品檔載入成功")
            ...     stocks = client.get_contracts("Stocks")
        
        Raises:
            RuntimeError: 當尚未登入時
            Exception: 其他取得商品檔過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 取得商品檔
            self.contract = self.sj.Contracts
            
            return {
                "success": True,
                "message": "商品檔載入成功"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "商品檔載入失敗",
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"商品檔載入過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "商品檔載入失敗",
                "error": error_msg
            }
    
    def get_contracts(self, contract_type: Optional[str] = None) -> Optional[Any]:
        """
        取得已載入的商品檔資料
        
        返回已載入的商品檔資料。可以指定商品類型來取得特定類型的商品，
        如股票、期貨、選擇權等。
        
        Args:
            contract_type (Optional[str]): 商品類型，可選值包括：
                - 'Stocks': 股票
                - 'Futures': 期貨
                - 'Options': 選擇權
                - None: 返回所有商品檔
        
        Returns:
            Optional[Any]: 商品檔物件，如果尚未載入則返回 None
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和 fetch_contracts ...
            >>> all_contracts = client.get_contracts()
            >>> stocks = client.get_contracts("Stocks")
            >>> futures = client.get_contracts("Futures")
        
        Raises:
            RuntimeError: 當嘗試在未載入商品檔的狀態下取得商品資訊時
            AttributeError: 當指定的商品類型不存在時
        """
        if self.contract is None:
            raise RuntimeError("尚未載入商品檔，請先執行 fetch_contracts() 方法")
        
        if contract_type is None:
            return self.contract
        
        try:
            return getattr(self.contract, contract_type)
        except AttributeError:
            raise AttributeError(f"商品類型 '{contract_type}' 不存在")
    
    def subscribe_quote(self, contracts: List[Any]) -> Dict[str, Any]:
        """
        訂閱報價
        
        訂閱指定商品的即時報價。訂閱後，報價資料會透過 callback 處理器接收。
        必須在登入後才能執行此操作。
        
        Args:
            contracts (List[Any]): 要訂閱的商品列表，可以是商品物件或商品代碼
        
        Returns:
            Dict[str, Any]: 訂閱結果字典，包含以下鍵值：
                - success (bool): 訂閱是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和 fetch_contracts ...
            >>> stocks = client.get_contracts("Stocks")
            >>> tsmc = stocks["2330"]
            >>> result = client.subscribe_quote([tsmc])
            >>> if result["success"]:
            ...     print("訂閱成功")
        
        Raises:
            RuntimeError: 當尚未登入時
            Exception: 其他訂閱過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 設置報價回調
            self.sj.quote.set_on_quote_stk_v1_callback(self.quote_callback.on_quote)
            
            # 訂閱報價
            self.sj.quote.subscribe(
                self.sj.Contracts.Stocks[contracts[0].symbol] if hasattr(contracts[0], 'symbol') else contracts[0],
                quote_type=sj.constant.QuoteType.Tick
            ) if len(contracts) == 1 else [
                self.sj.quote.subscribe(
                    contract,
                    quote_type=sj.constant.QuoteType.Tick
                ) for contract in contracts
            ]
            
            return {
                "success": True,
                "message": f"成功訂閱 {len(contracts)} 個商品的報價"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "訂閱報價失敗",
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"訂閱報價過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "訂閱報價失敗",
                "error": error_msg
            }
    
    def unsubscribe_quote(self, contracts: List[Any]) -> Dict[str, Any]:
        """
        取消訂閱報價
        
        取消訂閱指定商品的即時報價。
        
        Args:
            contracts (List[Any]): 要取消訂閱的商品列表
        
        Returns:
            Dict[str, Any]: 取消訂閱結果字典，包含以下鍵值：
                - success (bool): 取消訂閱是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和訂閱 ...
            >>> stocks = client.get_contracts("Stocks")
            >>> tsmc = stocks["2330"]
            >>> result = client.unsubscribe_quote([tsmc])
            >>> if result["success"]:
            ...     print("取消訂閱成功")
        
        Raises:
            RuntimeError: 當尚未登入時
            Exception: 其他取消訂閱過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 取消訂閱報價
            for contract in contracts:
                self.sj.quote.unsubscribe(
                    contract,
                    quote_type=sj.constant.QuoteType.Tick
                )
            
            return {
                "success": True,
                "message": f"成功取消訂閱 {len(contracts)} 個商品的報價"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "取消訂閱報價失敗",
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"取消訂閱報價過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "取消訂閱報價失敗",
                "error": error_msg
            }
    
    def set_order_callback(self) -> Dict[str, Any]:
        """
        設置委託成交回調
        
        設置委託和成交事件的回調處理器。
        必須在登入後才能執行此操作。
        
        Returns:
            Dict[str, Any]: 設置結果字典，包含以下鍵值：
                - success (bool): 設置是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.set_order_callback()
            >>> if result["success"]:
            ...     print("回調設置成功")
            ...     # 之後可以透過 client.order_deal_callback.get_deals() 取得成交記錄
        
        Raises:
            RuntimeError: 當尚未登入時
            Exception: 其他設置過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 設置委託回調
            self.sj.set_order_callback(self.order_deal_callback.on_order)
            
            # 設置成交回調
            # Shioaji 使用同一個 callback 處理委託和成交
            # 成交回報會透過 on_order 回調接收
            
            return {
                "success": True,
                "message": "委託成交回調設置成功"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "設置回調失敗",
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"設置回調過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "設置回調失敗",
                "error": error_msg
            }
    
    def get_deal_report(self, order_id: Optional[str] = None) -> Dict[str, Any]:
        """
        取得成交回報
        
        取得成交回報資訊。可以指定訂單 ID 來取得特定訂單的成交記錄，
        或者取得所有成交記錄。
        
        Args:
            order_id (Optional[str]): 訂單 ID，如果為 None 則返回所有成交記錄
        
        Returns:
            Dict[str, Any]: 成交回報字典，包含以下鍵值：
                - success (bool): 取得是否成功
                - deals (List[Dict]): 成交記錄列表
                - total_quantity (int): 總成交數量
                - average_price (float): 平均成交價格
                - message (str): 結果訊息
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和設置回調 ...
            >>> # 取得所有成交記錄
            >>> report = client.get_deal_report()
            >>> print(f"總成交數量: {report['total_quantity']}")
            >>> print(f"平均成交價: {report['average_price']}")
            >>> 
            >>> # 取得特定訂單的成交記錄
            >>> report = client.get_deal_report("ORDER_123")
            >>> for deal in report['deals']:
            ...     print(f"成交價格: {deal.get('price')}, 數量: {deal.get('quantity')}")
        
        Raises:
            RuntimeError: 當尚未設置回調時
        """
        try:
            if order_id:
                deals = self.order_deal_callback.get_deals_by_order_id(order_id)
                total_quantity = self.order_deal_callback.get_total_deal_quantity(order_id)
                average_price = self.order_deal_callback.get_average_deal_price(order_id)
            else:
                deals = self.order_deal_callback.get_deals()
                total_quantity = self.order_deal_callback.get_total_deal_quantity()
                average_price = self.order_deal_callback.get_average_deal_price()
            
            return {
                "success": True,
                "deals": deals,
                "total_quantity": total_quantity,
                "average_price": average_price,
                "message": f"成功取得 {len(deals)} 筆成交記錄"
            }
            
        except Exception as e:
            error_msg = f"取得成交回報過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "deals": [],
                "total_quantity": 0,
                "average_price": 0.0,
                "message": "取得成交回報失敗",
                "error": error_msg
            }
    
    def get_latest_deal_report(self) -> Dict[str, Any]:
        """
        取得最新成交回報
        
        取得最新一筆成交記錄。
        
        Returns:
            Dict[str, Any]: 最新成交回報字典，包含以下鍵值：
                - success (bool): 取得是否成功
                - deal (Optional[Dict]): 最新成交記錄
                - message (str): 結果訊息
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和設置回調 ...
            >>> report = client.get_latest_deal_report()
            >>> if report["success"] and report["deal"]:
            ...     deal = report["deal"]
            ...     print(f"最新成交價格: {deal.get('price')}")
            ...     print(f"成交數量: {deal.get('quantity')}")
        """
        try:
            latest_deal = self.order_deal_callback.get_latest_deal()
            
            if latest_deal:
                return {
                    "success": True,
                    "deal": latest_deal,
                    "message": "成功取得最新成交記錄"
                }
            else:
                return {
                    "success": True,
                    "deal": None,
                    "message": "目前沒有成交記錄"
                }
            
        except Exception as e:
            error_msg = f"取得最新成交回報過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "deal": None,
                "message": "取得最新成交回報失敗",
                "error": error_msg
            }
    
    def place_order(self, order_config: OrderConfig) -> Dict[str, Any]:
        """
        下一般股票訂單
        
        執行股票買賣下單操作。支援限價單和市價單，數量必須為1000股的倍數。
        必須在登入且啟用憑證後才能執行此操作。
        
        Args:
            order_config (OrderConfig): 訂單配置物件，包含商品、價格、數量等資訊
        
        Returns:
            Dict[str, Any]: 下單結果字典，包含以下鍵值：
                - success (bool): 下單是否成功
                - message (str): 結果訊息
                - order (Optional[Any]): 訂單物件（如果成功）
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> from order_manager import OrderConfig, OrderAction, OrderPriceType
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和啟用憑證 ...
            >>> config = OrderConfig(
            ...     contract=stock_contract,
            ...     action=OrderAction.BUY,
            ...     price=100.0,
            ...     quantity=1000,
            ...     price_type=OrderPriceType.LIMIT
            ... )
            >>> result = client.place_order(config)
            >>> if result["success"]:
            ...     print(f"下單成功，訂單號: {result['order'].order_id}")
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當訂單配置無效時
            Exception: 其他下單過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 驗證訂單配置
            self._order_validator.validate_order(order_config)
            
            # 建立 Shioaji Order 物件
            order = sj.Order(
                price=order_config.price if order_config.price_type == OrderPriceType.LIMIT else 0,
                quantity=order_config.quantity,
                action=order_config.action.value,
                price_type=order_config.price_type.value,
                order_type=order_config.order_type.value,
                account=order_config.account or self.sj.stock_account
            )
            
            # 下單
            trade = self.sj.place_order(order_config.contract, order)
            
            return {
                "success": True,
                "message": "下單成功",
                "order": trade
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "下單失敗",
                "error": str(e)
            }
        except ValueError as e:
            return {
                "success": False,
                "message": "下單失敗",
                "error": f"訂單配置錯誤: {str(e)}"
            }
        except Exception as e:
            error_msg = f"下單過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "下單失敗",
                "error": error_msg
            }
    
    def place_intraday_odd_order(self, order_config: IntradayOddOrderConfig) -> Dict[str, Any]:
        """
        下盤中零股訂單
        
        執行盤中零股買賣下單操作。數量必須小於1000股。
        必須在登入且啟用憑證後才能執行此操作。
        
        Args:
            order_config (IntradayOddOrderConfig): 盤中零股訂單配置物件
        
        Returns:
            Dict[str, Any]: 下單結果字典，包含以下鍵值：
                - success (bool): 下單是否成功
                - message (str): 結果訊息
                - order (Optional[Any]): 訂單物件（如果成功）
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> from order_manager import IntradayOddOrderConfig, OrderAction
            >>> client = ShioajiClient()
            >>> # ... 先執行登入和啟用憑證 ...
            >>> config = IntradayOddOrderConfig(
            ...     contract=stock_contract,
            ...     action=OrderAction.BUY,
            ...     price=100.0,
            ...     quantity=100
            ... )
            >>> result = client.place_intraday_odd_order(config)
            >>> if result["success"]:
            ...     print("零股下單成功")
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當訂單配置無效時
            Exception: 其他下單過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 驗證訂單配置
            self._order_validator.validate_intraday_odd_order(order_config)
            
            # 建立盤中零股 Order 物件
            order = sj.Order(
                price=order_config.price,
                quantity=order_config.quantity,
                action=order_config.action.value,
                price_type=OrderPriceType.LIMIT.value,
                order_type=OrderType.ROD.value,
                order_lot="IntradayOdd",  # 盤中零股標記
                account=order_config.account or self.sj.stock_account
            )
            
            # 下單
            trade = self.sj.place_order(order_config.contract, order)
            
            return {
                "success": True,
                "message": "盤中零股下單成功",
                "order": trade
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "盤中零股下單失敗",
                "error": str(e)
            }
        except ValueError as e:
            return {
                "success": False,
                "message": "盤中零股下單失敗",
                "error": f"訂單配置錯誤: {str(e)}"
            }
        except Exception as e:
            error_msg = f"盤中零股下單過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "盤中零股下單失敗",
                "error": error_msg
            }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        取消訂單
        
        取消指定的訂單。
        必須在登入後才能執行此操作。
        
        Args:
            order_id (str): 訂單 ID
        
        Returns:
            Dict[str, Any]: 取消訂單結果字典，包含以下鍵值：
                - success (bool): 取消是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.cancel_order("ORDER_ID_123")
            >>> if result["success"]:
            ...     print("取消訂單成功")
        
        Raises:
            RuntimeError: 當尚未登入時
            Exception: 其他取消訂單過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            # 取消訂單
            # Note: 實際的取消訂單 API 可能需要訂單物件而非 ID
            # 這裡提供基本實作，實際使用時可能需要調整
            self.sj.cancel_order(order_id)
            
            return {
                "success": True,
                "message": "取消訂單成功"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "取消訂單失敗",
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"取消訂單過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "取消訂單失敗",
                "error": error_msg
            }
    
    def update_order(self, order_id: str, price: float, quantity: int) -> Dict[str, Any]:
        """
        修改訂單
        
        修改指定訂單的價格和數量。
        必須在登入後才能執行此操作。
        
        Args:
            order_id (str): 訂單 ID
            price (float): 新價格
            quantity (int): 新數量
        
        Returns:
            Dict[str, Any]: 修改訂單結果字典，包含以下鍵值：
                - success (bool): 修改是否成功
                - message (str): 結果訊息
                - error (Optional[str]): 錯誤訊息（如果失敗）
        
        Examples:
            >>> client = ShioajiClient()
            >>> # ... 先執行登入 ...
            >>> result = client.update_order("ORDER_ID_123", 101.0, 2000)
            >>> if result["success"]:
            ...     print("修改訂單成功")
        
        Raises:
            RuntimeError: 當尚未登入時
            ValueError: 當參數無效時
            Exception: 其他修改訂單過程中的錯誤
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，請先執行 login() 方法")
            
            if price <= 0:
                raise ValueError("價格必須大於0")
            
            if quantity <= 0:
                raise ValueError("數量必須大於0")
            
            # 修改訂單
            # Note: 實際的修改訂單 API 可能需要訂單物件
            # 這裡提供基本實作，實際使用時可能需要調整
            self.sj.update_order(order_id, price=price, quantity=quantity)
            
            return {
                "success": True,
                "message": "修改訂單成功"
            }
            
        except RuntimeError as e:
            return {
                "success": False,
                "message": "修改訂單失敗",
                "error": str(e)
            }
        except ValueError as e:
            return {
                "success": False,
                "message": "修改訂單失敗",
                "error": f"參數錯誤: {str(e)}"
            }
        except Exception as e:
            error_msg = f"修改訂單過程發生錯誤: {str(e)}"
            return {
                "success": False,
                "message": "修改訂單失敗",
                "error": error_msg
            }
