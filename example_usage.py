"""Shioaji 交易系統使用範例

此範例展示如何使用 ShioajiTrader 類別進行登入與基本操作。
"""

from shioaji_trader import ShioajiTrader


def main():
    """主程式範例"""
    
    # 建立交易器實例
    trader = ShioajiTrader()
    
    # 方法 1：使用 API Key 登入（推薦）
    print("正在登入...")
    success = trader.login(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    # 方法 2：使用帳號密碼登入（替代方案）
    # success = trader.login(
    #     person_id="YOUR_PERSON_ID",
    #     passwd="YOUR_PASSWORD"
    # )
    
    if success:
        print("登入成功！")
        
        # 列出所有帳戶
        accounts = trader.list_accounts()
        print(f"\n可用帳戶數量：{len(accounts)}")
        for idx, account in enumerate(accounts):
            print(f"帳戶 {idx + 1}: {account}")
        
        # 查看預設證券帳戶
        if trader.stock_account:
            print(f"\n預設證券帳戶：{trader.stock_account}")
        
        # 查看預設期貨帳戶
        if trader.futopt_account:
            print(f"預設期貨帳戶：{trader.futopt_account}")
        
        # 如果有多個帳戶，可以設定預設帳戶
        if len(accounts) > 1:
            # trader.set_default_account(accounts[1])
            # print(f"\n已切換預設帳戶至：{accounts[1]}")
            pass
        
        # 使用 trader.sj 進行後續操作
        # 例如：取得合約、下單、查詢部位等
        print(f"\nShioaji API 實例已準備就緒：{trader.sj}")
        
        # 登出
        print("\n正在登出...")
        if trader.logout():
            print("登出成功！")
        
    else:
        print("登入失敗，請檢查憑證是否正確。")


if __name__ == "__main__":
    main()
