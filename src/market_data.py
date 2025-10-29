"""
市場資料抓取模組

此模組負責從永豐金證券 API 抓取股票的歷史交易資料。
"""

from typing import List, Optional, Dict
from datetime import datetime, date
import shioaji as sj
import pandas as pd
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DateRange:
    """
    日期區間資料類別
    
    Attributes:
        start_date (str): 開始日期，格式：YYYY-MM-DD
        end_date (str): 結束日期，格式：YYYY-MM-DD
    """
    start_date: str
    end_date: str
    
    def __post_init__(self) -> None:
        """驗證日期區間的有效性"""
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            
            if start > end:
                raise ValueError("開始日期不能晚於結束日期")
                
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError(f"日期格式錯誤，正確格式為 YYYY-MM-DD: {e}")
            raise


class MarketDataFetcher:
    """
    市場資料抓取服務
    
    此類別負責從永豐金證券 API 抓取全市場股票的歷史交易資料。
    
    職責：
    - 取得全市場股票列表
    - 抓取指定時間區間的股票 K 線資料
    - 將資料轉換為 DataFrame 格式
    - 處理資料抓取過程中的錯誤
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化市場資料抓取服務
        
        Args:
            api (sj.Shioaji): Shioaji API 實例
            
        Raises:
            TypeError: 當 api 不是 Shioaji 實例時
        """
        if not isinstance(api, sj.Shioaji):
            raise TypeError("api 必須是 Shioaji 實例")
        
        self._api = api
        logger.info("市場資料抓取服務已初始化")
    
    def get_all_stock_symbols(self) -> List[str]:
        """
        取得全市場股票代碼列表
        
        Returns:
            List[str]: 股票代碼列表
            
        Examples:
            >>> fetcher = MarketDataFetcher(api)
            >>> symbols = fetcher.get_all_stock_symbols()
            >>> print(len(symbols))
            1000
            
        Raises:
            RuntimeError: 當無法取得股票列表時
        """
        try:
            stocks = self._api.Contracts.Stocks
            all_symbols = []
            
            # 遍歷所有交易所
            for exchange in dir(stocks):
                if exchange.startswith('_'):
                    continue
                    
                exchange_obj = getattr(stocks, exchange)
                if not hasattr(exchange_obj, '__iter__'):
                    continue
                
                try:
                    for stock in exchange_obj:
                        if hasattr(stock, 'code'):
                            all_symbols.append(stock.code)
                except (TypeError, AttributeError):
                    continue
            
            logger.info(f"成功取得 {len(all_symbols)} 個股票代碼")
            return all_symbols
            
        except RuntimeError as e:
            logger.error(f"取得股票列表失敗: {e}")
            raise RuntimeError(f"無法取得股票列表: {e}")
    
    def fetch_stock_kbars(
        self,
        stock_code: str,
        date_range: DateRange
    ) -> Optional[pd.DataFrame]:
        """
        抓取單一股票的 K 線資料
        
        Args:
            stock_code (str): 股票代碼
            date_range (DateRange): 日期區間
            
        Returns:
            Optional[pd.DataFrame]: K 線資料的 DataFrame，若失敗則返回 None
            
        Examples:
            >>> fetcher = MarketDataFetcher(api)
            >>> date_range = DateRange("2023-01-01", "2023-01-31")
            >>> df = fetcher.fetch_stock_kbars("2330", date_range)
            >>> print(df.columns)
            Index(['ts', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
        Raises:
            ValueError: 當股票代碼無效或日期區間無效時
            RuntimeError: 當資料抓取失敗時
        """
        if not stock_code or not isinstance(stock_code, str):
            raise ValueError("stock_code 必須為非空字串")
        
        if not isinstance(date_range, DateRange):
            raise ValueError("date_range 必須是 DateRange 實例")
        
        try:
            # 取得股票合約
            contract = self._api.Contracts.Stocks[stock_code]
            
            if not contract:
                raise ValueError(f"找不到股票代碼: {stock_code}")
            
            logger.info(f"開始抓取 {stock_code} 的 K 線資料")
            
            # 抓取 K 線資料
            kbars = self._api.kbars(
                contract=contract,
                start=date_range.start_date,
                end=date_range.end_date
            )
            
            if not kbars or not kbars.ts:
                logger.warning(f"{stock_code} 在指定區間無資料")
                return None
            
            # 轉換為 DataFrame
            df = pd.DataFrame({
                'ts': kbars.ts,
                'Open': kbars.Open,
                'High': kbars.High,
                'Low': kbars.Low,
                'Close': kbars.Close,
                'Volume': kbars.Volume
            })
            
            # 將時間戳轉換為日期時間格式
            df['ts'] = pd.to_datetime(df['ts'], unit='ns')
            df['stock_code'] = stock_code
            
            logger.info(f"成功抓取 {stock_code} 的 {len(df)} 筆資料")
            return df
            
        except KeyError as e:
            logger.error(f"無效的股票代碼 {stock_code}: {e}")
            raise ValueError(f"無效的股票代碼: {stock_code}")
        except RuntimeError as e:
            logger.error(f"抓取 {stock_code} 資料失敗: {e}")
            raise RuntimeError(f"資料抓取失敗: {e}")
    
    def fetch_multiple_stocks_kbars(
        self,
        stock_codes: List[str],
        date_range: DateRange,
        skip_errors: bool = True
    ) -> pd.DataFrame:
        """
        批量抓取多支股票的 K 線資料
        
        Args:
            stock_codes (List[str]): 股票代碼列表
            date_range (DateRange): 日期區間
            skip_errors (bool): 是否跳過錯誤，預設為 True
            
        Returns:
            pd.DataFrame: 所有股票的 K 線資料
            
        Examples:
            >>> fetcher = MarketDataFetcher(api)
            >>> date_range = DateRange("2023-01-01", "2023-01-31")
            >>> df = fetcher.fetch_multiple_stocks_kbars(["2330", "2317"], date_range)
            >>> print(df.shape)
            (40, 7)
            
        Raises:
            ValueError: 當參數無效時
            RuntimeError: 當所有股票都抓取失敗且 skip_errors 為 False 時
        """
        if not stock_codes or not isinstance(stock_codes, list):
            raise ValueError("stock_codes 必須為非空列表")
        
        all_data = []
        success_count = 0
        error_count = 0
        
        for stock_code in stock_codes:
            try:
                df = self.fetch_stock_kbars(stock_code, date_range)
                if df is not None and not df.empty:
                    all_data.append(df)
                    success_count += 1
            except (ValueError, RuntimeError) as e:
                error_count += 1
                logger.warning(f"跳過股票 {stock_code}: {e}")
                if not skip_errors:
                    raise
        
        if not all_data:
            raise RuntimeError(f"所有股票資料抓取失敗 (成功: {success_count}, 失敗: {error_count})")
        
        # 合併所有資料
        result_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"批量抓取完成 (成功: {success_count}, 失敗: {error_count}, 總筆數: {len(result_df)})")
        
        return result_df
    
    def fetch_all_market_kbars(
        self,
        date_range: DateRange,
        skip_errors: bool = True
    ) -> pd.DataFrame:
        """
        抓取全市場股票的 K 線資料
        
        Args:
            date_range (DateRange): 日期區間
            skip_errors (bool): 是否跳過錯誤，預設為 True
            
        Returns:
            pd.DataFrame: 全市場股票的 K 線資料
            
        Examples:
            >>> fetcher = MarketDataFetcher(api)
            >>> date_range = DateRange("2023-01-01", "2023-01-31")
            >>> df = fetcher.fetch_all_market_kbars(date_range)
            >>> print(df.columns)
            Index(['ts', 'Open', 'High', 'Low', 'Close', 'Volume', 'stock_code'])
            
        Raises:
            RuntimeError: 當無法取得股票列表時
        """
        logger.info("開始抓取全市場股票資料")
        
        # 取得所有股票代碼
        stock_symbols = self.get_all_stock_symbols()
        
        # 批量抓取資料
        result_df = self.fetch_multiple_stocks_kbars(
            stock_codes=stock_symbols,
            date_range=date_range,
            skip_errors=skip_errors
        )
        
        logger.info(f"全市場資料抓取完成，共 {len(result_df)} 筆資料")
        return result_df
