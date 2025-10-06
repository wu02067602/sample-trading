"""
Shioaji Connector 使用範例

此檔案展示如何使用 ShioajiConnector 進行登入和基本操作。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
from shioaji_connector import ShioajiConnector, create_connector

# 設置日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_basic_usage():
    """
    範例 1: 基本使用方式
    
    展示如何建立連線器、登入和登出。
    """
    print("\n" + "="*60)
    print("範例 1: 基本使用方式")
    print("="*60)
    
    # 建立連線器 (模擬環境)
    connector = ShioajiConnector(simulation=True)
    print(f"連線器實例: {connector}")
    
    # 登入 (請替換為您的實際帳號密碼)
    # 注意：這裡使用模擬環境，實際使用請將 simulation 設為 False
    try:
        success = connector.login(
            person_id="YOUR_PERSON_ID",  # 替換為您的身分證字號
            passwd="YOUR_PASSWORD"        # 替換為您的密碼
        )
        
        if success:
            print("✅ 登入成功！")
            print(f"連線狀態: {connector.get_connection_status()}")
            
            # 使用 connector.sj 進行後續操作
            # 例如：查詢合約、下單等
            if connector.sj:
                print(f"Shioaji API 實例可用: {connector.sj}")
            
            # 登出
            connector.logout()
            print("✅ 登出成功！")
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_context_manager():
    """
    範例 2: 使用 Context Manager
    
    展示如何使用 with 語句自動管理連線生命週期。
    """
    print("\n" + "="*60)
    print("範例 2: Context Manager 使用方式")
    print("="*60)
    
    try:
        with ShioajiConnector(simulation=True) as connector:
            print(f"進入 with 區塊: {connector}")
            
            # 登入
            connector.login(
                person_id="YOUR_PERSON_ID",
                passwd="YOUR_PASSWORD"
            )
            
            # 進行交易操作
            status = connector.get_connection_status()
            print(f"連線狀態: {status}")
            
            # 離開 with 區塊時會自動登出
        print("✅ 已自動登出")
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_with_certificate():
    """
    範例 3: 使用憑證登入 (啟用下單功能)
    
    展示如何使用憑證進行完整登入，取得下單權限。
    """
    print("\n" + "="*60)
    print("範例 3: 使用憑證登入 (啟用下單功能)")
    print("="*60)
    
    try:
        connector = ShioajiConnector(
            api_key="YOUR_API_KEY",      # 替換為您的 API Key
            secret_key="YOUR_SECRET_KEY", # 替換為您的 Secret Key
            simulation=True
        )
        
        # 使用憑證登入
        success = connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD",
            ca_path="/path/to/your/certificate.pfx",  # 憑證檔案路徑
            ca_passwd="YOUR_CERT_PASSWORD"             # 憑證密碼
        )
        
        if success:
            print("✅ 登入成功，已啟用下單功能！")
            
            # 現在可以使用 connector.sj 進行下單操作
            # 例如：connector.sj.place_order(...)
            
            connector.logout()
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_convenience_function():
    """
    範例 4: 使用便利函數
    
    展示如何使用模組提供的便利函數快速建立連線器。
    """
    print("\n" + "="*60)
    print("範例 4: 使用便利函數")
    print("="*60)
    
    try:
        # 使用便利函數建立連線器
        connector = create_connector(
            api_key="YOUR_API_KEY",
            secret_key="YOUR_SECRET_KEY",
            simulation=True
        )
        
        print(f"連線器: {connector}")
        print(f"狀態: {connector.get_connection_status()}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_error_handling():
    """
    範例 5: 錯誤處理
    
    展示如何處理各種可能的錯誤情況。
    """
    print("\n" + "="*60)
    print("範例 5: 錯誤處理")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        
        # 測試：使用空的帳號密碼
        try:
            connector.login(person_id="", passwd="")
        except ValueError as e:
            print(f"✅ 捕獲預期的 ValueError: {e}")
        
        # 測試：查看未登入時的狀態
        status = connector.get_connection_status()
        print(f"未登入狀態: {status}")
        
        # 測試：未登入時嘗試登出
        result = connector.logout()
        print(f"未登入時登出結果: {result}")
        
    except Exception as e:
        print(f"❌ 未預期的錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji Connector 使用範例集")
    print("="*60)
    print("\n⚠️  注意事項：")
    print("1. 請先安裝 shioaji: pip install -r requirements.txt")
    print("2. 將範例中的 YOUR_PERSON_ID、YOUR_PASSWORD 等替換為實際值")
    print("3. 建議先在模擬環境測試 (simulation=True)")
    print("4. 憑證檔案需要從永豐金證券官網下載")
    
    # 執行範例
    try:
        example_1_basic_usage()
        example_2_context_manager()
        example_4_convenience_function()
        example_5_error_handling()
        
        # example_3_with_certificate()  # 需要實際憑證，預設註解
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
