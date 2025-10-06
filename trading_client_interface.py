"""
交易客戶端抽象介面模組

此模組定義了交易客戶端的抽象介面，遵循依賴反轉原則 (DIP)。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


# 前向聲明，避免循環導入
try:
    from order_manager import OrderConfig, IntradayOddOrderConfig
except ImportError:
    OrderConfig = Any
    IntradayOddOrderConfig = Any


@dataclass
class LoginConfig:
    """
    登入配置資料類別
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        person_id (str): 身分證字號或統一編號
        ca_password (Optional[str]): 憑證密碼，預設為 None
        simulation (bool): 是否使用模擬交易環境，預設為 True
    
    Examples:
        >>> config = LoginConfig(
        ...     api_key="YOUR_API_KEY",
        ...     secret_key="YOUR_SECRET_KEY",
        ...     person_id="A123456789"
        ... )
    """
    api_key: str
    secret_key: str
    person_id: str
    ca_password: Optional[str] = None
    simulation: bool = True


class ITradingClient(ABC):
    """
    交易客戶端抽象介面
    
    定義所有交易客戶端必須實作的方法，遵循依賴反轉原則 (DIP)。
    允許系統依賴抽象而非具體實作，便於未來擴展支援其他券商。
    
    Examples:
        >>> class MyTradingClient(ITradingClient):
        ...     def login(self, config: LoginConfig) -> Dict[str, Any]:
        ...         # 實作登入邏輯
        ...         pass
    
    Raises:
        NotImplementedError: 當子類別未實作抽象方法時
    """
    
    @abstractmethod
    def login(self, config: LoginConfig) -> Dict[str, Any]:
        """
        執行登入操作
        
        Args:
            config (LoginConfig): 登入配置物件
        
        Returns:
            Dict[str, Any]: 登入結果字典，包含 success、message 等鍵值
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def logout(self) -> Dict[str, Any]:
        """
        執行登出操作
        
        Returns:
            Dict[str, Any]: 登出結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def get_accounts(self) -> Optional[Any]:
        """
        取得帳戶資訊
        
        Returns:
            Optional[Any]: 帳戶資訊物件
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def fetch_contracts(self) -> Dict[str, Any]:
        """
        取得商品檔
        
        Returns:
            Dict[str, Any]: 商品檔取得結果字典，包含 success、message 等鍵值
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def get_contracts(self, contract_type: Optional[str] = None) -> Optional[Any]:
        """
        取得已載入的商品檔資料
        
        Args:
            contract_type (Optional[str]): 商品類型，如 'Stocks', 'Futures' 等
        
        Returns:
            Optional[Any]: 商品檔物件
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def subscribe_quote(self, contracts: List[Any]) -> Dict[str, Any]:
        """
        訂閱報價
        
        Args:
            contracts (List[Any]): 要訂閱的商品列表
        
        Returns:
            Dict[str, Any]: 訂閱結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def unsubscribe_quote(self, contracts: List[Any]) -> Dict[str, Any]:
        """
        取消訂閱報價
        
        Args:
            contracts (List[Any]): 要取消訂閱的商品列表
        
        Returns:
            Dict[str, Any]: 取消訂閱結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def place_order(self, order_config: Any) -> Dict[str, Any]:
        """
        下一般股票訂單
        
        Args:
            order_config (OrderConfig): 訂單配置物件
        
        Returns:
            Dict[str, Any]: 下單結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def place_intraday_odd_order(self, order_config: Any) -> Dict[str, Any]:
        """
        下盤中零股訂單
        
        Args:
            order_config (IntradayOddOrderConfig): 盤中零股訂單配置物件
        
        Returns:
            Dict[str, Any]: 下單結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        取消訂單
        
        Args:
            order_id (str): 訂單 ID
        
        Returns:
            Dict[str, Any]: 取消訂單結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass
    
    @abstractmethod
    def update_order(self, order_id: str, price: float, quantity: int) -> Dict[str, Any]:
        """
        修改訂單
        
        Args:
            order_id (str): 訂單 ID
            price (float): 新價格
            quantity (int): 新數量
        
        Returns:
            Dict[str, Any]: 修改訂單結果字典
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass


class IConfigValidator(ABC):
    """
    配置驗證器抽象介面
    
    定義配置驗證的抽象介面，遵循單一職責原則 (SRP) 和
    介面隔離原則 (ISP)。
    
    Examples:
        >>> class LoginConfigValidator(IConfigValidator):
        ...     def validate(self, config: LoginConfig) -> None:
        ...         # 實作驗證邏輯
        ...         pass
    
    Raises:
        NotImplementedError: 當子類別未實作抽象方法時
    """
    
    @abstractmethod
    def validate(self, config: LoginConfig) -> None:
        """
        驗證配置的有效性
        
        Args:
            config (LoginConfig): 要驗證的配置物件
        
        Raises:
            ValueError: 當配置無效時
            NotImplementedError: 子類別必須實作此方法
        """
        pass
