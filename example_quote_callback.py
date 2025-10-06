"""Shioaji 訂閱報價與 Callback 監控範例

此範例展示如何使用 ShioajiTrader 訂閱報價並透過 callback 監控資料。
"""

from shioaji_trader import ShioajiTrader
import time


def quote_callback(exchange: str, tick):
    """報價 callback 函數
    
    當收到訂閱的商品報價時，此函數會被呼叫。
    
    Args:
        exchange: 交易所代碼
        tick: 報價資料物件
    """
    print(f"\n=== 收到報價 ===")
    print(f"交易所: {exchange}")
    print(f"代碼: {tick['code']}")
    print(f"時間: {tick['datetime']}")
    print(f"成交價: {tick['close']}")
    print(f"成交量: {tick['volume']}")
    print(f"買價: {tick['bid_price']}")
    print(f"賣價: {tick['ask_price']}")
    print(f"買量: {tick['bid_volume']}")
    print(f"賣量: {tick['ask_volume']}")
    print("=" * 50)


def order_callback(stat, msg):
    """委託回報 callback 函數
    
    當收到委託狀態或成交回報時，此函數會被呼叫。
    
    Args:
        stat: 委託狀態
        msg: 委託或成交訊息
    """
    print(f"\n=== 委託回報 ===")
    print(f"狀態: {stat}")
    print(f"訊息: {msg}")
    print("=" * 50)


def main():
    """主程式"""
    
    # 建立交易器實例
    trader = ShioajiTrader()
    
    # 登入
    print("正在登入...")
    success = trader.login(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    if not success:
        print("登入失敗，請檢查憑證是否正確。")
        return
    
    print("登入成功！\n")
    
    # ========== 設定 Callback ==========
    print("=" * 50)
    print("設定 Callback 函數")
    print("=" * 50)
    
    # 設定報價 callback
    trader.set_quote_callback(quote_callback)
    
    # 設定委託回報 callback
    trader.set_order_callback(order_callback)
    
    # ========== 訂閱報價 ==========
    print("\n" + "=" * 50)
    print("訂閱商品報價")
    print("=" * 50)
    
    # 訂閱台積電
    print("\n訂閱台積電（2330）報價...")
    tsmc = trader.get_stock("2330")
    if tsmc:
        trader.subscribe_quote(tsmc, quote_type="tick")
    
    # 訂閱聯發科
    print("\n訂閱聯發科（2454）報價...")
    mtk = trader.get_stock("2454")
    if mtk:
        trader.subscribe_quote(mtk, quote_type="tick")
    
    # 顯示已訂閱的商品
    print("\n" + "=" * 50)
    print("已訂閱的商品")
    print("=" * 50)
    subscribed = trader.get_subscribed_contracts()
    for contract in subscribed:
        print(f"  {contract.code}: {contract.name}")
    
    # ========== 接收報價 ==========
    print("\n" + "=" * 50)
    print("開始接收報價（持續 30 秒）")
    print("按 Ctrl+C 可提前結束")
    print("=" * 50)
    
    try:
        # 持續接收報價 30 秒
        for i in range(30):
            time.sleep(1)
            if i % 10 == 0:
                print(f"\n已運行 {i} 秒...")
    
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    
    # ========== 取消訂閱 ==========
    print("\n" + "=" * 50)
    print("取消訂閱")
    print("=" * 50)
    
    if tsmc:
        trader.unsubscribe_quote(tsmc)
    if mtk:
        trader.unsubscribe_quote(mtk)
    
    # 登出
    print("\n正在登出...")
    if trader.logout():
        print("登出成功！")


def simple_example():
    """簡化版範例"""
    
    trader = ShioajiTrader()
    
    # 登入
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 定義簡單的 callback
    def simple_quote_callback(exchange, tick):
        print(f"{tick['code']}: {tick['close']} (量: {tick['volume']})")
    
    # 設定並訂閱
    trader.set_quote_callback(simple_quote_callback)
    tsmc = trader.get_stock("2330")
    trader.subscribe_quote(tsmc)
    
    # 接收報價 10 秒
    time.sleep(10)
    
    # 清理
    trader.unsubscribe_quote(tsmc)
    trader.logout()


if __name__ == "__main__":
    # 執行完整範例
    main()
    
    # 如果要執行簡化版範例，請註解掉上面的 main() 並取消註解下面這行
    # simple_example()
