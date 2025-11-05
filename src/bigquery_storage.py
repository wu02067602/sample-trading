"""
BigQuery 儲存模組

此模組負責將股票交易資料儲存到 Google BigQuery，
並提供資料完整性驗證功能。
"""

from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import logging

logger = logging.getLogger(__name__)


class BigQueryStorage:
    """
    BigQuery 儲存服務
    
    此類別負責將股票交易資料儲存到 Google BigQuery。
    
    職責：
    - 建立和管理 BigQuery 資料表
    - 將 DataFrame 資料上傳到 BigQuery
    - 處理資料插入過程中的錯誤
    """
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_path: Optional[str] = None
    ) -> None:
        """
        初始化 BigQuery 儲存服務
        
        Args:
            project_id (str): GCP 專案 ID
            dataset_id (str): BigQuery 資料集 ID
            table_id (str): BigQuery 資料表 ID
            credentials_path (Optional[str]): 服務帳號金鑰檔案路徑
            
        Examples:
            >>> storage = BigQueryStorage(
            ...     project_id="my-project",
            ...     dataset_id="stock_data",
            ...     table_id="daily_kbars"
            ... )
            
        Raises:
            ValueError: 當必要參數為空時
            RuntimeError: 當無法連接到 BigQuery 時
        """
        if not project_id:
            raise ValueError("project_id 不能為空")
        if not dataset_id:
            raise ValueError("dataset_id 不能為空")
        if not table_id:
            raise ValueError("table_id 不能為空")
        
        self._project_id = project_id
        self._dataset_id = dataset_id
        self._table_id = table_id
        
        try:
            if credentials_path:
                self._client = bigquery.Client.from_service_account_json(
                    credentials_path,
                    project=project_id
                )
            else:
                self._client = bigquery.Client(project=project_id)
            
            logger.info(f"BigQuery 客戶端已初始化: {project_id}.{dataset_id}.{table_id}")
            
        except RuntimeError as e:
            logger.error(f"BigQuery 客戶端初始化失敗: {e}")
            raise RuntimeError(f"無法連接到 BigQuery: {e}")
    
    @property
    def table_ref(self) -> str:
        """
        取得完整的資料表參考路徑
        
        Returns:
            str: 資料表完整路徑，格式為 project.dataset.table
        """
        return f"{self._project_id}.{self._dataset_id}.{self._table_id}"
    
    def create_table_if_not_exists(self) -> None:
        """
        建立資料表（如果不存在）
        
        建立包含股票 K 線資料欄位的資料表。
        
        Examples:
            >>> storage = BigQueryStorage("project", "dataset", "table")
            >>> storage.create_table_if_not_exists()
            
        Raises:
            RuntimeError: 當資料表建立失敗時
        """
        table_ref = self._client.dataset(self._dataset_id).table(self._table_id)
        
        try:
            self._client.get_table(table_ref)
            logger.info(f"資料表已存在: {self.table_ref}")
            return
        except NotFound:
            pass
        
        # 定義資料表 schema
        schema = [
            bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("stock_code", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Open", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("High", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("Low", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("Close", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("Volume", "INT64", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_ref, schema=schema)
        
        # 設定資料表分區（依日期）
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="ts"
        )
        
        # 設定叢集（依股票代碼）
        table.clustering_fields = ["stock_code"]
        
        try:
            table = self._client.create_table(table)
            logger.info(f"資料表已建立: {self.table_ref}")
        except RuntimeError as e:
            logger.error(f"資料表建立失敗: {e}")
            raise RuntimeError(f"無法建立資料表: {e}")
    
    def insert_dataframe(
        self,
        df: pd.DataFrame,
        write_disposition: str = "WRITE_APPEND"
    ) -> int:
        """
        將 DataFrame 資料插入到 BigQuery
        
        Args:
            df (pd.DataFrame): 要插入的資料
            write_disposition (str): 寫入模式，預設為 WRITE_APPEND
                - WRITE_APPEND: 附加資料
                - WRITE_TRUNCATE: 清空後寫入
                - WRITE_EMPTY: 僅在表格為空時寫入
                
        Returns:
            int: 成功插入的資料筆數
            
        Examples:
            >>> storage = BigQueryStorage("project", "dataset", "table")
            >>> df = pd.DataFrame({...})
            >>> count = storage.insert_dataframe(df)
            >>> print(f"已插入 {count} 筆資料")
            
        Raises:
            ValueError: 當 DataFrame 為空或格式錯誤時
            RuntimeError: 當資料插入失敗時
        """
        if df is None or df.empty:
            raise ValueError("DataFrame 不能為空")
        
        # 驗證必要欄位
        required_columns = ['ts', 'stock_code', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"DataFrame 缺少必要欄位: {missing_columns}")
        
        # 確保資料表存在
        self.create_table_if_not_exists()
        
        # 準備資料
        df_to_insert = df[required_columns].copy()

        # 將時間戳轉換為 UTC 時間
        df_to_insert['ts'] = df_to_insert['ts'].dt.tz_localize('Asia/Taipei').dt.tz_convert('UTC')
        logger.info("已將 ts 欄位從台灣時間轉換為 UTC")

        # 設定寫入配置
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            schema=[
                bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("stock_code", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("Open", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("High", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("Low", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("Close", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("Volume", "INT64", mode="REQUIRED"),
            ]
        )
        
        try:
            logger.info(f"開始插入 {len(df_to_insert)} 筆資料到 {self.table_ref}")
            
            job = self._client.load_table_from_dataframe(
                df_to_insert,
                self.table_ref,
                job_config=job_config
            )
            
            job.result()  # 等待完成
            
            logger.info(f"成功插入 {len(df_to_insert)} 筆資料")
            return len(df_to_insert)
            
        except RuntimeError as e:
            logger.error(f"資料插入失敗: {e}")
            raise RuntimeError(f"無法插入資料到 BigQuery: {e}")
    
    def query_data(
        self,
        query: str
    ) -> pd.DataFrame:
        """
        執行 SQL 查詢並返回結果
        
        Args:
            query (str): SQL 查詢語句
            
        Returns:
            pd.DataFrame: 查詢結果
            
        Examples:
            >>> storage = BigQueryStorage("project", "dataset", "table")
            >>> query = "SELECT * FROM `project.dataset.table` LIMIT 10"
            >>> df = storage.query_data(query)
            
        Raises:
            ValueError: 當查詢語句為空時
            RuntimeError: 當查詢執行失敗時
        """
        if not query:
            raise ValueError("查詢語句不能為空")
        
        try:
            logger.info("執行 BigQuery 查詢")
            df = self._client.query(query).to_dataframe()
            logger.info(f"查詢成功，返回 {len(df)} 筆資料")
            return df
            
        except RuntimeError as e:
            logger.error(f"查詢執行失敗: {e}")
            raise RuntimeError(f"BigQuery 查詢失敗: {e}")


class DataValidator:
    """
    資料完整性驗證服務
    
    此類別負責驗證 BigQuery 中儲存的股票交易資料是否完整無缺漏。
    
    職責：
    - 檢查指定日期範圍的資料是否存在
    - 驗證資料筆數是否合理
    - 檢查是否有缺失的股票或日期
    - 驗證資料品質
    """
    
    def __init__(self, storage: BigQueryStorage) -> None:
        """
        初始化資料驗證服務
        
        Args:
            storage (BigQueryStorage): BigQuery 儲存服務實例
            
        Raises:
            TypeError: 當 storage 不是 BigQueryStorage 實例時
        """
        if not isinstance(storage, BigQueryStorage):
            raise TypeError("storage 必須是 BigQueryStorage 實例")
        
        self._storage = storage
        logger.info("資料驗證服務已初始化")
    
    def check_data_exists(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> bool:
        """
        檢查指定股票在指定日期範圍內是否有資料
        
        Args:
            stock_code (str): 股票代碼
            start_date (str): 開始日期，格式：YYYY-MM-DD
            end_date (str): 結束日期，格式：YYYY-MM-DD
            
        Returns:
            bool: 有資料返回 True，否則返回 False
            
        Examples:
            >>> validator = DataValidator(storage)
            >>> exists = validator.check_data_exists("2330", "2023-01-01", "2023-01-31")
            >>> print(exists)
            True
            
        Raises:
            ValueError: 當參數無效時
        """
        if not stock_code:
            raise ValueError("stock_code 不能為空")
        
        query = f"""
        SELECT COUNT(*) as count
        FROM `{self._storage.table_ref}`
        WHERE stock_code = '{stock_code}'
        AND ts BETWEEN '{start_date}' AND '{end_date}'
        """
        
        df = self._storage.query_data(query)
        count = df['count'].iloc[0]
        
        logger.info(f"{stock_code} 在 {start_date} ~ {end_date} 有 {count} 筆資料")
        return count > 0
    
    def get_missing_dates(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        expected_trading_days: List[str]
    ) -> List[str]:
        """
        取得缺失的交易日期
        
        Args:
            stock_code (str): 股票代碼
            start_date (str): 開始日期
            end_date (str): 結束日期
            expected_trading_days (List[str]): 預期的交易日列表
            
        Returns:
            List[str]: 缺失的日期列表
            
        Examples:
            >>> validator = DataValidator(storage)
            >>> trading_days = ["2023-01-03", "2023-01-04", "2023-01-05"]
            >>> missing = validator.get_missing_dates("2330", "2023-01-03", "2023-01-05", trading_days)
            
        Raises:
            ValueError: 當參數無效時
        """
        if not stock_code:
            raise ValueError("stock_code 不能為空")
        if not expected_trading_days:
            raise ValueError("expected_trading_days 不能為空")
        
        query = f"""
        SELECT DISTINCT DATE(ts) as date
        FROM `{self._storage.table_ref}`
        WHERE stock_code = '{stock_code}'
        AND ts BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date
        """
        
        df = self._storage.query_data(query)
        existing_dates = set(df['date'].astype(str).tolist())
        expected_dates = set(expected_trading_days)
        
        missing_dates = sorted(list(expected_dates - existing_dates))
        
        if missing_dates:
            logger.warning(f"{stock_code} 缺少 {len(missing_dates)} 個交易日的資料")
        else:
            logger.info(f"{stock_code} 資料完整")
        
        return missing_dates
    
    def validate_data_quality(
        self,
        stock_code: Optional[str] = None
    ) -> Dict[str, int]:
        """
        驗證資料品質
        
        檢查是否有異常資料，例如：
        - 價格為負數
        - 成交量為負數
        - High < Low
        - Close > High 或 Close < Low
        
        Args:
            stock_code (Optional[str]): 股票代碼，若為 None 則檢查全部
            
        Returns:
            Dict[str, int]: 各類異常的數量
            
        Examples:
            >>> validator = DataValidator(storage)
            >>> issues = validator.validate_data_quality("2330")
            >>> print(issues)
            {'negative_price': 0, 'negative_volume': 0, 'invalid_high_low': 0}
            
        Raises:
            RuntimeError: 當查詢執行失敗時
        """
        where_clause = f"WHERE stock_code = '{stock_code}'" if stock_code else ""
        
        query = f"""
        SELECT
            COUNTIF(Open < 0 OR High < 0 OR Low < 0 OR Close < 0) as negative_price,
            COUNTIF(Volume < 0) as negative_volume,
            COUNTIF(High < Low) as invalid_high_low,
            COUNTIF(Close > High OR Close < Low) as invalid_close,
            COUNTIF(Open > High OR Open < Low) as invalid_open
        FROM `{self._storage.table_ref}`
        {where_clause}
        """
        
        df = self._storage.query_data(query)
        result = df.iloc[0].to_dict()
        
        total_issues = sum(result.values())
        if total_issues > 0:
            logger.warning(f"發現 {total_issues} 筆異常資料")
        else:
            logger.info("資料品質良好，未發現異常")
        
        return result
    
    def get_data_summary(self) -> Dict[str, any]:
        """
        取得資料摘要統計
        
        Returns:
            Dict[str, any]: 包含總筆數、股票數量、日期範圍等資訊
            
        Examples:
            >>> validator = DataValidator(storage)
            >>> summary = validator.get_data_summary()
            >>> print(summary)
            {'total_records': 10000, 'unique_stocks': 100, ...}
            
        Raises:
            RuntimeError: 當查詢執行失敗時
        """
        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT stock_code) as unique_stocks,
            MIN(DATE(ts)) as earliest_date,
            MAX(DATE(ts)) as latest_date
        FROM `{self._storage.table_ref}`
        """
        
        df = self._storage.query_data(query)
        summary = df.iloc[0].to_dict()
        
        logger.info(f"資料摘要: {summary}")
        return summary
