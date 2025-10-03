"""
永豐 Shioaji API 登入使用範例

此範例展示如何使用 Config 和 Login 類別進行登入管理。
"""

from src.config import Config, ConfigError
from src.login import Login, LoginError


def example_basic_login():
    """基本登入範例"""
    print("=" * 60)
    print("範例 1：基本登入")
    print("=" * 60)
    
    try:
        # 載入配置
        print("\n[1] 載入配置檔案...")
        config = Config("config.yaml")
        print(f"✅ 配置載入成功 - {config.person_id}")
        
        # 建立登入物件
        print("\n[2] 建立登入物件...")
        login = Login(config)
        print(f"✅ 登入物件已建立 - {repr(login)}")
        
        # 執行登入
        print("\n[3] 執行登入...")
        login.login()
        print("✅ 登入成功！")
        print(f"   登入狀態: {login.is_logged_in}")
        
        # 這裡可以使用 login.api 進行交易操作
        # 例如：查詢帳戶資訊、下單等
        
        # 登出
        print("\n[4] 執行登出...")
        login.logout()
        print("✅ 登出成功！")
        print(f"   登入狀態: {login.is_logged_in}")
        
    except ConfigError as e:
        print(f"\n⚠️ 配置錯誤: {e}")
    except LoginError as e:
        print(f"\n⚠️ 登入錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")


def example_context_manager():
    """使用 Context Manager 的範例（推薦）"""
    print("\n\n" + "=" * 60)
    print("範例 2：使用 Context Manager（推薦）")
    print("=" * 60)
    
    try:
        print("\n[1] 使用 with 語句自動管理登入/登出...")
        
        with Login(Config("config.yaml")) as login:
            print(f"✅ 自動登入成功 - {repr(login)}")
            print(f"   登入狀態: {login.is_logged_in}")
            
            # 這裡可以使用 login.api 進行交易
            print("\n[2] 可以在這裡進行交易操作...")
            # 例如：
            # contracts = login.api.Contracts
            # order = login.api.Order(...)
            
        print("\n✅ 自動登出完成（離開 with 區塊時自動執行）")
        
    except ConfigError as e:
        print(f"\n⚠️ 配置錯誤: {e}")
    except LoginError as e:
        print(f"\n⚠️ 登入錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")


def example_error_handling():
    """錯誤處理範例"""
    print("\n\n" + "=" * 60)
    print("範例 3：錯誤處理")
    print("=" * 60)
    
    # 範例：處理配置檔案不存在
    print("\n[測試 1] 配置檔案不存在...")
    try:
        config = Config("non_existent.yaml")
    except ConfigError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 範例：處理重複登入
    print("\n[測試 2] 重複登入...")
    try:
        config = Config("config.yaml")
        login = Login(config)
        
        # 模擬：如果 shioaji 未安裝，會在這裡失敗
        # login.login()
        # login.login()  # 第二次登入會拋出異常
        
        print("（跳過實際登入測試，避免真實 API 呼叫）")
        
    except ConfigError as e:
        print(f"✅ 配置錯誤: {e}")
    except LoginError as e:
        print(f"✅ 正確捕獲登入錯誤: {e}")


def main():
    """主程式"""
    print("🚀 永豐 Shioaji API 登入範例")
    print()
    
    # 範例 1：基本登入
    example_basic_login()
    
    # 範例 2：Context Manager
    example_context_manager()
    
    # 範例 3：錯誤處理
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)
    
    print("\n💡 提示：")
    print("1. 確保已建立 config.yaml 並填入正確的憑證")
    print("2. 建議使用 Context Manager 進行登入管理")
    print("3. 務必處理所有可能的異常")
    print("4. 實際使用時請安裝 shioaji：pip install shioaji")


if __name__ == "__main__":
    main()
