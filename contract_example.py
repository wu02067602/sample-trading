"""
Shioaji 商品檔查詢使用範例

此檔案展示如何使用 ShioajiConnector 查詢各種商品合約資訊。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
from shioaji_connector import ShioajiConnector

# 設置日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_get_all_contracts():
    """
    範例 1: 取得所有商品檔
    
    展示如何取得所有可交易的商品資訊。
    """
    print("\n" + "="*60)
    print("範例 1: 取得所有商品檔")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        
        # 登入並自動下載商品檔
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            fetch_contract=True  # 預設為 True
        )
        
        # 取得商品檔物件
        contracts = connector.get_contracts()
        
        if contracts:
            print("✅ 商品檔取得成功！")
            
            # 取得商品統計摘要
            summary = connector.get_contracts_summary()
            print(f"\n商品統計:")
            for category, count in summary.items():
                print(f"  - {category}: {count} 筆")
            
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_search_stock():
    """
    範例 2: 搜尋股票
    
    展示如何使用關鍵字搜尋股票。
    """
    print("\n" + "="*60)
    print("範例 2: 搜尋股票")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 使用股票代碼搜尋
        print("\n搜尋股票代碼: 2330")
        results = connector.search_stock("2330")
        
        if results:
            print(f"找到 {len(results)} 筆結果:")
            for stock in results:
                print(f"  - {stock.code} {stock.name}")
                print(f"    交易所: {stock.exchange}")
        
        # 使用股票名稱搜尋
        print("\n搜尋股票名稱: 台積電")
        results = connector.search_stock("台積電")
        
        if results:
            print(f"找到 {len(results)} 筆結果:")
            for stock in results:
                print(f"  - {stock.code} {stock.name}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_get_stock_by_code():
    """
    範例 3: 精確查詢股票
    
    展示如何使用股票代碼精確查詢單一股票。
    """
    print("\n" + "="*60)
    print("範例 3: 精確查詢股票")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 精確查詢
        stock_codes = ["2330", "2317", "2454"]
        
        for code in stock_codes:
            stock = connector.get_stock_by_code(code)
            
            if stock:
                print(f"\n股票代碼: {stock.code}")
                print(f"股票名稱: {stock.name}")
                print(f"交易所: {stock.exchange}")
                print(f"產業類別: {stock.category}")
            else:
                print(f"\n找不到股票代碼: {code}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_search_futures():
    """
    範例 4: 搜尋期貨
    
    展示如何搜尋期貨商品。
    """
    print("\n" + "="*60)
    print("範例 4: 搜尋期貨")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 搜尋台指期
        print("\n搜尋台指期 (TX):")
        results = connector.search_futures("TX")
        
        if results:
            print(f"找到 {len(results)} 筆結果:")
            for i, future in enumerate(results[:5], 1):  # 只顯示前 5 筆
                print(f"  {i}. {future.code} {future.name}")
                print(f"     到期日: {future.delivery_date if hasattr(future, 'delivery_date') else 'N/A'}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_direct_access():
    """
    範例 5: 直接訪問 contracts 屬性
    
    展示如何直接使用 connector.contracts 進行更複雜的操作。
    """
    print("\n" + "="*60)
    print("範例 5: 直接訪問 contracts 屬性")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 直接訪問 contracts
        if connector.contracts:
            print("✅ 可以直接使用 connector.contracts")
            
            # 取得所有股票
            print("\n取得部分股票列表:")
            stocks = list(connector.contracts.Stocks)[:5]
            for stock in stocks:
                print(f"  - {stock.code} {stock.name}")
            
            # 取得所有期貨
            print("\n取得部分期貨列表:")
            futures = list(connector.contracts.Futures)[:5]
            for future in futures:
                print(f"  - {future.code} {future.name}")
            
            # 如果有選擇權
            if hasattr(connector.contracts, 'Options'):
                options = list(connector.contracts.Options)[:5]
                print(f"\n選擇權總數: {len(list(connector.contracts.Options))}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_connection_status_with_contracts():
    """
    範例 6: 檢查連線狀態（包含商品檔狀態）
    
    展示如何檢查商品檔是否已載入。
    """
    print("\n" + "="*60)
    print("範例 6: 檢查連線狀態（包含商品檔）")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        
        # 登入前的狀態
        print("\n登入前:")
        status = connector.get_connection_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 登入並下載商品檔
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            fetch_contract=True
        )
        
        # 登入後的狀態
        print("\n登入後:")
        status = connector.get_connection_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 檢查商品檔
        if status['contracts_loaded']:
            print("\n✅ 商品檔已載入，可以進行商品查詢")
            summary = connector.get_contracts_summary()
            print(f"商品總數: {sum(summary.values())}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 商品檔查詢使用範例集")
    print("="*60)
    print("\n⚠️  注意事項：")
    print("1. 請先安裝 shioaji: pip install -r requirements.txt")
    print("2. 將範例中的 YOUR_PERSON_ID、YOUR_PASSWORD 替換為實際值")
    print("3. 建議先在模擬環境測試 (simulation=True)")
    print("4. 商品檔在登入時會自動下載（fetch_contract=True）")
    
    # 執行範例
    try:
        example_1_get_all_contracts()
        example_2_search_stock()
        example_3_get_stock_by_code()
        example_4_search_futures()
        example_5_direct_access()
        example_6_connection_status_with_contracts()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 提示：")
    print("- 使用 connector.search_stock() 搜尋股票")
    print("- 使用 connector.get_stock_by_code() 精確查詢")
    print("- 使用 connector.search_futures() 搜尋期貨")
    print("- 使用 connector.get_contracts_summary() 查看統計")
    print("- 直接使用 connector.contracts 進行更多操作")
