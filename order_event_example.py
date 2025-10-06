"""
Shioaji 委託回報（Order Event）使用範例

此檔案展示如何使用 ShioajiConnector 監控和查詢訂單委託回報。
委託回報是指訂單狀態的變更通知，包括已委託、部分成交、全部成交、已取消等狀態。

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


def example_1_order_event_tracking():
    """
    範例 1: 委託回報追蹤
    
    展示如何追蹤訂單的完整生命週期。
    """
    print("\n" + "="*60)
    print("範例 1: 委託回報追蹤")
    print("="*60)
    
    def order_event_handler(stat):
        """委託回報處理函數"""
        print(f"\n[委託回報]")
        print(f"  訂單編號: {stat.order_id}")
        print(f"  訂單狀態: {stat.status}")
        print(f"  委託數量: {stat.order.quantity}")
        print(f"  已成交數量: {stat.deal_quantity}")
        print(f"  未成交數量: {stat.order.quantity - stat.deal_quantity}")
        print("-" * 40)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊委託回報處理函數
        connector.set_order_callback(order_event_handler)
        print("✅ 已註冊委託回報處理函數")
        
        # 下單
        stock = connector.get_stock_by_code("2330")
        if stock:
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000
            )
            
            if trade:
                print(f"\n✅ 下單成功，訂單編號: {trade.order.id}")
                print("開始追蹤訂單狀態...")
                time.sleep(10)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_query_by_order_id():
    """
    範例 2: 按訂單編號查詢委託回報
    
    展示如何查詢特定訂單的所有狀態變更記錄。
    """
    print("\n" + "="*60)
    print("範例 2: 按訂單編號查詢委託回報")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊委託回報（簡單記錄）
        connector.set_order_callback(lambda stat: None)
        
        # 下單
        stock = connector.get_stock_by_code("2330")
        if stock:
            trade = connector.place_order(stock, "Buy", 600.0, 1000)
            
            if trade:
                order_id = trade.order.id
                print(f"訂單編號: {order_id}")
                
                # 等待接收委託回報
                time.sleep(5)
                
                # 查詢該訂單的所有狀態更新
                updates = connector.get_order_update_by_id(order_id)
                
                print(f"\n該訂單的委託回報記錄（共 {len(updates)} 筆）:")
                for i, update in enumerate(updates, 1):
                    print(f"\n更新 {i}:")
                    print(f"  時間: {update['timestamp'].strftime('%H:%M:%S')}")
                    print(f"  狀態: {update['status']}")
                    print(f"  已成交: {update['deal_quantity']} 股")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_query_by_status():
    """
    範例 3: 按狀態查詢委託回報
    
    展示如何查詢特定狀態的所有訂單。
    """
    print("\n" + "="*60)
    print("範例 3: 按狀態查詢委託回報")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊委託回報
        connector.set_order_callback(lambda stat: print(f"📝 {stat.order_id}: {stat.status}"))
        
        # 下多筆單
        stock = connector.get_stock_by_code("2330")
        if stock:
            # 下 3 筆不同的單
            connector.place_order(stock, "Buy", 600.0, 1000)  # 限價單
            time.sleep(1)
            connector.place_order(stock, "Buy", 0, 1000, price_type="MKT")  # 市價單
            time.sleep(1)
            
            # 下單後立即取消
            trade = connector.place_order(stock, "Buy", 610.0, 1000)
            if trade:
                time.sleep(1)
                connector.cancel_order(trade)
        
        # 等待接收委託回報
        time.sleep(5)
        
        # 按狀態查詢
        print("\n=== 委託回報分類查詢 ===")
        
        submitted = connector.get_order_updates_by_status("Submitted")
        print(f"\n已委託（Submitted）: {len(submitted)} 筆")
        for update in submitted:
            print(f"  - 訂單 {update['order_id']}")
        
        filled = connector.get_order_updates_by_status("Filled")
        print(f"\n已成交（Filled）: {len(filled)} 筆")
        for update in filled:
            print(f"  - 訂單 {update['order_id']}")
        
        cancelled = connector.get_order_updates_by_status("Cancelled")
        print(f"\n已取消（Cancelled）: {len(cancelled)} 筆")
        for update in cancelled:
            print(f"  - 訂單 {update['order_id']}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_order_status_summary():
    """
    範例 4: 委託狀態統計
    
    展示如何統計各種訂單狀態的數量。
    """
    print("\n" + "="*60)
    print("範例 4: 委託狀態統計")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊委託回報
        connector.set_order_callback(lambda stat: None)
        
        # 執行多筆交易
        stock = connector.get_stock_by_code("2330")
        if stock:
            for i in range(5):
                connector.place_order(stock, "Buy", 600.0 + i, 1000)
                time.sleep(0.5)
        
        # 等待接收委託回報
        time.sleep(5)
        
        # 取得統計摘要
        summary = connector.get_order_updates_summary()
        
        print("\n=== 委託回報統計摘要 ===")
        print(f"總委託回報數: {sum(summary.values())} 筆")
        print("\n各狀態分布:")
        for status, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / sum(summary.values())) * 100
            print(f"  {status:15s}: {count:3d} 筆 ({percentage:5.1f}%)")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_order_lifecycle():
    """
    範例 5: 訂單生命週期追蹤
    
    展示一個訂單從委託到成交的完整過程。
    """
    print("\n" + "="*60)
    print("範例 5: 訂單生命週期追蹤")
    print("="*60)
    
    # 記錄訂單生命週期
    order_lifecycle = []
    
    def lifecycle_tracker(stat):
        """追蹤訂單生命週期"""
        order_lifecycle.append({
            'time': time.strftime('%H:%M:%S'),
            'order_id': stat.order_id,
            'status': stat.status,
            'deal_quantity': stat.deal_quantity
        })
        print(f"[{time.strftime('%H:%M:%S')}] {stat.order_id} -> {stat.status}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊生命週期追蹤
        connector.set_order_callback(lifecycle_tracker)
        
        # 下市價單（容易成交）
        stock = connector.get_stock_by_code("2330")
        if stock:
            print("\n下市價單，追蹤訂單狀態變化...")
            trade = connector.place_order(
                stock, "Buy", 0, 1000, price_type="MKT"
            )
            
            if trade:
                order_id = trade.order.id
                
                # 等待完整的生命週期
                time.sleep(10)
                
                # 顯示完整生命週期
                print(f"\n=== 訂單 {order_id} 的完整生命週期 ===")
                for i, event in enumerate(order_lifecycle, 1):
                    print(f"\n階段 {i}:")
                    print(f"  時間: {event['time']}")
                    print(f"  狀態: {event['status']}")
                    print(f"  已成交: {event['deal_quantity']} 股")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_callback_management():
    """
    範例 6: 委託回報回調管理
    
    展示如何管理委託回報回調函數。
    """
    print("\n" + "="*60)
    print("範例 6: 委託回報回調管理")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 階段 1: 註冊回調
        print("\n階段 1: 註冊委託回報回調")
        connector.set_order_callback(lambda stat: print(f"📝 委託回報: {stat.status}"))
        
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.place_order(stock, "Buy", 600.0, 1000)
            time.sleep(3)
        
        # 階段 2: 清除回調
        print("\n階段 2: 清除委託回報回調")
        connector.clear_order_update_callbacks()
        print("✅ 已清除回調函數")
        
        if stock:
            print("\n下單後將不會收到委託回報通知...")
            connector.place_order(stock, "Buy", 601.0, 1000)
            time.sleep(3)
        
        # 階段 3: 重新註冊
        print("\n階段 3: 重新註冊委託回報回調")
        connector.set_order_callback(lambda stat: print(f"🔔 新回調: {stat.status}"))
        
        if stock:
            connector.place_order(stock, "Buy", 602.0, 1000)
            time.sleep(3)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_7_comprehensive_tracking():
    """
    範例 7: 綜合委託回報追蹤
    
    展示完整的委託回報監控和查詢功能。
    """
    print("\n" + "="*60)
    print("範例 7: 綜合委託回報追蹤")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊委託回報
        connector.set_order_callback(lambda stat: None)
        print("✅ 已啟動委託回報監控")
        
        # 執行多種交易
        stock = connector.get_stock_by_code("2330")
        if stock:
            print("\n執行多種交易操作...")
            
            # 限價單
            connector.place_order(stock, "Buy", 600.0, 1000)
            time.sleep(1)
            
            # 市價單
            connector.place_order(stock, "Buy", 0, 1000, price_type="MKT")
            time.sleep(1)
            
            # 下單後取消
            trade = connector.place_order(stock, "Buy", 610.0, 1000)
            if trade:
                time.sleep(1)
                connector.cancel_order(trade)
        
        # 等待接收所有委託回報
        time.sleep(5)
        
        # 綜合報告
        print("\n" + "="*60)
        print("=== 委託回報綜合報告 ===")
        print("="*60)
        
        # 1. 總體統計
        all_updates = connector.get_order_updates()
        print(f"\n1. 總體統計")
        print(f"   總委託回報數: {len(all_updates)} 筆")
        
        # 2. 狀態分布
        summary = connector.get_order_updates_summary()
        print(f"\n2. 狀態分布")
        for status, count in summary.items():
            print(f"   {status}: {count} 筆")
        
        # 3. 最新委託
        if all_updates:
            latest = all_updates[-1]
            print(f"\n3. 最新委託")
            print(f"   訂單編號: {latest['order_id']}")
            print(f"   狀態: {latest['status']}")
            print(f"   時間: {latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 4. 已成交訂單
        filled = connector.get_order_updates_by_status("Filled")
        print(f"\n4. 已成交訂單: {len(filled)} 筆")
        
        # 5. 已取消訂單
        cancelled = connector.get_order_updates_by_status("Cancelled")
        print(f"\n5. 已取消訂單: {len(cancelled)} 筆")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 委託回報（Order Event）使用範例集")
    print("="*60)
    print("\n⚠️  重要說明：")
    print("1. 委託回報 = 訂單狀態變更通知")
    print("2. 包括：已委託、部分成交、全部成交、已取消等")
    print("3. 需要啟用憑證才能下單和接收回報")
    print("4. 建議先在模擬環境測試 (simulation=True)")
    print("5. 請將 YOUR_PERSON_ID、YOUR_PASSWORD 等替換為實際值")
    
    # 執行範例
    try:
        example_1_order_event_tracking()
        example_2_query_by_order_id()
        example_3_query_by_status()
        example_4_order_status_summary()
        example_5_order_lifecycle()
        example_6_callback_management()
        example_7_comprehensive_tracking()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 委託回報功能總結：")
    print("- set_order_callback() - 註冊委託回報處理函數")
    print("- get_order_updates() - 取得所有委託回報記錄")
    print("- get_order_update_by_id() - 查詢特定訂單的委託記錄")
    print("- get_order_updates_by_status() - 按狀態查詢委託記錄")
    print("- get_order_updates_summary() - 取得委託狀態統計")
    print("- clear_order_update_callbacks() - 清除回調函數")
