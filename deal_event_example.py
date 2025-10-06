"""
Shioaji 成交回報使用範例

此檔案展示如何使用 ShioajiConnector 監控訂單狀態和成交回報。

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


def example_1_order_status_callback():
    """
    範例 1: 訂單狀態回報
    
    展示如何監控訂單狀態變更。
    """
    print("\n" + "="*60)
    print("範例 1: 訂單狀態回報")
    print("="*60)
    
    # 定義訂單狀態處理函數
    def order_status_handler(stat):
        """處理訂單狀態更新"""
        print(f"\n[訂單狀態更新]")
        print(f"  訂單編號: {stat.order_id}")
        print(f"  狀態: {stat.status}")
        print(f"  委託價格: {stat.order.price}")
        print(f"  委託數量: {stat.order.quantity}")
        print(f"  已成交數量: {stat.deal_quantity}")
        print(f"  動作: {stat.order.action}")
        print("-" * 40)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊訂單狀態回調
        connector.set_order_callback(order_status_handler)
        print("✅ 已註冊訂單狀態回調函數")
        
        # 下單
        stock = connector.get_stock_by_code("2330")
        if stock:
            print(f"\n準備下單: {stock.code} {stock.name}")
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000
            )
            
            if trade:
                print(f"✅ 下單成功，訂單編號: {trade.order.id}")
                print("\n等待訂單狀態更新...")
                time.sleep(5)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_deal_callback():
    """
    範例 2: 成交回報
    
    展示如何接收成交回報通知。
    """
    print("\n" + "="*60)
    print("範例 2: 成交回報")
    print("="*60)
    
    # 定義成交回報處理函數
    def deal_handler(deal):
        """處理成交回報"""
        print(f"\n[成交通知]")
        print(f"  商品代碼: {deal.code}")
        print(f"  成交價格: {deal.price}")
        print(f"  成交數量: {deal.quantity}")
        print(f"  成交時間: {deal.ts}")
        print(f"  訂單編號: {deal.order_id}")
        print(f"  成交序號: {deal.seqno}")
        print("-" * 40)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊成交回報回調
        connector.set_deal_callback(deal_handler)
        print("✅ 已註冊成交回報回調函數")
        
        # 下市價單（容易成交）
        stock = connector.get_stock_by_code("2330")
        if stock:
            print(f"\n準備下市價單: {stock.code} {stock.name}")
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=0,
                quantity=1000,
                price_type="MKT"
            )
            
            if trade:
                print(f"✅ 下單成功，等待成交...")
                time.sleep(5)
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_combined_callbacks():
    """
    範例 3: 同時監控訂單狀態和成交回報
    
    展示如何同時處理訂單狀態更新和成交回報。
    """
    print("\n" + "="*60)
    print("範例 3: 同時監控訂單狀態和成交回報")
    print("="*60)
    
    # 統計資訊
    stats = {
        'order_updates': 0,
        'deals': 0,
        'total_deal_quantity': 0
    }
    
    def order_handler(stat):
        """訂單狀態處理"""
        stats['order_updates'] += 1
        print(f"\n[{stats['order_updates']}] 訂單狀態: {stat.status}")
        print(f"    已成交: {stat.deal_quantity} 股")
    
    def deal_handler(deal):
        """成交回報處理"""
        stats['deals'] += 1
        stats['total_deal_quantity'] += deal.quantity
        print(f"\n[{stats['deals']}] 成交: {deal.code}")
        print(f"    價格: {deal.price}, 數量: {deal.quantity}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 同時註冊兩種回調
        connector.set_order_callback(order_handler)
        connector.set_deal_callback(deal_handler)
        print("✅ 已註冊訂單和成交回調函數")
        
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
                print(f"\n✅ 下單成功，開始監控...")
                time.sleep(10)
                
                # 顯示統計
                print(f"\n統計資訊:")
                print(f"  訂單狀態更新: {stats['order_updates']} 次")
                print(f"  成交回報: {stats['deals']} 次")
                print(f"  總成交數量: {stats['total_deal_quantity']} 股")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_deal_history():
    """
    範例 4: 查詢成交歷史
    
    展示如何查詢本次連線的成交記錄。
    """
    print("\n" + "="*60)
    print("範例 4: 查詢成交歷史")
    print("="*60)
    
    def deal_handler(deal):
        """簡單記錄成交"""
        print(f"✅ 成交: {deal.code} {deal.price} x {deal.quantity}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊成交回調
        connector.set_deal_callback(deal_handler)
        
        # 下幾筆單
        stock = connector.get_stock_by_code("2330")
        if stock:
            for i in range(3):
                connector.place_order(stock, "Buy", 600.0 + i, 1000)
                time.sleep(1)
        
        # 等待成交
        time.sleep(5)
        
        # 查詢成交歷史
        deals = connector.get_deals_history()
        print(f"\n成交歷史 (共 {len(deals)} 筆):")
        for i, deal in enumerate(deals, 1):
            print(f"\n成交 {i}:")
            print(f"  商品: {deal['code']}")
            print(f"  價格: {deal['price']}")
            print(f"  數量: {deal['quantity']}")
            print(f"  時間: {deal['ts']}")
            print(f"  本地時間: {deal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_order_updates_history():
    """
    範例 5: 查詢訂單更新歷史
    
    展示如何查詢訂單狀態變更記錄。
    """
    print("\n" + "="*60)
    print("範例 5: 查詢訂單更新歷史")
    print("="*60)
    
    def order_handler(stat):
        """記錄訂單狀態"""
        print(f"📝 訂單 {stat.order_id}: {stat.status}")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊訂單回調
        connector.set_order_callback(order_handler)
        
        # 下單並修改
        stock = connector.get_stock_by_code("2330")
        if stock:
            trade = connector.place_order(stock, "Buy", 600.0, 1000)
            time.sleep(2)
            
            # 修改訂單
            if trade:
                connector.update_order(trade, 605.0, 2000)
                time.sleep(2)
        
        # 查詢訂單更新歷史
        updates = connector.get_order_updates()
        print(f"\n訂單更新歷史 (共 {len(updates)} 筆):")
        for i, update in enumerate(updates, 1):
            print(f"\n更新 {i}:")
            print(f"  訂單編號: {update['order_id']}")
            print(f"  狀態: {update['status']}")
            print(f"  已成交數量: {update['deal_quantity']}")
            print(f"  時間: {update['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_multiple_callbacks():
    """
    範例 6: 註冊多個回調函數
    
    展示如何為同一事件註冊多個處理函數。
    """
    print("\n" + "="*60)
    print("範例 6: 註冊多個回調函數")
    print("="*60)
    
    # 第一個回調：記錄日誌
    def logger_callback(deal):
        print(f"[LOG] 成交: {deal.code} {deal.price} x {deal.quantity}")
    
    # 第二個回調：計算成本
    total_cost = {'value': 0}
    def cost_calculator(deal):
        cost = deal.price * deal.quantity
        total_cost['value'] += cost
        print(f"[COST] 本次成本: {cost:,.0f}, 累計: {total_cost['value']:,.0f}")
    
    # 第三個回調：發送通知
    def notification(deal):
        print(f"[NOTIFY] 📢 {deal.code} 已成交 {deal.quantity} 股")
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊多個回調函數
        connector.set_deal_callback(logger_callback)
        connector.set_deal_callback(cost_calculator)
        connector.set_deal_callback(notification)
        print("✅ 已註冊 3 個成交回調函數")
        
        # 下單
        stock = connector.get_stock_by_code("2330")
        if stock:
            connector.place_order(stock, "Buy", 600.0, 1000, price_type="MKT")
            time.sleep(5)
        
        print(f"\n總成本: {total_cost['value']:,.0f} 元")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_7_connection_status_with_deals():
    """
    範例 7: 檢查連線狀態（包含成交資訊）
    
    展示如何檢查成交和訂單更新的統計資訊。
    """
    print("\n" + "="*60)
    print("範例 7: 檢查連線狀態（包含成交資訊）")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 註冊回調
        connector.set_order_callback(lambda stat: None)
        connector.set_deal_callback(lambda deal: None)
        
        # 下幾筆單
        stock = connector.get_stock_by_code("2330")
        if stock:
            for i in range(3):
                connector.place_order(stock, "Buy", 600.0 + i, 1000)
                time.sleep(1)
        
        time.sleep(5)
        
        # 檢查連線狀態
        status = connector.get_connection_status()
        print("\n連線狀態:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 詳細統計
        print(f"\n詳細統計:")
        print(f"  下單次數: {len(connector.get_orders_history())}")
        print(f"  成交次數: {len(connector.get_deals_history())}")
        print(f"  訂單更新次數: {len(connector.get_order_updates())}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 成交回報使用範例集")
    print("="*60)
    print("\n⚠️  重要提醒：")
    print("1. 需要啟用憑證才能下單和接收回報")
    print("2. 建議先在模擬環境測試 (simulation=True)")
    print("3. 請將 YOUR_PERSON_ID、YOUR_PASSWORD 等替換為實際值")
    print("4. Callback 函數會在事件發生時自動被調用")
    print("5. 支援註冊多個 callback 函數")
    
    # 執行範例
    try:
        example_1_order_status_callback()
        example_2_deal_callback()
        example_3_combined_callbacks()
        example_4_deal_history()
        example_5_order_updates_history()
        example_6_multiple_callbacks()
        example_7_connection_status_with_deals()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 提示：")
    print("- 使用 connector.set_order_callback() 監控訂單狀態")
    print("- 使用 connector.set_deal_callback() 接收成交回報")
    print("- 使用 connector.get_deals_history() 查詢成交歷史")
    print("- 使用 connector.get_order_updates() 查詢訂單更新")
    print("- 支援同時註冊多個 callback 函數")
    print("- Callback 應該快速執行，避免阻塞")
