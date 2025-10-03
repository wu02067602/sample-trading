"""
永豐 Shioaji API 配置使用範例

此範例展示如何使用 Config 類別來管理 API 配置。
"""

from src.config import Config, ConfigError


def main():
    """主程式"""
    print("=" * 60)
    print("永豐 Shioaji API 配置管理範例")
    print("=" * 60)
    
    try:
        # 載入配置檔案
        print("\n[1] 載入配置檔案...")
        config = Config("config.yaml")
        print("✅ 配置載入成功！")
        
        # 顯示配置資訊
        print("\n[2] 配置資訊：")
        print(f"   - API Key: {config.api_key[:10]}..." if len(config.api_key) > 10 else config.api_key)
        print(f"   - Person ID: {config.person_id}")
        print(f"   - Simulation Mode: {config.simulation}")
        print(f"   - Contracts Timeout: {config.contracts_timeout}s")
        
        if config.ca_path:
            print(f"   - Certificate Path: {config.ca_path}")
        
        # 轉換為字典
        print("\n[3] 配置字典格式：")
        config_dict = config.to_dict()
        for key, value in config_dict.items():
            if "key" in key.lower() or "passwd" in key.lower():
                # 隱藏敏感資訊
                display_value = f"{str(value)[:8]}..." if value and len(str(value)) > 8 else "****"
            else:
                display_value = value
            print(f"   - {key}: {display_value}")
        
        # 顯示物件表示
        print("\n[4] 配置物件表示：")
        print(f"   {repr(config)}")
        
        print("\n" + "=" * 60)
        print("✅ 所有操作完成！")
        print("=" * 60)
        
    except ConfigError as e:
        print(f"\n❌ 配置錯誤: {e}")
        print("\n請確認：")
        print("1. config.yaml 檔案是否存在")
        print("2. 是否已填寫所有必填欄位")
        print("3. YAML 格式是否正確")
        print("\n提示：可以從 config.yaml.example 複製範本")
        
    except Exception as e:
        print(f"\n❌ 未預期的錯誤: {e}")


if __name__ == "__main__":
    main()
