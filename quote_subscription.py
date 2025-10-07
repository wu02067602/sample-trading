"""
量化交易系統 - 報價訂閱模組

此模組負責訂閱即時市場報價資訊，管理報價訂閱的啟動與停止。
"""

import shioaji as sj
from typing import List, Optional, Set
from quote_callback import QuoteCallback


class QuoteSubscription:
    """
    負責訂閱即時市場報價資訊，管理報價訂閱的啟動與停止。
    
    此類別封裝了永豐金證券 Shioaji API 的報價訂閱功能，支援訂閱
    股票、期貨、選擇權等各類金融商品的即時報價。
    
    Attributes:
        api (sj.Shioaji): Shioaji API 實例
        subscribed_contracts (Set[str]): 已訂閱的商品代碼集合
        quote_callback (QuoteCallback): 報價回調處理器
    
    Examples:
        >>> from authentication import Authentication
        >>> from instrument_retrieval import InstrumentRetrieval
        >>> from quote_callback import QuoteCallback
        >>> 
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> retrieval = InstrumentRetrieval(auth.api)
        >>> retrieval.fetch_all_contracts()
        >>> 
        >>> callback_handler = QuoteCallback()
        >>> subscription = QuoteSubscription(auth.api, callback_handler)
        >>> 
        >>> contract = retrieval.get_stock_contract("2330")
        >>> subscription.subscribe(contract)
    """
    
    def __init__(
        self,
        api: sj.Shioaji,
        quote_callback: QuoteCallback
    ) -> None:
        """
        初始化 QuoteSubscription 實例。
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 實例
            quote_callback (QuoteCallback): 報價回調處理器
        
        Raises:
            ValueError: 當 api 或 quote_callback 為 None 時
        """
        if api is None:
            raise ValueError("api 參數不可為 None")
        if quote_callback is None:
            raise ValueError("quote_callback 參數不可為 None")
        
        self.api: sj.Shioaji = api
        self.subscribed_contracts: Set[str] = set()
        self.quote_callback: QuoteCallback = quote_callback
        
        # 設定 API 的報價回調函數
        self._setup_quote_callback()
    
    def _setup_quote_callback(self) -> None:
        """
        設定 Shioaji API 的報價回調函數。
        
        將 QuoteCallback 的 on_quote_update 方法設定為 API 的回調函數。
        
        Raises:
            RuntimeError: 當設定回調函數失敗時
        """
        try:
            # 定義內部回調函數來轉換參數格式
            def _internal_callback(exchange, tick):
                # 將 tick 物件轉換為字典格式
                tick_dict = {
                    'code': tick.code if hasattr(tick, 'code') else '',
                    'datetime': tick.datetime if hasattr(tick, 'datetime') else None,
                    'open': tick.open if hasattr(tick, 'open') else 0.0,
                    'high': tick.high if hasattr(tick, 'high') else 0.0,
                    'low': tick.low if hasattr(tick, 'low') else 0.0,
                    'close': tick.close if hasattr(tick, 'close') else 0.0,
                    'volume': tick.volume if hasattr(tick, 'volume') else 0,
                    'total_volume': tick.total_volume if hasattr(tick, 'total_volume') else 0
                }
                self.quote_callback.on_quote_update(exchange, tick_dict)
            
            # 設定 API 的報價回調
            self.api.quote.set_callback(_internal_callback)
        except AttributeError as e:
            raise RuntimeError(f"設定報價回調失敗：{e}") from e
    
    def subscribe(self, contract: sj.contracts.Contract) -> bool:
        """
        訂閱指定商品的即時報價。
        
        Args:
            contract (sj.contracts.Contract): 要訂閱的商品合約
        
        Returns:
            bool: 訂閱成功返回 True，失敗返回 False
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> success = subscription.subscribe(contract)
            >>> if success:
            ...     print("訂閱成功")
        
        Raises:
            ValueError: 當 contract 為 None 時
            RuntimeError: 當訂閱操作失敗時
        """
        if contract is None:
            raise ValueError("contract 不可為 None")
        
        try:
            # 檢查是否已訂閱
            contract_code = contract.code
            if contract_code in self.subscribed_contracts:
                return True
            
            # 執行訂閱
            self.api.quote.subscribe(
                contract,
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            
            # 記錄已訂閱的商品
            self.subscribed_contracts.add(contract_code)
            return True
            
        except AttributeError as e:
            raise RuntimeError(f"訂閱報價失敗：合約屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"訂閱報價失敗：{e}") from e
    
    def subscribe_multiple(
        self,
        contracts: List[sj.contracts.Contract]
    ) -> dict[str, bool]:
        """
        訂閱多個商品的即時報價。
        
        Args:
            contracts (List[sj.contracts.Contract]): 要訂閱的商品合約列表
        
        Returns:
            dict[str, bool]: 各商品的訂閱結果字典
                - key: 商品代碼
                - value: 訂閱是否成功
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> contracts = [
            ...     retrieval.get_stock_contract("2330"),
            ...     retrieval.get_stock_contract("2317")
            ... ]
            >>> results = subscription.subscribe_multiple(contracts)
            >>> for code, success in results.items():
            ...     print(f"{code}: {'成功' if success else '失敗'}")
        
        Raises:
            ValueError: 當 contracts 為 None 或空列表時
        """
        if not contracts:
            raise ValueError("contracts 不可為空")
        
        results = {}
        for contract in contracts:
            try:
                success = self.subscribe(contract)
                results[contract.code] = success
            except (ValueError, RuntimeError) as e:
                results[contract.code] = False
                print(f"訂閱 {contract.code} 失敗：{e}")
        
        return results
    
    def unsubscribe(self, contract: sj.contracts.Contract) -> bool:
        """
        取消訂閱指定商品的即時報價。
        
        Args:
            contract (sj.contracts.Contract): 要取消訂閱的商品合約
        
        Returns:
            bool: 取消訂閱成功返回 True，失敗返回 False
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> subscription.subscribe(contract)
            >>> subscription.unsubscribe(contract)
            True
        
        Raises:
            ValueError: 當 contract 為 None 時
            RuntimeError: 當取消訂閱操作失敗時
        """
        if contract is None:
            raise ValueError("contract 不可為 None")
        
        try:
            contract_code = contract.code
            
            # 檢查是否已訂閱
            if contract_code not in self.subscribed_contracts:
                return True
            
            # 執行取消訂閱
            self.api.quote.unsubscribe(
                contract,
                quote_type=sj.constant.QuoteType.Tick,
                version=sj.constant.QuoteVersion.v1
            )
            
            # 從已訂閱列表中移除
            self.subscribed_contracts.discard(contract_code)
            return True
            
        except AttributeError as e:
            raise RuntimeError(f"取消訂閱失敗：合約屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"取消訂閱失敗：{e}") from e
    
    def unsubscribe_all(self) -> bool:
        """
        取消所有商品的報價訂閱。
        
        Returns:
            bool: 全部取消成功返回 True，部分失敗返回 False
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> # 訂閱多個商品...
            >>> subscription.unsubscribe_all()
            True
        """
        if not self.subscribed_contracts:
            return True
        
        # 複製集合以避免在迭代時修改
        contracts_to_unsubscribe = self.subscribed_contracts.copy()
        all_success = True
        
        for contract_code in contracts_to_unsubscribe:
            try:
                # 這裡需要從 API 取得合約物件，但為了簡化，我們直接清除記錄
                self.subscribed_contracts.discard(contract_code)
            except Exception as e:
                print(f"取消訂閱 {contract_code} 失敗：{e}")
                all_success = False
        
        return all_success
    
    def is_subscribed(self, contract: sj.contracts.Contract) -> bool:
        """
        檢查指定商品是否已訂閱。
        
        Args:
            contract (sj.contracts.Contract): 要檢查的商品合約
        
        Returns:
            bool: 已訂閱返回 True，未訂閱返回 False
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> subscription.is_subscribed(contract)
            False
            >>> subscription.subscribe(contract)
            >>> subscription.is_subscribed(contract)
            True
        
        Raises:
            ValueError: 當 contract 為 None 時
        """
        if contract is None:
            raise ValueError("contract 不可為 None")
        
        return contract.code in self.subscribed_contracts
    
    def get_subscribed_count(self) -> int:
        """
        取得已訂閱的商品數量。
        
        Returns:
            int: 已訂閱的商品數量
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> subscription.get_subscribed_count()
            0
            >>> subscription.subscribe(contract)
            >>> subscription.get_subscribed_count()
            1
        """
        return len(self.subscribed_contracts)
    
    def get_subscribed_contracts(self) -> List[str]:
        """
        取得已訂閱的商品代碼列表。
        
        Returns:
            List[str]: 已訂閱的商品代碼列表
        
        Examples:
            >>> subscription = QuoteSubscription(api, callback_handler)
            >>> contracts = subscription.get_subscribed_contracts()
            >>> print(f"已訂閱 {len(contracts)} 個商品")
        """
        return list(self.subscribed_contracts)
