"""Shioaji 委託回報功能範例

此範例展示如何使用 ShioajiTrader 的委託回報記錄功能。
"""

from shioaji_trader import ShioajiTrader
import time
from datetime import datetime


def demo_order_report_recording():
    """示範委託回報記錄功能
    
    展示如何啟用、查詢和管理委託回報記錄。
    """
    print("="*60)
    print("委託回報記錄功能示範")
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
    
    # ========== 示範 1：啟用委託回報記錄 ==========
    print("=" * 60)
    print("示範 1: 啟用委託回報記錄功能")
    print("=" * 60)
    
    print("\n啟用委託回報記錄...")
    trader.enable_order_report_recording()
    
    print("\n✓ 委託回報記錄功能已啟用")
    print("  - 所有委託回報會自動記錄")
    print("  - 所有成交回報會自動記錄")
    print("  - 可隨時查詢歷史記錄")
    
    # ========== 示範 2：下單並接收回報 ==========
    print("\n" + "=" * 60)
    print("示範 2: 下單並接收回報")
    print("=" * 60)
    
    print("\n⚠️ 以下為示範程式碼（已註解）")
    print("如需實際下單，請取消註解\n")
    
    # ⚠️ 取消下面的註解以執行真實下單
    # print("準備下單...")
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # print(f"✓ 下單成功，委託單號: {trade.status.id}\n")
    
    # # 等待接收回報
    # print("等待接收委託回報...")
    # time.sleep(3)
    
    # # 查詢委託回報
    # print("\n查詢委託回報記錄...")
    # order_reports = trader.get_order_reports()
    # print(f"✓ 收到 {len(order_reports)} 筆委託回報")
    
    # # 查詢成交回報
    # deal_reports = trader.get_deal_reports()
    # print(f"✓ 收到 {len(deal_reports)} 筆成交回報")
    
    print("⚠️ 實際下單程式碼已註解")
    
    # ========== 示範 3：查詢委託回報 ==========
    print("\n" + "=" * 60)
    print("示範 3: 查詢委託回報")
    print("=" * 60)
    
    print("\n取得所有委託回報...")
    order_reports = trader.get_order_reports()
    print(f"委託回報總數: {len(order_reports)}")
    
    if order_reports:
        print("\n最近的委託回報：")
        print("-" * 60)
        for i, report in enumerate(order_reports[-5:], 1):  # 顯示最後 5 筆
            timestamp = datetime.fromtimestamp(report['timestamp'])
            print(f"\n{i}. 時間: {timestamp.strftime('%H:%M:%S')}")
            print(f"   狀態: {report['stat']}")
            print(f"   類型: {report['type']}")
            print(f"   訊息: {report['msg']}")
    else:
        print("目前沒有委託回報記錄")
    
    # ========== 示範 4：查詢成交回報 ==========
    print("\n" + "=" * 60)
    print("示範 4: 查詢成交回報")
    print("=" * 60)
    
    print("\n取得所有成交回報...")
    deal_reports = trader.get_deal_reports()
    print(f"成交回報總數: {len(deal_reports)}")
    
    if deal_reports:
        print("\n最近的成交回報：")
        print("-" * 60)
        for i, report in enumerate(deal_reports[-5:], 1):  # 顯示最後 5 筆
            timestamp = datetime.fromtimestamp(report['timestamp'])
            print(f"\n{i}. 時間: {timestamp.strftime('%H:%M:%S')}")
            print(f"   狀態: {report['stat']}")
            print(f"   訊息: {report['msg']}")
    else:
        print("目前沒有成交回報記錄")
    
    # ========== 示範 5：取得回報摘要 ==========
    print("\n" + "=" * 60)
    print("示範 5: 取得回報摘要")
    print("=" * 60)
    
    print("\n查詢回報摘要...")
    summary = trader.get_report_summary()
    
    print("\n回報摘要：")
    print("-" * 60)
    print(f"委託回報數: {summary['order_count']}")
    print(f"成交回報數: {summary['deal_count']}")
    print(f"總回報數: {summary['total_count']}")
    
    if summary['first_report_time']:
        first_time = datetime.fromtimestamp(summary['first_report_time'])
        print(f"首筆回報時間: {first_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if summary['last_report_time']:
        last_time = datetime.fromtimestamp(summary['last_report_time'])
        print(f"最新回報時間: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========== 示範 6：取得最新的幾筆回報 ==========
    print("\n" + "=" * 60)
    print("示範 6: 取得最新的幾筆回報")
    print("=" * 60)
    
    print("\n取得最新 3 筆委託回報...")
    recent_orders = trader.get_order_reports(limit=3)
    print(f"✓ 取得 {len(recent_orders)} 筆委託回報")
    
    print("\n取得最新 3 筆成交回報...")
    recent_deals = trader.get_deal_reports(limit=3)
    print(f"✓ 取得 {len(recent_deals)} 筆成交回報")
    
    # ========== 示範 7：清除回報歷史 ==========
    print("\n" + "=" * 60)
    print("示範 7: 清除回報歷史")
    print("=" * 60)
    
    print("\n清除回報歷史記錄...")
    trader.clear_report_history()
    
    # 驗證已清除
    summary = trader.get_report_summary()
    print(f"\n清除後的統計：")
    print(f"  委託回報數: {summary['order_count']}")
    print(f"  成交回報數: {summary['deal_count']}")
    
    # 登出
    print("\n" + "=" * 60)
    print("登出")
    print("=" * 60)
    trader.logout()
    print("✓ 登出成功")
    
    print("\n" + "=" * 60)
    print("示範程式執行完畢")
    print("=" * 60)


def monitor_order_reports_example():
    """監控委託回報範例
    
    展示如何即時監控委託回報。
    """
    print("="*60)
    print("即時監控委託回報範例")
    print("="*60)
    print("⚠️ 此為示範程式碼（已註解）")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 啟用回報記錄
    trader.enable_order_report_recording()
    
    # ⚠️ 取消下面的註解以執行真實監控
    # print("開始監控委託回報（持續 30 秒）...")
    # print("下單後會自動記錄並顯示回報\n")
    
    # start_time = time.time()
    # last_count = 0
    
    # while time.time() - start_time < 30:
    #     # 取得當前回報數
    #     summary = trader.get_report_summary()
    #     current_count = summary['total_count']
        
    #     # 如果有新的回報
    #     if current_count > last_count:
    #         new_reports = current_count - last_count
    #         print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到 {new_reports} 筆新回報")
            
    #         # 顯示最新的回報
    #         order_reports = trader.get_order_reports(limit=new_reports)
    #         deal_reports = trader.get_deal_reports(limit=new_reports)
            
    #         for report in (order_reports + deal_reports)[-new_reports:]:
    #             print(f"  類型: {report['type']}, 狀態: {report['stat']}")
        
    #         last_count = current_count
        
    #     time.sleep(1)
    
    # print("\n監控結束")
    # summary = trader.get_report_summary()
    # print(f"總計收到 {summary['total_count']} 筆回報")
    
    print("⚠️ 實際監控程式碼已註解")
    
    trader.logout()
    print("✓ 完成")


def custom_report_handler_example():
    """自訂回報處理器範例
    
    展示如何結合自訂 callback 與回報記錄功能。
    """
    print("="*60)
    print("自訂回報處理器範例")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 定義自訂的 callback
    def my_order_callback(stat, msg):
        """自訂的委託回報處理器"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] 自訂處理器接收到回報")
        print(f"  狀態: {stat}")
        print(f"  訊息: {msg}")
        print()
    
    # 設定自訂 callback
    trader.set_order_callback(my_order_callback)
    
    # 啟用回報記錄（會保留自訂 callback）
    trader.enable_order_report_recording()
    
    print("✓ 已設定自訂 callback 並啟用回報記錄")
    print("  - 回報會同時觸發自訂 callback")
    print("  - 回報也會自動記錄到歷史中")
    print()
    
    # ⚠️ 下單測試（已註解）
    # trade = trader.buy_stock("2330", price=500.0, quantity=1000)
    # time.sleep(3)
    
    # # 查詢記錄的回報
    # reports = trader.get_order_reports()
    # print(f"記錄的回報數: {len(reports)}")
    
    trader.logout()
    print("✓ 完成")


def report_analysis_example():
    """回報分析範例
    
    展示如何分析委託回報資料。
    """
    print("="*60)
    print("回報分析範例")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    trader.enable_order_report_recording()
    
    print("取得回報資料進行分析...\n")
    
    # 取得所有回報
    order_reports = trader.get_order_reports()
    deal_reports = trader.get_deal_reports()
    
    print("="*60)
    print("回報分析結果")
    print("="*60)
    
    # 委託回報統計
    print(f"\n委託回報統計：")
    print(f"  總數: {len(order_reports)}")
    
    if order_reports:
        # 統計各狀態的數量
        status_count = {}
        for report in order_reports:
            status = report['stat']
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"  各狀態數量:")
        for status, count in status_count.items():
            print(f"    {status}: {count}")
    
    # 成交回報統計
    print(f"\n成交回報統計：")
    print(f"  總數: {len(deal_reports)}")
    
    # 時間分布分析
    if order_reports or deal_reports:
        all_reports = order_reports + deal_reports
        if all_reports:
            print(f"\n時間分布：")
            timestamps = [r['timestamp'] for r in all_reports]
            earliest = datetime.fromtimestamp(min(timestamps))
            latest = datetime.fromtimestamp(max(timestamps))
            duration = max(timestamps) - min(timestamps)
            
            print(f"  最早: {earliest.strftime('%H:%M:%S')}")
            print(f"  最晚: {latest.strftime('%H:%M:%S')}")
            print(f"  時間跨度: {duration:.1f} 秒")
            
            if duration > 0:
                rate = len(all_reports) / duration
                print(f"  平均頻率: {rate:.2f} 筆/秒")
    
    trader.logout()
    print("\n✓ 完成")


if __name__ == "__main__":
    # 執行完整示範
    demo_order_report_recording()
    
    # 如果要執行其他範例，請取消下面的註解
    # print("\n" + "="*80 + "\n")
    # monitor_order_reports_example()
    
    # print("\n" + "="*80 + "\n")
    # custom_report_handler_example()
    
    # print("\n" + "="*80 + "\n")
    # report_analysis_example()
