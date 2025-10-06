"""
Shioaji 帳戶資訊查詢使用範例

此檔案展示如何使用 ShioajiConnector 查詢帳戶餘額和持股資訊。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
from shioaji_connector import ShioajiConnector

# 設置日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_account_balance():
    """
    範例 1: 查詢帳戶餘額
    
    展示如何查詢帳戶的餘額資訊。
    """
    print("\n" + "="*60)
    print("範例 1: 查詢帳戶餘額")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢帳戶餘額
        balance = connector.get_account_balance()
        
        if balance:
            print("\n帳戶餘額資訊:")
            print(f"  帳戶總額: {balance.account_balance:,.0f} 元")
            print(f"  可用餘額: {balance.available_balance:,.0f} 元")
            print(f"  T日資金: {balance.T_money:,.0f} 元")
            print(f"  T+1日資金: {balance.T1_money:,.0f} 元")
            print(f"  T+2日資金: {balance.T2_money:,.0f} 元")
        else:
            print("❌ 查詢帳戶餘額失敗")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_2_account_balance_summary():
    """
    範例 2: 查詢帳戶餘額摘要
    
    展示如何以字典格式查詢帳戶餘額。
    """
    print("\n" + "="*60)
    print("範例 2: 查詢帳戶餘額摘要")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢餘額摘要
        summary = connector.get_account_balance_summary()
        
        print("\n帳戶餘額摘要:")
        print(f"  帳戶總額: {summary['account_balance']:,.0f} 元")
        print(f"  可用餘額: {summary['available_balance']:,.0f} 元")
        print(f"  T日資金: {summary['T_money']:,.0f} 元")
        print(f"  T+1日資金: {summary['T1_money']:,.0f} 元")
        print(f"  T+2日資金: {summary['T2_money']:,.0f} 元")
        print(f"  查詢時間: {summary['query_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_3_list_positions():
    """
    範例 3: 查詢持股明細
    
    展示如何查詢目前的持股資訊。
    """
    print("\n" + "="*60)
    print("範例 3: 查詢持股明細")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢持股
        positions = connector.list_positions()
        
        print(f"\n目前持股: 共 {len(positions)} 檔")
        
        for i, pos in enumerate(positions, 1):
            print(f"\n持股 {i}:")
            print(f"  商品代碼: {pos.code}")
            print(f"  持有數量: {pos.quantity:,} 股")
            print(f"  成本價格: {pos.price:.2f} 元")
            print(f"  現在價格: {pos.last_price:.2f} 元")
            print(f"  損益: {pos.pnl:,.0f} 元")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_4_list_positions_with_detail():
    """
    範例 4: 查詢持股明細（詳細版）
    
    展示如何查詢詳細的持股資訊（字典格式）。
    """
    print("\n" + "="*60)
    print("範例 4: 查詢持股明細（詳細版）")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢詳細持股
        positions = connector.list_positions(with_detail=True)
        
        print(f"\n持股詳細資訊: 共 {len(positions)} 檔")
        
        for i, pos in enumerate(positions, 1):
            print(f"\n持股 {i}:")
            print(f"  商品代碼: {pos['code']}")
            print(f"  持有數量: {pos['quantity']:,} 股")
            print(f"  昨日數量: {pos['yd_quantity']:,} 股")
            print(f"  成本價格: {pos['price']:.2f} 元")
            print(f"  現在價格: {pos['last_price']:.2f} 元")
            print(f"  損益金額: {pos['pnl']:,.0f} 元")
            print(f"  方向: {pos['direction']}")
            print(f"  狀態: {pos['cond']}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_5_positions_summary():
    """
    範例 5: 查詢持股摘要統計
    
    展示如何取得持股的統計資訊。
    """
    print("\n" + "="*60)
    print("範例 5: 查詢持股摘要統計")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢持股摘要
        summary = connector.get_positions_summary()
        
        print("\n持股摘要統計:")
        print(f"  持股檔數: {summary['total_stocks']} 檔")
        print(f"  總持有數量: {summary['total_quantity']:,} 股")
        print(f"  總成本: {summary['total_cost']:,.0f} 元")
        print(f"  總市值: {summary['total_value']:,.0f} 元")
        print(f"  總損益: {summary['total_pnl']:,.0f} 元")
        print(f"  報酬率: {summary['return_rate']:.2f}%")
        print(f"  查詢時間: {summary['query_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_6_account_overview():
    """
    範例 6: 帳戶總覽
    
    展示如何一次查詢帳戶餘額和持股資訊。
    """
    print("\n" + "="*60)
    print("範例 6: 帳戶總覽")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢帳戶餘額
        balance = connector.get_account_balance_summary()
        
        print("\n=== 帳戶資訊 ===")
        print(f"可用餘額: {balance['available_balance']:,.0f} 元")
        print(f"帳戶總額: {balance['account_balance']:,.0f} 元")
        
        # 查詢持股摘要
        positions_summary = connector.get_positions_summary()
        
        print("\n=== 持股資訊 ===")
        print(f"持股檔數: {positions_summary['total_stocks']} 檔")
        print(f"總市值: {positions_summary['total_value']:,.0f} 元")
        print(f"總損益: {positions_summary['total_pnl']:,.0f} 元")
        print(f"報酬率: {positions_summary['return_rate']:.2f}%")
        
        # 計算總資產
        total_assets = balance['available_balance'] + positions_summary['total_value']
        print("\n=== 總資產 ===")
        print(f"現金: {balance['available_balance']:,.0f} 元")
        print(f"股票: {positions_summary['total_value']:,.0f} 元")
        print(f"總資產: {total_assets:,.0f} 元")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_7_position_analysis():
    """
    範例 7: 持股分析
    
    展示如何分析持股的獲利情況。
    """
    print("\n" + "="*60)
    print("範例 7: 持股分析")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢詳細持股
        positions = connector.list_positions(with_detail=True)
        
        if not positions:
            print("\n目前沒有持股")
            connector.logout()
            return
        
        print(f"\n持股分析: 共 {len(positions)} 檔")
        
        # 分類持股
        profit_stocks = []  # 獲利股票
        loss_stocks = []    # 虧損股票
        
        for pos in positions:
            if pos['pnl'] > 0:
                profit_stocks.append(pos)
            elif pos['pnl'] < 0:
                loss_stocks.append(pos)
        
        # 獲利股票分析
        print(f"\n✅ 獲利股票: {len(profit_stocks)} 檔")
        for pos in sorted(profit_stocks, key=lambda x: x['pnl'], reverse=True):
            return_rate = (pos['last_price'] - pos['price']) / pos['price'] * 100
            print(f"  {pos['code']}: +{pos['pnl']:,.0f} 元 ({return_rate:+.2f}%)")
        
        # 虧損股票分析
        print(f"\n❌ 虧損股票: {len(loss_stocks)} 檔")
        for pos in sorted(loss_stocks, key=lambda x: x['pnl']):
            return_rate = (pos['last_price'] - pos['price']) / pos['price'] * 100
            print(f"  {pos['code']}: {pos['pnl']:,.0f} 元 ({return_rate:+.2f}%)")
        
        # 總體分析
        summary = connector.get_positions_summary()
        print(f"\n📊 總體績效:")
        print(f"  總損益: {summary['total_pnl']:,.0f} 元")
        print(f"  報酬率: {summary['return_rate']:+.2f}%")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


def example_8_check_buying_power():
    """
    範例 8: 檢查購買力
    
    展示如何根據帳戶餘額計算可以買多少股。
    """
    print("\n" + "="*60)
    print("範例 8: 檢查購買力")
    print("="*60)
    
    try:
        connector = ShioajiConnector(simulation=True)
        connector.login(
            person_id="YOUR_PERSON_ID",
            passwd="YOUR_PASSWORD"
        )
        
        # 查詢可用餘額
        balance = connector.get_account_balance_summary()
        available = balance['available_balance']
        
        print(f"\n可用餘額: {available:,.0f} 元")
        
        # 假設要買台積電（2330）
        stock_price = 600.0  # 假設股價
        
        # 計算可買股數（考慮手續費約 0.1425%）
        fee_rate = 0.001425
        max_buy_value = available / (1 + fee_rate)
        max_shares = int(max_buy_value / stock_price / 1000) * 1000  # 整股，1000的倍數
        
        print(f"\n假設股價: {stock_price:.2f} 元")
        print(f"最多可買: {max_shares:,} 股 ({max_shares // 1000} 張)")
        print(f"需要金額: {max_shares * stock_price:,.0f} 元")
        print(f"預估手續費: {max_shares * stock_price * fee_rate:,.0f} 元")
        print(f"剩餘金額: {available - max_shares * stock_price * (1 + fee_rate):,.0f} 元")
        
        connector.logout()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Shioaji 帳戶資訊查詢使用範例集")
    print("="*60)
    print("\n⚠️  重要提醒：")
    print("1. 需要先登入才能查詢帳戶資訊")
    print("2. 建議先在模擬環境測試 (simulation=True)")
    print("3. 請將 YOUR_PERSON_ID、YOUR_PASSWORD 替換為實際值")
    print("4. 帳戶餘額和持股資訊為即時資料")
    
    # 執行範例
    try:
        example_1_account_balance()
        example_2_account_balance_summary()
        example_3_list_positions()
        example_4_list_positions_with_detail()
        example_5_positions_summary()
        example_6_account_overview()
        example_7_position_analysis()
        example_8_check_buying_power()
        
    except ImportError as e:
        print(f"\n❌ 匯入錯誤: {e}")
        print("請先安裝依賴套件: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("範例執行完畢")
    print("="*60)
    print("\n💡 帳戶資訊查詢功能總結：")
    print("- get_account_balance() - 查詢帳戶餘額")
    print("- get_account_balance_summary() - 查詢餘額摘要")
    print("- list_positions() - 查詢持股明細")
    print("- list_positions(with_detail=True) - 查詢詳細持股")
    print("- get_positions_summary() - 查詢持股摘要統計")
