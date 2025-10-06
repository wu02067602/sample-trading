"""
報價回調處理模組

此模組提供報價和訂單回調的處理功能。
"""

from typing import Callable, Optional, Any, Dict
from abc import ABC, abstractmethod


class QuoteCallback(ABC):
    """
    報價回調抽象基類
    
    定義報價回調處理的介面。
    """
    
    @abstractmethod
    def on_quote(self, topic: str, data: Any) -> None:
        """
        處理報價資料的抽象方法。
        
        Args:
            topic (str): 報價主題（商品代碼）
            data (Any): 報價資料物件
        
        Returns:
            None
        
        Raises:
            None
        """
        pass


class OrderCallback(ABC):
    """
    訂單回調抽象基類
    
    定義訂單回調處理的介面。
    """
    
    @abstractmethod
    def on_order(self, state: str, data: Dict[str, Any]) -> None:
        """
        處理訂單狀態更新的抽象方法。
        
        Args:
            state (str): 訂單狀態
            data (Dict[str, Any]): 訂單資料字典
        
        Returns:
            None
        
        Raises:
            None
        """
        pass


class DefaultQuoteCallback(QuoteCallback):
    """
    預設報價回調實作
    
    提供基本的報價資料處理功能。
    
    Attributes:
        callback_func (Optional[Callable]): 自訂的回調函數
        quote_data (Dict[str, Any]): 儲存最新報價資料
    """
    
    def __init__(self, callback_func: Optional[Callable] = None):
        """
        初始化預設報價回調。
        
        Args:
            callback_func (Optional[Callable]): 自訂的回調函數，
                                                 接收 (topic, data) 參數
        
        Examples:
            >>> def my_callback(topic, data):
            ...     print(f"收到報價: {topic}")
            >>> handler = DefaultQuoteCallback(my_callback)
        
        Raises:
            None
        """
        self.callback_func = callback_func
        self.quote_data: Dict[str, Any] = {}
    
    def on_quote(self, topic: str, data: Any) -> None:
        """
        處理報價資料。
        
        儲存報價資料並觸發自訂回調函數（如果有設定）。
        
        Args:
            topic (str): 報價主題（商品代碼）
            data (Any): 報價資料物件
        
        Returns:
            None
        
        Examples:
            >>> handler = DefaultQuoteCallback()
            >>> handler.on_quote("TSE2330", quote_data)
            >>> latest = handler.get_latest_quote("TSE2330")
        
        Raises:
            None
        """
        # 儲存最新報價
        self.quote_data[topic] = data
        
        # 如果有自訂回調函數，則呼叫它
        if self.callback_func:
            try:
                self.callback_func(topic, data)
            except TypeError as e:
                # 回調函數參數錯誤
                raise TypeError(f"回調函數參數錯誤: {e}")
            except AttributeError as e:
                # 回調函數不可呼叫
                raise AttributeError(f"回調函數不可呼叫: {e}")
    
    def get_latest_quote(self, topic: str) -> Optional[Any]:
        """
        取得指定商品的最新報價。
        
        Args:
            topic (str): 報價主題（商品代碼）
        
        Returns:
            Optional[Any]: 最新報價資料，如果沒有則返回 None
        
        Examples:
            >>> handler = DefaultQuoteCallback()
            >>> quote = handler.get_latest_quote("TSE2330")
        
        Raises:
            None
        """
        return self.quote_data.get(topic)
    
    def clear_quote_data(self) -> None:
        """
        清除所有報價資料。
        
        Returns:
            None
        
        Examples:
            >>> handler = DefaultQuoteCallback()
            >>> handler.clear_quote_data()
        
        Raises:
            None
        """
        self.quote_data.clear()


class DefaultOrderCallback(OrderCallback):
    """
    預設訂單回調實作
    
    提供基本的訂單狀態處理功能。
    
    Attributes:
        callback_func (Optional[Callable]): 自訂的回調函數
        order_history (list[Dict[str, Any]]): 儲存訂單歷史記錄
    """
    
    def __init__(self, callback_func: Optional[Callable] = None):
        """
        初始化預設訂單回調。
        
        Args:
            callback_func (Optional[Callable]): 自訂的回調函數，
                                                 接收 (state, data) 參數
        
        Examples:
            >>> def my_callback(state, data):
            ...     print(f"訂單狀態: {state}")
            >>> handler = DefaultOrderCallback(my_callback)
        
        Raises:
            None
        """
        self.callback_func = callback_func
        self.order_history: list[Dict[str, Any]] = []
    
    def on_order(self, state: str, data: Dict[str, Any]) -> None:
        """
        處理訂單狀態更新。
        
        記錄訂單歷史並觸發自訂回調函數（如果有設定）。
        
        Args:
            state (str): 訂單狀態
            data (Dict[str, Any]): 訂單資料字典
        
        Returns:
            None
        
        Examples:
            >>> handler = DefaultOrderCallback()
            >>> handler.on_order("Filled", order_data)
            >>> history = handler.get_order_history()
        
        Raises:
            None
        """
        # 記錄訂單歷史
        order_record = {
            "state": state,
            "data": data
        }
        self.order_history.append(order_record)
        
        # 如果有自訂回調函數，則呼叫它
        if self.callback_func:
            try:
                self.callback_func(state, data)
            except TypeError as e:
                # 回調函數參數錯誤
                raise TypeError(f"回調函數參數錯誤: {e}")
            except AttributeError as e:
                # 回調函數不可呼叫
                raise AttributeError(f"回調函數不可呼叫: {e}")
    
    def get_order_history(self) -> list[Dict[str, Any]]:
        """
        取得訂單歷史記錄。
        
        Returns:
            list[Dict[str, Any]]: 訂單歷史記錄列表
        
        Examples:
            >>> handler = DefaultOrderCallback()
            >>> history = handler.get_order_history()
        
        Raises:
            None
        """
        return self.order_history.copy()
    
    def clear_order_history(self) -> None:
        """
        清除訂單歷史記錄。
        
        Returns:
            None
        
        Examples:
            >>> handler = DefaultOrderCallback()
            >>> handler.clear_order_history()
        
        Raises:
            None
        """
        self.order_history.clear()
