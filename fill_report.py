"""
量化交易系統 - 成交回報模組

此模組負責取得並處理訂單成交資訊，記錄成交價格、數量與時間。
"""

import shioaji as sj
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime


class FillReport:
    """
    負責取得並處理訂單成交資訊，記錄成交價格、數量與時間。
    
    此類別提供成交回報的接收、記錄與查詢功能，當訂單成交時會自動
    接收成交事件並記錄到歷史中。
    
    Attributes:
        api (sj.Shioaji): Shioaji API 實例
        fills (List[Dict[str, Any]]): 成交記錄列表
        callbacks (List[Callable]): 成交事件回調函數列表
    
    Examples:
        >>> from authentication import Authentication
        >>> 
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> 
        >>> fill_report = FillReport(auth.api)
        >>> 
        >>> # 註冊回調函數
        >>> def on_fill(trade, status):
        ...     print(f"成交：{status.code} {status.qty}股 @ {status.price}")
        >>> 
        >>> fill_report.register_callback(on_fill)
        >>> 
        >>> # 查詢成交記錄
        >>> fills = fill_report.get_fills()
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化 FillReport 實例。
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 實例
        
        Raises:
            ValueError: 當 api 參數為 None 時
        """
        if api is None:
            raise ValueError("api 參數不可為 None")
        
        self.api: sj.Shioaji = api
        self.fills: List[Dict[str, Any]] = []
        self.callbacks: List[Callable[[Any, Any], None]] = []
        
        # 設定成交回報 callback
        self._setup_fill_callback()
    
    def _setup_fill_callback(self) -> None:
        """
        設定 Shioaji API 的成交回報 callback 函數。
        
        Raises:
            RuntimeError: 當設定 callback 失敗時
        """
        try:
            # 定義內部 callback 函數
            @self.api.on_order_status
            def order_callback(trade, status):
                """處理訂單狀態更新事件"""
                # 檢查是否為成交事件
                if status.status == sj.constant.Status.Filled or status.status == sj.constant.Status.PartFilled:
                    self._on_fill_update(trade, status)
        except AttributeError as e:
            raise RuntimeError(f"設定成交回報 callback 失敗：{e}") from e
    
    def _on_fill_update(self, trade: Any, status: Any) -> None:
        """
        處理成交更新事件。
        
        當收到成交事件時，此方法會被自動呼叫，記錄成交資訊並
        觸發所有已註冊的 callback 函數。
        
        Args:
            trade: 交易物件
            status: 訂單狀態物件
        """
        # 記錄成交資訊
        fill_record = {
            'timestamp': datetime.now(),
            'order_id': status.id if hasattr(status, 'id') else None,
            'contract_code': status.code if hasattr(status, 'code') else None,
            'action': status.action if hasattr(status, 'action') else None,
            'price': float(status.price) if hasattr(status, 'price') else 0.0,
            'quantity': int(status.qty) if hasattr(status, 'qty') else 0,
            'filled_quantity': int(status.deal_quantity) if hasattr(status, 'deal_quantity') else 0,
            'status': status.status.value if hasattr(status, 'status') else None,
            'order_time': status.order_datetime if hasattr(status, 'order_datetime') else None,
            'deal_time': status.deal_time if hasattr(status, 'deal_time') else None
        }
        
        self.fills.append(fill_record)
        
        # 呼叫所有已註冊的 callback 函數
        for callback in self.callbacks:
            try:
                callback(trade, status)
            except Exception as e:
                print(f"成交回報 callback 執行錯誤：{e}")
    
    def register_callback(self, callback: Callable[[Any, Any], None]) -> None:
        """
        註冊成交事件回調函數。
        
        將回調函數加入到回調列表中。當有成交事件發生時，所有已註冊的
        回調函數都會被依序呼叫。
        
        Args:
            callback (Callable[[Any, Any], None]): 
                回調函數，接受兩個參數：
                - trade: 交易物件
                - status: 訂單狀態物件
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> def my_callback(trade, status):
            ...     print(f"成交通知：{status.code} {status.qty}股")
            >>> fill_report.register_callback(my_callback)
        
        Raises:
            ValueError: 當 callback 不是可呼叫物件時
        """
        if not callable(callback):
            raise ValueError("callback 必須是可呼叫的函數")
        
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[Any, Any], None]) -> bool:
        """
        取消註冊成交事件回調函數。
        
        Args:
            callback (Callable[[Any, Any], None]): 要移除的回調函數
        
        Returns:
            bool: 成功移除返回 True，函數不在列表中返回 False
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fill_report.register_callback(my_callback)
            >>> fill_report.unregister_callback(my_callback)
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
    
    def get_fills(self) -> List[Dict[str, Any]]:
        """
        取得所有成交記錄。
        
        Returns:
            List[Dict[str, Any]]: 成交記錄列表，每筆記錄包含：
                - timestamp: 記錄時間
                - order_id: 訂單編號
                - contract_code: 商品代碼
                - action: 買賣方向
                - price: 成交價格
                - quantity: 委託數量
                - filled_quantity: 已成交數量
                - status: 訂單狀態
                - order_time: 下單時間
                - deal_time: 成交時間
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fills = fill_report.get_fills()
            >>> for fill in fills:
            ...     print(f"{fill['contract_code']}: {fill['filled_quantity']}股 @ {fill['price']}")
        """
        return self.fills.copy()
    
    def get_fills_by_contract(self, contract_code: str) -> List[Dict[str, Any]]:
        """
        取得指定商品的成交記錄。
        
        Args:
            contract_code (str): 商品代碼
        
        Returns:
            List[Dict[str, Any]]: 符合條件的成交記錄列表
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fills = fill_report.get_fills_by_contract("2330")
            >>> print(f"台積電成交 {len(fills)} 筆")
        
        Raises:
            ValueError: 當 contract_code 為空字串時
        """
        if not contract_code:
            raise ValueError("contract_code 不可為空")
        
        return [
            fill for fill in self.fills
            if fill.get('contract_code') == contract_code
        ]
    
    def get_fills_by_order_id(self, order_id: str) -> List[Dict[str, Any]]:
        """
        取得指定訂單的成交記錄。
        
        Args:
            order_id (str): 訂單編號
        
        Returns:
            List[Dict[str, Any]]: 符合條件的成交記錄列表
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fills = fill_report.get_fills_by_order_id("ORDER123")
            >>> for fill in fills:
            ...     print(f"成交：{fill['filled_quantity']}股")
        
        Raises:
            ValueError: 當 order_id 為空字串時
        """
        if not order_id:
            raise ValueError("order_id 不可為空")
        
        return [
            fill for fill in self.fills
            if fill.get('order_id') == order_id
        ]
    
    def get_total_filled_quantity(self, contract_code: str) -> int:
        """
        計算指定商品的總成交數量。
        
        Args:
            contract_code (str): 商品代碼
        
        Returns:
            int: 總成交數量（單位：股）
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> total = fill_report.get_total_filled_quantity("2330")
            >>> print(f"台積電總成交：{total} 股")
        
        Raises:
            ValueError: 當 contract_code 為空字串時
        """
        if not contract_code:
            raise ValueError("contract_code 不可為空")
        
        fills = self.get_fills_by_contract(contract_code)
        return sum(fill.get('filled_quantity', 0) for fill in fills)
    
    def get_average_fill_price(self, contract_code: str) -> float:
        """
        計算指定商品的平均成交價格。
        
        Args:
            contract_code (str): 商品代碼
        
        Returns:
            float: 平均成交價格，無成交記錄時返回 0.0
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> avg_price = fill_report.get_average_fill_price("2330")
            >>> print(f"台積電平均成交價：{avg_price}")
        
        Raises:
            ValueError: 當 contract_code 為空字串時
        """
        if not contract_code:
            raise ValueError("contract_code 不可為空")
        
        fills = self.get_fills_by_contract(contract_code)
        
        if not fills:
            return 0.0
        
        total_amount = sum(
            fill.get('price', 0.0) * fill.get('filled_quantity', 0)
            for fill in fills
        )
        total_quantity = sum(fill.get('filled_quantity', 0) for fill in fills)
        
        if total_quantity == 0:
            return 0.0
        
        return total_amount / total_quantity
    
    def get_fill_summary(self) -> Dict[str, Any]:
        """
        取得成交統計摘要。
        
        Returns:
            Dict[str, Any]: 成交統計資訊，包含：
                - total_fills: 總成交筆數
                - unique_contracts: 不重複的商品數量
                - total_quantity: 總成交數量
                - contracts_summary: 各商品的成交摘要
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> summary = fill_report.get_fill_summary()
            >>> print(f"總成交筆數：{summary['total_fills']}")
            >>> print(f"交易商品數：{summary['unique_contracts']}")
        """
        contracts = {}
        total_quantity = 0
        
        for fill in self.fills:
            contract_code = fill.get('contract_code', 'Unknown')
            filled_qty = fill.get('filled_quantity', 0)
            
            if contract_code not in contracts:
                contracts[contract_code] = {
                    'count': 0,
                    'total_quantity': 0,
                    'average_price': 0.0
                }
            
            contracts[contract_code]['count'] += 1
            contracts[contract_code]['total_quantity'] += filled_qty
            total_quantity += filled_qty
        
        # 計算各商品的平均價格
        for contract_code in contracts:
            contracts[contract_code]['average_price'] = self.get_average_fill_price(contract_code)
        
        return {
            'total_fills': len(self.fills),
            'unique_contracts': len(contracts),
            'total_quantity': total_quantity,
            'contracts_summary': contracts
        }
    
    def clear_fills(self) -> None:
        """
        清空成交記錄。
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fill_report.clear_fills()
        """
        self.fills.clear()
    
    def get_callback_count(self) -> int:
        """
        取得已註冊的回調函數數量。
        
        Returns:
            int: 回調函數數量
        
        Examples:
            >>> fill_report = FillReport(api)
            >>> fill_report.register_callback(my_callback)
            >>> fill_report.get_callback_count()
            1
        """
        return len(self.callbacks)
