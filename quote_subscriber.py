"""訂閱報價模組

此模組負責處理永豐 Shioaji API 的報價訂閱功能。
"""

import shioaji as sj
from typing import Optional, List, Callable, Any, Dict
from datetime import datetime


class QuoteSubscriber:
    """負責訂閱即時市場報價
    
    此類別封裝了永豐 Shioaji API 的報價訂閱功能，
    支援股票、期貨等商品的即時報價訂閱。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化報價訂閱器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._subscribed_contracts: List[Any] = []
    
    def subscribe(
        self, 
        contract: Any, 
        quote_type: str = 'tick',
        version: str = 'v1'
    ) -> bool:
        """訂閱商品報價
        
        訂閱指定商品的即時報價資訊。
        
        Args:
            contract (Any): 商品合約物件，需從 Contracts 取得
            quote_type (str): 報價類型，'tick' 或 'bidask'，預設為 'tick'
            version (str): 報價版本，'v1' 或 'v0'，預設為 'v1'
        
        Returns:
            bool: 訂閱成功返回 True，失敗返回 False
        
        Examples:
            >>> from login import Login
            >>> from contract import ContractManager
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> contract_manager = ContractManager(api)
            >>> contract_manager.fetch_contracts()
            >>> subscriber = QuoteSubscriber(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> success = subscriber.subscribe(stock)
            >>> print(f"訂閱成功: {success}")
        
        Raises:
            ValueError: 當 contract 為 None 時
            ValueError: 當 quote_type 不是 'tick' 或 'bidask' 時
            ValueError: 當 version 不是 'v1' 或 'v0' 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if contract is None:
            raise ValueError("Contract 不可為 None")
        
        if quote_type not in ['tick', 'bidask']:
            raise ValueError(f"Quote type 必須是 'tick' 或 'bidask'，當前值: {quote_type}")
        
        if version not in ['v1', 'v0']:
            raise ValueError(f"Version 必須是 'v1' 或 'v0'，當前值: {version}")
        
        try:
            # 轉換字串參數為 Shioaji 常數
            qt = sj.constant.QuoteType.Tick if quote_type == 'tick' else sj.constant.QuoteType.BidAsk
            qv = sj.constant.QuoteVersion.v1 if version == 'v1' else sj.constant.QuoteVersion.v0
            
            # 訂閱報價
            self._api.quote.subscribe(
                contract,
                quote_type=qt,
                version=qv
            )
            
            # 記錄已訂閱的合約
            if contract not in self._subscribed_contracts:
                self._subscribed_contracts.append(contract)
            
            return True
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的合約物件: {e}")
    
    def unsubscribe(self, contract: Any) -> bool:
        """取消訂閱商品報價
        
        取消指定商品的報價訂閱。
        
        Args:
            contract (Any): 商品合約物件
        
        Returns:
            bool: 取消訂閱成功返回 True，失敗返回 False
        
        Examples:
            >>> subscriber = QuoteSubscriber(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> subscriber.subscribe(stock)
            >>> success = subscriber.unsubscribe(stock)
            >>> print(f"取消訂閱成功: {success}")
        
        Raises:
            ValueError: 當 contract 為 None 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if contract is None:
            raise ValueError("Contract 不可為 None")
        
        try:
            self._api.quote.unsubscribe(contract)
            
            # 從已訂閱列表中移除
            if contract in self._subscribed_contracts:
                self._subscribed_contracts.remove(contract)
            
            return True
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def get_subscribed_contracts(self) -> List[Any]:
        """取得已訂閱的合約列表
        
        Returns:
            List[Any]: 已訂閱的合約物件列表
        
        Examples:
            >>> subscriber = QuoteSubscriber(api)
            >>> subscriber.subscribe(stock1)
            >>> subscriber.subscribe(stock2)
            >>> contracts = subscriber.get_subscribed_contracts()
            >>> print(f"已訂閱 {len(contracts)} 個商品")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._subscribed_contracts.copy()
    
    def is_subscribed(self, contract: Any) -> bool:
        """檢查是否已訂閱指定商品
        
        Args:
            contract (Any): 商品合約物件
        
        Returns:
            bool: 已訂閱返回 True，否則返回 False
        
        Examples:
            >>> subscriber = QuoteSubscriber(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> subscriber.is_subscribed(stock)
            False
            >>> subscriber.subscribe(stock)
            >>> subscriber.is_subscribed(stock)
            True
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return contract in self._subscribed_contracts
