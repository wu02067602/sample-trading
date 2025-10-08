from trading_system import TradingSystem
from config import Config
from threading import Event

system = TradingSystem()
config = Config()
system.initialize(
    config=config
)
system.start_data_preparation(
    interval_seconds=10,
    count=100
)
system.subscribe_stocks_by_change_percent(
    threshold=4.0,
    count=100
)
system.register_signal_handler()
try:
    Event().wait()
except KeyboardInterrupt:
    system.print_daily_report()
    system.shutdown()