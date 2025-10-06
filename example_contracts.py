"""
Shioaji 商品檔使用範例

此檔案展示如何使用 ShioajiClient 取得和查詢商品檔。
"""

from shioaji_client import ShioajiClient, LoginConfig
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_get_contracts():
    """取得商品檔範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        # 登入（會自動載入商品檔）
        client.login(config)
        
        # 取得商品檔
        contracts = client.get_contracts()
        
        print("=== 商品檔資訊 ===")
        print(f"股票商品: {contracts.Stocks}")
        print(f"期貨商品: {contracts.Futures}")
        print(f"選擇權商品: {contracts.Options}")
        print(f"指數商品: {contracts.Indexs}")


def example_search_contracts():
    """搜尋商品檔範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 搜尋商品檔 ===")
        
        # 搜尋台積電
        results = client.search_contracts("2330")
        print(f"\n搜尋 '2330' 找到 {len(results)} 個結果:")
        for contract in results:
            print(f"  {contract.code} - {contract.name}")
        
        # 搜尋包含「台」的商品
        results = client.search_contracts("台")
        print(f"\n搜尋 '台' 找到 {len(results)} 個結果（顯示前 5 個）:")
        for contract in results[:5]:
            print(f"  {contract.code} - {contract.name}")


def example_get_stock():
    """取得特定股票範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 取得特定股票 ===")
        
        # 取得台積電
        tsmc = client.get_stock("2330")
        print(f"\n股票代碼: {tsmc.code}")
        print(f"股票名稱: {tsmc.name}")
        print(f"交易所: {tsmc.exchange}")
        print(f"參考價: {tsmc.reference}")
        print(f"漲停價: {tsmc.limit_up}")
        print(f"跌停價: {tsmc.limit_down}")
        print(f"更新時間: {tsmc.update_date}")


def example_get_index():
    """取得指數範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 取得指數 ===")
        
        contracts = client.get_contracts()
        
        # 取得加權指數
        tse001 = contracts.Indexs.TSE.TSE001
        print(f"\n指數代碼: {tse001.code}")
        print(f"指數名稱: {tse001.name}")
        print(f"符號: {tse001.symbol}")
        print(f"交易所: {tse001.exchange}")


def example_get_futures():
    """取得期貨範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 取得期貨 ===")
        
        contracts = client.get_contracts()
        
        # 取得台指期近月合約
        # 注意: TXFR1 為近月合約，實際代碼會隨月份改變
        print(f"\n台指期合約列表:")
        print(contracts.Futures.TXF)


def example_direct_access():
    """直接存取 contracts 屬性範例"""
    config = LoginConfig(
        person_id="YOUR_PERSON_ID",
        passwd="YOUR_PASSWORD",
        simulation=True
    )
    
    with ShioajiClient() as client:
        client.login(config)
        
        print("\n=== 直接存取 contracts 屬性 ===")
        
        # 方法 1: 透過 get_contracts() 方法
        contracts1 = client.get_contracts()
        tsmc1 = contracts1.Stocks["2330"]
        print(f"方法 1: {tsmc1.code} - {tsmc1.name}")
        
        # 方法 2: 直接存取 contracts 屬性
        tsmc2 = client.contracts.Stocks["2330"]
        print(f"方法 2: {tsmc2.code} - {tsmc2.name}")
        
        # 兩者結果相同
        print(f"\n兩個方法取得的物件相同: {tsmc1 == tsmc2}")


if __name__ == "__main__":
    print("=== Shioaji 商品檔使用範例 ===\n")
    
    print("請先修改範例程式碼中的認證資訊後執行")
    print("\n可用的範例:")
    print("1. example_get_contracts() - 取得商品檔")
    print("2. example_search_contracts() - 搜尋商品檔")
    print("3. example_get_stock() - 取得特定股票")
    print("4. example_get_index() - 取得指數")
    print("5. example_get_futures() - 取得期貨")
    print("6. example_direct_access() - 直接存取 contracts 屬性")
    
    # 取消註解以執行範例
    # example_get_contracts()
    # example_search_contracts()
    # example_get_stock()
    # example_get_index()
    # example_get_futures()
    # example_direct_access()
