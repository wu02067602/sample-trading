"""
Shioaji 報價訂閱與 Callback 使用範例

此檔案展示如何使用 ShioajiClient 訂閱報價和處理回調。
"""

from shioaji_client import ShioajiClient, LoginConfig
from quote_callback import DefaultQuoteCallback, DefaultOrderCallback, IQuoteCallback
import logging
import time

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_subscribe_quote():
    """訂閱報價範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        # 登入
        client.login(config)
        
        print("=== 訂閱報價範例 ===")
        
        # 1. 設定報價 callback
        quote_callback = DefaultQuoteCallback()
        client.set_quote_callback(quote_callback)
        
        # 2. 註冊報價回調
        client.register_quote_callback()
        
        # 3. 訂閱台積電報價
        tsmc = client.get_stock("2330")
        client.subscribe_quote(tsmc)
        
        print(f"已訂閱 {tsmc.code} - {tsmc.name}")
        print("等待報價資料... (按 Ctrl+C 停止)")
        
        # 持續接收報價
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止接收報價")
        
        # 4. 取消訂閱
        client.unsubscribe_quote(tsmc)
        print("已取消訂閱")


def example_subscribe_multiple_quotes():
    """訂閱多個商品報價範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 訂閱多個商品報價 ===")
        
        # 設定並註冊 callback
        quote_callback = DefaultQuoteCallback()
        client.set_quote_callback(quote_callback)
        client.register_quote_callback()
        
        # 訂閱多個商品
        stock_codes = ["2330", "2317", "2454"]  # 台積電、鴻海、聯發科
        
        for code in stock_codes:
            stock = client.get_stock(code)
            client.subscribe_quote(stock)
            print(f"已訂閱: {stock.code} - {stock.name}")
        
        # 查看已訂閱列表
        subscribed = client.get_subscribed_quotes()
        print(f"\n目前訂閱的商品: {subscribed}")
        
        print("\n等待報價資料... (按 Ctrl+C 停止)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止接收報價")


def example_custom_quote_callback():
    """使用自訂 callback 範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    # 自訂報價處理函數
    def my_quote_handler(topic: str, quote):
        """自訂報價處理邏輯"""
        if hasattr(quote, 'close') and hasattr(quote, 'volume'):
            print(f"[{topic}] 價格: {quote.close}, 成交量: {quote.volume}")
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 使用自訂 Callback ===")
        
        # 使用自訂處理函數
        quote_callback = DefaultQuoteCallback(custom_handler=my_quote_handler)
        client.set_quote_callback(quote_callback)
        client.register_quote_callback()
        
        # 訂閱報價
        tsmc = client.get_stock("2330")
        client.subscribe_quote(tsmc)
        
        print("使用自訂處理函數接收報價...")
        print("(按 Ctrl+C 停止)")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止接收")


def example_order_callback():
    """訂單回調範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 訂單回調範例 ===")
        
        # 設定並註冊訂單 callback
        order_callback = DefaultOrderCallback()
        client.set_order_callback(order_callback)
        client.register_order_callback()
        
        print("訂單回調已註冊")
        print("現在可以下單，系統會自動接收訂單狀態和成交通知")
        print("(此範例不包含下單邏輯)")


def example_custom_callback_class():
    """使用自訂 Callback 類別範例"""
    
    # 自訂 Callback 類別
    class MyQuoteCallback(IQuoteCallback):
        """自訂報價 Callback 類別"""
        
        def __init__(self):
            self.price_history = {}
        
        def on_quote(self, topic: str, quote) -> None:
            """處理報價並記錄價格歷史"""
            if hasattr(quote, 'close'):
                if topic not in self.price_history:
                    self.price_history[topic] = []
                
                self.price_history[topic].append(quote.close)
                
                # 只保留最近 10 筆
                if len(self.price_history[topic]) > 10:
                    self.price_history[topic].pop(0)
                
                # 計算平均價
                avg_price = sum(self.price_history[topic]) / len(self.price_history[topic])
                
                print(f"[{topic}] 最新: {quote.close}, 平均: {avg_price:.2f}")
    
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 使用自訂 Callback 類別 ===")
        
        # 使用自訂 Callback 類別
        my_callback = MyQuoteCallback()
        client.set_quote_callback(my_callback)
        client.register_quote_callback()
        
        # 訂閱報價
        tsmc = client.get_stock("2330")
        client.subscribe_quote(tsmc)
        
        print("使用自訂 Callback 類別，計算移動平均...")
        print("(按 Ctrl+C 停止)")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止接收")
            print(f"\n價格歷史: {my_callback.price_history}")


if __name__ == "__main__":
    print("=== Shioaji 報價訂閱與 Callback 使用範例 ===\n")
    
    print("請先修改範例程式碼中的認證資訊後執行")
    print("\n可用的範例:")
    print("1. example_subscribe_quote() - 訂閱單一商品報價")
    print("2. example_subscribe_multiple_quotes() - 訂閱多個商品報價")
    print("3. example_custom_quote_callback() - 使用自訂處理函數")
    print("4. example_order_callback() - 訂單回調")
    print("5. example_custom_callback_class() - 使用自訂 Callback 類別")
    
    # 取消註解以執行範例
    # example_subscribe_quote()
    # example_subscribe_multiple_quotes()
    # example_custom_quote_callback()
    # example_order_callback()
    # example_custom_callback_class()
