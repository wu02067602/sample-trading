"""Shioaji 商品檔查詢範例

此範例展示如何使用 ShioajiTrader 類別查詢商品檔資訊。
"""

from shioaji_trader import ShioajiTrader


def main():
    """商品檔查詢範例"""
    
    # 建立交易器實例並登入
    trader = ShioajiTrader()
    
    print("正在登入...")
    success = trader.login(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    
    if not success:
        print("登入失敗，請檢查憑證是否正確。")
        return
    
    print("登入成功！\n")
    
    # ========== 方法 1：使用 contracts 屬性直接訪問 ==========
    print("=" * 50)
    print("方法 1：使用 contracts 屬性直接訪問")
    print("=" * 50)
    
    # 訪問所有證券商品
    print("\n查詢台積電（2330）：")
    tsmc = trader.contracts.Stocks["2330"]
    print(f"  代碼：{tsmc.code}")
    print(f"  名稱：{tsmc.name}")
    print(f"  交易所：{tsmc.exchange}")
    print(f"  類別：{tsmc.category}")
    
    # 查詢期貨
    print("\n查詢台指期近月（TXFR1）：")
    try:
        txf = trader.contracts.Futures.TXF["TXFR1"]
        print(f"  代碼：{txf.code}")
        print(f"  名稱：{txf.name}")
        print(f"  到期月份：{txf.delivery_month}")
    except Exception as e:
        print(f"  查詢失敗：{e}")
    
    # 查詢指數
    print("\n查詢加權指數：")
    try:
        tse001 = trader.contracts.Indexs.TSE["001"]
        print(f"  代碼：{tse001.code}")
        print(f"  名稱：{tse001.name}")
        print(f"  交易所：{tse001.exchange}")
    except Exception as e:
        print(f"  查詢失敗：{e}")
    
    # ========== 方法 2：使用輔助方法查詢 ==========
    print("\n" + "=" * 50)
    print("方法 2：使用輔助方法查詢")
    print("=" * 50)
    
    # 查詢證券
    print("\n查詢聯發科（2454）：")
    mtk = trader.get_stock("2454")
    if mtk:
        print(f"  {mtk.code}: {mtk.name}")
        print(f"  交易所：{mtk.exchange}")
    
    # 查詢鴻海
    print("\n查詢鴻海（2317）：")
    foxconn = trader.get_stock("2317")
    if foxconn:
        print(f"  {foxconn.code}: {foxconn.name}")
    
    # ========== 方法 3：搜尋商品 ==========
    print("\n" + "=" * 50)
    print("方法 3：搜尋商品")
    print("=" * 50)
    
    # 搜尋包含「台積」的股票
    print("\n搜尋名稱包含「台積」的股票：")
    results = trader.search_contracts("台積")
    for contract in results[:5]:  # 顯示前 5 筆
        print(f"  {contract.code}: {contract.name}")
    
    # 搜尋包含「聯」的股票
    print("\n搜尋名稱包含「聯」的股票（顯示前 5 筆）：")
    results = trader.search_contracts("聯")
    for contract in results[:5]:
        print(f"  {contract.code}: {contract.name}")
    
    # 搜尋代碼包含「23」的股票
    print("\n搜尋代碼包含「23」的股票（顯示前 5 筆）：")
    results = trader.search_contracts("23")
    for contract in results[:5]:
        print(f"  {contract.code}: {contract.name}")
    
    # ========== 使用商品檔進行進階操作 ==========
    print("\n" + "=" * 50)
    print("進階使用範例")
    print("=" * 50)
    
    print("\n取得多支股票的資訊：")
    stock_codes = ["2330", "2454", "2317", "2412", "2882"]
    for code in stock_codes:
        stock = trader.get_stock(code)
        if stock:
            print(f"  {stock.code}: {stock.name}")
    
    # 登出
    print("\n正在登出...")
    if trader.logout():
        print("登出成功！")


if __name__ == "__main__":
    main()
