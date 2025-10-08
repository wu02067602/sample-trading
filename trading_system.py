"""交易系統主程式模組

此模組負責控制整個交易流程的協調與管理。
"""

import shioaji as sj
from typing import Optional, Any, Dict, List
from datetime import datetime
import logging
import time as time_module

from login import Login
from contract import ContractManager
from market_scanner import MarketScanner
from strategy_data_preparer import StrategyDataPreparer
from quote_subscriber import QuoteSubscriber
from quote_callback import QuoteCallback
from strategy import MomentumStrategy, TradingSignal
from order_executor import OrderExecutor
from trade_monitor import TradeMonitor
from account_manager import AccountManager
from config import Config


class TradingSystem:
    """交易系統主程式
    
    此類別負責控制整個交易流程的協調與管理，
    整合登入、商品檔、市場掃描、策略執行、下單與帳戶管理等功能。
    """
    
    def __init__(self) -> None:
        """初始化交易系統"""
        self._login: Optional[Login] = None
        self._contract_manager: Optional[ContractManager] = None
        self._market_scanner: Optional[MarketScanner] = None
        self._strategy_data_preparer: Optional[StrategyDataPreparer] = None
        self._quote_subscriber: Optional[QuoteSubscriber] = None
        self._quote_callback: Optional[QuoteCallback] = None
        self._strategy: Optional[MomentumStrategy] = None
        self._order_executor: Optional[OrderExecutor] = None
        self._trade_monitor: Optional[TradeMonitor] = None
        self._account_manager: Optional[AccountManager] = None
        
        self._api: Optional[sj.Shioaji] = None
        self._is_initialized: bool = False
        self._subscribed_stocks: List[str] = []
        self._executed_trades: List[Any] = []
        
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize(self, config: Config) -> None:
        """初始化系統並登入
        
        Args:
            api_key (str): API 金鑰
            secret_key (str): API 密鑰
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(config)
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            RuntimeError: 當系統已初始化時
        """
        if self._is_initialized:
            raise RuntimeError("系統已初始化")
        
        self._logger.info("開始初始化交易系統...")
        
        # 步驟 1: 登入
        self._login_to_system(config)
        
        # 步驟 2: 取得商品檔
        self._fetch_contracts()
        
        # 步驟 3: 初始化其他模組
        self._initialize_modules()
        
        self._is_initialized = True
        self._logger.info("交易系統初始化完成")
    
    def _login_to_system(self, config: Config) -> None:
        """登入系統（內部方法）
        
        Args:
            config (Config): 配置物件
        
        Raises:
            ValueError: 當登入參數無效時
            ConnectionError: 當無法連線時
        """
        self._logger.info("步驟 1/3: 執行登入...")
        
        self._login = Login(config)
        self._api = self._login.login()
        
        self._logger.info("登入成功")
    
    def _fetch_contracts(self) -> None:
        """取得商品檔（內部方法）
        
        Raises:
            RuntimeError: 當尚未登入時
            ConnectionError: 當無法取得商品檔時
        """
        if self._api is None:
            raise RuntimeError("尚未登入，請先執行登入")
        
        self._logger.info("步驟 2/3: 取得商品檔...")
        
        self._contract_manager = ContractManager(self._api)
        self._contract_manager.fetch_contracts()
        
        self._logger.info("商品檔取得完成")
    
    def _initialize_modules(self) -> None:
        """初始化其他模組（內部方法）
        
        Raises:
            RuntimeError: 當尚未登入時
        """
        if self._api is None:
            raise RuntimeError("尚未登入，請先執行登入")
        
        self._logger.info("步驟 3/3: 初始化其他模組...")
        
        # 初始化市場掃描器
        self._market_scanner = MarketScanner(self._api)
        
        # 初始化報價相關模組
        self._quote_callback = QuoteCallback(self._api)
        self._quote_subscriber = QuoteSubscriber(self._api)
        
        # 初始化策略數據準備器
        self._strategy_data_preparer = StrategyDataPreparer(
            self._market_scanner,
            self._quote_callback
        )
        
        # 初始化交易策略
        self._strategy = MomentumStrategy(self._quote_callback)
        
        # 初始化下單執行器
        self._order_executor = OrderExecutor(self._api)
        
        # 初始化交易監控
        self._trade_monitor = TradeMonitor(self._api)
        
        # 初始化帳戶管理
        self._account_manager = AccountManager(self._api)
        
        self._logger.info("所有模組初始化完成")
    
    def get_market_ranking(self, count: int = 100) -> List[Any]:
        """取得市場交易狀況排行
        
        Args:
            count (int): 排行數量，範圍 0-200，預設為 100
        
        Returns:
            List[Any]: 市場排行列表
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(config)
            >>> ranking = system.get_market_ranking(count=50)
        
        Raises:
            RuntimeError: 當系統尚未初始化時
            ValueError: 當 count 不在有效範圍內時
            ConnectionError: 當無法取得市場排行時
        """
        if not self._is_initialized:
            raise RuntimeError("系統尚未初始化，請先執行 initialize()")
        
        self._logger.info(f"取得市場交易狀況排行（前 {count} 名）...")
        
        ranking = self._market_scanner.get_change_percent_rank(count=count)
        
        self._logger.info(f"取得 {len(ranking)} 筆市場排行資料")
        return ranking
    
    def start_data_preparation(self, interval_seconds: int = 600, count: int = 100) -> None:
        """啟動策略數據準備
        
        使用策略數據準備功能，定期取得市場交易狀況排行。
        
        Args:
            interval_seconds (int): 更新間隔（秒），預設為 600 秒（10 分鐘）
            count (int): 每次取得的排行數量，預設為 100
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(config)
            >>> system.start_data_preparation(interval_seconds=600, count=50)
        
        Raises:
            RuntimeError: 當系統尚未初始化時
            ValueError: 當參數無效時
        """
        if not self._is_initialized:
            raise RuntimeError("系統尚未初始化，請先執行 initialize()")
        
        self._logger.info(f"啟動策略數據準備（間隔 {interval_seconds} 秒）...")
        
        self._strategy_data_preparer.set_update_interval(interval_seconds)
        self._strategy_data_preparer.start_auto_update(count=count)
        
        self._logger.info("策略數據準備已啟動")
    
    def subscribe_stocks_by_change_percent(
        self, 
        threshold: float = 4.0,
        count: int = 100
    ) -> List[str]:
        """訂閱漲幅超過閾值的股票報價
        
        從市場交易狀況排行中，找出漲幅大於閾值的股票並訂閱其報價。
        
        Args:
            threshold (float): 漲幅閾值（百分比），預設為 4.0
            count (int): 檢查的排行數量，預設為 100
        
        Returns:
            List[str]: 已訂閱的股票代碼列表
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(config)
            >>> subscribed = system.subscribe_stocks_by_change_percent(threshold=4.0)
        
        Raises:
            RuntimeError: 當系統尚未初始化時
            ValueError: 當參數無效時
            ConnectionError: 當訂閱失敗時
        """
        if not self._is_initialized:
            raise RuntimeError("系統尚未初始化，請先執行 initialize()")
        
        self._logger.info(f"檢查市場排行，訂閱漲幅 > {threshold}% 的股票...")
        
        # 取得市場排行
        ranking = self.get_market_ranking(count=count)
        
        subscribed_count = 0
        for stock in ranking:
            try:
                # 檢查是否有漲跌幅屬性
                change_percent = getattr(stock, 'change_percent', None)
                if change_percent is None:
                    continue
                
                # 如果漲幅大於閾值且尚未訂閱
                if change_percent > threshold and stock.code not in self._subscribed_stocks:
                    # 取得股票合約
                    contract = self._contract_manager.get_stock(stock.code)
                    if contract is not None:
                        # 訂閱報價
                        success = self._quote_subscriber.subscribe(contract)
                        if success:
                            self._subscribed_stocks.append(stock.code)
                            subscribed_count += 1
                            self._logger.info(
                                f"訂閱股票 {stock.code}（漲幅 {change_percent:.2f}%）"
                            )
            
            except AttributeError as e:
                self._logger.warning(f"無法處理股票資料: {e}")
                continue
        
        self._logger.info(f"共訂閱 {subscribed_count} 支股票報價")
        return self._subscribed_stocks.copy()
    
    def register_signal_handler(self, handler: Optional[callable] = None) -> None:
        """註冊交易訊號處理器
        
        當策略產生交易訊號時，會觸發此處理器。
        如果不提供 handler，則使用預設的下單處理器。
        
        Args:
            handler (Optional[callable]): 自訂的訊號處理函數，
                                         接收 TradingSignal 作為參數
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(config)
            >>> system.register_signal_handler()  # 使用預設處理器
        
        Raises:
            RuntimeError: 當系統尚未初始化時
            ValueError: 當 handler 不是可呼叫的函數時
        """
        if not self._is_initialized:
            raise RuntimeError("系統尚未初始化，請先執行 initialize()")
        
        if handler is None:
            # 使用預設的訊號處理器
            handler = self._default_signal_handler
        elif not callable(handler):
            raise ValueError("Handler 必須是可呼叫的函數")
        
        self._strategy.register_signal_callback(handler)
        self._logger.info("交易訊號處理器已註冊")
    
    def _default_signal_handler(self, signal: TradingSignal) -> None:
        """預設的交易訊號處理器（內部方法）
        
        Args:
            signal (TradingSignal): 交易訊號
        """
        self._logger.info(f"收到交易訊號: {signal}")
        
        try:
            # 執行下單
            trade = self._execute_order(signal)
            
            if trade is not None:
                # 監控委託狀態
                self._monitor_order_status(trade)
                
                # 監控成交狀態
                self._monitor_deal_status(trade)
        
        except (ValueError, ConnectionError, RuntimeError) as e:
            self._logger.error(f"處理訊號時發生錯誤: {e}")
    
    def _execute_order(self, signal: TradingSignal) -> Optional[Any]:
        """執行下單（內部方法）
        
        Args:
            signal (TradingSignal): 交易訊號
        
        Returns:
            Optional[Any]: Trade 物件，如果下單失敗則返回 None
        """
        self._logger.info(f"執行下單: {signal.code} {signal.action} @ {signal.price}")
        
        try:
            # 取得股票合約
            contract = self._contract_manager.get_stock(signal.code)
            if contract is None:
                self._logger.error(f"無法取得股票 {signal.code} 的合約")
                return None
            
            # 執行下單
            trade = self._order_executor.place_stock_order(
                contract=contract,
                action=signal.action,
                price=signal.price,
                quantity=signal.quantity,
                order_type='ROD',
                price_type='LMT'
            )
            
            self._executed_trades.append(trade)
            self._logger.info(f"下單成功: 訂單 ID {trade.status.id}")
            
            return trade
        
        except (ValueError, ConnectionError, RuntimeError) as e:
            self._logger.error(f"下單失敗: {e}")
            return None
    
    def _monitor_order_status(
        self, 
        trade: Any, 
        max_wait_seconds: int = 300,
        check_interval: int = 5
    ) -> bool:
        """監控委託回報狀態（內部方法）
        
        Args:
            trade (Any): Trade 物件
            max_wait_seconds (int): 最大等待時間（秒），預設為 300 秒
            check_interval (int): 檢查間隔（秒），預設為 5 秒
        
        Returns:
            bool: 委託是否成功
        """
        self._logger.info(f"開始監控委託回報（訂單 ID: {trade.status.id}）...")
        
        start_time = time_module.time()
        
        while True:
            # 檢查是否超時
            if time_module.time() - start_time > max_wait_seconds:
                self._logger.warning(f"監控委託回報超時（訂單 ID: {trade.status.id}）")
                return False
            
            # 更新訂單狀態
            try:
                self._trade_monitor.update_status()
                
                # 查詢訂單
                current_trade = self._trade_monitor.get_trade_by_id(trade.status.id)
                
                if current_trade is not None:
                    status = current_trade.status.status
                    
                    if status == 'Filled':
                        self._logger.info(f"委託已完全成交（訂單 ID: {trade.status.id}）")
                        return True
                    elif status in ['Cancelled', 'Failed']:
                        self._logger.warning(f"委託失敗或已取消（訂單 ID: {trade.status.id}）")
                        return False
                    else:
                        self._logger.debug(f"委託狀態: {status}")
            
            except (ConnectionError, RuntimeError) as e:
                self._logger.warning(f"更新訂單狀態時發生錯誤: {e}")
            
            # 等待一段時間再檢查
            time_module.sleep(check_interval)
    
    def _monitor_deal_status(
        self, 
        trade: Any,
        max_wait_seconds: int = 300,
        check_interval: int = 5
    ) -> bool:
        """監控成交回報狀態（內部方法）
        
        Args:
            trade (Any): Trade 物件
            max_wait_seconds (int): 最大等待時間（秒），預設為 300 秒
            check_interval (int): 檢查間隔（秒），預設為 5 秒
        
        Returns:
            bool: 成交是否成功
        """
        self._logger.info(f"開始監控成交回報（訂單 ID: {trade.status.id}）...")
        
        start_time = time_module.time()
        
        while True:
            # 檢查是否超時
            if time_module.time() - start_time > max_wait_seconds:
                self._logger.warning(f"監控成交回報超時（訂單 ID: {trade.status.id}）")
                return False
            
            # 查詢成交明細
            try:
                deals = self._trade_monitor.get_deals(trade)
                
                if deals and len(deals) > 0:
                    total_quantity = sum(deal.quantity for deal in deals)
                    self._logger.info(
                        f"成交明細: 訂單 ID {trade.status.id}，"
                        f"共 {len(deals)} 筆成交，總數量 {total_quantity}"
                    )
                    return True
            
            except (ConnectionError, RuntimeError) as e:
                self._logger.warning(f"查詢成交回報時發生錯誤: {e}")
            
            # 等待一段時間再檢查
            time_module.sleep(check_interval)
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """產生當日交易摘要報表
        
        Returns:
            Dict[str, Any]: 交易摘要報表
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(api_key="...", secret_key="...")
            >>> # ... 執行交易 ...
            >>> report = system.generate_daily_report()
            >>> print(report)
        
        Raises:
            RuntimeError: 當系統尚未初始化時
        """
        if not self._is_initialized:
            raise RuntimeError("系統尚未初始化，請先執行 initialize()")
        
        self._logger.info("產生當日交易摘要報表...")
        
        # 取得所有訊號
        signals = self._strategy.get_signals()
        
        # 取得所有交易
        trades = self._executed_trades
        
        # 取得帳戶資訊
        try:
            positions = self._account_manager.list_positions()
            position_summary = self._account_manager.get_position_summary()
        except (ConnectionError, RuntimeError):
            positions = []
            position_summary = {}
        
        # 建立報表
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_signals': len(signals),
                'total_trades': len(trades),
                'subscribed_stocks': len(self._subscribed_stocks),
                'current_positions': len(positions),
                'total_unrealized_pnl': position_summary.get('total_unrealized_pnl', 0.0)
            },
            'signals': [
                {
                    'code': signal.code,
                    'action': signal.action,
                    'price': signal.price,
                    'quantity': signal.quantity,
                    'reason': signal.reason,
                    'timestamp': signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
                for signal in signals
            ],
            'trades': [
                {
                    'order_id': trade.status.id,
                    'code': trade.contract.code,
                    'action': trade.order.action,
                    'price': trade.order.price,
                    'quantity': trade.order.quantity,
                    'status': trade.status.status
                }
                for trade in trades
            ],
            'positions': [
                {
                    'code': position.code,
                    'quantity': position.quantity,
                    'price': getattr(position, 'price', 0),
                    'pnl': getattr(position, 'pnl', 0)
                }
                for position in positions
            ]
        }
        
        self._logger.info("交易摘要報表已產生")
        return report
    
    def print_daily_report(self) -> None:
        """輸出當日交易摘要報表
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(api_key="...", secret_key="...")
            >>> # ... 執行交易 ...
            >>> system.print_daily_report()
        
        Raises:
            RuntimeError: 當系統尚未初始化時
        """
        report = self.generate_daily_report()
        
        print("\n" + "=" * 80)
        print(f"交易摘要報表 - {report['date']}")
        print("=" * 80)
        
        print("\n【摘要統計】")
        summary = report['summary']
        print(f"  交易訊號數: {summary['total_signals']}")
        print(f"  執行交易數: {summary['total_trades']}")
        print(f"  訂閱股票數: {summary['subscribed_stocks']}")
        print(f"  當前持倉數: {summary['current_positions']}")
        print(f"  未實現損益: {summary['total_unrealized_pnl']:.2f}")
        
        if report['signals']:
            print("\n【交易訊號】")
            for i, signal in enumerate(report['signals'], 1):
                print(f"  {i}. {signal['code']} {signal['action']} @ {signal['price']}")
                print(f"     原因: {signal['reason']}")
                print(f"     時間: {signal['timestamp']}")
        
        if report['trades']:
            print("\n【執行交易】")
            for i, trade in enumerate(report['trades'], 1):
                print(f"  {i}. 訂單 {trade['order_id']}: {trade['code']} {trade['action']} "
                      f"@ {trade['price']} x {trade['quantity']} ({trade['status']})")
        
        if report['positions']:
            print("\n【當前持倉】")
            for i, position in enumerate(report['positions'], 1):
                print(f"  {i}. {position['code']}: {position['quantity']} 張 "
                      f"@ {position['price']:.2f} (損益: {position['pnl']:.2f})")
        
        print("\n" + "=" * 80)
    
    def shutdown(self) -> None:
        """關閉交易系統
        
        Examples:
            >>> system = TradingSystem()
            >>> system.initialize(api_key="...", secret_key="...")
            >>> # ... 執行交易 ...
            >>> system.shutdown()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._logger.info("關閉交易系統...")
        
        # 停止策略數據準備
        if self._strategy_data_preparer is not None:
            try:
                self._strategy_data_preparer.stop_auto_update()
            except Exception as e:
                self._logger.warning(f"停止策略數據準備時發生錯誤: {e}")
        
        # 登出
        if self._login is not None:
            try:
                self._login.logout()
            except Exception as e:
                self._logger.warning(f"登出時發生錯誤: {e}")
        
        self._is_initialized = False
        self._logger.info("交易系統已關閉")
