"""
永豐 Shioaji API Controller 使用範例

此範例展示如何使用 Controller 類別簡化 API 使用流程。
"""

from src import Controller, ControllerError, ConfigError, LoginError


def example_simple_usage():
    """最簡單的使用方式"""
    print("=" * 60)
    print("範例 1：最簡單的使用方式（推薦）")
    print("=" * 60)
    
    try:
        print("\n[使用 with 語句自動管理連線]")
        
        # 使用 with 語句，自動連線和中斷連線
        with Controller("config.yaml") as ctrl:
            print(f"✅ 自動連線成功！")
            print(f"   Person ID: {ctrl.config.person_id}")
            print(f"   Simulation: {ctrl.config.simulation}")
            print(f"   已連線: {ctrl.is_connected()}")
            
            # 取得狀態
            status = ctrl.get_status()
            print(f"\n[連線狀態]")
            for key, value in status.items():
                print(f"   {key}: {value}")
            
            # 使用 ctrl.sj 進行交易
            print(f"\n[可以使用 ctrl.sj 進行交易]")
            print(f"   Shioaji 實例: {ctrl.sj}")
            # 實際交易操作：
            # contracts = ctrl.sj.Contracts
            # positions = ctrl.sj.list_positions()
            # ...
        
        print("\n✅ 自動中斷連線完成（離開 with 區塊時自動執行）")
        
    except ConfigError as e:
        print(f"\n⚠️ 配置錯誤: {e}")
    except LoginError as e:
        print(f"\n⚠️ 登入錯誤: {e}")
    except ControllerError as e:
        print(f"\n⚠️ 控制器錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")


def example_manual_control():
    """手動管理連線的方式"""
    print("\n\n" + "=" * 60)
    print("範例 2：手動管理連線")
    print("=" * 60)
    
    try:
        print("\n[1] 建立控制器...")
        controller = Controller("config.yaml")
        print(f"✅ 控制器已建立 - {repr(controller)}")
        
        print("\n[2] 檢查連線狀態（連線前）...")
        print(f"   已連線: {controller.is_connected()}")
        
        print("\n[3] 執行連線...")
        controller.connect()
        print("✅ 連線成功！")
        
        print("\n[4] 檢查連線狀態（連線後）...")
        print(f"   已連線: {controller.is_connected()}")
        print(f"   Controller: {repr(controller)}")
        
        print("\n[5] 取得狀態資訊...")
        status = controller.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n[6] 使用 controller.sj 進行交易...")
        print(f"   Shioaji 實例: {controller.sj}")
        # 實際交易操作...
        
        print("\n[7] 執行中斷連線...")
        controller.disconnect()
        print("✅ 中斷連線成功！")
        
        print("\n[8] 檢查連線狀態（中斷連線後）...")
        print(f"   已連線: {controller.is_connected()}")
        
    except ConfigError as e:
        print(f"\n⚠️ 配置錯誤: {e}")
    except LoginError as e:
        print(f"\n⚠️ 登入錯誤: {e}")
    except ControllerError as e:
        print(f"\n⚠️ 控制器錯誤: {e}")
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")


def example_different_init_methods():
    """不同的初始化方式"""
    print("\n\n" + "=" * 60)
    print("範例 3：不同的初始化方式")
    print("=" * 60)
    
    from pathlib import Path
    from src import Config
    
    try:
        # 方法 1：使用字串路徑
        print("\n[方法 1] 使用字串路徑")
        ctrl1 = Controller("config.yaml")
        print(f"✅ {repr(ctrl1)}")
        
        # 方法 2：使用 Path 物件
        print("\n[方法 2] 使用 Path 物件")
        ctrl2 = Controller(Path("config.yaml"))
        print(f"✅ {repr(ctrl2)}")
        
        # 方法 3：使用 Config 物件
        print("\n[方法 3] 使用 Config 物件")
        config = Config("config.yaml")
        ctrl3 = Controller(config)
        print(f"✅ {repr(ctrl3)}")
        
        print("\n✅ 所有初始化方式都可以正常運作！")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


def example_error_handling():
    """錯誤處理範例"""
    print("\n\n" + "=" * 60)
    print("範例 4：錯誤處理")
    print("=" * 60)
    
    # 測試 1：配置檔案不存在
    print("\n[測試 1] 配置檔案不存在")
    try:
        controller = Controller("non_existent.yaml")
    except ConfigError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試 2：重複連線
    print("\n[測試 2] 重複連線")
    try:
        controller = Controller("config.yaml")
        # 如果 shioaji 未安裝，這裡會失敗
        # controller.connect()
        # controller.connect()  # 第二次連線會拋出異常
        print("（跳過實際連線測試，避免真實 API 呼叫）")
    except ControllerError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試 3：未連線時中斷連線
    print("\n[測試 3] 未連線時中斷連線")
    try:
        controller = Controller("config.yaml")
        controller.disconnect()  # 未連線就中斷
    except ControllerError as e:
        print(f"✅ 正確捕獲錯誤: {e}")


def example_status_check():
    """狀態檢查範例"""
    print("\n\n" + "=" * 60)
    print("範例 5：狀態檢查")
    print("=" * 60)
    
    try:
        controller = Controller("config.yaml")
        
        print("\n[連線前]")
        print(f"   is_connected(): {controller.is_connected()}")
        status = controller.get_status()
        print("   get_status():")
        for key, value in status.items():
            print(f"      {key}: {value}")
        
        # 如果要測試連線後的狀態，需要實際連線
        print("\n（連線後的狀態檢查需要實際 API 連線）")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


def main():
    """主程式"""
    print("🚀 永豐 Shioaji API Controller 使用範例")
    print()
    
    # 範例 1：最簡單的使用方式
    example_simple_usage()
    
    # 範例 2：手動管理連線
    example_manual_control()
    
    # 範例 3：不同的初始化方式
    example_different_init_methods()
    
    # 範例 4：錯誤處理
    example_error_handling()
    
    # 範例 5：狀態檢查
    example_status_check()
    
    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)
    
    print("\n💡 提示：")
    print("1. 使用 with 語句是最簡單且推薦的方式")
    print("2. Controller 整合了 Config 和 Login，使用更方便")
    print("3. controller.sj 就是 Shioaji API 實例")
    print("4. 記得處理所有可能的異常")
    print("5. 實際使用時請安裝 shioaji：pip install shioaji")


if __name__ == "__main__":
    main()
