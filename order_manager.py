"""
訂單管理模組

此模組定義了訂單相關的資料結構和訂單管理介面，遵循單一職責原則 (SRP)。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class OrderAction(Enum):
    """
    訂單動作枚舉
    
    定義訂單的買賣方向。
    
    Attributes:
        BUY: 買進
        SELL: 賣出
    """
    BUY = "Buy"
    SELL = "Sell"


class OrderPriceType(Enum):
    """
    訂單價格類型枚舉
    
    定義訂單的價格類型。
    
    Attributes:
        LIMIT: 限價
        MARKET: 市價
    """
    LIMIT = "LMT"
    MARKET = "MKT"


class OrderType(Enum):
    """
    訂單類型枚舉
    
    定義訂單的交易類型。
    
    Attributes:
        ROD: 當日有效 (Rest of Day)
        IOC: 立即成交否則取消 (Immediate or Cancel)
        FOK: 全部成交否則取消 (Fill or Kill)
    """
    ROD = "ROD"
    IOC = "IOC"
    FOK = "FOK"


@dataclass
class OrderConfig:
    """
    訂單配置資料類別
    
    封裝下單所需的完整參數。
    
    Attributes:
        contract (Any): 商品合約物件
        action (OrderAction): 買賣方向
        price (float): 價格（限價單使用）
        quantity (int): 數量
        price_type (OrderPriceType): 價格類型，預設為限價
        order_type (OrderType): 訂單類型，預設為當日有效
        account (Optional[Any]): 交易帳戶，預設為 None
    
    Examples:
        >>> from order_manager import OrderConfig, OrderAction, OrderPriceType
        >>> config = OrderConfig(
        ...     contract=stock_contract,
        ...     action=OrderAction.BUY,
        ...     price=100.0,
        ...     quantity=1000
        ... )
    """
    contract: Any
    action: OrderAction
    price: float
    quantity: int
    price_type: OrderPriceType = OrderPriceType.LIMIT
    order_type: OrderType = OrderType.ROD
    account: Optional[Any] = None


@dataclass
class IntradayOddOrderConfig:
    """
    盤中零股訂單配置資料類別
    
    封裝盤中零股下單所需的參數。
    
    Attributes:
        contract (Any): 商品合約物件
        action (OrderAction): 買賣方向
        price (float): 價格
        quantity (int): 數量（必須小於1000股）
        account (Optional[Any]): 交易帳戶，預設為 None
    
    Examples:
        >>> from order_manager import IntradayOddOrderConfig, OrderAction
        >>> config = IntradayOddOrderConfig(
        ...     contract=stock_contract,
        ...     action=OrderAction.BUY,
        ...     price=100.0,
        ...     quantity=100
        ... )
    
    Raises:
        ValueError: 當數量大於等於1000股時
    """
    contract: Any
    action: OrderAction
    price: float
    quantity: int
    account: Optional[Any] = None
    
    def __post_init__(self):
        """
        驗證盤中零股訂單配置
        
        Raises:
            ValueError: 當數量不符合零股規定時
        """
        if self.quantity >= 1000:
            raise ValueError("盤中零股數量必須小於1000股")
        if self.quantity <= 0:
            raise ValueError("訂單數量必須大於0")


class IOrderManager(ABC):
    """
    訂單管理器抽象介面
    
    定義訂單管理的抽象介面，遵循單一職責原則 (SRP) 和
    介面隔離原則 (ISP)。
    
    Examples:
        >>> class MyOrderManager(IOrderManager):
        ...     def place_order(self, order_config: OrderConfig) -> Dict[str, Any]:
        ...         # 實作下單邏輯
        ...         pass
    
    Raises:
        NotImplementedError: 當子類別未實作抽象方法時
    """
    
    @abstractmethod
    def place_order(self, order_config: OrderConfig) -> Dict[str, Any]:
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
    def place_intraday_odd_order(self, order_config: IntradayOddOrderConfig) -> Dict[str, Any]:
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


class OrderValidator:
    """
    訂單驗證器
    
    負責驗證訂單配置的有效性，遵循單一職責原則 (SRP)。
    
    Examples:
        >>> validator = OrderValidator()
        >>> config = OrderConfig(
        ...     contract=stock_contract,
        ...     action=OrderAction.BUY,
        ...     price=100.0,
        ...     quantity=1000
        ... )
        >>> validator.validate_order(config)
    """
    
    def validate_order(self, order_config: OrderConfig) -> None:
        """
        驗證一般訂單配置
        
        Args:
            order_config (OrderConfig): 訂單配置物件
        
        Raises:
            ValueError: 當訂單配置無效時
        
        Examples:
            >>> validator = OrderValidator()
            >>> config = OrderConfig(
            ...     contract=stock_contract,
            ...     action=OrderAction.BUY,
            ...     price=100.0,
            ...     quantity=1000
            ... )
            >>> validator.validate_order(config)
        """
        if order_config.contract is None:
            raise ValueError("商品合約不可為空")
        
        if order_config.price <= 0 and order_config.price_type == OrderPriceType.LIMIT:
            raise ValueError("限價單價格必須大於0")
        
        if order_config.quantity <= 0:
            raise ValueError("訂單數量必須大於0")
        
        # 一般股票交易單位為1000股
        if order_config.quantity % 1000 != 0:
            raise ValueError("一般股票訂單數量必須為1000股的倍數")
    
    def validate_intraday_odd_order(self, order_config: IntradayOddOrderConfig) -> None:
        """
        驗證盤中零股訂單配置
        
        Args:
            order_config (IntradayOddOrderConfig): 盤中零股訂單配置物件
        
        Raises:
            ValueError: 當訂單配置無效時
        
        Examples:
            >>> validator = OrderValidator()
            >>> config = IntradayOddOrderConfig(
            ...     contract=stock_contract,
            ...     action=OrderAction.BUY,
            ...     price=100.0,
            ...     quantity=100
            ... )
            >>> validator.validate_intraday_odd_order(config)
        """
        if order_config.contract is None:
            raise ValueError("商品合約不可為空")
        
        if order_config.price <= 0:
            raise ValueError("價格必須大於0")
        
        if order_config.quantity <= 0:
            raise ValueError("訂單數量必須大於0")
        
        if order_config.quantity >= 1000:
            raise ValueError("盤中零股數量必須小於1000股")
