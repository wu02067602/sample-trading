"""下單執行模組

此模組負責處理永豐 Shioaji API 的下單功能。
"""

import shioaji as sj
from typing import Optional, Any
from datetime import datetime


class OrderExecutor:
    """負責執行交易訂單
    
    此類別封裝了永豐 Shioaji API 的下單功能，
    支援股票整股、盤中零股的買賣下單。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化下單執行器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._last_trade: Optional[Any] = None
    
    def place_stock_order(
        self,
        contract: Any,
        action: str,
        price: float,
        quantity: int,
        order_type: str = 'ROD',
        price_type: str = 'LMT',
        order_lot: str = 'Common',
        timeout: int = 5000
    ) -> Any:
        """下股票委託單
        
        執行股票買賣委託，支援整股和盤中零股交易。
        
        Args:
            contract (Any): 商品合約物件，需從 ContractManager 取得
            action (str): 買賣別，'Buy' 或 'Sell'
            price (float): 委託價格
            quantity (int): 委託數量（整股以張為單位，盤中零股以股為單位）
            order_type (str): 委託類型，'ROD'（當日有效）、'IOC'（立即成交否則取消）、'FOK'（全部成交否則取消），預設為 'ROD'
            price_type (str): 價格類型，'LMT'（限價）、'MKT'（市價）、'MKP'（範圍市價），預設為 'LMT'
            order_lot (str): 交易批次，'Common'（整股）或 'IntradayOdd'（盤中零股），預設為 'Common'
            timeout (int): 逾時時間（毫秒），預設為 5000 毫秒（5 秒）
        
        Returns:
            Any: Trade 物件，包含 contract, order, status 等資訊
        
        Examples:
            >>> from login import Login
            >>> from contract import ContractManager
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> contract_manager = ContractManager(api)
            >>> contract_manager.fetch_contracts()
            >>> executor = OrderExecutor(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> trade = executor.place_stock_order(
            ...     contract=stock,
            ...     action='Buy',
            ...     price=500.0,
            ...     quantity=1
            ... )
            >>> print(f"訂單狀態: {trade.status.status}")
        
        Raises:
            ValueError: 當 contract 為 None 時
            ValueError: 當 action 不是 'Buy' 或 'Sell' 時
            ValueError: 當 price 小於等於 0 時
            ValueError: 當 quantity 小於等於 0 時
            ValueError: 當 order_type 不在允許的值中時
            ValueError: 當 price_type 不在允許的值中時
            ValueError: 當 order_lot 不在允許的值中時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            RuntimeError: 當尚未設定股票帳戶時
        """
        # 參數驗證
        if contract is None:
            raise ValueError("Contract 不可為 None")
        
        if action not in ['Buy', 'Sell']:
            raise ValueError(f"Action 必須是 'Buy' 或 'Sell'，當前值: {action}")
        
        if price <= 0:
            raise ValueError(f"Price 必須大於 0，當前值: {price}")
        
        if quantity <= 0:
            raise ValueError(f"Quantity 必須大於 0，當前值: {quantity}")
        
        if order_type not in ['ROD', 'IOC', 'FOK']:
            raise ValueError(f"Order type 必須是 'ROD', 'IOC' 或 'FOK'，當前值: {order_type}")
        
        if price_type not in ['LMT', 'MKT', 'MKP']:
            raise ValueError(f"Price type 必須是 'LMT', 'MKT' 或 'MKP'，當前值: {price_type}")
        
        if order_lot not in ['Common', 'IntradayOdd']:
            raise ValueError(f"Order lot 必須是 'Common' 或 'IntradayOdd'，當前值: {order_lot}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        # 檢查是否有股票帳戶
        if not hasattr(self._api, 'stock_account') or self._api.stock_account is None:
            raise RuntimeError("尚未設定股票帳戶，請先登入並確認帳戶設定")
        
        try:
            # 轉換字串參數為 Shioaji 常數
            action_const = sj.constant.Action.Buy if action == 'Buy' else sj.constant.Action.Sell
            
            order_type_map = {
                'ROD': sj.constant.OrderType.ROD,
                'IOC': sj.constant.OrderType.IOC,
                'FOK': sj.constant.OrderType.FOK
            }
            order_type_const = order_type_map[order_type]
            
            price_type_map = {
                'LMT': sj.constant.StockPriceType.LMT,
                'MKT': sj.constant.StockPriceType.MKT,
                'MKP': sj.constant.StockPriceType.MKP
            }
            price_type_const = price_type_map[price_type]
            
            order_lot_map = {
                'Common': sj.constant.StockOrderLot.Common,
                'IntradayOdd': sj.constant.StockOrderLot.IntradayOdd
            }
            order_lot_const = order_lot_map[order_lot]
            
            # 建立委託單
            order = self._api.Order(
                price=price,
                quantity=quantity,
                action=action_const,
                price_type=price_type_const,
                order_type=order_type_const,
                order_lot=order_lot_const,
                account=self._api.stock_account
            )
            
            # 下單
            trade = self._api.place_order(contract, order, timeout=timeout)
            
            # 儲存最後一筆交易
            self._last_trade = trade
            
            return trade
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的參數或合約物件: {e}")
    
    def update_order(
        self,
        trade: Any,
        price: Optional[float] = None,
        quantity: Optional[int] = None,
        timeout: int = 5000
    ) -> Any:
        """改單
        
        修改委託單的價格或數量。
        注意：盤中零股只能減量，不能改價。
        
        Args:
            trade (Any): 原委託單的 Trade 物件
            price (Optional[float]): 新的委託價格，None 表示不修改
            quantity (Optional[int]): 新的委託數量，None 表示不修改
            timeout (int): 逾時時間（毫秒），預設為 5000 毫秒（5 秒）
        
        Returns:
            Any: 更新後的 Trade 物件
        
        Examples:
            >>> executor = OrderExecutor(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> trade = executor.place_stock_order(stock, 'Buy', 500.0, 1)
            >>> updated_trade = executor.update_order(trade, price=505.0)
            >>> print(f"新價格: {updated_trade.order.price}")
        
        Raises:
            ValueError: 當 trade 為 None 時
            ValueError: 當 price 和 quantity 都為 None 時
            ValueError: 當 price 小於等於 0 時
            ValueError: 當 quantity 小於等於 0 時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if trade is None:
            raise ValueError("Trade 不可為 None")
        
        if price is None and quantity is None:
            raise ValueError("Price 和 Quantity 至少需要指定一個")
        
        if price is not None and price <= 0:
            raise ValueError(f"Price 必須大於 0，當前值: {price}")
        
        if quantity is not None and quantity <= 0:
            raise ValueError(f"Quantity 必須大於 0，當前值: {quantity}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            updated_trade = self._api.update_order(
                trade=trade,
                price=price,
                qty=quantity,
                timeout=timeout
            )
            
            self._last_trade = updated_trade
            
            return updated_trade
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的 Trade 物件: {e}")
    
    def cancel_order(self, trade: Any, timeout: int = 5000) -> Any:
        """取消委託單
        
        取消尚未成交的委託單。
        
        Args:
            trade (Any): 要取消的 Trade 物件
            timeout (int): 逾時時間（毫秒），預設為 5000 毫秒（5 秒）
        
        Returns:
            Any: 取消後的 Trade 物件
        
        Examples:
            >>> executor = OrderExecutor(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> trade = executor.place_stock_order(stock, 'Buy', 500.0, 1)
            >>> cancelled_trade = executor.cancel_order(trade)
            >>> print(f"訂單狀態: {cancelled_trade.status.status}")
        
        Raises:
            ValueError: 當 trade 為 None 時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if trade is None:
            raise ValueError("Trade 不可為 None")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            cancelled_trade = self._api.cancel_order(trade, timeout=timeout)
            
            self._last_trade = cancelled_trade
            
            return cancelled_trade
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的 Trade 物件: {e}")
    
    def get_last_trade(self) -> Optional[Any]:
        """取得最後一筆交易
        
        Returns:
            Optional[Any]: 最後一筆交易的 Trade 物件，如果尚未執行過交易則返回 None
        
        Examples:
            >>> executor = OrderExecutor(api)
            >>> stock = contract_manager.get_stock("2330")
            >>> executor.place_stock_order(stock, 'Buy', 500.0, 1)
            >>> last_trade = executor.get_last_trade()
            >>> print(f"最後交易: {last_trade.order.id}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._last_trade
