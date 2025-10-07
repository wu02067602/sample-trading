"""
永豐證券 Shioaji 券商介面模組

此模組提供與永豐證券 Shioaji SDK 的整合介面。
"""

import logging
from typing import Optional
import shioaji as sj
from .callback_handler_interface import ICallbackHandler


class ShioajiBroker:
    """
    永豐證券券商介面
    
    負責與永豐證券 Shioaji SDK 進行連線、登入及設定委託回報。
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        初始化永豐證券券商介面
        
        Args:
            logger (logging.Logger): 日誌記錄器，如果為 None 則使用預設記錄器
        """
        self._api: Optional[sj.Shioaji] = None
        self._order_handler: Optional[ICallbackHandler] = None
        self._is_connected: bool = False
        self._logger = logger or logging.getLogger(__name__)
    
    def connect(self, api_key: str, secret_key: str, simulation: bool = True) -> None:
        """
        連線到永豐證券
        
        Args:
            api_key (str): API 金鑰
            secret_key (str): 密鑰
            simulation (bool): 是否使用模擬環境，預設為 True
        
        Examples:
            >>> broker = ShioajiBroker()
            >>> broker.connect("your_api_key", "your_secret_key", simulation=True)
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空時
            ConnectionError: 當連線失敗時
        """
        if not api_key or not secret_key:
            raise ValueError("API key and secret key must not be empty")
        
        try:
            self._api = sj.Shioaji(simulation=simulation)
            self._api.login(
                api_key=api_key,
                secret_key=secret_key
            )
            self._is_connected = True
            self._logger.info(f"Successfully connected to Shioaji (simulation={simulation})")
        except (ConnectionError, TimeoutError) as e:
            self._logger.error(f"Failed to connect to Shioaji: {e}", exc_info=True)
            raise ConnectionError(f"Failed to connect to Shioaji: {e}")
        except (ValueError, KeyError) as e:
            self._logger.error(f"Invalid credentials: {e}", exc_info=True)
            raise ValueError(f"Invalid API credentials: {e}")
    
    def disconnect(self) -> None:
        """
        斷開與永豐證券的連線
        
        Examples:
            >>> broker = ShioajiBroker()
            >>> broker.connect("key", "secret")
            >>> broker.disconnect()
        
        Raises:
            RuntimeError: 當尚未連線時
        """
        if not self._is_connected or self._api is None:
            raise RuntimeError("Not connected to Shioaji")
        
        try:
            self._api.logout()
            self._is_connected = False
            self._api = None
            self._logger.info("Successfully disconnected from Shioaji")
        except ConnectionError as e:
            self._logger.error(f"Failed to disconnect from Shioaji: {e}", exc_info=True)
            raise RuntimeError(f"Failed to disconnect from Shioaji: {e}")
    
    def setup_order_callback(self, order_handler: ICallbackHandler) -> None:
        """
        設定委託回報處理器
        
        註冊委託狀態變更和成交回報的回調函數到 Shioaji SDK。
        
        Args:
            order_handler (ICallbackHandler): 委託回報處理器實例
        
        Examples:
            >>> broker = ShioajiBroker()
            >>> broker.connect("key", "secret")
            >>> handler = OrderCallbackHandler()
            >>> broker.setup_order_callback(handler)
        
        Raises:
            RuntimeError: 當尚未連線時
            TypeError: 當 order_handler 類型不正確時
        """
        if not self._is_connected or self._api is None:
            raise RuntimeError("Must connect to Shioaji before setting up callbacks")
        
        if not isinstance(order_handler, ICallbackHandler):
            raise TypeError(f"order_handler must implement ICallbackHandler, got {type(order_handler)}")
        
        self._order_handler = order_handler
        
        # 設定委託狀態回調
        self._api.set_order_callback(order_handler.handle_order_callback)
        
        # 設定成交回報回調
        self._api.set_deal_callback(order_handler.handle_deal_callback)
        
        self._logger.info("Order callback handler successfully set up")
    
    def get_api(self) -> sj.Shioaji:
        """
        取得 Shioaji API 實例
        
        Returns:
            sj.Shioaji: Shioaji API 實例
        
        Examples:
            >>> broker = ShioajiBroker()
            >>> broker.connect("key", "secret")
            >>> api = broker.get_api()
        
        Raises:
            RuntimeError: 當尚未連線時
        """
        if not self._is_connected or self._api is None:
            raise RuntimeError("Not connected to Shioaji")
        
        return self._api
    
    @property
    def is_connected(self) -> bool:
        """
        檢查是否已連線
        
        Returns:
            bool: 是否已連線到永豐證券
        
        Examples:
            >>> broker = ShioajiBroker()
            >>> broker.is_connected
            False
            >>> broker.connect("key", "secret")
            >>> broker.is_connected
            True
        """
        return self._is_connected
