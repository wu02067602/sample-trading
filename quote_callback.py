"""報價回調處理模組

此模組負責處理永豐 Shioaji API 的報價回調功能。
"""

import shioaji as sj
from typing import Optional, Callable, Any, Dict, List
from datetime import datetime
import logging


class QuoteCallback:
    """負責處理接收到的報價資料
    
    此類別封裝了永豐 Shioaji API 的報價回調處理功能，
    提供自訂回調函數的註冊與管理。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化報價回調處理器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._quote_callbacks: List[Callable] = []
        self._order_callbacks: List[Callable] = []
        self._latest_quotes: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        self._callback_registered: bool = False
    
    def set_quote_callback(self, callback: Callable[[str, Any], None]) -> None:
        """設定報價回調函數
        
        註冊一個回調函數，當收到報價資料時會被呼叫。
        支援多個回調函數，所有已註冊的回調都會被觸發。
        
        Args:
            callback (Callable[[str, Any], None]): 
                回調函數，接收兩個參數：
                - exchange (str): 交易所代碼
                - tick (Any): 報價資料物件
        
        Examples:
            >>> def my_quote_handler(exchange, tick):
            ...     print(f"收到報價: {tick.code} - {tick.close}")
            >>> 
            >>> callback_handler = QuoteCallback(api)
            >>> callback_handler.set_quote_callback(my_quote_handler)
        
        Raises:
            ValueError: 當 callback 不是可呼叫的函數時
        """
        if not callable(callback):
            raise ValueError("Callback 必須是可呼叫的函數")
        
        # 將回調添加到列表中
        self._quote_callbacks.append(callback)
        self._logger.info(f"已註冊報價回調函數，目前共 {len(self._quote_callbacks)} 個回調")
        
        # 只在第一次註冊時設定 API callback
        if not self._callback_registered:
            def master_callback(exchange: str, tick: Any) -> None:
                """主回調函數，用於呼叫所有已註冊的使用者回調"""
                try:
                    code = getattr(tick, 'code', 'N/A')
                    close = getattr(tick, 'close', 'N/A')
                    # 記錄收到報價
                    self._logger.info(f"[QuoteCallback] 收到報價更新: {code} @ {close}")
                    
                    # 儲存最新報價
                    self._latest_quotes[tick.code] = {
                        'exchange': exchange,
                        'tick': tick,
                        'timestamp': datetime.now()
                    }
                    
                    # 呼叫所有已註冊的使用者回調函數
                    for user_callback in self._quote_callbacks:
                        try:
                            user_callback(exchange, tick)
                        except Exception as e:
                            self._logger.error(f"呼叫使用者回調函數時發生錯誤: {e}")
                    
                except AttributeError as e:
                    self._logger.error(f"報價資料格式錯誤: {e}")
                except KeyError as e:
                    self._logger.error(f"報價資料缺少必要欄位: {e}")
            
            # 註冊主回調到 API
            self._api.quote.set_on_tick_stk_v1_callback(master_callback)
            self._callback_registered = True
            self._logger.info("主回調函數已註冊到 Shioaji API")
    
    def set_order_callback(self, callback: Callable[[Any, Any], None]) -> None:
        """設定委託回報回調函數
        
        註冊一個回調函數，當收到委託或成交回報時會被呼叫。
        
        Args:
            callback (Callable[[Any, Any], None]): 
                回調函數，接收兩個參數：
                - stat: 委託狀態
                - msg: 委託訊息
        
        Examples:
            >>> def my_order_handler(stat, msg):
            ...     print(f"委託回報: {stat} - {msg}")
            >>> 
            >>> callback_handler = QuoteCallback(api)
            >>> callback_handler.set_order_callback(my_order_handler)
        
        Raises:
            ValueError: 當 callback 不是可呼叫的函數時
        """
        if not callable(callback):
            raise ValueError("Callback 必須是可呼叫的函數")
        
        # 包裝使用者的回調函數
        def wrapped_callback(stat: Any, msg: Any) -> None:
            """包裝的回調函數，用於記錄並呼叫使用者函數"""
            try:
                # 記錄委託回報
                self._logger.info(f"委託回報 - 狀態: {stat}, 訊息: {msg}")
                
                # 呼叫使用者的回調函數
                callback(stat, msg)
                
            except AttributeError as e:
                self._logger.error(f"委託回報資料格式錯誤: {e}")
        
        # 註冊到 API
        self._api.set_order_callback(wrapped_callback)
        self._order_callbacks.append(callback)
    
    def get_latest_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """取得指定商品的最新報價
        
        Args:
            code (str): 商品代碼
        
        Returns:
            Optional[Dict[str, Any]]: 最新報價資料，包含 exchange, tick, timestamp
                                      如果沒有報價資料則返回 None
        
        Examples:
            >>> callback_handler = QuoteCallback(api)
            >>> latest = callback_handler.get_latest_quote("2330")
            >>> if latest:
            ...     print(f"最新價格: {latest['tick'].close}")
        
        Raises:
            ValueError: 當 code 為空字串時
        """
        if not code:
            raise ValueError("商品代碼不可為空")
        
        return self._latest_quotes.get(code)
    
    def get_all_latest_quotes(self) -> Dict[str, Dict[str, Any]]:
        """取得所有已訂閱商品的最新報價
        
        Returns:
            Dict[str, Dict[str, Any]]: 所有商品的最新報價，鍵為商品代碼
        
        Examples:
            >>> callback_handler = QuoteCallback(api)
            >>> all_quotes = callback_handler.get_all_latest_quotes()
            >>> for code, data in all_quotes.items():
            ...     print(f"{code}: {data['tick'].close}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._latest_quotes.copy()
    
    def clear_callbacks(self) -> None:
        """清除所有已註冊的回調函數
        
        Examples:
            >>> callback_handler = QuoteCallback(api)
            >>> callback_handler.set_quote_callback(my_handler)
            >>> callback_handler.clear_callbacks()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._quote_callbacks.clear()
        self._order_callbacks.clear()
        self._latest_quotes.clear()
