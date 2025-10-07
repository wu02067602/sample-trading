"""策略數據準備模組

此模組負責準備策略所需的市場數據。
"""

import shioaji as sj
from typing import List, Optional, Any, Dict, Callable
from datetime import datetime, timedelta
import threading
import logging


class StrategyDataPreparer:
    """負責準備策略所需的市場數據
    
    此類別封裝了市場數據的收集與準備功能，
    定期獲取市場交易狀況排行，供交易策略使用。
    """
    
    def __init__(self, market_scanner: Any, quote_callback: Any) -> None:
        """初始化策略數據準備器
        
        Args:
            market_scanner (Any): MarketScanner 實例，用於獲取市場排行
            quote_callback (Any): QuoteCallback 實例，用於獲取即時報價
        
        Raises:
            ValueError: 當 market_scanner 或 quote_callback 為 None 時
        """
        if market_scanner is None:
            raise ValueError("Market scanner 不可為 None")
        if quote_callback is None:
            raise ValueError("Quote callback 不可為 None")
        
        self._market_scanner = market_scanner
        self._quote_callback = quote_callback
        self._market_data: Dict[str, Any] = {}
        self._update_interval: int = 600  # 預設 10 分鐘（600 秒）
        self._timer: Optional[threading.Timer] = None
        self._is_running: bool = False
        self._logger = logging.getLogger(__name__)
    
    def set_update_interval(self, seconds: int) -> None:
        """設定數據更新間隔
        
        Args:
            seconds (int): 更新間隔秒數，必須大於 0
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.set_update_interval(600)  # 設定為 10 分鐘
        
        Raises:
            ValueError: 當 seconds 小於等於 0 時
        """
        if seconds <= 0:
            raise ValueError(f"Update interval 必須大於 0，當前值: {seconds}")
        
        self._update_interval = seconds
    
    def update_market_data(self, count: int = 100) -> Dict[str, Any]:
        """更新市場數據
        
        獲取市場交易狀況排行並更新內部數據。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
        
        Returns:
            Dict[str, Any]: 更新後的市場數據，包含以下鍵值：
                - 'change_percent_rank': 漲跌幅排行
                - 'volume_rank': 成交量排行
                - 'update_time': 更新時間
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> data = preparer.update_market_data(count=50)
            >>> print(f"漲跌幅排行前 3 名:")
            >>> for rank in data['change_percent_rank'][:3]:
            ...     print(f"{rank.name}: {rank.change_percent}%")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        try:
            # 獲取漲跌幅排行
            change_percent_rank = self._market_scanner.get_change_percent_rank(count=count)
            
            # 獲取成交量排行
            volume_rank = self._market_scanner.get_volume_rank(count=count)
            
            # 更新市場數據
            self._market_data = {
                'change_percent_rank': change_percent_rank,
                'volume_rank': volume_rank,
                'update_time': datetime.now()
            }
            
            self._logger.info(f"市場數據已更新，時間: {self._market_data['update_time']}")
            
            return self._market_data
            
        except ConnectionError as e:
            self._logger.error(f"更新市場數據失敗: {e}")
            raise
        except ValueError as e:
            self._logger.error(f"參數錯誤: {e}")
            raise
    
    def start_auto_update(self, count: int = 100) -> None:
        """啟動自動更新市場數據
        
        啟動定時器，每隔指定時間自動更新市場數據。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.set_update_interval(600)  # 10 分鐘
            >>> preparer.start_auto_update(count=50)
            >>> # ... 使用策略 ...
            >>> preparer.stop_auto_update()
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            RuntimeError: 當自動更新已經在運行時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if self._is_running:
            raise RuntimeError("自動更新已在運行中")
        
        self._is_running = True
        self._schedule_update(count)
        self._logger.info(f"自動更新已啟動，間隔: {self._update_interval} 秒")
    
    def _schedule_update(self, count: int) -> None:
        """排程下次更新（內部方法）
        
        Args:
            count (int): 排行數量
        """
        if not self._is_running:
            return
        
        try:
            # 執行更新
            self.update_market_data(count)
            
            # 排程下次更新
            self._timer = threading.Timer(
                self._update_interval, 
                self._schedule_update, 
                args=[count]
            )
            self._timer.daemon = True
            self._timer.start()
            
        except (ConnectionError, ValueError) as e:
            self._logger.error(f"自動更新失敗: {e}")
    
    def stop_auto_update(self) -> None:
        """停止自動更新市場數據
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.start_auto_update()
            >>> # ... 一段時間後 ...
            >>> preparer.stop_auto_update()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._is_running = False
        
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        
        self._logger.info("自動更新已停止")
    
    def get_market_data(self) -> Dict[str, Any]:
        """取得目前的市場數據
        
        Returns:
            Dict[str, Any]: 市場數據，包含漲跌幅排行、成交量排行和更新時間
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.update_market_data()
            >>> data = preparer.get_market_data()
            >>> print(f"數據更新時間: {data['update_time']}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._market_data.copy()
    
    def get_top_gainers(self, top_n: int = 10) -> List[Any]:
        """取得漲幅最大的股票
        
        Args:
            top_n (int): 取前 N 名，預設為 10
        
        Returns:
            List[Any]: 漲幅最大的股票列表
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.update_market_data()
            >>> top_gainers = preparer.get_top_gainers(5)
            >>> for stock in top_gainers:
            ...     print(f"{stock.name}: {stock.change_percent}%")
        
        Raises:
            ValueError: 當 top_n 小於等於 0 時
            RuntimeError: 當尚未更新市場數據時
        """
        if top_n <= 0:
            raise ValueError(f"Top N 必須大於 0，當前值: {top_n}")
        
        if 'change_percent_rank' not in self._market_data:
            raise RuntimeError("尚未更新市場數據，請先呼叫 update_market_data()")
        
        return self._market_data['change_percent_rank'][:top_n]
    
    def get_top_volume(self, top_n: int = 10) -> List[Any]:
        """取得成交量最大的股票
        
        Args:
            top_n (int): 取前 N 名，預設為 10
        
        Returns:
            List[Any]: 成交量最大的股票列表
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.update_market_data()
            >>> top_volume = preparer.get_top_volume(5)
            >>> for stock in top_volume:
            ...     print(f"{stock.name}: {stock.volume}")
        
        Raises:
            ValueError: 當 top_n 小於等於 0 時
            RuntimeError: 當尚未更新市場數據時
        """
        if top_n <= 0:
            raise ValueError(f"Top N 必須大於 0，當前值: {top_n}")
        
        if 'volume_rank' not in self._market_data:
            raise RuntimeError("尚未更新市場數據，請先呼叫 update_market_data()")
        
        return self._market_data['volume_rank'][:top_n]
    
    def get_latest_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """取得指定商品的最新報價
        
        Args:
            code (str): 商品代碼
        
        Returns:
            Optional[Dict[str, Any]]: 最新報價資料，如果沒有則返回 None
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> quote = preparer.get_latest_quote("2330")
            >>> if quote:
            ...     print(f"最新價格: {quote['tick'].close}")
        
        Raises:
            ValueError: 當 code 為空字串時
        """
        if not code:
            raise ValueError("商品代碼不可為空")
        
        return self._quote_callback.get_latest_quote(code)
    
    def is_auto_update_running(self) -> bool:
        """檢查自動更新是否正在運行
        
        Returns:
            bool: 如果自動更新正在運行則返回 True，否則返回 False
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.is_auto_update_running()
            False
            >>> preparer.start_auto_update()
            >>> preparer.is_auto_update_running()
            True
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._is_running
    
    def get_last_update_time(self) -> Optional[datetime]:
        """取得上次更新時間
        
        Returns:
            Optional[datetime]: 上次更新市場數據的時間，如果尚未更新過則返回 None
        
        Examples:
            >>> preparer = StrategyDataPreparer(scanner, callback)
            >>> preparer.update_market_data()
            >>> last_time = preparer.get_last_update_time()
            >>> print(f"上次更新: {last_time}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._market_data.get('update_time')
