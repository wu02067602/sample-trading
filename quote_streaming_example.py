"""
Shioaji 即時報價訂閱與 Callback 使用範例

此檔案展示如何使用 ShioajiConnector 訂閱即時報價並處理 callback 事件。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
import time
from shioaji_connector import ShioajiConnector

# 設置日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_basic_quote_subscription():
    """
    範例 1: 基本報價訂閱
    
    展示如何訂閱單一股票的即時報價。
    """
    print("\n" + "="*60)
    print("範例 1: 基本報價訂閱")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 取得股票合約
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 訂閱逐筆報價
            success = connector.subscribe_quote(stock, "tick")
            
            if success:
                print(f"✅ 成功訂閱 {stock.code} {stock.name} 的即時報價")
                print("開始接收報價資料...")
                
                # 等待接收報價
                time.sleep(5)
                
                # 取消訂閱
                connector.unsubscribe_quote(stock)
                print("✅ 已取消訂閱")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_with_callback():
    """
    範例 2: 使用 Callback 處理報價
    
    展示如何註冊 callback 函數來處理即時報價。
    """
    print("\n" + "="*60)
    print("範例 2: 使用 Callback 處理報價")
    print("="*60)
    
    # 定義報價處理函數
    def quote_handler(topic, quote):
        """處理接收到的報價資料"""
        try:
            code = quote.get('code', 'N/A')
            close = quote.get('close', 0)
            volume = quote.get('volume', 0)
            timestamp = quote.get('datetime', 'N/A')
            
            print(f"[報價更新] {topic}")
            print(f"  代碼: {code}")
            print(f"  價格: {close}")
            print(f"  成交量: {volume}")
            print(f"  時間: {timestamp}")
            print("-" * 40)
        except Exception as e:
            print(f"處理報價時發生錯誤: {e}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 註冊 callback
        connector.set_quote_callback(quote_handler, "tick")
        print("✅ 已註冊報價 callback 函數")
        
        # 訂閱股票
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.subscribe_quote(stock, "tick")
            print(f"✅ 已訂閱 {stock.code} {stock.name}")
            
            # 持續接收報價 10 秒
            print("\n開始接收報價（10秒）...")
            time.sleep(10)
            
            # 取消訂閱
            connector.unsubscribe_quote(stock)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_multiple_stocks():
    """
    範例 3: 訂閱多個股票
    
    展示如何同時訂閱多個股票的報價。
    """
    print("\n" + "="*60)
    print("範例 3: 訂閱多個股票")
    print("="*60)
    
    # 統計資訊
    quote_count = {}
    
    def multi_quote_handler(topic, quote):
        """處理多個股票的報價"""
        code = quote.get('code', 'N/A')
        close = quote.get('close', 0)
        
        # 統計
        if code not in quote_count:
            quote_count[code] = 0
        quote_count[code] += 1
        
        print(f"[{code}] 價格: {close}, 累計更新: {quote_count[code]} 次")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 註冊 callback
        connector.set_quote_callback(multi_quote_handler, "tick")
        
        # 訂閱多個股票
        stock_codes = ["2330", "2317", "2454"]
        
        for code in stock_codes:
            stock = connector.get_stock_by_code(code)
            if stock:
                connector.subscribe_quote(stock, "tick")
                print(f"✅ 已訂閱 {stock.code} {stock.name}")
        
        # 顯示已訂閱的商品
        subscribed = connector.get_subscribed_contracts()
        print(f"\n目前訂閱 {len(subscribed)} 個商品:")
        for code, contract in subscribed.items():
            print(f"  - {code}: {contract.name}")
        
        # 接收報價
        print("\n開始接收報價（15秒）...")
        time.sleep(15)
        
        # 顯示統計
        print("\n報價更新統計:")
        for code, count in quote_count.items():
            print(f"  {code}: {count} 次更新")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_bidask_quote():
    """
    範例 4: 訂閱五檔報價
    
    展示如何訂閱五檔委買委賣報價。
    """
    print("\n" + "="*60)
    print("範例 4: 訂閱五檔報價")
    print("="*60)
    
    def bidask_handler(topic, quote):
        """處理五檔報價"""
        code = quote.get('code', 'N/A')
        
        print(f"\n[五檔報價] {code}")
        
        # 顯示委買（買盤）
        print("委買（Buy）:")
        for i in range(5):
            price_key = f'bid_price_{i}'
            volume_key = f'bid_volume_{i}'
            if price_key in quote:
                print(f"  {i+1}. 價格: {quote[price_key]}, 量: {quote[volume_key]}")
        
        # 顯示委賣（賣盤）
        print("委賣（Sell）:")
        for i in range(5):
            price_key = f'ask_price_{i}'
            volume_key = f'ask_volume_{i}'
            if price_key in quote:
                print(f"  {i+1}. 價格: {quote[price_key]}, 量: {quote[volume_key]}")
        
        print("-" * 40)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 註冊五檔報價 callback
        connector.set_quote_callback(bidask_handler, "bidask")
        
        # 訂閱五檔報價
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.subscribe_quote(stock, "bidask")
            print(f"✅ 已訂閱 {stock.code} {stock.name} 的五檔報價")
            
            # 接收報價
            print("\n開始接收五檔報價（10秒）...")
            time.sleep(10)
            
            connector.unsubscribe_quote(stock)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_get_latest_quote():
    """
    範例 5: 取得最新報價快照
    
    展示如何取得已訂閱商品的最新報價快照。
    """
    print("\n" + "="*60)
    print("範例 5: 取得最新報價快照")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 訂閱股票
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.subscribe_quote(stock, "tick")
            print(f"✅ 已訂閱 {stock.code} {stock.name}")
            
            # 等待接收報價
            print("\n等待接收報價...")
            time.sleep(3)
            
            # 取得最新報價快照
            quote = connector.get_latest_quote("2330")
            
            if quote:
                print("\n最新報價快照:")
                print(f"  代碼: {quote.get('code')}")
                print(f"  價格: {quote.get('close')}")
                print(f"  成交量: {quote.get('volume')}")
                print(f"  時間: {quote.get('datetime')}")
            else:
                print("尚未接收到報價資料")
            
            connector.unsubscribe_quote(stock)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_multiple_callbacks():
    """
    範例 6: 註冊多個 Callback
    
    展示如何為同一事件註冊多個 callback 函數。
    """
    print("\n" + "="*60)
    print("範例 6: 註冊多個 Callback")
    print("="*60)
    
    # 第一個 callback: 記錄日誌
    def log_handler(topic, quote):
        code = quote.get('code', 'N/A')
        close = quote.get('close', 0)
        print(f"[LOG] {code} - 價格: {close}")
    
    # 第二個 callback: 價格監控
    def price_monitor(topic, quote):
        code = quote.get('code', 'N/A')
        close = quote.get('close', 0)
        
        # 假設監控價格突破 600
        if close > 600:
            print(f"⚠️  [警告] {code} 價格突破 600: {close}")
    
    # 第三個 callback: 統計資料
    stats = {'count': 0, 'total_volume': 0}
    
    def stats_handler(topic, quote):
        stats['count'] += 1
        stats['total_volume'] += quote.get('volume', 0)
        
        if stats['count'] % 10 == 0:
            print(f"📊 [統計] 累計 {stats['count']} 筆, 總成交量: {stats['total_volume']}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 註冊多個 callback
        connector.set_quote_callback(log_handler, "tick")
        connector.set_quote_callback(price_monitor, "tick")
        connector.set_quote_callback(stats_handler, "tick")
        print("✅ 已註冊 3 個 callback 函數")
        
        # 訂閱股票
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.subscribe_quote(stock, "tick")
            print(f"✅ 已訂閱 {stock.code} {stock.name}")
            
            # 接收報價
            print("\n開始接收報價（10秒）...")
            time.sleep(10)
            
            # 清除 callback
            connector.clear_quote_callbacks("tick")
            print("\n✅ 已清除所有 callback")
            
            connector.unsubscribe_quote(stock)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_7_connection_status():
    """
    範例 7: 檢查連線狀態（含訂閱資訊）
    
    展示如何檢查連線狀態和訂閱資訊。
    """
    print("\n" + "="*60)
    print("範例 7: 檢查連線狀態")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        
        # 登入前
        print("\n登入前:")
        status = connector.get_connection_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 登入
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 訂閱股票
        stock_codes = ["2330", "2317"]
        for code in stock_codes:
            stock = connector.get_stock_by_code(code)
            if stock:
                connector.subscribe_quote(stock)
        
        # 註冊 callback
        def dummy_handler(topic, quote):
            pass
        
        connector.set_quote_callback(dummy_handler, "tick")
        
        # 登入並訂閱後
        print("\n登入並訂閱後:")
        status = connector.get_connection_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 顯示訂閱詳情
        subscribed = connector.get_subscribed_contracts()
        print(f"\n已訂閱商品詳情:")
        for code, contract in subscribed.items():
            print(f"  - {code}: {contract.name}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 即時報價訂閱與 Callback 使用範例集")
    print("="*60)
    print("\n⚠️  注意事項：")
    print("1. 請先安裝 shioaji: pip install -r requirements.txt")
    print("2. 將範例中的 YOUR_PERSON_ID、YOUR_PASSWORD 替換為實際值")
    print("3. 建議先在模擬環境測試 (simulation=True)")
    print("4. 報價訂閱需要市場開盤時間才會有資料")
    print("5. Callback 函數應該快速執行，避免阻塞")
    
    # 執行範例
    try:
        example_1_basic_quote_subscription()
        example_2_with_callback()
        example_3_multiple_stocks()
        example_4_bidask_quote()
        example_5_get_latest_quote()
        example_6_multiple_callbacks()
        example_7_connection_status()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 提示：")
    print("- 使用 connector.subscribe_quote() 訂閱報價")
    print("- 使用 connector.set_quote_callback() 註冊處理函數")
    print("- 使用 connector.get_latest_quote() 取得最新快照")
    print("- 支援同時訂閱多個商品和多個 callback")
    print("- 記得使用 unsubscribe_quote() 取消訂閱")
