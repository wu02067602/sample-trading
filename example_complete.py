"""Shioaji 完整功能示範

此範例展示 ShioajiTrader 的所有功能：
1. 登入與帳戶管理
2. 商品檔查詢
3. 報價訂閱與 Callback
4. 委託回報監控
"""

from shioaji_trader import ShioajiTrader
import time
from datetime import datetime


class TradingBot:
    """交易機器人範例
    
    展示如何整合所有功能建立一個簡單的交易系統。
    """
    
    def __init__(self):
        """初始化交易機器人"""
        self.trader = ShioajiTrader()
        self.quote_count = 0
        self.order_count = 0
    
    def on_quote(self, exchange: str, tick):
        """報價處理函數"""
        self.quote_count += 1
        
        # 只顯示部分報價，避免輸出過多
        if self.quote_count % 10 == 0:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] {tick['code']}: "
                  f"價={tick['close']}, 量={tick['volume']}, "
                  f"買={tick['bid_price']}, 賣={tick['ask_price']}")
    
    def on_order(self, stat, msg):
        """委託回報處理函數"""
        self.order_count += 1
        print(f"\n{'='*50}")
        print(f"[委託回報 #{self.order_count}]")
        print(f"狀態: {stat}")
        print(f"訊息: {msg}")
        print(f"{'='*50}\n")
    
    def run(self):
        """執行交易機器人"""
        
        # ========== 1. 登入 ==========
        print("="*60)
        print("步驟 1: 登入系統")
        print("="*60)
        
        success = self.trader.login(
            api_key="YOUR_API_KEY",
            secret_key="YOUR_SECRET_KEY"
        )
        
        if not success:
            print("登入失敗！")
            return
        
        print("✓ 登入成功\n")
        
        # ========== 2. 查看帳戶 ==========
        print("="*60)
        print("步驟 2: 查看帳戶資訊")
        print("="*60)
        
        accounts = self.trader.list_accounts()
        print(f"可用帳戶數: {len(accounts)}")
        
        if self.trader.stock_account:
            print(f"證券帳戶: {self.trader.stock_account}")
        
        if self.trader.futopt_account:
            print(f"期貨帳戶: {self.trader.futopt_account}")
        
        print()
        
        # ========== 3. 查詢商品 ==========
        print("="*60)
        print("步驟 3: 查詢商品資訊")
        print("="*60)
        
        # 查詢台積電
        tsmc = self.trader.get_stock("2330")
        print(f"✓ 查詢到: {tsmc.code} - {tsmc.name}")
        
        # 查詢聯發科
        mtk = self.trader.get_stock("2454")
        print(f"✓ 查詢到: {mtk.code} - {mtk.name}")
        
        # 搜尋包含「台」的股票
        print("\n搜尋名稱包含「台」的股票（前 5 筆）：")
        results = self.trader.search_contracts("台")
        for i, contract in enumerate(results[:5], 1):
            print(f"  {i}. {contract.code}: {contract.name}")
        
        print()
        
        # ========== 4. 設定 Callback ==========
        print("="*60)
        print("步驟 4: 設定 Callback 函數")
        print("="*60)
        
        # 設定報價 callback
        self.trader.set_quote_callback(self.on_quote)
        print("✓ 報價 Callback 已設定")
        
        # 設定委託回報 callback
        self.trader.set_order_callback(self.on_order)
        print("✓ 委託回報 Callback 已設定")
        
        print()
        
        # ========== 5. 訂閱報價 ==========
        print("="*60)
        print("步驟 5: 訂閱即時報價")
        print("="*60)
        
        if tsmc:
            self.trader.subscribe_quote(tsmc, quote_type="tick")
        
        if mtk:
            self.trader.subscribe_quote(mtk, quote_type="tick")
        
        # 顯示已訂閱的商品
        subscribed = self.trader.get_subscribed_contracts()
        print(f"\n已訂閱 {len(subscribed)} 個商品:")
        for contract in subscribed:
            print(f"  • {contract.code}: {contract.name}")
        
        print()
        
        # ========== 6. 接收報價 ==========
        print("="*60)
        print("步驟 6: 接收即時報價（持續 20 秒）")
        print("="*60)
        print("提示: 只顯示每 10 筆報價的其中 1 筆")
        print("按 Ctrl+C 可提前結束\n")
        
        try:
            start_time = time.time()
            duration = 20  # 持續 20 秒
            
            while time.time() - start_time < duration:
                remaining = int(duration - (time.time() - start_time))
                if remaining % 5 == 0 and remaining > 0:
                    print(f"\n剩餘時間: {remaining} 秒")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n使用者中斷程式")
        
        # ========== 7. 統計資訊 ==========
        print("\n" + "="*60)
        print("步驟 7: 顯示統計資訊")
        print("="*60)
        print(f"總共收到 {self.quote_count} 筆報價")
        print(f"總共收到 {self.order_count} 筆委託回報")
        print()
        
        # ========== 8. 清理 ==========
        print("="*60)
        print("步驟 8: 清理並登出")
        print("="*60)
        
        # 取消訂閱
        for contract in subscribed:
            self.trader.unsubscribe_quote(contract)
        
        # 登出
        if self.trader.logout():
            print("✓ 登出成功")
        
        print("\n程式執行完畢！")


def simple_monitoring_example():
    """簡化版監控範例
    
    展示如何快速設定報價監控。
    """
    print("="*60)
    print("簡化版報價監控範例")
    print("="*60 + "\n")
    
    # 初始化
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 定義 callback
    def simple_callback(exchange, tick):
        print(f"{tick['code']}: {tick['close']} (vol: {tick['volume']})")
    
    # 設定並訂閱
    trader.set_quote_callback(simple_callback)
    
    # 訂閱多個商品
    codes = ["2330", "2454", "2317"]  # 台積電、聯發科、鴻海
    for code in codes:
        stock = trader.get_stock(code)
        if stock:
            trader.subscribe_quote(stock)
            print(f"✓ 已訂閱 {code}")
    
    # 監控 15 秒
    print(f"\n開始監控 15 秒...\n")
    time.sleep(15)
    
    # 清理
    for code in codes:
        stock = trader.get_stock(code)
        if stock:
            trader.unsubscribe_quote(stock)
    
    trader.logout()
    print("\n✓ 監控結束")


if __name__ == "__main__":
    # 執行完整範例
    bot = TradingBot()
    bot.run()
    
    # 如果要執行簡化版範例，請註解掉上面兩行並取消註解下面這行
    # simple_monitoring_example()
