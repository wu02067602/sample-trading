"""
報價回調處理器模組

此模組定義了報價回調處理的抽象介面和具體實作，遵循單一職責原則 (SRP)。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Dict, List
from datetime import datetime


class IQuoteCallback(ABC):
    """
    報價回調處理器抽象介面
    
    定義報價回調處理的抽象介面，遵循單一職責原則 (SRP) 和
    介面隔離原則 (ISP)。
    
    Examples:
        >>> class MyQuoteCallback(IQuoteCallback):
        ...     def on_quote(self, topic: str, quote: Any) -> None:
        ...         print(f"收到報價: {quote}")
    
    Raises:
        NotImplementedError: 當子類別未實作抽象方法時
    """
    
    @abstractmethod
    def on_quote(self, topic: str, quote: Any) -> None:
        """
        處理報價回調
        
        Args:
            topic (str): 報價主題
            quote (Any): 報價資料物件
        
        Raises:
            NotImplementedError: 子類別必須實作此方法
        """
        pass


class QuoteCallbackHandler(IQuoteCallback):
    """
    報價回調處理器實作
    
    此類別負責處理來自 Shioaji API 的報價回調，支援自訂處理函數。
    遵循單一職責原則，僅負責報價資料的接收和處理。
    
    Attributes:
        quotes (Dict[str, List[Dict[str, Any]]]): 儲存接收到的報價資料
        custom_handler (Optional[Callable]): 自訂的報價處理函數
    
    Examples:
        >>> def my_handler(topic, quote):
        ...     print(f"Topic: {topic}, Price: {quote.close}")
        >>> handler = QuoteCallbackHandler(custom_handler=my_handler)
        >>> # handler 會在收到報價時自動呼叫 my_handler
    
    Raises:
        Exception: 處理報價時發生的錯誤
    """
    
    def __init__(self, custom_handler: Optional[Callable[[str, Any], None]] = None) -> None:
        """
        初始化報價回調處理器
        
        Args:
            custom_handler (Optional[Callable]): 自訂的報價處理函數，
                接受 (topic: str, quote: Any) 兩個參數
        
        Examples:
            >>> handler = QuoteCallbackHandler()  # 使用預設處理
            >>> def custom(topic, quote):
            ...     print(f"收到 {topic} 報價")
            >>> handler = QuoteCallbackHandler(custom_handler=custom)
        """
        self.quotes: Dict[str, List[Dict[str, Any]]] = {}
        self.custom_handler: Optional[Callable[[str, Any], None]] = custom_handler
    
    def on_quote(self, topic: str, quote: Any) -> None:
        """
        處理報價回調
        
        接收並處理來自 Shioaji API 的報價資料。
        資料會被儲存到 quotes 字典中，並執行自訂處理函數（如果有設定）。
        
        Args:
            topic (str): 報價主題（通常是商品代碼）
            quote (Any): 報價資料物件
        
        Examples:
            >>> handler = QuoteCallbackHandler()
            >>> # 模擬接收報價
            >>> class MockQuote:
            ...     close = 100.0
            ...     volume = 1000
            >>> handler.on_quote("2330", MockQuote())
        
        Raises:
            Exception: 處理報價過程中的錯誤
        """
        try:
            # 將報價資料轉換為字典格式儲存
            quote_data = self._convert_quote_to_dict(topic, quote)
            
            # 儲存報價資料
            if topic not in self.quotes:
                self.quotes[topic] = []
            self.quotes[topic].append(quote_data)
            
            # 執行自訂處理函數
            if self.custom_handler:
                self.custom_handler(topic, quote)
                
        except Exception as e:
            print(f"處理報價時發生錯誤: {str(e)}")
    
    def _convert_quote_to_dict(self, topic: str, quote: Any) -> Dict[str, Any]:
        """
        將報價物件轉換為字典格式
        
        Args:
            topic (str): 報價主題
            quote (Any): 報價資料物件
        
        Returns:
            Dict[str, Any]: 報價資料字典
        
        Examples:
            >>> handler = QuoteCallbackHandler()
            >>> class MockQuote:
            ...     close = 100.0
            >>> data = handler._convert_quote_to_dict("2330", MockQuote())
            >>> print(data["topic"])
            2330
        """
        quote_dict = {
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
        
        # 提取報價物件的屬性
        if hasattr(quote, '__dict__'):
            quote_dict.update(quote.__dict__)
        
        return quote_dict
    
    def get_latest_quote(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        取得指定主題的最新報價
        
        Args:
            topic (str): 報價主題（商品代碼）
        
        Returns:
            Optional[Dict[str, Any]]: 最新報價資料，如果沒有則返回 None
        
        Examples:
            >>> handler = QuoteCallbackHandler()
            >>> # ... 接收報價後 ...
            >>> latest = handler.get_latest_quote("2330")
            >>> if latest:
            ...     print(latest["close"])
        
        Raises:
            KeyError: 當指定的主題不存在時
        """
        if topic in self.quotes and len(self.quotes[topic]) > 0:
            return self.quotes[topic][-1]
        return None
    
    def get_all_quotes(self, topic: str) -> List[Dict[str, Any]]:
        """
        取得指定主題的所有報價歷史
        
        Args:
            topic (str): 報價主題（商品代碼）
        
        Returns:
            List[Dict[str, Any]]: 報價歷史列表
        
        Examples:
            >>> handler = QuoteCallbackHandler()
            >>> # ... 接收報價後 ...
            >>> all_quotes = handler.get_all_quotes("2330")
            >>> print(f"共收到 {len(all_quotes)} 筆報價")
        """
        return self.quotes.get(topic, [])
    
    def clear_quotes(self, topic: Optional[str] = None) -> None:
        """
        清除報價資料
        
        Args:
            topic (Optional[str]): 要清除的報價主題，
                如果為 None 則清除所有報價
        
        Examples:
            >>> handler = QuoteCallbackHandler()
            >>> handler.clear_quotes("2330")  # 清除特定商品報價
            >>> handler.clear_quotes()  # 清除所有報價
        """
        if topic is None:
            self.quotes.clear()
        elif topic in self.quotes:
            del self.quotes[topic]


class OrderDealCallbackHandler:
    """
    委託成交回調處理器
    
    此類別負責處理來自 Shioaji API 的委託成交回調。
    遵循單一職責原則，僅負責委託成交資料的接收和處理。
    
    Attributes:
        orders (List[Dict[str, Any]]): 儲存接收到的委託資料
        deals (List[Dict[str, Any]]): 儲存接收到的成交資料
        custom_order_handler (Optional[Callable]): 自訂的委託處理函數
        custom_deal_handler (Optional[Callable]): 自訂的成交處理函數
    
    Examples:
        >>> def on_order(order):
        ...     print(f"收到委託: {order.order_id}")
        >>> def on_deal(deal):
        ...     print(f"成交價格: {deal.price}")
        >>> handler = OrderDealCallbackHandler(
        ...     custom_order_handler=on_order,
        ...     custom_deal_handler=on_deal
        ... )
    """
    
    def __init__(
        self,
        custom_order_handler: Optional[Callable[[Any], None]] = None,
        custom_deal_handler: Optional[Callable[[Any], None]] = None
    ) -> None:
        """
        初始化委託成交回調處理器
        
        Args:
            custom_order_handler (Optional[Callable]): 自訂的委託處理函數
            custom_deal_handler (Optional[Callable]): 自訂的成交處理函數
        
        Examples:
            >>> handler = OrderDealCallbackHandler()  # 使用預設處理
            >>> def on_order(order):
            ...     print("收到委託")
            >>> handler = OrderDealCallbackHandler(custom_order_handler=on_order)
        """
        self.orders: List[Dict[str, Any]] = []
        self.deals: List[Dict[str, Any]] = []
        self.custom_order_handler: Optional[Callable[[Any], None]] = custom_order_handler
        self.custom_deal_handler: Optional[Callable[[Any], None]] = custom_deal_handler
    
    def on_order(self, order: Any) -> None:
        """
        處理委託回調
        
        Args:
            order (Any): 委託資料物件
        
        Examples:
            >>> handler = OrderDealCallbackHandler()
            >>> # 模擬接收委託
            >>> class MockOrder:
            ...     order_id = "123"
            >>> handler.on_order(MockOrder())
        
        Raises:
            Exception: 處理委託過程中的錯誤
        """
        try:
            # 儲存委託資料
            order_data = {
                "timestamp": datetime.now().isoformat()
            }
            if hasattr(order, '__dict__'):
                order_data.update(order.__dict__)
            
            self.orders.append(order_data)
            
            # 執行自訂處理函數
            if self.custom_order_handler:
                self.custom_order_handler(order)
                
        except Exception as e:
            print(f"處理委託時發生錯誤: {str(e)}")
    
    def on_deal(self, deal: Any) -> None:
        """
        處理成交回調
        
        Args:
            deal (Any): 成交資料物件
        
        Examples:
            >>> handler = OrderDealCallbackHandler()
            >>> # 模擬接收成交
            >>> class MockDeal:
            ...     price = 100.0
            >>> handler.on_deal(MockDeal())
        
        Raises:
            Exception: 處理成交過程中的錯誤
        """
        try:
            # 儲存成交資料
            deal_data = {
                "timestamp": datetime.now().isoformat()
            }
            if hasattr(deal, '__dict__'):
                deal_data.update(deal.__dict__)
            
            self.deals.append(deal_data)
            
            # 執行自訂處理函數
            if self.custom_deal_handler:
                self.custom_deal_handler(deal)
                
        except Exception as e:
            print(f"處理成交時發生錯誤: {str(e)}")
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """
        取得所有委託記錄
        
        Returns:
            List[Dict[str, Any]]: 委託記錄列表
        
        Examples:
            >>> handler = OrderDealCallbackHandler()
            >>> orders = handler.get_orders()
            >>> print(f"共有 {len(orders)} 筆委託")
        """
        return self.orders
    
    def get_deals(self) -> List[Dict[str, Any]]:
        """
        取得所有成交記錄
        
        Returns:
            List[Dict[str, Any]]: 成交記錄列表
        
        Examples:
            >>> handler = OrderDealCallbackHandler()
            >>> deals = handler.get_deals()
            >>> print(f"共有 {len(deals)} 筆成交")
        """
        return self.deals
