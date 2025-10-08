"""市場交易狀況排行模組

此模組負責處理永豐 Shioaji API 的市場交易狀況排行功能。
"""

import shioaji as sj
from typing import List, Optional, Any
from datetime import datetime


class MarketScanner:
    """負責匯總和展示當前交易狀況
    
    此類別封裝了永豐 Shioaji API 的市場交易狀況排行功能，
    提供漲跌幅、成交量、成交金額等各種排行查詢。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化市場掃描器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._last_scan_result: Optional[List[Any]] = None
        self._last_scan_time: Optional[datetime] = None
    
    def get_change_percent_rank(
        self, 
        count: int = 100, 
        ascending: bool = True,
        date: Optional[str] = None,
        timeout: int = 30000
    ) -> List[Any]:
        """取得漲跌幅排行
        
        取得證券市場依價格漲跌幅排序的排行榜。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
            ascending (bool): 是否由小到大排序，True 為由大到小（漲幅），False 為由小到大（跌幅），預設為 True
            date (Optional[str]): 日期，格式為 'YYYY-MM-DD'，None 表示當日
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Returns:
            List[Any]: 漲跌幅排行列表，每個元素包含 date, code, name, open, high, low, close 等資訊
        
        Examples:
            >>> from login import Login
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> scanner = MarketScanner(api)
            >>> top_gainers = scanner.get_change_percent_rank(count=10)
            >>> for rank in top_gainers:
            ...     print(f"{rank.name} ({rank.code}): {rank.change_percent}%")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當請求逾時時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            result = self._api.scanners(
                scanner_type=sj.constant.ScannerType.ChangePercentRank,
                count=count,
                ascending=ascending,
                date=date,
                timeout=timeout
            )
            
            self._last_scan_result = result
            self._last_scan_time = datetime.now()
            
            return result
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"請求逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_change_price_rank(
        self, 
        count: int = 100, 
        ascending: bool = True,
        date: Optional[str] = None,
        timeout: int = 30000
    ) -> List[Any]:
        """取得漲跌排行
        
        取得證券市場依價格漲跌排序的排行榜。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
            ascending (bool): 是否由小到大排序，True 為由大到小（漲價），False 為由小到大（跌價），預設為 True
            date (Optional[str]): 日期，格式為 'YYYY-MM-DD'，None 表示當日
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Returns:
            List[Any]: 漲跌排行列表
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> top_price_gainers = scanner.get_change_price_rank(count=10)
            >>> for rank in top_price_gainers:
            ...     print(f"{rank.name}: {rank.change_price}")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當請求逾時時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            result = self._api.scanners(
                scanner_type=sj.constant.ScannerType.ChangePriceRank,
                count=count,
                ascending=ascending,
                date=date,
                timeout=timeout
            )
            
            self._last_scan_result = result
            self._last_scan_time = datetime.now()
            
            return result
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"請求逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_volume_rank(
        self, 
        count: int = 100, 
        ascending: bool = True,
        date: Optional[str] = None,
        timeout: int = 30000
    ) -> List[Any]:
        """取得成交量排行
        
        取得證券市場依成交量排序的排行榜。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
            ascending (bool): 是否由小到大排序，True 為由大到小，False 為由小到大，預設為 True
            date (Optional[str]): 日期，格式為 'YYYY-MM-DD'，None 表示當日
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Returns:
            List[Any]: 成交量排行列表
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> top_volume = scanner.get_volume_rank(count=10)
            >>> for rank in top_volume:
            ...     print(f"{rank.name}: {rank.volume}")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當請求逾時時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            result = self._api.scanners(
                scanner_type=sj.constant.ScannerType.VolumeRank,
                count=count,
                ascending=ascending,
                date=date,
                timeout=timeout
            )
            
            self._last_scan_result = result
            self._last_scan_time = datetime.now()
            
            return result
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"請求逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_amount_rank(
        self, 
        count: int = 100, 
        ascending: bool = True,
        date: Optional[str] = None,
        timeout: int = 30000
    ) -> List[Any]:
        """取得成交金額排行
        
        取得證券市場依成交金額排序的排行榜。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
            ascending (bool): 是否由小到大排序，True 為由大到小，False 為由小到大，預設為 True
            date (Optional[str]): 日期，格式為 'YYYY-MM-DD'，None 表示當日
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Returns:
            List[Any]: 成交金額排行列表
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> top_amount = scanner.get_amount_rank(count=10)
            >>> for rank in top_amount:
            ...     print(f"{rank.name}: {rank.amount}")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當請求逾時時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            result = self._api.scanners(
                scanner_type=sj.constant.ScannerType.AmountRank,
                count=count,
                ascending=ascending,
                date=date,
                timeout=timeout
            )
            
            self._last_scan_result = result
            self._last_scan_time = datetime.now()
            
            return result
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"請求逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_day_range_rank(
        self, 
        count: int = 100, 
        ascending: bool = True,
        date: Optional[str] = None,
        timeout: int = 30000
    ) -> List[Any]:
        """取得高低價差排行
        
        取得證券市場依當日高低價差排序的排行榜。
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
            ascending (bool): 是否由小到大排序，True 為由大到小，False 為由小到大，預設為 True
            date (Optional[str]): 日期，格式為 'YYYY-MM-DD'，None 表示當日
            timeout (int): 逾時時間（毫秒），預設為 30000 毫秒（30 秒）
        
        Returns:
            List[Any]: 高低價差排行列表
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> top_range = scanner.get_day_range_rank(count=10)
            >>> for rank in top_range:
            ...     print(f"{rank.name}: {rank.day_range}")
        
        Raises:
            ValueError: 當 count 不在 0-200 範圍內時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當請求逾時時
        """
        if not 0 <= count <= 200:
            raise ValueError(f"Count 必須在 0-200 範圍內，當前值: {count}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            result = self._api.scanners(
                scanner_type=sj.constant.ScannerType.DayRangeRank,
                count=count,
                ascending=ascending,
                date=date,
                timeout=timeout
            )
            
            self._last_scan_result = result
            self._last_scan_time = datetime.now()
            
            return result
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"請求逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_last_scan_result(self) -> Optional[List[Any]]:
        """取得上次掃描結果
        
        Returns:
            Optional[List[Any]]: 上次掃描的排行結果，如果尚未執行過掃描則返回 None
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> scanner.get_change_percent_rank(count=10)
            >>> last_result = scanner.get_last_scan_result()
            >>> print(f"上次掃描有 {len(last_result)} 筆資料")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._last_scan_result
    
    def get_last_scan_time(self) -> Optional[datetime]:
        """取得上次掃描時間
        
        Returns:
            Optional[datetime]: 上次掃描的時間，如果尚未執行過掃描則返回 None
        
        Examples:
            >>> scanner = MarketScanner(api)
            >>> scanner.get_change_percent_rank(count=10)
            >>> last_time = scanner.get_last_scan_time()
            >>> print(f"上次掃描時間: {last_time}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._last_scan_time
