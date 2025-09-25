"""
BrokerClient - 永豐金證券交易客戶端

此模組實作了完整的交易功能，包括訂單管理、市場資料訂閱、帳戶查詢等功能。
聚合 BrokerageAuth 進行認證和 Session 管理。

Author: 資深後端工程師
"""

import json
import time
import logging
from typing import Optional, Dict, Any, List, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from threading import Thread, Event
import queue

from brokerage_auth import (
    BrokerageAuth, 
    SessionData,
    AuthenticationError, 
    NetworkError,
    TokenRefreshError
)

# 嘗試導入 requests，如果不存在則使用模擬版本
try:
    import requests
except ImportError:
    from brokerage_auth import requests


class OrderSide(Enum):
    """訂單方向"""
    BUY = "Buy"
    SELL = "Sell"


class OrderType(Enum):
    """訂單類型"""
    MARKET = "Market"      # 市價單
    LIMIT = "Limit"        # 限價單
    STOP = "Stop"          # 停損單
    STOP_LIMIT = "StopLimit"  # 停損限價單


class OrderStatus(Enum):
    """訂單狀態"""
    PENDING = "Pending"        # 待處理
    SUBMITTED = "Submitted"    # 已提交
    PARTIAL_FILLED = "PartialFilled"  # 部分成交
    FILLED = "Filled"          # 完全成交
    CANCELLED = "Cancelled"    # 已取消
    REJECTED = "Rejected"      # 已拒絕


@dataclass
class Order:
    """
    訂單資料結構
    
    屬性:
        symbol (str): 股票代號
        side (OrderSide): 買賣方向
        order_type (OrderType): 訂單類型
        quantity (int): 數量
        price (Optional[float]): 價格（市價單可為 None）
        stop_price (Optional[float]): 停損價格
        time_in_force (str): 有效期限 (DAY, GTC, IOC, FOK)
        order_id (Optional[str]): 訂單 ID（由系統生成）
    """
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    order_id: Optional[str] = None


@dataclass
class OrderStatusInfo:
    """
    訂單狀態資訊
    
    屬性:
        order_id (str): 訂單 ID
        status (OrderStatus): 訂單狀態
        filled_quantity (int): 已成交數量
        remaining_quantity (int): 剩餘數量
        avg_price (float): 平均成交價格
        last_update (datetime): 最後更新時間
        message (str): 狀態訊息
    """
    order_id: str
    status: OrderStatus
    filled_quantity: int
    remaining_quantity: int
    avg_price: float
    last_update: datetime
    message: str = ""


@dataclass
class TickData:
    """
    即時報價資料
    
    屬性:
        symbol (str): 股票代號
        price (float): 現價
        volume (int): 成交量
        bid_price (float): 買價
        ask_price (float): 賣價
        bid_volume (int): 買量
        ask_volume (int): 賣量
        timestamp (datetime): 時間戳
        change (float): 漲跌
        change_percent (float): 漲跌幅
    """
    symbol: str
    price: float
    volume: int
    bid_price: float
    ask_price: float
    bid_volume: int
    ask_volume: int
    timestamp: datetime
    change: float = 0.0
    change_percent: float = 0.0


@dataclass
class TopGainer:
    """
    漲幅排行資料
    
    屬性:
        symbol (str): 股票代號
        name (str): 股票名稱
        price (float): 現價
        change (float): 漲跌
        change_percent (float): 漲跌幅
        volume (int): 成交量
        market_cap (float): 市值
    """
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float


@dataclass
class AccountBalance:
    """
    帳戶餘額資訊
    
    屬性:
        cash_balance (float): 現金餘額
        buying_power (float): 可用資金
        total_value (float): 總資產價值
        unrealized_pnl (float): 未實現損益
        realized_pnl (float): 已實現損益
        margin_used (float): 已使用保證金
        margin_available (float): 可用保證金
    """
    cash_balance: float
    buying_power: float
    total_value: float
    unrealized_pnl: float
    realized_pnl: float
    margin_used: float
    margin_available: float


class BrokerClientError(Exception):
    """BrokerClient 基礎例外類別"""
    pass


class DataFormatError(BrokerClientError):
    """資料格式錯誤"""
    pass


class UnauthorizedError(BrokerClientError):
    """未授權錯誤 (401)"""
    pass


class ForbiddenError(BrokerClientError):
    """權限不足錯誤 (403)"""
    pass


class OrderError(BrokerClientError):
    """訂單相關錯誤"""
    pass


class SubscriptionError(BrokerClientError):
    """訂閱相關錯誤"""
    pass


class BrokerClient:
    """
    永豐金證券交易客戶端
    
    聚合 BrokerageAuth 進行認證管理，提供完整的交易功能包括：
    - 即時報價訂閱
    - 市場掃描
    - 訂單管理
    - 帳戶查詢
    - 事件回調處理
    
    使用範例:
        >>> client = BrokerClient()
        >>> client.subscribeTick("2330", False)
        >>> client.onTick(lambda tick: print(f"價格: {tick.price}"))
        >>> gainers = client.scanTopGainers()
        >>> order = Order("2330", OrderSide.BUY, OrderType.LIMIT, 1000, 500.0)
        >>> order_id = client.placeOrder(order)
    """

    def __init__(self):
        """
        初始化 BrokerClient
        
        自動建立 BrokerageAuth 實例進行認證管理
        
        異常:
            所有 BrokerageAuth 相關例外
        """
        self._auth = BrokerageAuth()
        self._base_url = "https://api.sinotrade.com.tw"
        
        # 設定日誌
        self._logger = logging.getLogger(__name__)
        
        # 回調函數
        self._tick_callbacks: List[Callable[[TickData], None]] = []
        self._order_callbacks: List[Callable[[OrderStatusInfo], None]] = []
        self._deal_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # 訂閱管理
        self._subscribed_symbols: Dict[str, bool] = {}  # symbol -> oddlot
        self._subscription_thread: Optional[Thread] = None
        self._subscription_stop_event = Event()
        self._tick_queue = queue.Queue()
        
        # 啟動事件處理執行緒
        self._start_event_handlers()

    def _start_event_handlers(self) -> None:
        """啟動事件處理執行緒"""
        self._subscription_thread = Thread(target=self._subscription_worker, daemon=True)
        self._subscription_thread.start()

    def _subscription_worker(self) -> None:
        """訂閱工作執行緒，處理即時資料"""
        while not self._subscription_stop_event.is_set():
            try:
                # 模擬接收即時資料
                for symbol, oddlot in self._subscribed_symbols.items():
                    if self._subscription_stop_event.is_set():
                        break
                    
                    # 生成模擬報價資料
                    tick_data = self._generate_mock_tick(symbol, oddlot)
                    
                    # 通知所有回調函數
                    for callback in self._tick_callbacks:
                        try:
                            callback(tick_data)
                        except Exception as e:
                            self._logger.error(f"Tick 回調錯誤: {e}")
                
                # 等待一秒後繼續
                self._subscription_stop_event.wait(1.0)
                
            except Exception as e:
                self._logger.error(f"訂閱工作執行緒錯誤: {e}")
                time.sleep(1.0)

    def _generate_mock_tick(self, symbol: str, oddlot: bool) -> TickData:
        """生成模擬報價資料"""
        import random
        
        base_price = 500.0 if symbol == "2330" else 100.0
        price_variation = random.uniform(-5.0, 5.0)
        current_price = base_price + price_variation
        
        return TickData(
            symbol=symbol,
            price=current_price,
            volume=random.randint(1000, 10000),
            bid_price=current_price - 0.5,
            ask_price=current_price + 0.5,
            bid_volume=random.randint(100, 1000),
            ask_volume=random.randint(100, 1000),
            timestamp=datetime.now(),
            change=price_variation,
            change_percent=(price_variation / base_price) * 100
        )

    def _make_authenticated_request(self, endpoint: str, method: str = 'GET', 
                                  data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        發送已認證的 API 請求
        
        參數:
            endpoint (str): API 端點
            method (str): HTTP 方法
            data (Optional[Dict[str, Any]]): 請求資料
            
        返回:
            Dict[str, Any]: API 回應資料
            
        異常:
            UnauthorizedError: 401 未授權
            ForbiddenError: 403 權限不足
            NetworkError: 網路連線錯誤
            DataFormatError: 資料格式錯誤
        """
        try:
            # 取得認證 Session
            session = self._auth.getSession()
            
            # 準備請求標頭
            headers = {
                'Authorization': f'Bearer {session.token}',
                'Content-Type': 'application/json',
                'X-User-ID': session.user_id,
                'X-Timestamp': datetime.now().isoformat()
            }
            
            # 發送請求
            url = f"{self._base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, params=data, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            # 處理 HTTP 狀態碼
            if response.status_code == 401:
                # Token 可能過期，嘗試刷新
                try:
                    self._auth.refresh()
                    # 重新發送請求
                    return self._make_authenticated_request(endpoint, method, data)
                except TokenRefreshError:
                    raise UnauthorizedError("認證失敗，請重新登入")
                    
            elif response.status_code == 403:
                raise ForbiddenError("權限不足，無法存取此資源")
            elif 400 <= response.status_code < 500:
                raise NetworkError(f"客戶端錯誤 ({response.status_code}): {response.text}")
            elif response.status_code >= 500:
                raise NetworkError(f"伺服器錯誤 ({response.status_code}): {response.text}")
                
            response.raise_for_status()
            
            # 解析 JSON 回應
            try:
                return response.json()
            except json.JSONDecodeError as e:
                raise DataFormatError(f"JSON 解析錯誤: {str(e)}")
                
        except requests.exceptions.Timeout:
            raise NetworkError("請求逾時")
        except requests.exceptions.ConnectionError:
            raise NetworkError("連線錯誤")
        except (UnauthorizedError, ForbiddenError, DataFormatError):
            # 重新拋出已知錯誤
            raise
        except Exception as e:
            raise NetworkError(f"請求失敗: {str(e)}")

    def subscribeTick(self, symbol: str, oddlot: bool = False) -> None:
        """
        訂閱股票即時報價
        
        參數:
            symbol (str): 股票代號（例如 "2330"）
            oddlot (bool): 是否包含零股交易，預設 False
            
        異常:
            SubscriptionError: 訂閱失敗
            NetworkError: 網路連線錯誤
            UnauthorizedError: 認證失敗
            
        使用範例:
            >>> client = BrokerClient()
            >>> client.subscribeTick("2330", False)  # 訂閱台積電報價
            >>> client.subscribeTick("0050", True)   # 訂閱 ETF 含零股
        """
        self._logger.info(f"訂閱股票報價: {symbol}, 零股: {oddlot}")
        
        try:
            # 模擬訂閱 API 呼叫
            request_data = {
                'symbol': symbol,
                'oddlot': oddlot,
                'action': 'subscribe'
            }
            
            # TODO: 實際實作時需要呼叫真實 API
            # response = self._make_authenticated_request('/market/subscribe', 'POST', request_data)
            
            # 模擬成功回應
            response = {'success': True, 'message': f'成功訂閱 {symbol}'}
            
            if response.get('success'):
                self._subscribed_symbols[symbol] = oddlot
                self._logger.info(f"成功訂閱 {symbol}")
            else:
                error_msg = response.get('message', '訂閱失敗')
                raise SubscriptionError(f"訂閱失敗: {error_msg}")
                
        except (NetworkError, UnauthorizedError, ForbiddenError):
            raise
        except Exception as e:
            raise SubscriptionError(f"訂閱過程發生錯誤: {str(e)}")

    def onTick(self, callback: Callable[[TickData], None]) -> None:
        """
        註冊即時報價回調函數
        
        參數:
            callback (Callable[[TickData], None]): 
                接收 TickData 物件的回調函數
                
        使用範例:
            >>> def print_tick(tick):
            ...     print(f"{tick.symbol}: {tick.price} ({tick.change_percent:+.2f}%)")
            >>> 
            >>> client = BrokerClient()
            >>> client.onTick(print_tick)
            >>> client.subscribeTick("2330")
        """
        if not callable(callback):
            raise ValueError("回調函數必須是可呼叫的")
            
        self._tick_callbacks.append(callback)
        self._logger.info("已註冊 Tick 回調函數")

    def scanTopGainers(self, limit: int = 100) -> List[TopGainer]:
        """
        掃描漲幅排行榜
        
        參數:
            limit (int): 回傳筆數限制，預設 100
            
        返回:
            List[TopGainer]: 漲幅排行清單，依漲幅由高到低排序
            
        異常:
            NetworkError: 網路連線錯誤
            DataFormatError: 資料格式錯誤
            UnauthorizedError: 認證失敗
            
        使用範例:
            >>> client = BrokerClient()
            >>> gainers = client.scanTopGainers(50)
            >>> for gainer in gainers[:10]:  # 顯示前 10 名
            ...     print(f"{gainer.symbol}: +{gainer.change_percent:.2f}%")
        """
        self._logger.info(f"掃描前 {limit} 漲幅排行")
        
        try:
            # TODO: 實際實作時需要呼叫真實 API
            # response = self._make_authenticated_request(f'/market/gainers?limit={limit}')
            
            # 暫時回傳模擬資料
            mock_gainers = self._generate_mock_gainers(limit)
            
            self._logger.info(f"取得 {len(mock_gainers)} 筆漲幅資料")
            return mock_gainers
            
        except (NetworkError, UnauthorizedError, ForbiddenError, DataFormatError):
            raise
        except Exception as e:
            raise NetworkError(f"掃描漲幅排行失敗: {str(e)}")

    def _generate_mock_gainers(self, limit: int) -> List[TopGainer]:
        """生成模擬漲幅資料"""
        import random
        
        # 模擬股票清單
        mock_stocks = [
            ("2330", "台積電"), ("2317", "鴻海"), ("2454", "聯發科"),
            ("2881", "富邦金"), ("2882", "國泰金"), ("2886", "兆豐金"),
            ("2357", "華碩"), ("2382", "廣達"), ("2412", "中華電"),
            ("2303", "聯電"), ("6505", "台塑化"), ("2002", "中鋼")
        ]
        
        gainers = []
        for i, (symbol, name) in enumerate(mock_stocks):
            if i >= limit:
                break
                
            base_price = random.uniform(50, 500)
            change_percent = random.uniform(0.1, 10.0)
            change = base_price * (change_percent / 100)
            
            gainers.append(TopGainer(
                symbol=symbol,
                name=name,
                price=base_price + change,
                change=change,
                change_percent=change_percent,
                volume=random.randint(10000, 1000000),
                market_cap=random.uniform(1000000, 50000000)
            ))
        
        # 依漲幅排序
        gainers.sort(key=lambda x: x.change_percent, reverse=True)
        return gainers

    def placeOrder(self, order: Order) -> str:
        """
        下單
        
        參數:
            order (Order): 訂單物件，包含股票代號、買賣方向、數量、價格等資訊
            
        返回:
            str: 訂單 ID
            
        異常:
            OrderError: 訂單相關錯誤
            NetworkError: 網路連線錯誤
            UnauthorizedError: 認證失敗
            DataFormatError: 資料格式錯誤
            
        使用範例:
            >>> from broker_client import Order, OrderSide, OrderType
            >>> 
            >>> order = Order(
            ...     symbol="2330",
            ...     side=OrderSide.BUY,
            ...     order_type=OrderType.LIMIT,
            ...     quantity=1000,
            ...     price=500.0
            ... )
            >>> order_id = client.placeOrder(order)
            >>> print(f"訂單已提交，ID: {order_id}")
        """
        self._logger.info(f"提交訂單: {order.symbol} {order.side.value} {order.quantity}@{order.price}")
        
        try:
            # 驗證訂單資料
            self._validate_order(order)
            
            # 準備訂單資料
            order_data = {
                'symbol': order.symbol,
                'side': order.side.value,
                'type': order.order_type.value,
                'quantity': order.quantity,
                'price': order.price,
                'stop_price': order.stop_price,
                'time_in_force': order.time_in_force
            }
            
            # TODO: 實際實作時需要呼叫真實 API
            # response = self._make_authenticated_request('/orders', 'POST', order_data)
            
            # 模擬回應
            import uuid
            import random
            mock_order_id = f"ORD{int(time.time())}{random.randint(1000, 9999)}"
            
            # 更新訂單 ID
            order.order_id = mock_order_id
            
            self._logger.info(f"訂單提交成功，ID: {mock_order_id}")
            
            # 模擬訂單狀態更新回調
            self._simulate_order_status_update(mock_order_id, order)
            
            return mock_order_id
            
        except OrderError:
            raise
        except (NetworkError, UnauthorizedError, ForbiddenError, DataFormatError):
            raise
        except Exception as e:
            raise OrderError(f"下單失敗: {str(e)}")

    def _validate_order(self, order: Order) -> None:
        """驗證訂單資料"""
        if not order.symbol:
            raise OrderError("股票代號不能為空")
        
        if order.quantity <= 0:
            raise OrderError("數量必須大於 0")
        
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            if order.price is None or order.price <= 0:
                raise OrderError("限價單必須指定有效價格")
        
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if order.stop_price is None or order.stop_price <= 0:
                raise OrderError("停損單必須指定有效停損價格")

    def _simulate_order_status_update(self, order_id: str, order: Order) -> None:
        """模擬訂單狀態更新"""
        def delayed_update():
            time.sleep(1)  # 模擬延遲
            
            status_info = OrderStatusInfo(
                order_id=order_id,
                status=OrderStatus.SUBMITTED,
                filled_quantity=0,
                remaining_quantity=order.quantity,
                avg_price=0.0,
                last_update=datetime.now(),
                message="訂單已提交"
            )
            
            # 通知回調函數
            for callback in self._order_callbacks:
                try:
                    callback(status_info)
                except Exception as e:
                    self._logger.error(f"訂單回調錯誤: {e}")
        
        # 在背景執行緒中執行
        Thread(target=delayed_update, daemon=True).start()

    def queryOrderStatus(self, order_id: str) -> OrderStatusInfo:
        """
        查詢訂單狀態
        
        參數:
            order_id (str): 訂單 ID
            
        返回:
            OrderStatusInfo: 訂單狀態資訊
            
        異常:
            OrderError: 訂單不存在或查詢失敗
            NetworkError: 網路連線錯誤
            UnauthorizedError: 認證失敗
            
        使用範例:
            >>> order_id = client.placeOrder(order)
            >>> status = client.queryOrderStatus(order_id)
            >>> print(f"訂單狀態: {status.status.value}")
            >>> print(f"已成交: {status.filled_quantity}/{status.filled_quantity + status.remaining_quantity}")
        """
        self._logger.info(f"查詢訂單狀態: {order_id}")
        
        try:
            # TODO: 實際實作時需要呼叫真實 API
            # response = self._make_authenticated_request(f'/orders/{order_id}')
            
            # 模擬回應
            import random
            
            mock_status = OrderStatusInfo(
                order_id=order_id,
                status=random.choice(list(OrderStatus)),
                filled_quantity=random.randint(0, 1000),
                remaining_quantity=random.randint(0, 1000),
                avg_price=random.uniform(100, 600),
                last_update=datetime.now(),
                message="模擬訂單狀態"
            )
            
            return mock_status
            
        except (NetworkError, UnauthorizedError, ForbiddenError, DataFormatError):
            raise
        except Exception as e:
            raise OrderError(f"查詢訂單狀態失敗: {str(e)}")

    def onOrderCallback(self, callback: Callable[[OrderStatusInfo], None]) -> None:
        """
        註冊訂單狀態更新回調函數
        
        參數:
            callback (Callable[[OrderStatusInfo], None]): 
                接收 OrderStatusInfo 物件的回調函數
                
        使用範例:
            >>> def handle_order_update(status):
            ...     print(f"訂單 {status.order_id} 狀態更新: {status.status.value}")
            ...     if status.status == OrderStatus.FILLED:
            ...         print(f"完全成交，平均價格: {status.avg_price}")
            >>> 
            >>> client = BrokerClient()
            >>> client.onOrderCallback(handle_order_update)
        """
        if not callable(callback):
            raise ValueError("回調函數必須是可呼叫的")
            
        self._order_callbacks.append(callback)
        self._logger.info("已註冊訂單回調函數")

    def onDealCallback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        註冊成交回調函數
        
        參數:
            callback (Callable[[Dict[str, Any]], None]): 
                接收成交資訊字典的回調函數
                
        使用範例:
            >>> def handle_deal(deal):
            ...     print(f"成交通知: {deal['symbol']} {deal['quantity']}股 @ {deal['price']}")
            >>> 
            >>> client = BrokerClient()
            >>> client.onDealCallback(handle_deal)
        """
        if not callable(callback):
            raise ValueError("回調函數必須是可呼叫的")
            
        self._deal_callbacks.append(callback)
        self._logger.info("已註冊成交回調函數")

    def getAccountBalance(self) -> AccountBalance:
        """
        取得帳戶餘額資訊
        
        返回:
            AccountBalance: 帳戶餘額和資產資訊
            
        異常:
            NetworkError: 網路連線錯誤
            UnauthorizedError: 認證失敗
            DataFormatError: 資料格式錯誤
            
        使用範例:
            >>> client = BrokerClient()
            >>> balance = client.getAccountBalance()
            >>> print(f"現金餘額: ${balance.cash_balance:,.2f}")
            >>> print(f"可用資金: ${balance.buying_power:,.2f}")
            >>> print(f"總資產: ${balance.total_value:,.2f}")
        """
        self._logger.info("查詢帳戶餘額")
        
        try:
            # TODO: 實際實作時需要呼叫真實 API
            # response = self._make_authenticated_request('/account/balance')
            
            # 模擬回應
            import random
            
            cash_balance = random.uniform(100000, 1000000)
            unrealized_pnl = random.uniform(-50000, 100000)
            
            mock_balance = AccountBalance(
                cash_balance=cash_balance,
                buying_power=cash_balance * 0.8,
                total_value=cash_balance + unrealized_pnl,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=random.uniform(-10000, 50000),
                margin_used=random.uniform(0, 200000),
                margin_available=cash_balance * 0.6
            )
            
            return mock_balance
            
        except (NetworkError, UnauthorizedError, ForbiddenError, DataFormatError):
            raise
        except Exception as e:
            raise NetworkError(f"查詢帳戶餘額失敗: {str(e)}")

    def unsubscribeTick(self, symbol: str) -> None:
        """
        取消訂閱股票報價
        
        參數:
            symbol (str): 股票代號
            
        異常:
            SubscriptionError: 取消訂閱失敗
        """
        if symbol in self._subscribed_symbols:
            del self._subscribed_symbols[symbol]
            self._logger.info(f"已取消訂閱 {symbol}")
        else:
            raise SubscriptionError(f"股票 {symbol} 未訂閱")

    def getSubscribedSymbols(self) -> List[str]:
        """
        取得已訂閱的股票代號清單
        
        返回:
            List[str]: 已訂閱的股票代號清單
        """
        return list(self._subscribed_symbols.keys())

    def close(self) -> None:
        """
        關閉客戶端，清理資源
        """
        self._logger.info("關閉 BrokerClient")
        
        # 停止訂閱執行緒
        self._subscription_stop_event.set()
        if self._subscription_thread and self._subscription_thread.is_alive():
            self._subscription_thread.join(timeout=5.0)
        
        # 清空訂閱
        self._subscribed_symbols.clear()
        
        # 登出認證
        self._auth.logout()

    def __enter__(self):
        """支援 context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支援 context manager"""
        self.close()