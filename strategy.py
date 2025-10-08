"""交易策略模組

此模組負責實現交易策略邏輯與決策。
"""

from typing import Optional, Any, Dict, List, Callable
from datetime import datetime
import logging


class TradingSignal:
    """交易訊號資料類別"""
    
    def __init__(
        self, 
        code: str, 
        action: str, 
        price: float, 
        quantity: int,
        reason: str,
        timestamp: datetime
    ) -> None:
        """初始化交易訊號
        
        Args:
            code (str): 股票代碼
            action (str): 買賣動作，'Buy' 或 'Sell'
            price (float): 建議價格
            quantity (int): 建議數量（張）
            reason (str): 訊號產生原因
            timestamp (datetime): 訊號產生時間
        """
        self.code = code
        self.action = action
        self.price = price
        self.quantity = quantity
        self.reason = reason
        self.timestamp = timestamp
    
    def __repr__(self) -> str:
        return (f"TradingSignal(code={self.code}, action={self.action}, "
                f"price={self.price}, quantity={self.quantity}, "
                f"reason={self.reason}, timestamp={self.timestamp})")


class MomentumStrategy:
    """動能交易策略
    
    此類別實現基於漲幅和成交量的動能交易策略，
    當股票漲幅大於指定閾值且成交量大於指定張數時產生買入訊號。
    """
    
    def __init__(
        self, 
        quote_callback: Any,
        change_percent_threshold: float = 6.0,
        volume_threshold: int = 1000
    ) -> None:
        """初始化動能交易策略
        
        Args:
            quote_callback (Any): QuoteCallback 實例，用於註冊報價回調
            change_percent_threshold (float): 漲幅閾值（百分比），預設為 6.0
            volume_threshold (int): 成交量閾值（張），預設為 1000
        
        Raises:
            ValueError: 當 quote_callback 為 None 時
            ValueError: 當 change_percent_threshold 小於等於 0 時
            ValueError: 當 volume_threshold 小於等於 0 時
        """
        if quote_callback is None:
            raise ValueError("Quote callback 不可為 None")
        if change_percent_threshold <= 0:
            raise ValueError(f"Change percent threshold 必須大於 0，當前值: {change_percent_threshold}")
        if volume_threshold <= 0:
            raise ValueError(f"Volume threshold 必須大於 0，當前值: {volume_threshold}")
        
        self._quote_callback = quote_callback
        self._change_percent_threshold = change_percent_threshold
        self._volume_threshold = volume_threshold
        self._signals: List[TradingSignal] = []
        self._signal_callbacks: List[Callable[[TradingSignal], None]] = []
        self._monitored_stocks: Dict[str, bool] = {}  # 追蹤已經產生訊號的股票，避免重複
        self._logger = logging.getLogger(__name__)
        
        # 註冊報價回調
        self._quote_callback.set_quote_callback(self._on_quote_received)
    
    def set_change_percent_threshold(self, threshold: float) -> None:
        """設定漲幅閾值
        
        Args:
            threshold (float): 漲幅閾值（百分比）
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> strategy.set_change_percent_threshold(8.0)  # 設定為 8%
        
        Raises:
            ValueError: 當 threshold 小於等於 0 時
        """
        if threshold <= 0:
            raise ValueError(f"Threshold 必須大於 0，當前值: {threshold}")
        
        self._change_percent_threshold = threshold
        self._logger.info(f"漲幅閾值已更新為: {threshold}%")
    
    def set_volume_threshold(self, threshold: int) -> None:
        """設定成交量閾值
        
        Args:
            threshold (int): 成交量閾值（張）
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> strategy.set_volume_threshold(2000)  # 設定為 2000 張
        
        Raises:
            ValueError: 當 threshold 小於等於 0 時
        """
        if threshold <= 0:
            raise ValueError(f"Threshold 必須大於 0，當前值: {threshold}")
        
        self._volume_threshold = threshold
        self._logger.info(f"成交量閾值已更新為: {threshold} 張")
    
    def register_signal_callback(self, callback: Callable[[TradingSignal], None]) -> None:
        """註冊訊號回調函數
        
        當產生交易訊號時，會呼叫已註冊的回調函數。
        
        Args:
            callback (Callable[[TradingSignal], None]): 
                回調函數，接收 TradingSignal 作為參數
        
        Examples:
            >>> def on_signal(signal: TradingSignal):
            ...     print(f"收到訊號: {signal.code} - {signal.action}")
            >>> 
            >>> strategy = MomentumStrategy(callback)
            >>> strategy.register_signal_callback(on_signal)
        
        Raises:
            ValueError: 當 callback 不是可呼叫的函數時
        """
        if not callable(callback):
            raise ValueError("Callback 必須是可呼叫的函數")
        
        self._signal_callbacks.append(callback)
    
    def _on_quote_received(self, exchange: str, tick: Any) -> None:
        """處理接收到的報價資料（內部方法）
        
        Args:
            exchange (str): 交易所代碼
            tick (Any): 報價資料物件
        """
        try:
            # 檢查必要屬性
            if not hasattr(tick, 'code'):
                self._logger.warning("報價資料缺少 code 屬性")
                return
            
            code = tick.code
            self._logger.info(f"[策略] 處理股票 {code} 的報價")
            
            # 如果這支股票已經產生過訊號，跳過
            if self._monitored_stocks.get(code, False):
                self._logger.debug(f"股票 {code} 已產生過訊號，跳過")
                return
            
            # 檢查是否符合策略條件
            if self._check_signal_conditions(tick):
                signal = self._generate_signal(tick)
                self._signals.append(signal)
                self._monitored_stocks[code] = True
                
                self._logger.info(f"產生交易訊號: {signal}")
                
                # 呼叫已註冊的回調函數
                for callback in self._signal_callbacks:
                    try:
                        callback(signal)
                    except Exception as e:
                        self._logger.error(f"執行訊號回調失敗: {e}")
            else:
                # 記錄不符合條件的原因
                change_percent = self._calculate_change_percent(tick)
                volume_lots = self._get_volume_in_lots(tick)
                self._logger.info(
                    f"股票 {code} 不符合策略條件 - "
                    f"漲幅: {change_percent:.2f}% (閾值: {self._change_percent_threshold}%), "
                    f"成交量: {volume_lots} 張 (閾值: {self._volume_threshold} 張)"
                )
        
        except AttributeError as e:
            self._logger.error(f"報價資料格式錯誤: {e}")
        except Exception as e:
            self._logger.error(f"處理報價時發生錯誤: {e}")
    
    def _check_signal_conditions(self, tick: Any) -> bool:
        """檢查是否符合訊號條件（內部方法）
        
        Args:
            tick (Any): 報價資料物件
        
        Returns:
            bool: 是否符合條件
        """
        try:
            # 檢查漲幅
            change_percent = self._calculate_change_percent(tick)
            if change_percent is None:
                return False
            
            # 檢查成交量（轉換為張，1 張 = 1000 股）
            volume_lots = self._get_volume_in_lots(tick)
            if volume_lots is None:
                return False
            
            # 判斷是否符合條件
            meets_change = change_percent > self._change_percent_threshold
            meets_volume = volume_lots > self._volume_threshold
            
            if meets_change and meets_volume:
                self._logger.info(
                    f"股票 {tick.code} 符合策略條件！ - "
                    f"漲幅: {change_percent:.2f}% > {self._change_percent_threshold}%, "
                    f"成交量: {volume_lots} 張 > {self._volume_threshold} 張"
                )
                return True
            
            return False
            
        except AttributeError as e:
            self._logger.error(f"計算條件時發生錯誤: {e}")
            return False
    
    def _calculate_change_percent(self, tick: Any) -> Optional[float]:
        """計算漲跌幅（內部方法）
        
        Args:
            tick (Any): 報價資料物件
        
        Returns:
            Optional[float]: 漲跌幅百分比，如果無法計算則返回 None
        """
        try:
            # 嘗試不同的屬性名稱
            close = getattr(tick, 'close', None)
            reference = getattr(tick, 'reference', None)
            
            # 如果沒有 reference，嘗試使用 yesterday_close
            if reference is None:
                reference = getattr(tick, 'yesterday_close', None)
            
            if close is None or reference is None:
                return None
            
            if reference == 0:
                return None
            
            change_percent = ((close - reference) / reference) * 100
            return change_percent
            
        except (AttributeError, TypeError, ZeroDivisionError):
            return None
    
    def _get_volume_in_lots(self, tick: Any) -> Optional[int]:
        """取得成交量（張）（內部方法）
        
        Args:
            tick (Any): 報價資料物件
        
        Returns:
            Optional[int]: 成交量（張），如果無法取得則返回 None
        """
        try:
            # 嘗試不同的屬性名稱
            volume = getattr(tick, 'volume', None)
            
            # 如果沒有 volume，嘗試使用 total_volume
            if volume is None:
                volume = getattr(tick, 'total_volume', None)
            
            if volume is None:
                return None
            
            # 轉換為張（1 張 = 1000 股）
            volume_lots = int(volume / 1000)
            return volume_lots
            
        except (AttributeError, TypeError, ValueError):
            return None
    
    def _generate_signal(self, tick: Any) -> TradingSignal:
        """產生交易訊號（內部方法）
        
        Args:
            tick (Any): 報價資料物件
        
        Returns:
            TradingSignal: 交易訊號
        """
        change_percent = self._calculate_change_percent(tick)
        volume_lots = self._get_volume_in_lots(tick)
        
        reason = (f"漲幅 {change_percent:.2f}% > {self._change_percent_threshold}%, "
                  f"成交量 {volume_lots} 張 > {self._volume_threshold} 張")
        
        signal = TradingSignal(
            code=tick.code,
            action='Buy',  # 動能策略產生買入訊號
            price=tick.close,
            quantity=1,  # 預設買入 1 張
            reason=reason,
            timestamp=datetime.now()
        )
        
        return signal
    
    def get_signals(self) -> List[TradingSignal]:
        """取得所有已產生的交易訊號
        
        Returns:
            List[TradingSignal]: 交易訊號列表
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> # ... 等待訊號產生 ...
            >>> signals = strategy.get_signals()
            >>> for signal in signals:
            ...     print(f"{signal.code}: {signal.action} @ {signal.price}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._signals.copy()
    
    def get_latest_signal(self) -> Optional[TradingSignal]:
        """取得最新的交易訊號
        
        Returns:
            Optional[TradingSignal]: 最新的交易訊號，如果沒有則返回 None
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> signal = strategy.get_latest_signal()
            >>> if signal:
            ...     print(f"最新訊號: {signal.code}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        if not self._signals:
            return None
        return self._signals[-1]
    
    def clear_signals(self) -> None:
        """清除所有已產生的訊號
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> strategy.clear_signals()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._signals.clear()
        self._monitored_stocks.clear()
        self._logger.info("所有訊號已清除")
    
    def reset_monitored_stock(self, code: str) -> None:
        """重置指定股票的監控狀態
        
        允許該股票再次產生訊號。
        
        Args:
            code (str): 股票代碼
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> strategy.reset_monitored_stock("2330")
        
        Raises:
            ValueError: 當 code 為空字串時
        """
        if not code:
            raise ValueError("股票代碼不可為空")
        
        if code in self._monitored_stocks:
            del self._monitored_stocks[code]
            self._logger.info(f"股票 {code} 監控狀態已重置")
    
    def get_monitored_stocks(self) -> List[str]:
        """取得已監控的股票列表
        
        Returns:
            List[str]: 股票代碼列表
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> stocks = strategy.get_monitored_stocks()
            >>> print(f"已監控 {len(stocks)} 支股票")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return list(self._monitored_stocks.keys())
    
    def get_thresholds(self) -> Dict[str, Any]:
        """取得目前的閾值設定
        
        Returns:
            Dict[str, Any]: 包含閾值設定的字典
        
        Examples:
            >>> strategy = MomentumStrategy(callback)
            >>> thresholds = strategy.get_thresholds()
            >>> print(f"漲幅閾值: {thresholds['change_percent']}%")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return {
            'change_percent': self._change_percent_threshold,
            'volume': self._volume_threshold
        }
