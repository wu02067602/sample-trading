#!/usr/bin/env python3
"""
BrokerageAuth 最小使用範例

此檔案展示 BrokerageAuth 的基本使用方法，
適合快速上手和整合到現有專案中。

使用前請確保環境變數已設定：
export BROKER_API_KEY="your_api_key"
export BROKER_CERT_PATH="/path/to/your/cert.pem"

Author: Senior Backend Engineer
Date: 2025-09-25
"""

from brokerage_auth import BrokerageAuth, BrokerageAuthError


def simple_usage_example():
    """最簡單的使用方式"""
    print("🚀 最簡單的使用方式")
    print("-" * 30)
    
    try:
        # 一行初始化，自動處理所有認證邏輯
        auth = BrokerageAuth()
        session = auth.get_session()  # 自動登入 + 自動刷新
        
        print("✅ 認證成功！可以開始使用 API")
        print(f"Session 類型: {type(session)}")
        
        # 使用 Session 進行 API 調用（範例）
        # contracts = session.Contracts.Stocks
        # print(f"股票合約數量: {len(contracts)}")
        
        return session
        
    except BrokerageAuthError as e:
        print(f"❌ 認證失敗: {e}")
        return None


def advanced_usage_example():
    """進階使用方式，展示更多控制選項"""
    print("\n🔧 進階使用方式")
    print("-" * 30)
    
    try:
        # 自訂 Token 有效期限
        auth = BrokerageAuth(token_lifetime_hours=12)
        
        # 檢查初始狀態
        status = auth.get_status()
        print(f"初始狀態: {status['logged_in']}")
        
        # 手動登入
        login_result = auth.login()
        print(f"登入時間: {login_result['login_time']}")
        
        # 檢查登入狀態
        if auth.is_logged_in():
            print("✅ 確認已登入")
            
            # 獲取詳細狀態
            status = auth.get_status()
            print(f"下次刷新時間: {status['next_refresh_time']}")
            
            # 主動刷新（通常不需要，get_session 會自動處理）
            refresh_result = auth.refresh()
            print(f"刷新完成: {refresh_result['status']}")
        
        return auth.get_session()
        
    except BrokerageAuthError as e:
        print(f"❌ 進階操作失敗: {e}")
        return None


def error_handling_example():
    """錯誤處理範例"""
    print("\n🛡️ 錯誤處理範例")
    print("-" * 30)
    
    from brokerage_auth import (
        EnvironmentError, CertificateError, 
        AuthenticationError, SessionError
    )
    
    try:
        auth = BrokerageAuth()
        session = auth.get_session()
        print("✅ 正常情況下的認證流程")
        
    except EnvironmentError as e:
        print(f"🔧 環境設定問題: {e}")
        print("💡 請檢查環境變數 BROKER_API_KEY 和 BROKER_CERT_PATH")
        
    except CertificateError as e:
        print(f"📜 憑證檔案問題: {e}")
        print("💡 請確認憑證檔案路徑正確且有讀取權限")
        
    except AuthenticationError as e:
        print(f"🔐 認證失敗: {e}")
        print("💡 請檢查 API Key 正確性和網路連線")
        
    except SessionError as e:
        print(f"📱 Session 錯誤: {e}")
        print("💡 請重新執行認證流程")


def integration_example():
    """整合到現有專案的範例"""
    print("\n🔗 專案整合範例")
    print("-" * 30)
    
    class TradingBot:
        """交易機器人範例類別"""
        
        def __init__(self):
            self.auth = BrokerageAuth()
            self.session = None
        
        def start(self):
            """啟動交易機器人"""
            try:
                print("🤖 啟動交易機器人...")
                self.session = self.auth.get_session()
                print("✅ 認證完成，交易機器人已就緒")
                return True
                
            except BrokerageAuthError as e:
                print(f"❌ 交易機器人啟動失敗: {e}")
                return False
        
        def get_market_data(self):
            """獲取市場資料"""
            if not self.session:
                print("⚠️ 未登入，重新認證中...")
                self.session = self.auth.get_session()
            
            # 使用 Session 獲取市場資料
            print("📊 獲取市場資料中...")
            # market_data = self.session.marketdata.something()
            return "模擬市場資料"
        
        def place_order(self, order_details):
            """下單"""
            if not self.auth.is_logged_in():
                print("⚠️ Session 無效，重新認證...")
                self.session = self.auth.get_session()
            
            print(f"📝 執行下單: {order_details}")
            # result = self.session.place_order(order_details)
            return "下單成功（模擬）"
        
        def stop(self):
            """停止交易機器人"""
            print("🛑 停止交易機器人...")
            if self.auth:
                logout_result = self.auth.logout()
                print(f"👋 {logout_result['message']}")
    
    # 使用範例
    try:
        bot = TradingBot()
        if bot.start():
            # 模擬交易操作
            market_data = bot.get_market_data()
            order_result = bot.place_order({"symbol": "2330", "qty": 1000})
            print(f"市場資料: {market_data}")
            print(f"下單結果: {order_result}")
        
        bot.stop()
        
    except Exception as e:
        print(f"❌ 交易機器人運行錯誤: {e}")


def main():
    """主程式 - 執行所有範例"""
    print("📚 BrokerageAuth 使用範例")
    print("=" * 50)
    
    # 1. 最簡單的使用方式
    session = simple_usage_example()
    
    # 2. 進階使用方式（如果簡單方式成功）
    if session:
        advanced_usage_example()
    
    # 3. 錯誤處理範例
    error_handling_example()
    
    # 4. 專案整合範例
    integration_example()
    
    print("\n🎉 範例展示完成！")
    print("\n💡 建議:")
    print("   - 生產環境中使用 simple_usage_example() 的方式")
    print("   - 根據需要添加適當的錯誤處理")
    print("   - 定期檢查認證狀態以確保服務穩定")


if __name__ == "__main__":
    main()