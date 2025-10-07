"""
委託回報使用範例

此範例展示如何使用 ShioajiBroker 和 OrderCallbackHandler 來接收委託回報。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.broker.shioaji_broker import ShioajiBroker
from src.broker.order_callback_handler import OrderCallbackHandler, OrderEventListener


class MyOrderListener:
    """自訂委託事件監聽器範例"""
    
    def on_order_status_changed(self, order_status: dict) -> None:
        """
        處理委託狀態變更事件
        
        Args:
            order_status (dict): 委託狀態資訊
        """
        print("=" * 50)
        print("委託狀態變更通知")
        print(f"委託編號: {order_status['order_id']}")
        print(f"狀態: {order_status['status']}")
        print(f"股票代碼: {order_status['stock_id']}")
        print(f"委託數量: {order_status['order_quantity']}")
        print(f"成交數量: {order_status['deal_quantity']}")
        print(f"委託價格: {order_status['order_price']}")
        print(f"委託時間: {order_status['order_time']}")
        print("=" * 50)
    
    def on_deal_received(self, deal_info: dict) -> None:
        """
        處理成交回報事件
        
        Args:
            deal_info (dict): 成交資訊
        """
        print("=" * 50)
        print("成交回報通知")
        print(f"委託編號: {deal_info['order_id']}")
        print(f"股票代碼: {deal_info['stock_id']}")
        print(f"成交數量: {deal_info['deal_quantity']}")
        print(f"成交價格: {deal_info['deal_price']}")
        print(f"成交時間: {deal_info['deal_time']}")
        print("=" * 50)


def main():
    """主程式"""
    # 永豐證券 API 金鑰（請替換為您的金鑰）
    API_KEY = "YOUR_API_KEY"
    SECRET_KEY = "YOUR_SECRET_KEY"
    
    # 建立券商實例
    broker = ShioajiBroker()
    
    try:
        # 連線到永豐證券（使用模擬環境）
        print("正在連線到永豐證券...")
        broker.connect(API_KEY, SECRET_KEY, simulation=True)
        print("連線成功！")
        
        # 建立委託回報處理器
        order_handler = OrderCallbackHandler()
        
        # 建立並註冊監聽器
        listener = MyOrderListener()
        order_handler.register_listener(listener)
        print("已註冊委託事件監聽器")
        
        # 設定委託回報回調
        broker.setup_order_callback(order_handler)
        print("已設定委託回報回調")
        
        # 保持程式運行以接收回報
        print("\n等待委託回報...")
        print("按 Ctrl+C 結束程式\n")
        
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        if broker.is_connected:
            print("正在斷開連線...")
            broker.disconnect()
            print("已斷開連線")


if __name__ == "__main__":
    main()
