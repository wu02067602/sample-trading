"""
量化交易系統 - 委託回報模組

此模組負責取得並處理委託單狀態資訊，追蹤委託單的各種狀態變化。
"""

import shioaji as sj
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime


class OrderReport:
    """
    負責取得並處理委託單狀態資訊，追蹤委託單的各種狀態變化。
    
    此類別提供委託回報的接收、記錄與查詢功能，當委託單狀態變化時
    會自動接收事件並記錄到歷史中。
    
    Attributes:
        api (sj.Shioaji): Shioaji API 實例
        orders (List[Dict[str, Any]]): 委託記錄列表
        callbacks (List[Callable]): 委託事件回調函數列表
    
    Examples:
        >>> from authentication import Authentication
        >>> 
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> 
        >>> order_report = OrderReport(auth.api)
        >>> 
        >>> # 註冊回調函數
        >>> def on_order_update(trade, status):
        ...     print(f"委託狀態：{status.status}")
        >>> 
        >>> order_report.register_callback(on_order_update)
        >>> 
        >>> # 查詢委託記錄
        >>> orders = order_report.get_orders()
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化 OrderReport 實例。
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 實例
        
        Raises:
            ValueError: 當 api 參數為 None 時
        """
        if api is None:
            raise ValueError("api 參數不可為 None")
        
        self.api: sj.Shioaji = api
        self.orders: List[Dict[str, Any]] = []
        self.callbacks: List[Callable[[Any, Any], None]] = []
        
        # 設定委託回報 callback
        self._setup_order_callback()
    
    def _setup_order_callback(self) -> None:
        """
        設定 Shioaji API 的委託回報 callback 函數。
        
        Raises:
            RuntimeError: 當設定 callback 失敗時
        """
        try:
            # 定義內部 callback 函數
            @self.api.on_order_status
            def order_callback(trade, status):
                """處理訂單狀態更新事件"""
                self._on_order_update(trade, status)
        except AttributeError as e:
            raise RuntimeError(f"設定委託回報 callback 失敗：{e}") from e
    
    def _on_order_update(self, trade: Any, status: Any) -> None:
        """
        處理委託更新事件。
        
        當收到委託狀態變化時，此方法會被自動呼叫，記錄委託資訊並
        觸發所有已註冊的 callback 函數。
        
        Args:
            trade: 交易物件
            status: 訂單狀態物件
        """
        # 記錄委託資訊
        order_record = {
            'timestamp': datetime.now(),
            'order_id': status.id if hasattr(status, 'id') else None,
            'contract_code': status.code if hasattr(status, 'code') else None,
            'action': status.action if hasattr(status, 'action') else None,
            'price': float(status.price) if hasattr(status, 'price') else 0.0,
            'quantity': int(status.qty) if hasattr(status, 'qty') else 0,
            'filled_quantity': int(status.deal_quantity) if hasattr(status, 'deal_quantity') else 0,
            'status': status.status.value if hasattr(status, 'status') else None,
            'order_time': status.order_datetime if hasattr(status, 'order_datetime') else None,
            'modified_price': float(status.modified_price) if hasattr(status, 'modified_price') else 0.0,
            'cancel_quantity': int(status.cancel_quantity) if hasattr(status, 'cancel_quantity') else 0
        }
        
        self.orders.append(order_record)
        
        # 呼叫所有已註冊的 callback 函數
        for callback in self.callbacks:
            try:
                callback(trade, status)
            except Exception as e:
                print(f"委託回報 callback 執行錯誤：{e}")
    
    def register_callback(self, callback: Callable[[Any, Any], None]) -> None:
        """
        註冊委託事件回調函數。
        
        將回調函數加入到回調列表中。當有委託狀態變化時，所有已註冊的
        回調函數都會被依序呼叫。
        
        Args:
            callback (Callable[[Any, Any], None]): 
                回調函數，接受兩個參數：
                - trade: 交易物件
                - status: 訂單狀態物件
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> def my_callback(trade, status):
            ...     print(f"委託更新：{status.status}")
            >>> order_report.register_callback(my_callback)
        
        Raises:
            ValueError: 當 callback 不是可呼叫物件時
        """
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[Any, Any], None]) -> bool:
        """
        取消註冊委託事件回調函數。
        
        Args:
            callback (Callable[[Any, Any], None]): 要移除的回調函數
        
        Returns:
            bool: 成功移除返回 True，函數不在列表中返回 False
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> order_report.register_callback(my_callback)
            >>> order_report.unregister_callback(my_callback)
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
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """
        取得所有委託記錄。
        
        Returns:
            List[Dict[str, Any]]: 委託記錄列表，每筆記錄包含：
                - timestamp: 記錄時間
                - order_id: 訂單編號
                - contract_code: 商品代碼
                - action: 買賣方向
                - price: 委託價格
                - quantity: 委託數量
                - filled_quantity: 已成交數量
                - status: 訂單狀態
                - order_time: 下單時間
                - modified_price: 修改後價格
                - cancel_quantity: 取消數量
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> orders = order_report.get_orders()
            >>> for order in orders:
            ...     print(f"{order['contract_code']}: {order['status']}")
        """
        return self.orders.copy()
    
    def get_orders_by_contract(self, contract_code: str) -> List[Dict[str, Any]]:
        """
        取得指定商品的委託記錄。
        
        Args:
            contract_code (str): 商品代碼
        
        Returns:
            List[Dict[str, Any]]: 符合條件的委託記錄列表
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> orders = order_report.get_orders_by_contract("2330")
            >>> print(f"台積電委託 {len(orders)} 筆")
        
        Raises:
            ValueError: 當 contract_code 為空字串時
        """
        if not contract_code:
            raise ValueError("contract_code 不可為空")
        
        return [
            order for order in self.orders
            if order.get('contract_code') == contract_code
        ]
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        根據訂單編號取得委託記錄。
        
        Args:
            order_id (str): 訂單編號
        
        Returns:
            Optional[Dict[str, Any]]: 委託記錄，找不到時返回 None
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> order = order_report.get_order_by_id("ORDER123")
            >>> if order:
            ...     print(f"委託狀態：{order['status']}")
        
        Raises:
            ValueError: 當 order_id 為空字串時
        """
        if not order_id:
            raise ValueError("order_id 不可為空")
        
        # 反向搜尋，返回最新的記錄
        for order in reversed(self.orders):
            if order.get('order_id') == order_id:
                return order
        
        return None
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        取得指定狀態的委託記錄。
        
        Args:
            status (str): 訂單狀態（例如：'Filled', 'PartFilled', 'Submitted', 'Cancelled'）
        
        Returns:
            List[Dict[str, Any]]: 符合條件的委託記錄列表
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> filled_orders = order_report.get_orders_by_status("Filled")
            >>> print(f"已成交訂單：{len(filled_orders)} 筆")
        
        Raises:
            ValueError: 當 status 為空字串時
        """
        if not status:
            raise ValueError("status 不可為空")
        
        return [
            order for order in self.orders
            if order.get('status') == status
        ]
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """
        取得所有待成交的委託記錄。
        
        Returns:
            List[Dict[str, Any]]: 待成交的委託記錄列表
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> pending = order_report.get_pending_orders()
            >>> print(f"待成交訂單：{len(pending)} 筆")
        """
        pending_statuses = ['Submitted', 'PartFilled', 'PreSubmitted']
        return [
            order for order in self.orders
            if order.get('status') in pending_statuses
        ]
    
    def get_order_summary(self) -> Dict[str, Any]:
        """
        取得委託統計摘要。
        
        Returns:
            Dict[str, Any]: 委託統計資訊，包含：
                - total_orders: 總委託筆數
                - unique_contracts: 不重複的商品數量
                - status_summary: 各狀態的訂單數量
                - contracts_summary: 各商品的委託摘要
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> summary = order_report.get_order_summary()
            >>> print(f"總委託筆數：{summary['total_orders']}")
            >>> print(f"各狀態統計：{summary['status_summary']}")
        """
        contracts = {}
        status_count = {}
        
        for order in self.orders:
            contract_code = order.get('contract_code', 'Unknown')
            status = order.get('status', 'Unknown')
            
            # 統計商品
            if contract_code not in contracts:
                contracts[contract_code] = {
                    'count': 0,
                    'total_quantity': 0,
                    'filled_quantity': 0
                }
            
            contracts[contract_code]['count'] += 1
            contracts[contract_code]['total_quantity'] += order.get('quantity', 0)
            contracts[contract_code]['filled_quantity'] += order.get('filled_quantity', 0)
            
            # 統計狀態
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            'total_orders': len(self.orders),
            'unique_contracts': len(contracts),
            'status_summary': status_count,
            'contracts_summary': contracts
        }
    
    def clear_orders(self) -> None:
        """
        清空委託記錄。
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> order_report.clear_orders()
        """
        self.orders.clear()
    
    def get_callback_count(self) -> int:
        """
        取得已註冊的回調函數數量。
        
        Returns:
            int: 回調函數數量
        
        Examples:
            >>> order_report = OrderReport(api)
            >>> order_report.register_callback(my_callback)
            >>> order_report.get_callback_count()
            1
        """
        return len(self.callbacks)
