"""
量化交易系統 - 商品檔取得模組

此模組負責取得可交易的金融商品資訊，提供商品代碼、規格等基本資料。
"""

import shioaji as sj
from typing import Optional, Dict, List


class InstrumentRetrieval:
    """
    負責取得可交易的金融商品資訊，提供商品代碼、規格等基本資料。
    
    此類別封裝了永豐金證券 Shioaji API 的商品檔查詢功能，支援查詢
    股票、期貨、選擇權等各類金融商品的合約資訊。
    
    Attributes:
        api (sj.Shioaji): Shioaji API 實例，用於查詢商品資訊
        contracts (Optional[Dict]): 所有商品合約資訊的字典
    
    Examples:
        >>> from authentication import Authentication
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> retrieval = InstrumentRetrieval(auth.api)
        >>> retrieval.fetch_all_contracts()
        >>> stock = retrieval.get_stock_contract("2330")
        >>> print(stock.name)  # 台積電
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化 InstrumentRetrieval 實例。
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 實例
        
        Raises:
            ValueError: 當 api 參數為 None 時
        """
        if api is None:
            raise ValueError("api 參數不可為 None")
        
        self.api: sj.Shioaji = api
        self.contracts: Optional[Dict] = None
    
    def fetch_all_contracts(self) -> Dict:
        """
        取得所有商品合約資訊。
        
        此方法會從 API 取得所有可交易商品的合約資訊，包括股票、期貨、
        選擇權等，並將結果儲存在 self.contracts 屬性中供後續使用。
        
        Returns:
            Dict: 包含所有商品合約資訊的字典
                - 'Stocks': 股票合約列表
                - 'Futures': 期貨合約列表
                - 'Options': 選擇權合約列表
        
        Examples:
            >>> retrieval = InstrumentRetrieval(api)
            >>> contracts = retrieval.fetch_all_contracts()
            >>> print(len(contracts['Stocks']))  # 顯示股票數量
        
        Raises:
            RuntimeError: 當 API 尚未登入或取得合約失敗時
        """
        if not hasattr(self.api, 'Contracts'):
            raise RuntimeError("API 尚未登入或 Contracts 屬性不存在")
        
        try:
            # 取得所有合約資訊
            self.contracts = {
                'Stocks': self.api.Contracts.Stocks,
                'Futures': self.api.Contracts.Futures,
                'Options': self.api.Contracts.Options
            }
            return self.contracts
        except AttributeError as e:
            raise RuntimeError(f"取得合約資訊失敗：{e}") from e
    
    def get_stock_contract(self, symbol: str) -> Optional[sj.contracts.Contract]:
        """
        取得指定股票的合約資訊。
        
        Args:
            symbol (str): 股票代碼（例如：'2330' 代表台積電）
        
        Returns:
            Optional[sj.contracts.Contract]: 股票合約物件，找不到時返回 None
        
        Examples:
            >>> retrieval = InstrumentRetrieval(api)
            >>> retrieval.fetch_all_contracts()
            >>> tsmc = retrieval.get_stock_contract("2330")
            >>> if tsmc:
            ...     print(f"{tsmc.symbol}: {tsmc.name}")
        
        Raises:
            ValueError: 當 symbol 為空字串時
            RuntimeError: 當尚未執行 fetch_all_contracts() 時
        """
        if not symbol:
            raise ValueError("symbol 不可為空")
        
        if self.contracts is None:
            raise RuntimeError("請先執行 fetch_all_contracts() 取得商品資訊")
        
        try:
            # 從股票合約中搜尋指定代碼
            for contract in self.contracts.get('Stocks', []):
                if contract.code == symbol:
                    return contract
            return None
        except (AttributeError, KeyError) as e:
            raise RuntimeError(f"查詢股票合約失敗：{e}") from e
    
    def get_futures_contract(
        self,
        symbol: str,
        contract_date: Optional[str] = None
    ) -> Optional[sj.contracts.Contract]:
        """
        取得指定期貨的合約資訊。
        
        Args:
            symbol (str): 期貨代碼（例如：'TX' 代表台指期）
            contract_date (Optional[str]): 合約到期日（格式：'YYYYMM'），
                若為 None 則返回最近月份合約
        
        Returns:
            Optional[sj.contracts.Contract]: 期貨合約物件，找不到時返回 None
        
        Examples:
            >>> retrieval = InstrumentRetrieval(api)
            >>> retrieval.fetch_all_contracts()
            >>> tx = retrieval.get_futures_contract("TX", "202501")
            >>> if tx:
            ...     print(f"{tx.symbol}: {tx.name}")
        
        Raises:
            ValueError: 當 symbol 為空字串時
            RuntimeError: 當尚未執行 fetch_all_contracts() 時
        """
        if not symbol:
            raise ValueError("symbol 不可為空")
        
        if self.contracts is None:
            raise RuntimeError("請先執行 fetch_all_contracts() 取得商品資訊")
        
        try:
            futures = self.contracts.get('Futures', [])
            
            if contract_date:
                # 查詢指定到期日的合約
                for contract in futures:
                    if contract.code == symbol and contract.delivery_date == contract_date:
                        return contract
            else:
                # 返回最近月份的合約
                matching_contracts = [c for c in futures if c.code == symbol]
                if matching_contracts:
                    # 按到期日排序，返回最近的
                    return sorted(matching_contracts, key=lambda x: x.delivery_date)[0]
            
            return None
        except (AttributeError, KeyError) as e:
            raise RuntimeError(f"查詢期貨合約失敗：{e}") from e
    
    def search_contracts(self, keyword: str) -> List[sj.contracts.Contract]:
        """
        搜尋包含指定關鍵字的商品合約。
        
        此方法會在股票、期貨、選擇權等所有商品中搜尋名稱或代碼
        包含指定關鍵字的合約。
        
        Args:
            keyword (str): 搜尋關鍵字（可以是代碼或名稱的一部分）
        
        Returns:
            List[sj.contracts.Contract]: 符合條件的合約列表
        
        Examples:
            >>> retrieval = InstrumentRetrieval(api)
            >>> retrieval.fetch_all_contracts()
            >>> results = retrieval.search_contracts("台積")
            >>> for contract in results:
            ...     print(f"{contract.code}: {contract.name}")
        
        Raises:
            ValueError: 當 keyword 為空字串時
            RuntimeError: 當尚未執行 fetch_all_contracts() 時
        """
        if not keyword:
            raise ValueError("keyword 不可為空")
        
        if self.contracts is None:
            raise RuntimeError("請先執行 fetch_all_contracts() 取得商品資訊")
        
        results = []
        keyword_lower = keyword.lower()
        
        try:
            # 在所有商品類型中搜尋
            for contract_type in ['Stocks', 'Futures', 'Options']:
                contracts_list = self.contracts.get(contract_type, [])
                for contract in contracts_list:
                    # 檢查代碼或名稱是否包含關鍵字
                    if (keyword_lower in contract.code.lower() or
                        keyword_lower in contract.name.lower()):
                        results.append(contract)
            
            return results
        except (AttributeError, KeyError) as e:
            raise RuntimeError(f"搜尋合約失敗：{e}") from e
    
    def get_contract_count(self) -> Dict[str, int]:
        """
        取得各類商品的合約數量統計。
        
        Returns:
            Dict[str, int]: 各類商品的數量字典
                - 'Stocks': 股票數量
                - 'Futures': 期貨數量
                - 'Options': 選擇權數量
                - 'Total': 總數量
        
        Examples:
            >>> retrieval = InstrumentRetrieval(api)
            >>> retrieval.fetch_all_contracts()
            >>> count = retrieval.get_contract_count()
            >>> print(f"股票數量：{count['Stocks']}")
        
        Raises:
            RuntimeError: 當尚未執行 fetch_all_contracts() 時
        """
        if self.contracts is None:
            raise RuntimeError("請先執行 fetch_all_contracts() 取得商品資訊")
        
        try:
            stock_count = len(self.contracts.get('Stocks', []))
            futures_count = len(self.contracts.get('Futures', []))
            options_count = len(self.contracts.get('Options', []))
            
            return {
                'Stocks': stock_count,
                'Futures': futures_count,
                'Options': options_count,
                'Total': stock_count + futures_count + options_count
            }
        except (AttributeError, TypeError) as e:
            raise RuntimeError(f"統計合約數量失敗：{e}") from e
