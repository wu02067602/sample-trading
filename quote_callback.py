"""
量化交易系統 - 報價回調處理模組

此模組負責接收並處理報價更新事件，將即時報價資料傳遞至相關模組。
"""

from typing import Callable, List, Dict, Any
import shioaji as sj
from datetime import datetime


class QuoteCallback:
    """
    負責接收並處理報價更新事件，將即時報價資料傳遞至相關模組。
    
    此類別提供報價回調函數的註冊與管理機制，當收到報價更新時，
    會依序呼叫所有已註冊的回調函數。
    
    Attributes:
        callbacks (List[Callable]): 已註冊的回調函數列表
        quote_history (List[Dict]): 報價歷史記錄
    
    Examples:
        >>> def my_callback(exchange, tick):
        ...     print(f"收到報價：{tick['code']} {tick['close']}")
        >>> 
        >>> callback_handler = QuoteCallback()
        >>> callback_handler.register_callback(my_callback)
        >>> # 當報價更新時，my_callback 會被自動呼叫
    """
    
    def __init__(self) -> None:
        """
        初始化 QuoteCallback 實例。
        
        建立空的回調函數列表和報價歷史記錄。
        """
        self.callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self.quote_history: List[Dict[str, Any]] = []
    
    def register_callback(
        self,
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        註冊報價更新回調函數。
        
        將回調函數加入到回調列表中。當報價更新時，所有已註冊的回調函數
        都會被依序呼叫。
        
        Args:
            callback (Callable[[str, Dict[str, Any]], None]): 
                回調函數，接受兩個參數：
                - exchange (str): 交易所名稱
                - tick (Dict[str, Any]): 報價資訊字典
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> def print_quote(exchange, tick):
            ...     print(f"{tick['code']}: {tick['close']}")
            >>> callback_handler.register_callback(print_quote)
        
        Raises:
            ValueError: 當 callback 不是可呼叫物件時
        """
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        self.callbacks.append(callback)
    
    def unregister_callback(
        self,
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> bool:
        """
        取消註冊報價更新回調函數。
        
        Args:
            callback (Callable[[str, Dict[str, Any]], None]): 要移除的回調函數
        
        Returns:
            bool: 成功移除返回 True，函數不在列表中返回 False
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> callback_handler.register_callback(my_callback)
            >>> callback_handler.unregister_callback(my_callback)
            True
        
        Raises:
            ValueError: 當 callback 不是可呼叫物件時
        """
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        try:
            self.callbacks.remove(callback)
            return True
        except ValueError:
            return False
    
    def on_quote_update(self, exchange: str, tick: Dict[str, Any]) -> None:
        """
        處理報價更新事件。
        
        此方法會在收到報價更新時被 Shioaji API 呼叫。它會將報價資訊
        記錄到歷史中，並依序呼叫所有已註冊的回調函數。
        
        Args:
            exchange (str): 交易所名稱（例如：'TSE', 'OTC'）
            tick (Dict[str, Any]): 報價資訊字典，包含以下欄位：
                - code (str): 商品代碼
                - datetime (datetime): 報價時間
                - open (float): 開盤價
                - high (float): 最高價
                - low (float): 最低價
                - close (float): 最新成交價
                - volume (int): 成交量
                - total_volume (int): 總成交量
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> tick_data = {
            ...     'code': '2330',
            ...     'close': 580.0,
            ...     'volume': 1000
            ... }
            >>> callback_handler.on_quote_update('TSE', tick_data)
        
        Raises:
            ValueError: 當 exchange 為空或 tick 為 None 時
        """
        if not exchange:
            raise ValueError("exchange 不可為空")
        if tick is None:
            raise ValueError("tick 不可為 None")
        
        # 記錄報價到歷史中
        quote_record = {
            'exchange': exchange,
            'timestamp': datetime.now(),
            **tick
        }
        self.quote_history.append(quote_record)
        
        # 呼叫所有已註冊的回調函數
        for callback in self.callbacks:
            try:
                callback(exchange, tick)
            except Exception as e:
                # 記錄錯誤但不中斷其他回調的執行
                print(f"回調函數執行錯誤：{e}")
    
    def get_latest_quote(self, code: str) -> Dict[str, Any]:
        """
        取得指定商品的最新報價。
        
        Args:
            code (str): 商品代碼
        
        Returns:
            Dict[str, Any]: 最新報價資訊，找不到時返回空字典
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> latest = callback_handler.get_latest_quote("2330")
            >>> if latest:
            ...     print(f"最新價格：{latest['close']}")
        
        Raises:
            ValueError: 當 code 為空字串時
        """
        if not code:
            raise ValueError("code 不可為空")
        
        # 從歷史記錄中反向搜尋最新的報價
        for quote in reversed(self.quote_history):
            if quote.get('code') == code:
                return quote
        
        return {}
    
    def get_quote_history(
        self,
        code: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        取得指定商品的報價歷史記錄。
        
        Args:
            code (str): 商品代碼
            limit (int): 返回的最大記錄數，預設為 100
        
        Returns:
            List[Dict[str, Any]]: 報價歷史記錄列表，按時間由舊到新排序
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> history = callback_handler.get_quote_history("2330", limit=50)
            >>> for quote in history:
            ...     print(f"{quote['timestamp']}: {quote['close']}")
        
        Raises:
            ValueError: 當 code 為空或 limit 小於等於 0 時
        """
        if not code:
            raise ValueError("code 不可為空")
        if limit <= 0:
            raise ValueError("limit 必須大於 0")
        
        # 篩選指定商品的報價記錄
        filtered_history = [
            quote for quote in self.quote_history
            if quote.get('code') == code
        ]
        
        # 返回最新的 limit 筆記錄
        return filtered_history[-limit:]
    
    def clear_history(self) -> None:
        """
        清空報價歷史記錄。
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> callback_handler.clear_history()
        """
        self.quote_history.clear()
    
    def get_callback_count(self) -> int:
        """
        取得已註冊的回調函數數量。
        
        Returns:
            int: 回調函數數量
        
        Examples:
            >>> callback_handler = QuoteCallback()
            >>> callback_handler.register_callback(my_callback)
            >>> callback_handler.get_callback_count()
            1
        """
        return len(self.callbacks)
