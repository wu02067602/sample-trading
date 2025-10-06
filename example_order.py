"""Shioaji 下單功能範例

此範例展示如何使用 ShioajiTrader 進行股票下單。

⚠️ 警告：此範例包含真實下單操作，請謹慎使用！
建議先使用永豐金證券的模擬帳號進行測試。
"""

from shioaji_trader import ShioajiTrader
import time


def order_callback(stat, msg):
    """委託回報 callback"""
    print(f"\n{'='*60}")
    print(f"[委託回報]")
    print(f"狀態: {stat}")
    print(f"訊息: {msg}")
    print(f"{'='*60}\n")


def demo_place_order():
    """示範基本下單功能
    
    ⚠️ 此為示範程式，實際使用時請注意：
    1. 確認帳戶餘額足夠
    2. 確認價格合理
    3. 注意交易時間
    """
    print("="*60)
    print("基本下單功能示範")
    print("="*60)
    print("⚠️ 警告：此為真實下單操作！")
    print("="*60 + "\n")
    
    # 初始化
    trader = ShioajiTrader()
    
    # 登入
    print("正在登入...")
    success = trader.login(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    if not success:
        print("登入失敗！")
        return
    
    print("✓ 登入成功\n")
    
    # 設定委託回報 callback
    trader.set_order_callback(order_callback)
    
    # ========== 示範 1：使用 place_order() 下單 ==========
    print("\n" + "="*60)
    print("示範 1: 使用 place_order() 下單")
    print("="*60)
    
    # 查詢台積電
    tsmc = trader.get_stock("2330")
    print(f"商品: {tsmc.code} - {tsmc.name}")
    
    # 下單買進（此為示範，實際使用時請調整參數）
    print("\n準備下單...")
    print("⚠️ 請確認以下參數是否正確：")
    print(f"  商品: {tsmc.code}")
    print(f"  動作: 買進")
    print(f"  價格: 500.0")
    print(f"  數量: 1000 股 (1 張)")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.place_order(
    #     contract=tsmc,
    #     action="Buy",
    #     price=500.0,
    #     quantity=1000,
    #     price_type="LMT",
    #     order_type="ROD",
    #     order_lot="Common"
    # )
    # print(f"\n下單結果: {trade}")
    
    print("\n⚠️ 此為示範程式，實際下單程式碼已註解")
    
    # ========== 示範 2：使用簡化方法下單 ==========
    print("\n" + "="*60)
    print("示範 2: 使用簡化方法下單")
    print("="*60)
    
    print("\n2.1 買進整股")
    print("-" * 40)
    print("使用 buy_stock() 買進台積電 1 張")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # print(f"下單結果: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n2.2 賣出整股")
    print("-" * 40)
    print("使用 sell_stock() 賣出台積電 1 張")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.sell_stock("2330", price=510.0, quantity=1000)
    # print(f"下單結果: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n2.3 買進零股")
    print("-" * 40)
    print("使用 buy_odd_lot() 買進台積電 100 股")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_odd_lot("2330", price=500.0, quantity=100)
    # print(f"下單結果: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n2.4 賣出零股")
    print("-" * 40)
    print("使用 sell_odd_lot() 賣出台積電 100 股")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.sell_odd_lot("2330", price=510.0, quantity=100)
    # print(f"下單結果: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # ========== 示範 3：不同價格類型 ==========
    print("\n" + "="*60)
    print("示範 3: 不同價格類型")
    print("="*60)
    
    print("\n3.1 限價單 (LMT)")
    print("-" * 40)
    print("指定價格下單，只在該價格或更好的價格成交")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="LMT")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n3.2 市價單 (MKT)")
    print("-" * 40)
    print("以市場當前最佳價格立即成交")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000, price_type="MKT")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # ========== 示範 4：不同委託類型 ==========
    print("\n" + "="*60)
    print("示範 4: 不同委託類型")
    print("="*60)
    
    print("\n4.1 ROD (當日有效)")
    print("-" * 40)
    print("委託單在當日收盤前有效")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="ROD")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n4.2 IOC (立即成交否則取消)")
    print("-" * 40)
    print("立即以最佳價格成交，未成交部分取消")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="IOC")
    
    print("⚠️ 實際下單程式碼已註解")
    
    print("\n4.3 FOK (全部成交否則取消)")
    print("-" * 40)
    print("必須全部數量立即成交，否則整筆取消")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000, order_type="FOK")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # 登出
    print("\n" + "="*60)
    print("登出")
    print("="*60)
    trader.logout()
    print("✓ 登出成功")
    
    print("\n" + "="*60)
    print("示範程式執行完畢")
    print("="*60)
    print("\n⚠️ 提醒：")
    print("1. 此為示範程式，實際下單程式碼都已註解")
    print("2. 實際使用時請取消註解並調整參數")
    print("3. 建議先使用模擬帳號測試")
    print("4. 注意確認價格、數量是否合理")
    print("5. 注意交易時間（09:00-13:30）")


def simple_order_example():
    """簡單下單範例
    
    展示最基本的下單流程。
    """
    print("="*60)
    print("簡單下單範例")
    print("="*60)
    print("⚠️ 警告：此為真實下單操作！")
    print("="*60 + "\n")
    
    # 初始化並登入
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 設定 callback
    def my_callback(stat, msg):
        print(f"委託回報: {stat} - {msg}")
    
    trader.set_order_callback(my_callback)
    
    # 買進 1 張台積電（限價 500 元）
    print("準備買進 1 張台積電...")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # print(f"下單成功: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # 買進 100 股台積電零股
    print("\n準備買進 100 股台積電零股...")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # trade = trader.buy_odd_lot("2330", price=500.0, quantity=100)
    # print(f"下單成功: {trade}")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # 登出
    trader.logout()
    print("\n✓ 完成")


def order_parameters_guide():
    """下單參數說明
    
    說明各種下單參數的用法。
    """
    print("="*60)
    print("下單參數說明")
    print("="*60 + "\n")
    
    print("1. 買賣方向 (action)")
    print("-" * 40)
    print("  • Buy  - 買進")
    print("  • Sell - 賣出")
    
    print("\n2. 價格類型 (price_type)")
    print("-" * 40)
    print("  • LMT (限價) - 指定價格，只在該價格或更好的價格成交")
    print("  • MKT (市價) - 以市場當前最佳價格立即成交")
    
    print("\n3. 委託類型 (order_type)")
    print("-" * 40)
    print("  • ROD - 當日有效，委託單在當日收盤前有效")
    print("  • IOC - 立即成交否則取消，未成交部分立即取消")
    print("  • FOK - 全部成交否則取消，必須全部立即成交")
    
    print("\n4. 交易單位 (order_lot)")
    print("-" * 40)
    print("  • Common      - 整股，數量必須是 1000 的倍數")
    print("  • IntradayOdd - 盤中零股，數量可以是 1-999 股")
    
    print("\n5. 注意事項")
    print("-" * 40)
    print("  • 整股最小單位：1000 股（1 張）")
    print("  • 零股數量範圍：1-999 股")
    print("  • 零股只能使用 ROD 委託類型")
    print("  • 注意交易時間：09:00-13:30")
    print("  • 確認帳戶餘額充足")
    print("  • 市價單可能會有較大價差")
    
    print("\n6. 使用範例")
    print("-" * 40)
    print("""
# 買進 1 張台積電（整股）
trader.buy_stock("2330", price=500.0, quantity=1000)

# 賣出 2 張台積電（整股）
trader.sell_stock("2330", price=510.0, quantity=2000)

# 買進 100 股台積電（零股）
trader.buy_odd_lot("2330", price=500.0, quantity=100)

# 賣出 50 股台積電（零股）
trader.sell_odd_lot("2330", price=510.0, quantity=50)

# 以市價買進
trader.buy_stock("2330", price=500.0, quantity=1000, price_type="MKT")

# 使用 IOC 委託
trader.buy_stock("2330", price=500.0, quantity=1000, order_type="IOC")
    """)


if __name__ == "__main__":
    # 顯示參數說明
    order_parameters_guide()
    
    print("\n" + "="*80 + "\n")
    
    # 執行完整示範
    demo_place_order()
    
    # 如果要執行簡單範例，請取消下面的註解
    # print("\n" + "="*80 + "\n")
    # simple_order_example()
