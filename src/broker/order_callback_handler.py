"""
委託回報處理器模組

此模組負責處理來自永豐證券 Shioaji SDK 的委託回報事件。
"""

import logging
from typing import Protocol
from .callback_handler_interface import ICallbackHandler


class OrderEventListener(Protocol):
    """委託事件監聽器協議"""
    
    def on_order_status_changed(self, order_status: dict) -> None:
        """
        當委託狀態改變時觸發
        
        Args:
            order_status (dict): 委託狀態資訊
        """
        ...
    
    def on_deal_received(self, deal_info: dict) -> None:
        """
        當收到成交回報時觸發
        
        Args:
            deal_info (dict): 成交資訊
        """
        ...


class OrderCallbackHandler(ICallbackHandler):
    """
    委託回報處理器
    
    負責接收和處理來自 Shioaji SDK 的委託回報，
    並通知註冊的監聽器。
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        初始化委託回報處理器
        
        Args:
            logger (logging.Logger): 日誌記錄器，如果為 None 則使用預設記錄器
        """
        self._listeners: list[OrderEventListener] = []
        self._logger = logger or logging.getLogger(__name__)
    
    def register_listener(self, listener: OrderEventListener) -> None:
        """
        註冊委託事件監聽器
        
        Args:
            listener (OrderEventListener): 要註冊的監聽器
        
        Examples:
            >>> handler = OrderCallbackHandler()
            >>> listener = MyOrderListener()
            >>> handler.register_listener(listener)
        
        Raises:
            TypeError: 當 listener 不符合 OrderEventListener 協議時
        """
        if not hasattr(listener, 'on_order_status_changed') or \
           not hasattr(listener, 'on_deal_received'):
            raise TypeError("Listener must implement OrderEventListener protocol")
        
        self._listeners.append(listener)
    
    def remove_listener(self, listener: OrderEventListener) -> None:
        """
        移除委託事件監聽器
        
        Args:
            listener (OrderEventListener): 要移除的監聽器
        
        Examples:
            >>> handler = OrderCallbackHandler()
            >>> listener = MyOrderListener()
            >>> handler.register_listener(listener)
            >>> handler.remove_listener(listener)
        
        Raises:
            ValueError: 當 listener 不在已註冊列表中時
        """
        if listener not in self._listeners:
            raise ValueError("Listener not found in registered listeners")
        
        self._listeners.remove(listener)
    
    def handle_order_callback(self, stat: int, msg: dict) -> None:
        """
        處理委託回報回調
        
        這是 Shioaji SDK 的回調函數，當委託狀態變更時會被調用。
        
        Args:
            stat (int): 狀態碼
            msg (dict): 委託訊息字典，包含委託狀態資訊
        
        Examples:
            >>> handler = OrderCallbackHandler()
            >>> # 由 Shioaji SDK 自動調用
            >>> # api.set_order_callback(handler.handle_order_callback)
        
        Raises:
            ValueError: 當 msg 格式不正確時
        """
        if not isinstance(msg, dict):
            raise ValueError(f"Message must be a dict, got {type(msg)}")
        
        order_status = self._parse_order_status(stat, msg)
        
        for listener in self._listeners:
            try:
                listener.on_order_status_changed(order_status)
            except (AttributeError, TypeError) as e:
                # 記錄錯誤但繼續通知其他監聽器
                self._logger.error(f"Error notifying listener {listener}: {e}", exc_info=True)
            except ValueError as e:
                self._logger.error(f"Invalid data when notifying listener {listener}: {e}", exc_info=True)
    
    def handle_deal_callback(self, stat: int, msg: dict) -> None:
        """
        處理成交回報回調
        
        這是 Shioaji SDK 的回調函數，當收到成交回報時會被調用。
        
        Args:
            stat (int): 狀態碼
            msg (dict): 成交訊息字典，包含成交資訊
        
        Examples:
            >>> handler = OrderCallbackHandler()
            >>> # 由 Shioaji SDK 自動調用
            >>> # api.set_deal_callback(handler.handle_deal_callback)
        
        Raises:
            ValueError: 當 msg 格式不正確時
        """
        if not isinstance(msg, dict):
            raise ValueError(f"Message must be a dict, got {type(msg)}")
        
        deal_info = self._parse_deal_info(stat, msg)
        
        for listener in self._listeners:
            try:
                listener.on_deal_received(deal_info)
            except (AttributeError, TypeError) as e:
                # 記錄錯誤但繼續通知其他監聽器
                self._logger.error(f"Error notifying listener {listener}: {e}", exc_info=True)
            except ValueError as e:
                self._logger.error(f"Invalid data when notifying listener {listener}: {e}", exc_info=True)
    
    def _parse_order_status(self, stat: int, msg: dict) -> dict:
        """
        解析委託狀態訊息
        
        Args:
            stat (int): 狀態碼
            msg (dict): 原始委託訊息
        
        Returns:
            dict: 標準化的委託狀態資訊
        
        Raises:
            KeyError: 當必要欄位缺失時
        """
        try:
            return {
                'status_code': stat,
                'order_id': msg.get('order_id', ''),
                'status': msg.get('status', ''),
                'order_quantity': msg.get('order_quantity', 0),
                'deal_quantity': msg.get('deal_quantity', 0),
                'order_price': msg.get('order_price', 0.0),
                'stock_id': msg.get('stock_id', ''),
                'operation': msg.get('operation', ''),
                'order_time': msg.get('order_time', ''),
                'raw_message': msg
            }
        except KeyError as e:
            raise KeyError(f"Missing required field in order message: {e}")
    
    def _parse_deal_info(self, stat: int, msg: dict) -> dict:
        """
        解析成交資訊
        
        Args:
            stat (int): 狀態碼
            msg (dict): 原始成交訊息
        
        Returns:
            dict: 標準化的成交資訊
        
        Raises:
            KeyError: 當必要欄位缺失時
        """
        try:
            return {
                'status_code': stat,
                'order_id': msg.get('order_id', ''),
                'deal_quantity': msg.get('deal_quantity', 0),
                'deal_price': msg.get('deal_price', 0.0),
                'stock_id': msg.get('stock_id', ''),
                'deal_time': msg.get('deal_time', ''),
                'raw_message': msg
            }
        except KeyError as e:
            raise KeyError(f"Missing required field in deal message: {e}")
