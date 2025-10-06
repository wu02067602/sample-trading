"""
Shioaji 客戶端使用範例

此檔案展示如何使用 ShioajiClient 進行登入和基本操作。
"""

from shioaji_client import ShioajiClient, LoginConfig
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_basic_login():
    """基本登入範例"""
    # 建立登入配置
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",  # 請替換為您的身分證字號
        passwd="YOUR_PASSWORD",       # 請替換為您的密碼
        simulation=True               # 使用模擬環境進行測試
    )
    
    # 建立客戶端並登入
    client = ShioajiClient()
    
    try:
        # 執行登入
        success = client.login(config)
        print(f"登入成功: {success}")
        
        # 取得帳戶資訊
        accounts = client.get_accounts()
        print(f"股票帳戶: {accounts['stock_account']}")
        print(f"期貨帳戶: {accounts['futopt_account']}")
        
        # 使用 client.sj 進行後續操作
        # ... 您的交易邏輯 ...
        
    finally:
        # 登出
        if client.is_logged_in:
            client.logout()
            print("已登出")


def example_ca_login():
    """使用 CA 憑證登入範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        ca_path="/path/to/your/certificate.pfx",
        ca_passwd="YOUR_CA_PASSWORD",
        simulation=True
    )
    
    client = ShioajiClient()
    
    try:
        success = client.login(config)
        print(f"CA 登入成功: {success}")
        
        # 進行交易操作...
        
    finally:
        if client.is_logged_in:
            client.logout()


def example_context_manager():
    """使用 Context Manager 範例（自動登出）"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    # 使用 with 語句，自動處理登出
    with ShioajiClient() as client:
        client.login(config)
        print("已登入，執行交易操作...")
        
        # 取得帳戶資訊
        accounts = client.get_accounts()
        print(accounts)
        
        # 進行交易操作...
        
    # 離開 with 區塊後自動登出
    print("已自動登出")


if __name__ == "__main__":
    print("=== Shioaji 客戶端使用範例 ===\n")
    
    print("範例 1: 基本登入")
    print("-" * 50)
    # example_basic_login()  # 取消註解並填入正確的認證資訊後執行
    
    print("\n範例 2: CA 憑證登入")
    print("-" * 50)
    # example_ca_login()  # 取消註解並填入正確的認證資訊後執行
    
    print("\n範例 3: 使用 Context Manager")
    print("-" * 50)
    # example_context_manager()  # 取消註解並填入正確的認證資訊後執行
    
    print("\n請修改範例程式碼中的認證資訊後執行")
