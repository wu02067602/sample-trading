"""
永豐 Shioaji 交易客戶端模組

此模組提供與永豐證券 Shioaji API 的整合功能，包括登入、認證等操作。
遵循 SOLID 原則，透過抽象介面實現依賴反轉。
"""

import shioaji as sj
from typing import Optional, Dict, Any
from trading_client_interface import ITradingClient, LoginConfig, IConfigValidator
from config_validator import LoginConfigValidator


class ShioajiClient(ITradingClient):
    """
    永豐 Shioaji 交易客戶端類別
    
    此類別封裝了與永豐證券 Shioaji API 的互動邏輯，提供登入、
    憑證認證等功能。
    
    Attributes:
        sj (Optional[sj.Shioaji]): Shioaji API 實例
        is_logged_in (bool): 登入狀態標記
        contract (Optional[Any]): 商品檔資料
    
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
    
    def __init__(self, validator: Optional[IConfigValidator] = None) -> None:
        """
        初始化 ShioajiClient 實例
        
        創建一個新的客戶端實例，初始化必要的屬性。
        遵循依賴注入原則，允許外部注入驗證器。
        
        Args:
            validator (Optional[IConfigValidator]): 配置驗證器，預設為 LoginConfigValidator
        
        Examples:
            >>> client = ShioajiClient()  # 使用預設驗證器
            >>> custom_validator = LoginConfigValidator()
            >>> client = ShioajiClient(validator=custom_validator)  # 注入自訂驗證器
        """
        self.sj: Optional[sj.Shioaji] = None
        self.is_logged_in: bool = False
        self.contract: Optional[Any] = None
        self._validator: IConfigValidator = validator or LoginConfigValidator()
    
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
