import os
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from src.client import SinotradeClient
from src.market_data import MarketDataFetcher, DateRange
from src.bigquery_storage import BigQueryStorage, DataValidator

# 建立 log 資料夾（如果不存在）
os.makedirs("log", exist_ok=True)
# 設定詳細的 logging 格式，log 檔寫入 log 資料夾
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # 輸出到 console
        logging.FileHandler(f'log/log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')  # 寫入 log 資料夾
    ]
)

logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("開始執行股票資料抓取與儲存流程")
logger.info("=" * 60)

# 1. 初始化並登入
logger.info("步驟 1: 初始化客戶端")
client = SinotradeClient(simulation=True)
logger.info("步驟 2: 執行登入")
client.login(api_key=os.getenv("API_KEY"), secret_key=os.getenv("API_SECRET"))

# 2. 抓取市場資料
logger.info("步驟 3: 初始化市場資料抓取服務")
fetcher = MarketDataFetcher(api=client.api)
date_range = DateRange(start_date="2023-01-01", end_date="2023-01-31")
logger.info(f"步驟 4: 開始抓取股票全市場的資料 (日期範圍: {date_range.start_date} ~ {date_range.end_date})")
df = fetcher.fetch_all_market_kbars(date_range)
logger.info(f"成功抓取 {len(df)} 筆資料")

# 3. 儲存到 BigQuery
logger.info("步驟 5: 初始化 BigQuery 儲存服務")
storage = BigQueryStorage(
    project_id="life-is-a-vacation",
    dataset_id="stock_data",
    table_id="daily_kbars"
)
logger.info("步驟 6: 檢查並建立資料表（如果不存在）")
storage.create_table_if_not_exists()
logger.info("步驟 7: 將資料插入 BigQuery")
storage.insert_dataframe(df)

# 4. 驗證資料
logger.info("步驟 8: 執行資料品質驗證")
validator = DataValidator(storage)
issues = validator.validate_data_quality()
logger.info(f"資料品質檢查結果: {issues}")

# 5. 登出
logger.info("步驟 9: 執行登出")
client.logout()

logger.info("=" * 60)
logger.info("流程執行完成")
logger.info("=" * 60)