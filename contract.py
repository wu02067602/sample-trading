"""商品檔模組

此模組負責處理永豐 Shioaji API 的商品檔獲取與管理功能。
"""

import shioaji as sj
from typing import Optional, Dict, Any


class ContractManager:
    """負責獲取可交易的商品資訊
    
    此類別封裝了永豐 Shioaji API 的商品檔管理功能，
    提供證券、期貨、選擇權和指數等商品資訊的存取。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化商品檔管理器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self.contracts: Optional[Any] = None
    
    def fetch_contracts(self, contract_download: bool = True, timeout: int = 10000) -> Any:
        """獲取商品檔資料
        
        從永豐 API 下載或更新商品檔資訊，包含證券、期貨、選擇權和指數等商品。
        
        Args:
            contract_download (bool): 是否下載商品檔，預設為 True
            timeout (int): 下載逾時時間（毫秒），預設為 10000 毫秒（10 秒）
        
        Returns:
            Any: Shioaji Contracts 物件，包含所有商品資訊
        
        Examples:
            >>> from login import Login
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> contract_manager = ContractManager(api)
            >>> contracts = contract_manager.fetch_contracts()
            >>> print(f"商品檔已下載: {contracts}")
        
        Raises:
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            TimeoutError: 當下載商品檔逾時時
        """
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            # 獲取商品檔
            self._api.fetch_contracts(contract_download=contract_download)
            
            # 等待商品檔下載完成（透過存取 Contracts 確認）
            self.contracts = self._api.Contracts
            
            return self.contracts
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except TimeoutError as e:
            raise TimeoutError(f"下載商品檔逾時（{timeout} 毫秒）: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_stock(self, stock_code: str) -> Optional[Any]:
        """取得特定證券商品
        
        根據股票代碼取得對應的證券商品資訊。
        
        Args:
            stock_code (str): 股票代碼，例如 "2890"、"2330"
        
        Returns:
            Optional[Any]: 商品物件，如果找不到則返回 None
        
        Examples:
            >>> contract_manager.fetch_contracts()
            >>> stock = contract_manager.get_stock("2890")
            >>> print(f"股票名稱: {stock.name}")
        
        Raises:
            ValueError: 當 stock_code 為空字串時
            RuntimeError: 當尚未獲取商品檔時
        """
        if not stock_code:
            raise ValueError("股票代碼不可為空")
        
        if self.contracts is None:
            raise RuntimeError("尚未獲取商品檔，請先呼叫 fetch_contracts()")
        
        try:
            return self.contracts.Stocks[stock_code]
        except KeyError:
            return None
    
    def get_future(self, future_code: str) -> Optional[Any]:
        """取得特定期貨商品
        
        根據期貨代碼取得對應的期貨商品資訊。
        
        Args:
            future_code (str): 期貨代碼，例如 "TXFR1"（台指期近月）
        
        Returns:
            Optional[Any]: 商品物件，如果找不到則返回 None
        
        Examples:
            >>> contract_manager.fetch_contracts()
            >>> future = contract_manager.get_future("TXFR1")
            >>> print(f"期貨名稱: {future.name}")
        
        Raises:
            ValueError: 當 future_code 為空字串時
            RuntimeError: 當尚未獲取商品檔時
        """
        if not future_code:
            raise ValueError("期貨代碼不可為空")
        
        if self.contracts is None:
            raise RuntimeError("尚未獲取商品檔，請先呼叫 fetch_contracts()")
        
        try:
            # 期貨可能需要透過不同的交易所代碼存取
            for exchange in self.contracts.Futures:
                if hasattr(exchange, future_code):
                    return getattr(exchange, future_code)
            return None
        except (KeyError, AttributeError):
            return None
    
    def get_all_stocks(self) -> Dict[str, Any]:
        """取得所有證券商品
        
        Returns:
            Dict[str, Any]: 所有證券商品的字典，鍵為股票代碼
        
        Examples:
            >>> contract_manager.fetch_contracts()
            >>> all_stocks = contract_manager.get_all_stocks()
            >>> print(f"總共有 {len(all_stocks)} 支股票")
        
        Raises:
            RuntimeError: 當尚未獲取商品檔時
        """
        if self.contracts is None:
            raise RuntimeError("尚未獲取商品檔，請先呼叫 fetch_contracts()")
        
        return dict(self.contracts.Stocks)
    
    def is_contracts_ready(self) -> bool:
        """檢查商品檔是否已就緒
        
        Returns:
            bool: 如果商品檔已下載則返回 True，否則返回 False
        
        Examples:
            >>> contract_manager = ContractManager(api)
            >>> contract_manager.is_contracts_ready()
            False
            >>> contract_manager.fetch_contracts()
            >>> contract_manager.is_contracts_ready()
            True
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self.contracts is not None
