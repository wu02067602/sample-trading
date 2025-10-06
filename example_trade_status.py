"""Shioaji 成交回報查詢範例

此範例展示如何使用 ShioajiTrader 查詢委託單狀態與成交回報。
"""

from shioaji_trader import ShioajiTrader
import time


def order_callback(stat, msg):
    """委託回報 callback"""
    print(f"\n{'='*60}")
    print(f"[委託回報 Callback]")
    print(f"狀態: {stat}")
    print(f"訊息: {msg}")
    print(f"{'='*60}\n")


def demo_trade_status():
    """示範查詢委託狀態與成交回報
    
    展示如何查詢委託單的狀態、成交資訊、持倉與損益。
    """
    print("="*60)
    print("成交回報查詢功能示範")
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
    
    # ========== 示範 1：列出所有委託單 ==========
    print("\n" + "="*60)
    print("示範 1: 列出所有委託單")
    print("="*60)
    
    trades = trader.list_trades()
    print(f"\n找到 {len(trades)} 筆委託單\n")
    
    if trades:
        print("委託單列表：")
        print("-" * 60)
        for i, trade in enumerate(trades, 1):
            print(f"\n{i}. 委託單 {trade.status.id}")
            print(f"   商品: {trade.contract.code} - {trade.contract.name}")
            print(f"   方向: {trade.order.action}")
            print(f"   價格: {trade.order.price}")
            print(f"   數量: {trade.order.quantity}")
            print(f"   狀態: {trade.status.status}")
            
            # 如果有成交資訊
            if hasattr(trade.status, 'deal_quantity') and trade.status.deal_quantity > 0:
                print(f"   已成交: {trade.status.deal_quantity} 股")
    else:
        print("目前沒有委託單")
    
    # ========== 示範 2：下單並查詢狀態 ==========
    print("\n" + "="*60)
    print("示範 2: 下單並查詢狀態")
    print("="*60)
    
    print("\n⚠️ 以下為示範程式碼（已註解）")
    print("如需實際下單，請取消註解\n")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # print("準備下單買進台積電...")
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # print(f"✓ 下單成功，委託單號: {trade.status.id}\n")
    
    # # 等待一段時間讓委託處理
    # print("等待委託處理...")
    # time.sleep(2)
    
    # # 更新並查詢狀態
    # print("\n查詢委託狀態...")
    # status = trader.get_trade_status(trade)
    # print(f"\n委託單資訊：")
    # print(f"  委託單號: {status['id']}")
    # print(f"  狀態: {status['status']}")
    # print(f"  委託數量: {status['quantity']} 股")
    # print(f"  成交數量: {status['deal_quantity']} 股")
    # print(f"  委託時間: {status['order_datetime']}")
    
    # # 如果有成交明細
    # if status['deals']:
    #     print(f"\n成交明細：")
    #     for i, deal in enumerate(status['deals'], 1):
    #         print(f"  {i}. 成交價: {deal.price}, 成交量: {deal.quantity}")
    
    # ========== 示範 3：更新所有委託狀態 ==========
    print("\n" + "="*60)
    print("示範 3: 更新所有委託狀態")
    print("="*60)
    
    print("\n更新所有委託單狀態...")
    trader.update_status()
    print("✓ 更新完成")
    
    # 再次列出委託單（已更新）
    trades = trader.list_trades()
    if trades:
        print(f"\n委託單狀態（已更新）：")
        print("-" * 60)
        for trade in trades[:3]:  # 顯示前 3 筆
            print(f"委託單 {trade.status.id}: {trade.status.status}")
    
    # ========== 示範 4：查詢持倉部位 ==========
    print("\n" + "="*60)
    print("示範 4: 查詢持倉部位")
    print("="*60)
    
    print("\n查詢持倉部位...")
    positions = trader.list_positions()
    
    if positions:
        print(f"\n找到 {len(positions)} 個持倉部位\n")
        print("持倉列表：")
        print("-" * 60)
        for pos in positions:
            print(f"\n股票: {pos.code}")
            print(f"數量: {pos.quantity} 股")
            if hasattr(pos, 'price'):
                print(f"成本: {pos.price}")
            if hasattr(pos, 'last_price'):
                print(f"現價: {pos.last_price}")
    else:
        print("目前沒有持倉")
    
    # ========== 示範 5：查詢當日損益 ==========
    print("\n" + "="*60)
    print("示範 5: 查詢當日損益")
    print("="*60)
    
    print("\n查詢當日損益...")
    pnl = trader.list_profit_loss()
    
    if pnl:
        print(f"\n損益資訊：")
        print("-" * 60)
        print(pnl)
    else:
        print("無法取得損益資訊")
    
    # ========== 示範 6：查詢帳戶額度 ==========
    print("\n" + "="*60)
    print("示範 6: 查詢帳戶額度")
    print("="*60)
    
    print("\n查詢帳戶額度...")
    margin = trader.get_account_margin()
    
    if margin:
        print(f"\n帳戶額度資訊：")
        print("-" * 60)
        print(margin)
    else:
        print("無法取得帳戶額度資訊")
    
    # 登出
    print("\n" + "="*60)
    print("登出")
    print("="*60)
    trader.logout()
    print("✓ 登出成功")
    
    print("\n" + "="*60)
    print("示範程式執行完畢")
    print("="*60)


def monitor_trade_example():
    """監控委託單範例
    
    展示如何持續監控委託單狀態直到成交。
    """
    print("="*60)
    print("監控委託單範例")
    print("="*60)
    print("⚠️ 此為示範程式碼（已註解）")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # ⚠️ 取消下面的註解以執行真實監控
    # # 下單
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # print(f"下單成功，委託單號: {trade.status.id}\n")
    
    # # 監控委託狀態
    # print("開始監控委託狀態...")
    # max_attempts = 30  # 最多監控 30 次
    # attempt = 0
    
    # while attempt < max_attempts:
    #     attempt += 1
        
    #     # 更新狀態
    #     status = trader.get_trade_status(trade)
        
    #     print(f"[{attempt}] 狀態: {status['status']}, "
    #           f"已成交: {status['deal_quantity']}/{status['quantity']} 股")
        
    #     # 檢查是否完全成交
    #     if status['status'] in ['Filled', 'filled']:
    #         print(f"\n✓ 委託已完全成交！")
    #         break
        
    #     # 檢查是否被取消或失敗
    #     if status['status'] in ['Cancelled', 'Failed', 'cancelled', 'failed']:
    #         print(f"\n✗ 委託已{status['status']}")
    #         break
        
    #     # 等待 2 秒後再次查詢
    #     time.sleep(2)
    
    # print("\n監控結束")
    
    trader.logout()
    print("✓ 完成")


def position_management_example():
    """持倉管理範例
    
    展示如何管理持倉、計算損益等。
    """
    print("="*60)
    print("持倉管理範例")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 查詢持倉
    print("查詢持倉部位...")
    positions = trader.list_positions()
    
    if positions:
        print(f"\n持倉摘要：")
        print("="*60)
        
        total_value = 0
        for pos in positions:
            print(f"\n股票: {pos.code}")
            print(f"  數量: {pos.quantity} 股")
            
            if hasattr(pos, 'price') and hasattr(pos, 'last_price'):
                cost = pos.price * pos.quantity
                current = pos.last_price * pos.quantity
                pnl = current - cost
                pnl_pct = (pnl / cost * 100) if cost > 0 else 0
                
                print(f"  成本價: {pos.price}")
                print(f"  現價: {pos.last_price}")
                print(f"  成本金額: {cost:,.0f}")
                print(f"  現值: {current:,.0f}")
                print(f"  未實現損益: {pnl:,.0f} ({pnl_pct:+.2f}%)")
                
                total_value += current
        
        print(f"\n總市值: {total_value:,.0f}")
    else:
        print("目前沒有持倉")
    
    trader.logout()
    print("\n✓ 完成")


if __name__ == "__main__":
    # 執行完整示範
    demo_trade_status()
    
    # 如果要執行其他範例，請取消下面的註解
    # print("\n" + "="*80 + "\n")
    # monitor_trade_example()
    
    # print("\n" + "="*80 + "\n")
    # position_management_example()
