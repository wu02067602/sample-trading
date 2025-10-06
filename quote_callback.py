"""
報價 Callback 處理模組

此模組定義了報價回調處理的抽象介面和預設實作。
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import logging
from datetime import datetime


class IQuoteCallback(ABC):
    """
    報價 Callback 抽象介面
    
    此介面定義了報價回調處理的標準方法，
    遵循依賴反轉原則，允許不同的實作。
    
    Examples:
        >>> class MyQuoteCallback(IQuoteCallback):
        ...     def on_quote(self, topic: str, quote: Any) -> None:
        ...         print(f"收到報價: {quote}")
    """
    
    @abstractmethod
    def on_quote(self, topic: str, quote: Any) -> None:
        """
        處理報價回調
        
        Args:
            topic: 訂閱主題（通常是商品代碼）
            quote: 報價資料物件
        
        Examples:
            >>> def on_quote(self, topic: str, quote: Any) -> None:
            ...     print(f"商品 {topic}: 最新價 {quote.close}")
        """
        pass


class IOrderCallback(ABC):
    """
    訂單 Callback 抽象介面
    
    此介面定義了訂單相關回調處理的標準方法。
    
    Examples:
        >>> class MyOrderCallback(IOrderCallback):
        ...     def on_order(self, stat: str, order: Any) -> None:
        ...         print(f"訂單狀態: {stat}")
        ...     def on_deal(self, stat: str, deal: Any) -> None:
        ...         print(f"成交通知: {stat}")
    """
    
    @abstractmethod
    def on_order(self, stat: str, order: Any) -> None:
        """
        處理訂單狀態回調
        
        Args:
            stat: 訂單狀態
            order: 訂單資料物件
        
        Examples:
            >>> def on_order(self, stat: str, order: Any) -> None:
            ...     if stat == "OrderState.StockOrder":
            ...         print("股票訂單更新")
        """
        pass
    
    @abstractmethod
    def on_deal(self, stat: str, deal: Any) -> None:
        """
        處理成交回調
        
        Args:
            stat: 成交狀態
            deal: 成交資料物件
        
        Examples:
            >>> def on_deal(self, stat: str, deal: Any) -> None:
            ...     print(f"成交價: {deal.price}, 數量: {deal.quantity}")
        """
        pass


class DefaultQuoteCallback(IQuoteCallback):
    """
    預設報價 Callback 實作
    
    提供基本的報價回調處理，將報價資訊記錄到日誌。
    
    Attributes:
        logger: 日誌記錄器
        custom_handler: 自訂處理函數（可選）
    
    Examples:
        >>> callback = DefaultQuoteCallback()
        >>> # 或使用自訂處理函數
        >>> def my_handler(topic, quote):
        ...     print(f"{topic}: {quote.close}")
        >>> callback = DefaultQuoteCallback(custom_handler=my_handler)
    """
    
    def __init__(self, custom_handler: Optional[Callable[[str, Any], None]] = None):
        """
        初始化預設報價 Callback
        
        Args:
            custom_handler: 自訂處理函數，接收 (topic, quote) 參數
        
        Examples:
            >>> callback = DefaultQuoteCallback()
            >>> # 或使用 lambda
            >>> callback = DefaultQuoteCallback(
            ...     custom_handler=lambda t, q: print(f"{t}: {q.close}")
            ... )
        """
        self.logger = logging.getLogger(__name__)
        self.custom_handler = custom_handler
        self.quote_count = 0
        
    def on_quote(self, topic: str, quote: Any) -> None:
        """
        處理報價回調
        
        記錄報價資訊到日誌，並調用自訂處理函數（如果有）。
        
        Args:
            topic: 訂閱主題
            quote: 報價資料物件
        
        Examples:
            >>> callback = DefaultQuoteCallback()
            >>> callback.on_quote("2330", quote_data)
            # 日誌: 收到報價 [2330]: 最新價 500.0
        """
        self.quote_count += 1
        
        try:
            # 記錄基本資訊
            if hasattr(quote, 'close') and hasattr(quote, 'datetime'):
                self.logger.info(
                    f"收到報價 [{topic}]: "
                    f"時間={quote.datetime}, "
                    f"最新價={quote.close}, "
                    f"成交量={getattr(quote, 'volume', 'N/A')}"
                )
            else:
                self.logger.info(f"收到報價 [{topic}]: {quote}")
            
            # 調用自訂處理函數
            if self.custom_handler:
                self.custom_handler(topic, quote)
                
        except Exception as e:
            self.logger.error(f"處理報價時發生錯誤: {e}")


class DefaultOrderCallback(IOrderCallback):
    """
    預設訂單 Callback 實作
    
    提供基本的訂單和成交回調處理，將資訊記錄到日誌。
    
    Attributes:
        logger: 日誌記錄器
        order_handler: 訂單自訂處理函數（可選）
        deal_handler: 成交自訂處理函數（可選）
    
    Examples:
        >>> callback = DefaultOrderCallback()
        >>> # 或使用自訂處理函數
        >>> callback = DefaultOrderCallback(
        ...     order_handler=lambda s, o: print(f"訂單: {s}"),
        ...     deal_handler=lambda s, d: print(f"成交: {s}")
        ... )
    """
    
    def __init__(
        self,
        order_handler: Optional[Callable[[str, Any], None]] = None,
        deal_handler: Optional[Callable[[str, Any], None]] = None
    ):
        """
        初始化預設訂單 Callback
        
        Args:
            order_handler: 訂單自訂處理函數，接收 (stat, order) 參數
            deal_handler: 成交自訂處理函數，接收 (stat, deal) 參數
        
        Examples:
            >>> callback = DefaultOrderCallback(
            ...     order_handler=lambda s, o: print(f"訂單狀態: {s}"),
            ...     deal_handler=lambda s, d: print(f"成交通知: {s}")
            ... )
        """
        self.logger = logging.getLogger(__name__)
        self.order_handler = order_handler
        self.deal_handler = deal_handler
        self.order_count = 0
        self.deal_count = 0
        
    def on_order(self, stat: str, order: Any) -> None:
        """
        處理訂單狀態回調
        
        Args:
            stat: 訂單狀態
            order: 訂單資料物件
        
        Examples:
            >>> callback = DefaultOrderCallback()
            >>> callback.on_order("OrderState.StockOrder", order_data)
            # 日誌: 訂單狀態更新 [OrderState.StockOrder]: ...
        """
        self.order_count += 1
        
        try:
            self.logger.info(f"訂單狀態更新 [{stat}]: {order}")
            
            # 調用自訂處理函數
            if self.order_handler:
                self.order_handler(stat, order)
                
        except Exception as e:
            self.logger.error(f"處理訂單回調時發生錯誤: {e}")
    
    def on_deal(self, stat: str, deal: Any) -> None:
        """
        處理成交回調
        
        Args:
            stat: 成交狀態
            deal: 成交資料物件
        
        Examples:
            >>> callback = DefaultOrderCallback()
            >>> callback.on_deal("OrderState.StockDeal", deal_data)
            # 日誌: 成交通知 [OrderState.StockDeal]: ...
        """
        self.deal_count += 1
        
        try:
            if hasattr(deal, 'price') and hasattr(deal, 'quantity'):
                self.logger.info(
                    f"成交通知 [{stat}]: "
                    f"商品={getattr(deal, 'code', 'N/A')}, "
                    f"價格={deal.price}, "
                    f"數量={deal.quantity}, "
                    f"動作={getattr(deal, 'action', 'N/A')}"
                )
            else:
                self.logger.info(f"成交通知 [{stat}]: {deal}")
            
            # 調用自訂處理函數
            if self.deal_handler:
                self.deal_handler(stat, deal)
                
        except Exception as e:
            self.logger.error(f"處理成交回調時發生錯誤: {e}")
