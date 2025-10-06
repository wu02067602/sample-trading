"""
Shioaji 證券下單使用範例

此檔案展示如何使用 ShioajiConnector 進行股票下單操作。

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


def example_1_basic_stock_order():
    """
    範例 1: 基本股票下單
    
    展示如何進行基本的股票買賣下單。
    """
    print("\n" + "="*60)
    print("範例 1: 基本股票下單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        
        # 登入並啟用憑證（下單需要憑證）
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 取得股票合約
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            print(f"準備下單: {stock.code} {stock.name}")
            
            # 限價買入 1000 股
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000,
                order_type="ROD",
                price_type="LMT"
            )
            
            if trade:
                print("✅ 下單成功！")
                print(f"訂單編號: {trade.order.id}")
                print(f"委託價格: {trade.order.price}")
                print(f"委託數量: {trade.order.quantity}")
            else:
                print("❌ 下單失敗")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_market_order():
    """
    範例 2: 市價下單
    
    展示如何進行市價單下單。
    """
    print("\n" + "="*60)
    print("範例 2: 市價下單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 市價買入（價格設為 0）
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=0,  # 市價單價格設為 0
                quantity=1000,
                price_type="MKT"
            )
            
            if trade:
                print("✅ 市價單下單成功！")
                print(f"訂單編號: {trade.order.id}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_odd_lot_order():
    """
    範例 3: 盤中零股下單
    
    展示如何進行盤中零股交易。
    """
    print("\n" + "="*60)
    print("範例 3: 盤中零股下單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 買入 100 股零股
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=100,  # 零股數量 < 1000
                odd_lot=True   # 標記為零股交易
            )
            
            if trade:
                print("✅ 零股下單成功！")
                print(f"訂單編號: {trade.order.id}")
                print(f"零股數量: {trade.order.quantity}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_ioc_order():
    """
    範例 4: IOC 委託
    
    展示立即成交否則取消的委託類型。
    """
    print("\n" + "="*60)
    print("範例 4: IOC 委託（立即成交否則取消）")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # IOC 委託
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000,
                order_type="IOC"  # 立即成交否則取消
            )
            
            if trade:
                print("✅ IOC 委託成功！")
                print("此訂單會立即嘗試成交，無法成交的部分將被取消")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_cancel_order():
    """
    範例 5: 取消訂單
    
    展示如何取消已下的訂單。
    """
    print("\n" + "="*60)
    print("範例 5: 取消訂單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 先下單
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000
            )
            
            if trade:
                print("✅ 下單成功")
                print(f"訂單編號: {trade.order.id}")
                
                # 等待一下
                time.sleep(1)
                
                # 取消訂單
                success = connector.cancel_order(trade)
                
                if success:
                    print("✅ 訂單已取消")
                else:
                    print("❌ 取消訂單失敗")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_update_order():
    """
    範例 6: 修改訂單
    
    展示如何修改已下訂單的價格和數量。
    """
    print("\n" + "="*60)
    print("範例 6: 修改訂單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 先下單
            trade = connector.place_order(
                contract=stock,
                action="Buy",
                price=600.0,
                quantity=1000
            )
            
            if trade:
                print("✅ 原始下單成功")
                print(f"原始價格: {trade.order.price}")
                print(f"原始數量: {trade.order.quantity}")
                
                # 等待一下
                time.sleep(1)
                
                # 修改訂單
                new_trade = connector.update_order(
                    trade=trade,
                    price=605.0,
                    quantity=2000
                )
                
                if new_trade:
                    print("✅ 訂單已修改")
                    print(f"新價格: 605.0")
                    print(f"新數量: 2000")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_7_list_positions():
    """
    範例 7: 查詢持股明細
    
    展示如何查詢目前的持股。
    """
    print("\n" + "="*60)
    print("範例 7: 查詢持股明細")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 查詢持股
        positions = connector.list_positions()
        
        if positions:
            print(f"\n目前持股 {len(positions)} 檔:")
            for pos in positions:
                print(f"\n商品: {pos.code}")
                print(f"數量: {pos.quantity}")
                print(f"成本: {pos.price}")
                print(f"市值: {pos.pnl}")
        else:
            print("目前無持股")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_8_list_trades():
    """
    範例 8: 查詢今日委託
    
    展示如何查詢今日所有的委託記錄。
    """
    print("\n" + "="*60)
    print("範例 8: 查詢今日委託")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 查詢委託
        trades = connector.list_trades()
        
        if trades:
            print(f"\n今日委託 {len(trades)} 筆:")
            for trade in trades:
                print(f"\n訂單編號: {trade.order.id}")
                print(f"商品: {trade.contract.code} {trade.contract.name}")
                print(f"動作: {trade.order.action}")
                print(f"價格: {trade.order.price}")
                print(f"數量: {trade.order.quantity}")
                print(f"狀態: {trade.status.status}")
        else:
            print("今日無委託記錄")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_9_orders_history():
    """
    範例 9: 查詢本次連線下單歷史
    
    展示如何查詢本次連線期間的所有下單記錄。
    """
    print("\n" + "="*60)
    print("範例 9: 查詢下單歷史")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 進行幾筆下單
        stock = connector.get_stock_by_code("2330")
        
        if stock:
            # 下單 1
            connector.place_order(stock, "Buy", 600.0, 1000)
            time.sleep(0.5)
            
            # 下單 2
            connector.place_order(stock, "Sell", 605.0, 1000)
            time.sleep(0.5)
        
        # 查詢下單歷史
        history = connector.get_orders_history()
        
        print(f"\n本次連線共下 {len(history)} 筆訂單:")
        for i, order in enumerate(history, 1):
            print(f"\n訂單 {i}:")
            print(f"  商品: {order['contract'].code} {order['contract'].name}")
            print(f"  動作: {order['action']}")
            print(f"  價格: {order['price']}")
            print(f"  數量: {order['quantity']}")
            print(f"  類型: {'零股' if order['odd_lot'] else '整股'}")
            print(f"  時間: {order['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_10_multiple_orders():
    """
    範例 10: 批量下單
    
    展示如何批量下多個訂單。
    """
    print("\n" + "="*60)
    print("範例 10: 批量下單")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/cert.pfx",
            ca_passwd="CERT_PASSWORD"
        )
        
        # 準備下單列表
        orders = [
            {"code": "2330", "action": "Buy", "price": 600.0, "quantity": 1000},
            {"code": "2317", "action": "Buy", "price": 120.0, "quantity": 2000},
            {"code": "2454", "action": "Buy", "price": 1000.0, "quantity": 1000},
        ]
        
        success_count = 0
        
        for order_info in orders:
            stock = connector.get_stock_by_code(order_info["code"])
            
            if stock:
                trade = connector.place_order(
                    contract=stock,
                    action=order_info["action"],
                    price=order_info["price"],
                    quantity=order_info["quantity"]
                )
                
                if trade:
                    success_count += 1
                    print(f"✅ {stock.code} {stock.name} 下單成功")
                else:
                    print(f"❌ {stock.code} 下單失敗")
                
                # 避免下單太快
                time.sleep(0.3)
        
        print(f"\n批量下單完成: 成功 {success_count}/{len(orders)} 筆")
        
        # 查看連線狀態
        status = connector.get_connection_status()
        print(f"本次連線共下 {status['orders_count']} 筆訂單")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 證券下單使用範例集")
    print("="*60)
    print("\n⚠️  重要警告：")
    print("1. 下單功能會產生實際交易，請謹慎使用！")
    print("2. 建議先在模擬環境測試 (simulation=True)")
    print("3. 需要啟用憑證才能下單")
    print("4. 請將 YOUR_PERSON_ID、YOUR_PASSWORD 等替換為實際值")
    print("5. 盤中零股交易時間：09:00-13:30")
    print("6. 整股交易時間：09:00-13:30")
    
    # 執行範例
    try:
        example_1_basic_stock_order()
        example_2_market_order()
        example_3_odd_lot_order()
        example_4_ioc_order()
        example_5_cancel_order()
        example_6_update_order()
        example_7_list_positions()
        example_8_list_trades()
        example_9_orders_history()
        example_10_multiple_orders()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 提示：")
    print("- 使用 connector.place_order() 下單")
    print("- 使用 connector.cancel_order() 取消訂單")
    print("- 使用 connector.update_order() 修改訂單")
    print("- 使用 connector.list_positions() 查詢持股")
    print("- 使用 connector.list_trades() 查詢委託")
    print("- ROD: 當日有效單")
    print("- IOC: 立即成交否則取消")
    print("- FOK: 全部成交否則取消")
