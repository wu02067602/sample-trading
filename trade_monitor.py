"""交易監控模組

此模組負責處理永豐 Shioaji API 的成交回報與委託回報功能。
"""

import shioaji as sj
from typing import List, Optional, Any, Dict
from datetime import datetime


class TradeMonitor:
    """負責獲取已成交訂單資訊與委託訂單狀態
    
    此類別封裝了永豐 Shioaji API 的交易監控功能，
    提供成交回報、委託回報的查詢與管理。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化交易監控器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._trades_cache: Dict[str, Any] = {}
        self._last_update_time: Optional[datetime] = None
    
    def list_trades(self, account: Optional[Any] = None) -> List[Any]:
        """列出所有交易記錄
        
        取得指定帳戶的所有委託交易記錄。
        
        Args:
            account (Optional[Any]): 帳戶物件，None 表示使用預設股票帳戶
        
        Returns:
            List[Any]: Trade 物件列表，每個 Trade 包含 contract, order, status 等資訊
        
        Examples:
            >>> from login import Login
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> monitor = TradeMonitor(api)
            >>> trades = monitor.list_trades()
            >>> for trade in trades:
            ...     print(f"訂單 {trade.order.id}: {trade.status.status}")
        
        Raises:
            RuntimeError: 當尚未設定股票帳戶且未提供 account 參數時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        # 如果沒有提供帳戶，使用預設股票帳戶
        if account is None:
            if not hasattr(self._api, 'stock_account') or self._api.stock_account is None:
                raise RuntimeError("尚未設定股票帳戶，請先登入並確認帳戶設定")
            account = self._api.stock_account
        
        try:
            trades = self._api.list_trades()
            
            # 更新快取
            for trade in trades:
                if hasattr(trade.order, 'id'):
                    self._trades_cache[trade.order.id] = trade
            
            self._last_update_time = datetime.now()
            
            return trades
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的帳戶物件: {e}")
    
    def update_status(self, account: Optional[Any] = None, timeout: int = 30000) -> None:
        """更新委託狀態
        
        更新指定帳戶的所有委託單狀態，包括成交資訊。
        
        Args:
            account (Optional[Any]): 帳戶物件，None 表示使用預設股票帳戶
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.update_status()
            >>> trades = monitor.list_trades()
            >>> print(f"更新了 {len(trades)} 筆委託狀態")
        
        Raises:
            RuntimeError: 當尚未設定股票帳戶且未提供 account 參數時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if account is None:
            if not hasattr(self._api, 'stock_account') or self._api.stock_account is None:
                raise RuntimeError("尚未設定股票帳戶，請先登入並確認帳戶設定")
            account = self._api.stock_account
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            self._api.update_status(account, timeout=timeout)
            self._last_update_time = datetime.now()
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的帳戶物件: {e}")
    
    def get_trade_by_id(self, order_id: str) -> Optional[Any]:
        """根據訂單 ID 取得交易記錄
        
        Args:
            order_id (str): 訂單 ID
        
        Returns:
            Optional[Any]: Trade 物件，如果找不到則返回 None
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.list_trades()
            >>> trade = monitor.get_trade_by_id("531e27af")
            >>> if trade:
            ...     print(f"訂單狀態: {trade.status.status}")
        
        Raises:
            ValueError: 當 order_id 為空字串時
        """
        if not order_id:
            raise ValueError("Order ID 不可為空")
        
        return self._trades_cache.get(order_id)
    
    def get_filled_trades(self) -> List[Any]:
        """取得已完全成交的交易
        
        Returns:
            List[Any]: 已完全成交的 Trade 物件列表
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.update_status()
            >>> monitor.list_trades()
            >>> filled_trades = monitor.get_filled_trades()
            >>> print(f"已完全成交: {len(filled_trades)} 筆")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        filled_trades = []
        for trade in self._trades_cache.values():
            if hasattr(trade, 'status') and hasattr(trade.status, 'status'):
                # 檢查狀態是否為 Filled
                status_str = str(trade.status.status)
                if 'Filled' in status_str or 'filled' in status_str.lower():
                    filled_trades.append(trade)
        
        return filled_trades
    
    def get_filling_trades(self) -> List[Any]:
        """取得部分成交的交易
        
        Returns:
            List[Any]: 部分成交的 Trade 物件列表
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.update_status()
            >>> monitor.list_trades()
            >>> filling_trades = monitor.get_filling_trades()
            >>> print(f"部分成交: {len(filling_trades)} 筆")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        filling_trades = []
        for trade in self._trades_cache.values():
            if hasattr(trade, 'status') and hasattr(trade.status, 'status'):
                status_str = str(trade.status.status)
                if 'Filling' in status_str or 'filling' in status_str.lower():
                    filling_trades.append(trade)
        
        return filling_trades
    
    def get_submitted_trades(self) -> List[Any]:
        """取得已送出但尚未成交的交易
        
        Returns:
            List[Any]: 已送出但尚未成交的 Trade 物件列表
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.update_status()
            >>> monitor.list_trades()
            >>> submitted_trades = monitor.get_submitted_trades()
            >>> print(f"尚未成交: {len(submitted_trades)} 筆")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        submitted_trades = []
        for trade in self._trades_cache.values():
            if hasattr(trade, 'status') and hasattr(trade.status, 'status'):
                status_str = str(trade.status.status)
                if 'Submitted' in status_str or 'submitted' in status_str.lower():
                    submitted_trades.append(trade)
        
        return submitted_trades
    
    def get_deals(self, trade: Any) -> List[Any]:
        """取得指定交易的成交明細
        
        Args:
            trade (Any): Trade 物件
        
        Returns:
            List[Any]: 成交明細列表，每個元素包含成交價格、數量、時間等資訊
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> trades = monitor.list_trades()
            >>> for trade in trades:
            ...     deals = monitor.get_deals(trade)
            ...     for deal in deals:
            ...         print(f"成交價: {deal.price}, 成交量: {deal.quantity}")
        
        Raises:
            ValueError: 當 trade 為 None 時
            AttributeError: 當 trade 物件缺少必要屬性時
        """
        if trade is None:
            raise ValueError("Trade 不可為 None")
        
        try:
            if hasattr(trade, 'status') and hasattr(trade.status, 'deals'):
                return trade.status.deals
            return []
        except AttributeError as e:
            raise AttributeError(f"Trade 物件缺少必要屬性: {e}")
    
    def get_last_update_time(self) -> Optional[datetime]:
        """取得上次更新時間
        
        Returns:
            Optional[datetime]: 上次更新委託狀態的時間，如果尚未更新過則返回 None
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.update_status()
            >>> last_time = monitor.get_last_update_time()
            >>> print(f"上次更新: {last_time}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._last_update_time
    
    def clear_cache(self) -> None:
        """清除交易快取
        
        Examples:
            >>> monitor = TradeMonitor(api)
            >>> monitor.list_trades()
            >>> monitor.clear_cache()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._trades_cache.clear()
        self._last_update_time = None
