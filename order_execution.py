"""
量化交易系統 - 訂單執行模組

此模組負責執行交易下單操作，處理買賣單的送出與取消。
"""

import shioaji as sj
from typing import Optional, Dict, Any
from enum import Enum


class OrderType(Enum):
    """訂單類型列舉"""
    ROD = "ROD"  # 當日有效單
    IOC = "IOC"  # 立即成交否則取消
    FOK = "FOK"  # 全部成交否則取消


class PriceType(Enum):
    """價格類型列舉"""
    LIMIT = "LMT"  # 限價
    MARKET = "MKT"  # 市價
    MKP = "MKP"  # 範圍市價


class Action(Enum):
    """買賣方向列舉"""
    BUY = "Buy"
    SELL = "Sell"


class OrderExecution:
    """
    負責執行交易下單操作，處理買賣單的送出與取消。
    
    此類別封裝了永豐金證券 Shioaji API 的下單功能，支援股票、
    期貨、選擇權等各類金融商品的交易下單與取消操作。
    
    Attributes:
        api (sj.Shioaji): Shioaji API 實例
        order_history (list): 訂單歷史記錄
    
    Examples:
        >>> from authentication import Authentication
        >>> from instrument_retrieval import InstrumentRetrieval
        >>> 
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> retrieval = InstrumentRetrieval(auth.api)
        >>> retrieval.fetch_all_contracts()
        >>> 
        >>> order_exec = OrderExecution(auth.api)
        >>> contract = retrieval.get_stock_contract("2330")
        >>> trade = order_exec.place_stock_order(
        ...     contract=contract,
        ...     action=Action.BUY,
        ...     price=580.0,
        ...     quantity=1
        ... )
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """
        初始化 OrderExecution 實例。
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 實例
        
        Raises:
            ValueError: 當 api 參數為 None 時
        """
        if api is None:
            raise ValueError("api 參數不可為 None")
        
        self.api: sj.Shioaji = api
        self.order_history: list = []
    
    def place_stock_order(
        self,
        contract: sj.contracts.Contract,
        action: Action,
        price: float,
        quantity: int,
        order_type: OrderType = OrderType.ROD,
        price_type: PriceType = PriceType.LIMIT
    ) -> Optional[sj.order.Trade]:
        """
        執行股票下單操作（整股交易）。
        
        Args:
            contract (sj.contracts.Contract): 股票合約
            action (Action): 買賣方向（BUY 或 SELL）
            price (float): 委託價格（市價單可設為 0）
            quantity (int): 委託數量（單位：張，1 張 = 1000 股）
            order_type (OrderType): 訂單類型，預設為 ROD（當日有效單）
            price_type (PriceType): 價格類型，預設為 LIMIT（限價）
        
        Returns:
            Optional[sj.order.Trade]: 交易物件，包含訂單資訊，失敗時返回 None
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> # 限價買進 1 張台積電，價格 580 元
            >>> trade = order_exec.place_stock_order(
            ...     contract=contract,
            ...     action=Action.BUY,
            ...     price=580.0,
            ...     quantity=1
            ... )
            >>> if trade:
            ...     print(f"訂單編號：{trade.order.id}")
        
        Raises:
            ValueError: 當參數不合法時
            RuntimeError: 當下單操作失敗時
        """
        if contract is None:
            raise ValueError("contract 不可為 None")
        if price < 0:
            raise ValueError(f"price 必須大於等於 0，當前值：{price}")
        if quantity <= 0:
            raise ValueError(f"quantity 必須大於 0，當前值：{quantity}")
        
        try:
            # 建立股票訂單物件
            order = self.api.Order(
                price=price,
                quantity=quantity,
                action=action.value,
                price_type=price_type.value,
                order_type=order_type.value,
                order_lot=sj.constant.StockOrderLot.Common,  # 整股
                account=self.api.stock_account
            )
            
            # 執行下單
            trade = self.api.place_order(contract, order)
            
            # 記錄訂單到歷史
            self._record_order(trade, "stock")
            
            return trade
            
        except AttributeError as e:
            raise RuntimeError(f"下單失敗：API 屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"下單失敗：{e}") from e
    
    def place_odd_lot_order(
        self,
        contract: sj.contracts.Contract,
        action: Action,
        price: float,
        quantity: int,
        order_type: OrderType = OrderType.ROD,
        price_type: PriceType = PriceType.LIMIT
    ) -> Optional[sj.order.Trade]:
        """
        執行盤中零股下單操作。
        
        盤中零股交易時間為 9:00-13:30，交易單位為股（非張）。
        
        Args:
            contract (sj.contracts.Contract): 股票合約
            action (Action): 買賣方向（BUY 或 SELL）
            price (float): 委託價格（市價單可設為 0）
            quantity (int): 委託數量（單位：股，1-999 股）
            order_type (OrderType): 訂單類型，預設為 ROD（當日有效單）
            price_type (PriceType): 價格類型，預設為 LIMIT（限價）
        
        Returns:
            Optional[sj.order.Trade]: 交易物件，包含訂單資訊，失敗時返回 None
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> # 限價買進 100 股台積電，價格 580 元
            >>> trade = order_exec.place_odd_lot_order(
            ...     contract=contract,
            ...     action=Action.BUY,
            ...     price=580.0,
            ...     quantity=100
            ... )
        
        Raises:
            ValueError: 當參數不合法時（quantity 必須在 1-999 之間）
            RuntimeError: 當下單操作失敗時
        """
        if contract is None:
            raise ValueError("contract 不可為 None")
        if price < 0:
            raise ValueError(f"price 必須大於等於 0，當前值：{price}")
        if quantity <= 0 or quantity >= 1000:
            raise ValueError(f"零股數量必須在 1-999 之間，當前值：{quantity}")
        
        try:
            # 建立零股訂單物件
            order = self.api.Order(
                price=price,
                quantity=quantity,
                action=action.value,
                price_type=price_type.value,
                order_type=order_type.value,
                order_lot=sj.constant.StockOrderLot.IntradayOdd,  # 盤中零股
                account=self.api.stock_account
            )
            
            # 執行下單
            trade = self.api.place_order(contract, order)
            
            # 記錄訂單到歷史
            self._record_order(trade, "odd_lot")
            
            return trade
            
        except AttributeError as e:
            raise RuntimeError(f"零股下單失敗：API 屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"零股下單失敗：{e}") from e
    
    def place_market_order(
        self,
        contract: sj.contracts.Contract,
        action: Action,
        quantity: int,
        order_type: OrderType = OrderType.ROD
    ) -> Optional[sj.order.Trade]:
        """
        執行市價單下單操作。
        
        市價單會以市場當前最佳價格立即成交。
        
        Args:
            contract (sj.contracts.Contract): 股票合約
            action (Action): 買賣方向（BUY 或 SELL）
            quantity (int): 委託數量（單位：張）
            order_type (OrderType): 訂單類型，預設為 ROD
        
        Returns:
            Optional[sj.order.Trade]: 交易物件，包含訂單資訊
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> contract = retrieval.get_stock_contract("2330")
            >>> trade = order_exec.place_market_order(
            ...     contract=contract,
            ...     action=Action.BUY,
            ...     quantity=1
            ... )
        
        Raises:
            ValueError: 當參數不合法時
            RuntimeError: 當下單操作失敗時
        """
        return self.place_stock_order(
            contract=contract,
            action=action,
            price=0.0,  # 市價單價格設為 0
            quantity=quantity,
            order_type=order_type,
            price_type=PriceType.MARKET
        )
    
    def cancel_order(self, trade: sj.order.Trade) -> bool:
        """
        取消指定的委託單。
        
        Args:
            trade (sj.order.Trade): 要取消的交易物件
        
        Returns:
            bool: 取消成功返回 True，失敗返回 False
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> trade = order_exec.place_stock_order(...)
            >>> # 取消剛才的訂單
            >>> success = order_exec.cancel_order(trade)
            >>> if success:
            ...     print("訂單已取消")
        
        Raises:
            ValueError: 當 trade 為 None 時
            RuntimeError: 當取消操作失敗時
        """
        if trade is None:
            raise ValueError("trade 不可為 None")
        
        try:
            result = self.api.cancel_order(trade)
            return bool(result)
        except AttributeError as e:
            raise RuntimeError(f"取消訂單失敗：API 屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"取消訂單失敗：{e}") from e
    
    def update_order(
        self,
        trade: sj.order.Trade,
        price: Optional[float] = None,
        quantity: Optional[int] = None
    ) -> Optional[sj.order.Trade]:
        """
        修改指定的委託單。
        
        Args:
            trade (sj.order.Trade): 要修改的交易物件
            price (Optional[float]): 新的委託價格，None 表示不修改
            quantity (Optional[int]): 新的委託數量，None 表示不修改
        
        Returns:
            Optional[sj.order.Trade]: 修改後的交易物件
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> trade = order_exec.place_stock_order(...)
            >>> # 修改訂單價格為 585 元
            >>> updated_trade = order_exec.update_order(trade, price=585.0)
        
        Raises:
            ValueError: 當參數不合法時
            RuntimeError: 當修改操作失敗時
        """
        if trade is None:
            raise ValueError("trade 不可為 None")
        if price is not None and price < 0:
            raise ValueError(f"price 必須大於等於 0，當前值：{price}")
        if quantity is not None and quantity <= 0:
            raise ValueError(f"quantity 必須大於 0，當前值：{quantity}")
        
        try:
            # 建立新的訂單物件
            order = trade.order
            
            if price is not None:
                order.price = price
            if quantity is not None:
                order.quantity = quantity
            
            # 執行訂單修改
            updated_trade = self.api.update_order(trade, order)
            
            return updated_trade
            
        except AttributeError as e:
            raise RuntimeError(f"修改訂單失敗：API 屬性錯誤 - {e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"修改訂單失敗：{e}") from e
    
    def _record_order(self, trade: sj.order.Trade, order_category: str) -> None:
        """
        記錄訂單到歷史記錄。
        
        Args:
            trade (sj.order.Trade): 交易物件
            order_category (str): 訂單類別（stock, odd_lot, futures, etc.）
        """
        if trade is None:
            return
        
        order_record = {
            'trade': trade,
            'category': order_category,
            'order_id': trade.order.id if hasattr(trade.order, 'id') else None,
            'contract_code': trade.contract.code if hasattr(trade.contract, 'code') else None,
            'action': trade.order.action if hasattr(trade.order, 'action') else None,
            'price': trade.order.price if hasattr(trade.order, 'price') else None,
            'quantity': trade.order.quantity if hasattr(trade.order, 'quantity') else None
        }
        
        self.order_history.append(order_record)
    
    def get_order_history(self) -> list:
        """
        取得訂單歷史記錄。
        
        Returns:
            list: 訂單歷史記錄列表
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> # 下單後...
            >>> history = order_exec.get_order_history()
            >>> for record in history:
            ...     print(f"訂單 {record['order_id']}: {record['action']}")
        """
        return self.order_history.copy()
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        根據訂單編號取得訂單記錄。
        
        Args:
            order_id (str): 訂單編號
        
        Returns:
            Optional[Dict[str, Any]]: 訂單記錄，找不到時返回 None
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> order = order_exec.get_order_by_id("ORDER123")
            >>> if order:
            ...     print(f"訂單價格：{order['price']}")
        
        Raises:
            ValueError: 當 order_id 為空字串時
        """
        if not order_id:
            raise ValueError("order_id 不可為空")
        
        for record in self.order_history:
            if record.get('order_id') == order_id:
                return record
        
        return None
    
    def clear_history(self) -> None:
        """
        清空訂單歷史記錄。
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> order_exec.clear_history()
        """
        self.order_history.clear()
    
    def get_order_count(self) -> int:
        """
        取得訂單歷史記錄總數。
        
        Returns:
            int: 訂單數量
        
        Examples:
            >>> order_exec = OrderExecution(api)
            >>> count = order_exec.get_order_count()
            >>> print(f"已下 {count} 筆訂單")
        """
        return len(self.order_history)
