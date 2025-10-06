"""Shioaji 帳戶餘額查詢範例

此範例展示如何使用 ShioajiTrader 查詢帳戶餘額、交割資訊與帳戶摘要。
"""

from shioaji_trader import ShioajiTrader


def demo_account_balance():
    """示範帳戶餘額查詢功能
    
    展示如何查詢帳戶餘額、交割資訊與完整帳戶摘要。
    """
    print("="*60)
    print("帳戶餘額查詢功能示範")
    print("="*60 + "\n")
    
    # 初始化
    trader = ShioajiTrader()
    
    # 登入
    print("正在登入...")
    success = trader.login(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    if not success:
        print("登入失敗！")
        return
    
    print("✓ 登入成功\n")
    
    # ========== 示範 1：查詢帳戶餘額 ==========
    print("=" * 60)
    print("示範 1: 查詢帳戶餘額")
    print("=" * 60)
    
    print("\n查詢帳戶銀行餘額...")
    balance = trader.get_account_balance()
    
    if balance:
        print("\n帳戶餘額資訊：")
        print("-" * 60)
        print(balance)
    else:
        print("無法取得帳戶餘額資訊")
    
    # ========== 示範 2：查詢交割資訊 ==========
    print("\n" + "=" * 60)
    print("示範 2: 查詢交割資訊")
    print("=" * 60)
    
    print("\n查詢交割資訊...")
    settlements = trader.get_settlements()
    
    if settlements:
        print("\n交割資訊：")
        print("-" * 60)
        
        # 顯示 T日、T+1日、T+2日的交割金額
        if isinstance(settlements, dict):
            for key, value in settlements.items():
                print(f"{key}: {value:,}")
        else:
            print(settlements)
    else:
        print("無法取得交割資訊")
    
    # ========== 示範 3：查詢帳戶額度 ==========
    print("\n" + "=" * 60)
    print("示範 3: 查詢帳戶額度")
    print("=" * 60)
    
    print("\n查詢帳戶額度...")
    margin = trader.get_account_margin()
    
    if margin:
        print("\n帳戶額度資訊：")
        print("-" * 60)
        print(margin)
    else:
        print("無法取得帳戶額度資訊")
    
    # ========== 示範 4：查詢持倉部位 ==========
    print("\n" + "=" * 60)
    print("示範 4: 查詢持倉部位")
    print("=" * 60)
    
    print("\n查詢持倉部位...")
    positions = trader.list_positions()
    
    if positions:
        print(f"\n找到 {len(positions)} 個持倉部位\n")
        print("持倉明細：")
        print("-" * 60)
        
        total_cost = 0
        total_market_value = 0
        total_pnl = 0
        
        for i, pos in enumerate(positions, 1):
            print(f"\n{i}. {pos.code}")
            print(f"   方向: {pos.direction if hasattr(pos, 'direction') else 'N/A'}")
            print(f"   數量: {pos.quantity} 股")
            print(f"   成本價: {pos.price}")
            print(f"   現價: {pos.last_price if hasattr(pos, 'last_price') else 'N/A'}")
            
            if hasattr(pos, 'price') and hasattr(pos, 'quantity'):
                cost = pos.price * pos.quantity
                total_cost += cost
                print(f"   成本: {cost:,.0f}")
            
            if hasattr(pos, 'last_price') and hasattr(pos, 'quantity'):
                market_value = pos.last_price * pos.quantity
                total_market_value += market_value
                print(f"   市值: {market_value:,.0f}")
            
            if hasattr(pos, 'pnl'):
                total_pnl += pos.pnl
                print(f"   損益: {pos.pnl:,.0f}")
        
        print("\n" + "=" * 60)
        print(f"總成本: {total_cost:,.0f}")
        print(f"總市值: {total_market_value:,.0f}")
        print(f"總損益: {total_pnl:,.0f}")
        if total_cost > 0:
            pnl_pct = (total_pnl / total_cost) * 100
            print(f"報酬率: {pnl_pct:+.2f}%")
    else:
        print("目前沒有持倉")
    
    # ========== 示範 5：查詢損益 ==========
    print("\n" + "=" * 60)
    print("示範 5: 查詢當日損益")
    print("=" * 60)
    
    print("\n查詢當日損益...")
    pnl = trader.list_profit_loss()
    
    if pnl:
        print("\n損益資訊：")
        print("-" * 60)
        print(pnl)
    else:
        print("無法取得損益資訊")
    
    # ========== 示範 6：取得完整帳戶摘要 ==========
    print("\n" + "=" * 60)
    print("示範 6: 取得完整帳戶摘要")
    print("=" * 60)
    
    print("\n取得帳戶摘要資訊...")
    summary = trader.get_account_summary()
    
    if summary:
        print("\n帳戶摘要：")
        print("=" * 60)
        
        print(f"\n帳戶: {summary.get('account', 'N/A')}")
        
        print(f"\n持倉數量: {summary.get('position_count', 0)}")
        print(f"總市值: {summary.get('total_value', 0):,.0f}")
        
        balance = summary.get('balance', {})
        if balance:
            print(f"\n帳戶餘額:")
            print(balance)
        
        settlements = summary.get('settlements', {})
        if settlements:
            print(f"\n交割資訊:")
            if isinstance(settlements, dict):
                for key, value in settlements.items():
                    print(f"  {key}: {value:,}")
            else:
                print(f"  {settlements}")
        
        pnl = summary.get('profit_loss', {})
        if pnl:
            print(f"\n損益資訊:")
            print(pnl)
    else:
        print("無法取得帳戶摘要")
    
    # 登出
    print("\n" + "=" * 60)
    print("登出")
    print("=" * 60)
    trader.logout()
    print("✓ 登出成功")
    
    print("\n" + "=" * 60)
    print("示範程式執行完畢")
    print("=" * 60)


def simple_balance_check():
    """簡化版帳戶餘額查詢
    
    展示如何快速查詢帳戶餘額。
    """
    print("="*60)
    print("簡化版帳戶餘額查詢")
    print("="*60 + "\n")
    
    # 初始化並登入
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    # 查詢餘額
    print("查詢帳戶資訊...\n")
    
    balance = trader.get_account_balance()
    print(f"帳戶餘額: {balance}")
    
    settlements = trader.get_settlements()
    print(f"交割資訊: {settlements}")
    
    positions = trader.list_positions()
    print(f"持倉數量: {len(positions) if positions else 0}")
    
    # 登出
    trader.logout()
    print("\n✓ 完成")


def account_health_check():
    """帳戶健康檢查
    
    檢查帳戶狀態是否健康，包含餘額、持倉、風險等。
    """
    print("="*60)
    print("帳戶健康檢查")
    print("="*60 + "\n")
    
    trader = ShioajiTrader()
    trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
    
    print("執行帳戶健康檢查...\n")
    
    # 取得完整摘要
    summary = trader.get_account_summary()
    
    if not summary:
        print("❌ 無法取得帳戶資訊")
        trader.logout()
        return
    
    print("="*60)
    print("健康檢查報告")
    print("="*60)
    
    # 1. 持倉檢查
    print("\n1. 持倉狀態")
    print("-" * 60)
    position_count = summary.get('position_count', 0)
    total_value = summary.get('total_value', 0)
    
    print(f"持倉數量: {position_count}")
    print(f"總市值: {total_value:,.0f}")
    
    if position_count == 0:
        print("狀態: ⚠️ 無持倉")
    elif position_count > 10:
        print("狀態: ⚠️ 持倉過於分散")
    else:
        print("狀態: ✓ 正常")
    
    # 2. 餘額檢查
    print("\n2. 餘額狀態")
    print("-" * 60)
    balance = summary.get('balance', {})
    if balance:
        print(f"餘額: {balance}")
        print("狀態: ✓ 正常")
    else:
        print("狀態: ⚠️ 無法取得餘額資訊")
    
    # 3. 交割檢查
    print("\n3. 交割狀態")
    print("-" * 60)
    settlements = summary.get('settlements', {})
    if settlements:
        if isinstance(settlements, dict):
            for key, value in settlements.items():
                print(f"{key}: {value:,}")
        else:
            print(settlements)
        print("狀態: ✓ 正常")
    else:
        print("狀態: ⚠️ 無法取得交割資訊")
    
    # 4. 風險評估
    print("\n4. 風險評估")
    print("-" * 60)
    positions = summary.get('positions', [])
    
    if positions:
        # 計算最大持倉比例
        if total_value > 0:
            max_position_ratio = 0
            for pos in positions:
                if hasattr(pos, 'last_price') and hasattr(pos, 'quantity'):
                    position_value = pos.last_price * pos.quantity
                    ratio = (position_value / total_value) * 100
                    if ratio > max_position_ratio:
                        max_position_ratio = ratio
            
            print(f"最大持倉比例: {max_position_ratio:.2f}%")
            
            if max_position_ratio > 50:
                print("風險: ⚠️ 高（單一持倉過大）")
            elif max_position_ratio > 30:
                print("風險: ⚠️ 中等")
            else:
                print("風險: ✓ 正常")
    
    print("\n" + "="*60)
    print("健康檢查完成")
    print("="*60)
    
    trader.logout()
    print("\n✓ 完成")


if __name__ == "__main__":
    # 執行完整示範
    demo_account_balance()
    
    # 如果要執行其他範例，請取消下面的註解
    # print("\n" + "="*80 + "\n")
    # simple_balance_check()
    
    # print("\n" + "="*80 + "\n")
    # account_health_check()
