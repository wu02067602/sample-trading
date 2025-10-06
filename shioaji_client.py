"""
Shioaji 交易客戶端模組

此模組提供與永豐金證券 Shioaji API 的整合介面，用於量化交易系統。
"""

import shioaji as sj
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

from trading_interface import ITradingClient, IConfigValidator


@dataclass
class LoginConfig(IConfigValidator):
    """
    登入配置資料類別
    
    Attributes:
        person_id: 使用者身分證字號或統一編號
        passwd: 使用者密碼
        ca_path: CA 憑證路徑（可選）
        ca_passwd: CA 憑證密碼（可選）
        simulation: 是否使用模擬環境，預設為 False
    
    Examples:
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password"
        ... )
    """
    person_id: str
    passwd: str
    ca_path: Optional[str] = None
    ca_passwd: Optional[str] = None
    simulation: bool = False
    
    def validate(self) -> None:
        """
        驗證配置參數的有效性
        
        Raises:
            ValueError: 當必要的參數缺失或無效時
        
        Examples:
            >>> config = LoginConfig(person_id="", passwd="password")
            >>> config.validate()  # 會拋出 ValueError
        """
        if not self.person_id or not self.person_id.strip():
            raise ValueError("person_id 不可為空")
        if not self.passwd or not self.passwd.strip():
            raise ValueError("passwd 不可為空")
        if self.ca_path and not self.ca_passwd:
            raise ValueError("提供 ca_path 時必須同時提供 ca_passwd")
        if self.ca_passwd and not self.ca_path:
            raise ValueError("提供 ca_passwd 時必須同時提供 ca_path")


class ShioajiClient(ITradingClient):
    """
    Shioaji 交易客戶端
    
    此類別封裝了 Shioaji API 的登入、登出等基本功能，
    並提供統一的介面供量化交易系統使用。
    
    Attributes:
        sj: Shioaji API 實例，登入成功後可用於後續交易操作
        is_logged_in: 登入狀態標記
        config: 登入配置資訊
    
    Examples:
        基本登入範例：
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password"
        ... )
        >>> client = ShioajiClient()
        >>> client.login(config)
        >>> # 使用 client.sj 進行後續操作
        >>> client.logout()
        
        使用 CA 憑證登入：
        >>> config = LoginConfig(
        ...     person_id="A123456789",
        ...     passwd="your_password",
        ...     ca_path="/path/to/cert.pfx",
        ...     ca_passwd="cert_password"
        ... )
        >>> client = ShioajiClient()
        >>> client.login(config)
    
    Raises:
        ValueError: 當登入參數不正確時
        ConnectionError: 當連線失敗時
        RuntimeError: 當登入過程發生錯誤時
    """
    
    def __init__(self):
        """
        初始化 Shioaji 客戶端
        
        建立 Shioaji API 實例並設定日誌記錄器。
        
        Examples:
            >>> client = ShioajiClient()
        """
        self.sj: Optional[sj.Shioaji] = None
        self.is_logged_in: bool = False
        self.config: Optional[LoginConfig] = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self, config: LoginConfig) -> bool:
        """
        連接到 Shioaji 交易系統（實作 ITradingClient.connect）
        
        此方法為 login 的別名，遵循介面定義。
        
        Args:
            config: LoginConfig 登入配置物件
        
        Returns:
            bool: 連線成功返回 True，失敗返回 False
        
        Raises:
            ValueError: 當配置參數無效時
            ConnectionError: 當連線失敗時
            RuntimeError: 當發生其他錯誤時
        
        Examples:
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client = ShioajiClient()
            >>> client.connect(config)
        """
        return self.login(config)
    
    def login(self, config: LoginConfig) -> bool:
        """
        執行登入操作
        
        根據提供的配置進行登入。如果提供了 CA 憑證資訊，
        將使用憑證登入；否則使用基本帳號密碼登入。
        
        Args:
            config: LoginConfig 登入配置物件
        
        Returns:
            bool: 登入成功返回 True，失敗返回 False
        
        Raises:
            ValueError: 當必要的登入參數缺失時
            ConnectionError: 當無法連接到 Shioaji 伺服器時
            RuntimeError: 當登入過程發生其他錯誤時
        
        Examples:
            基本登入：
            >>> config = LoginConfig(
            ...     person_id="A123456789",
            ...     passwd="your_password"
            ... )
            >>> client = ShioajiClient()
            >>> success = client.login(config)
            >>> print(f"登入狀態: {success}")
            
            CA 憑證登入：
            >>> config = LoginConfig(
            ...     person_id="A123456789",
            ...     passwd="your_password",
            ...     ca_path="/path/to/cert.pfx",
            ...     ca_passwd="cert_password"
            ... )
            >>> success = client.login(config)
        """
        try:
            # 驗證配置參數
            config.validate()
            
            # 建立 Shioaji 實例
            self.sj = sj.Shioaji(simulation=config.simulation)
            self.logger.info(f"開始登入 Shioaji API (模擬模式: {config.simulation})")
            
            # 執行登入
            accounts = self.sj.login(
                person_id=config.person_id,
                passwd=config.passwd
            )
            
            self.logger.info(f"登入成功，取得 {len(accounts)} 個帳戶")
            
            # 如果提供了 CA 憑證，進行憑證啟用
            if config.ca_path and config.ca_passwd:
                self.logger.info("開始啟用 CA 憑證")
                self.sj.activate_ca(
                    ca_path=config.ca_path,
                    ca_passwd=config.ca_passwd,
                    person_id=config.person_id
                )
                self.logger.info("CA 憑證啟用成功")
            
            # 更新狀態
            self.is_logged_in = True
            self.config = config
            
            return True
            
        except ValueError as e:
            self.logger.error(f"登入參數錯誤: {e}")
            raise
        except ConnectionError as e:
            self.logger.error(f"連線失敗: {e}")
            raise
        except Exception as e:
            self.logger.error(f"登入過程發生錯誤: {e}")
            raise RuntimeError(f"登入失敗: {e}") from e
    
    def disconnect(self) -> bool:
        """
        斷開與 Shioaji 交易系統的連線（實作 ITradingClient.disconnect）
        
        此方法為 logout 的別名，遵循介面定義。
        
        Returns:
            bool: 斷線成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未連線或斷線過程發生錯誤時
        
        Examples:
            >>> client.disconnect()
        """
        return self.logout()
    
    def logout(self) -> bool:
        """
        執行登出操作
        
        關閉與 Shioaji 伺服器的連線。為了維持良好的服務品質，
        建議在不使用時主動登出。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未登入或登出過程發生錯誤時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> # 執行交易操作...
            >>> client.logout()
            >>> print(f"登出狀態: {not client.is_logged_in}")
        """
        try:
            if not self.is_logged_in or self.sj is None:
                raise RuntimeError("尚未登入，無法執行登出操作")
            
            self.logger.info("開始登出 Shioaji API")
            result = self.sj.logout()
            
            # 重置狀態
            self.is_logged_in = False
            self.sj = None
            
            self.logger.info("登出成功")
            return result
            
        except Exception as e:
            self.logger.error(f"登出過程發生錯誤: {e}")
            raise RuntimeError(f"登出失敗: {e}") from e
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        取得帳戶資訊
        
        Returns:
            Dict[str, Any]: 包含股票帳戶和期貨帳戶的字典
        
        Raises:
            RuntimeError: 當尚未登入時
        
        Examples:
            >>> client = ShioajiClient()
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> accounts = client.get_accounts()
            >>> print(accounts['stock_account'])
            >>> print(accounts['futopt_account'])
        """
        if not self.is_logged_in or self.sj is None:
            raise RuntimeError("尚未登入，無法取得帳戶資訊")
        
        return {
            'stock_account': self.sj.stock_account,
            'futopt_account': self.sj.futopt_account
        }
    
    def __enter__(self):
        """
        支援 context manager 的進入方法
        
        Returns:
            ShioajiClient: 客戶端實例本身
        
        Examples:
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> with ShioajiClient() as client:
            ...     client.login(config)
            ...     # 執行交易操作
            ...     # 自動登出
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支援 context manager 的退出方法，自動登出
        
        Args:
            exc_type: 例外類型
            exc_val: 例外值
            exc_tb: 例外追蹤資訊
        """
        if self.is_logged_in:
            try:
                self.logout()
            except Exception as e:
                self.logger.error(f"自動登出時發生錯誤: {e}")
    
    def is_connected(self) -> bool:
        """
        檢查是否已連線到 Shioaji 系統（實作 ITradingClient.is_connected）
        
        Returns:
            bool: 已連線返回 True，未連線返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> print(client.is_connected())  # False
            >>> config = LoginConfig(person_id="A123456789", passwd="password")
            >>> client.login(config)
            >>> print(client.is_connected())  # True
        """
        return self.is_logged_in and self.sj is not None
