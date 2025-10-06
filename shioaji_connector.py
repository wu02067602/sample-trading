"""
Shioaji 交易連線管理模組

此模組提供永豐金證券 Shioaji API 的連線管理功能，
包含登入、登出以及連線狀態管理。

Author: Trading System Team
Date: 2025-10-06
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import shioaji as sj
except ImportError:
    sj = None
    logging.warning("Shioaji module not installed. Please install it using: pip install shioaji")


class ShioajiConnector:
    """
    Shioaji 交易連線管理類別
    
    此類別負責管理與永豐金證券 Shioaji API 的連線，包含登入、
    登出、憑證管理等功能。遵循單一職責原則(SRP)，專注於連線管理。
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        sj (shioaji.Shioaji): Shioaji API 實例，登入成功後可使用
        is_connected (bool): 連線狀態
        login_time (datetime): 登入時間
        
    Examples:
        >>> connector = ShioajiConnector(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET")
        >>> connector.login(person_id="A123456789", passwd="YOUR_PASSWORD")
        >>> if connector.is_connected:
        >>>     print("登入成功")
        >>>     # 使用 connector.sj 進行後續操作
        >>>     connector.logout()
        
    Note:
        - 使用前請確保已安裝 shioaji: pip install shioaji
        - API Key 和 Secret Key 需要從永豐金證券申請
        - 個人 ID 和密碼為證券帳戶的登入憑證
    """
    
    def __init__(self, api_key: str = "", secret_key: str = "", simulation: bool = False):
        """
        初始化 Shioaji 連線器
        
        Args:
            api_key (str, optional): API 金鑰。預設為空字串。
            secret_key (str, optional): 密鑰。預設為空字串。
            simulation (bool, optional): 是否使用模擬環境。預設為 False。
            
        Raises:
            ImportError: 當 shioaji 模組未安裝時拋出
            
        Examples:
            >>> # 正式環境
            >>> connector = ShioajiConnector(api_key="key123", secret_key="secret456")
            >>> 
            >>> # 模擬環境
            >>> connector = ShioajiConnector(simulation=True)
        """
        if sj is None:
            raise ImportError(
                "Shioaji module is not installed. "
                "Please install it using: pip install shioaji"
            )
        
        self.api_key: str = api_key
        self.secret_key: str = secret_key
        self.simulation: bool = simulation
        self.sj: Optional[sj.Shioaji] = None
        self.is_connected: bool = False
        self.login_time: Optional[datetime] = None
        
        # 設置日誌
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 初始化 Shioaji API 實例
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """
        初始化 Shioaji API 實例
        
        此為私有方法，在建構子中調用，負責創建 Shioaji API 物件。
        
        Raises:
            Exception: 當 API 初始化失敗時拋出
        """
        try:
            self.sj = sj.Shioaji(simulation=self.simulation)
            self.logger.info(f"Shioaji API 初始化成功 (模擬環境: {self.simulation})")
        except Exception as e:
            self.logger.error(f"Shioaji API 初始化失敗: {str(e)}")
            raise
    
    def login(
        self,
        person_id: str,
        passwd: str,
        ca_path: Optional[str] = None,
        ca_passwd: Optional[str] = None,
        fetch_contract: bool = True
    ) -> bool:
        """
        登入永豐金證券 Shioaji API
        
        執行登入流程，包含帳號密碼驗證。若提供憑證路徑，
        則會同時進行憑證認證以啟用下單功能。
        
        Args:
            person_id (str): 使用者身分證字號或帳號
            passwd (str): 使用者密碼
            ca_path (str, optional): 憑證檔案路徑 (.pfx 檔案)。預設為 None。
            ca_passwd (str, optional): 憑證密碼。預設為 None。
            fetch_contract (bool, optional): 是否下載合約檔。預設為 True。
            
        Returns:
            bool: 登入成功返回 True，失敗返回 False
            
        Raises:
            ValueError: 當必要參數為空時拋出
            ConnectionError: 當連線失敗時拋出
            AuthenticationError: 當認證失敗時拋出
            
        Examples:
            >>> # 基本登入 (僅查詢功能)
            >>> connector = ShioajiConnector()
            >>> success = connector.login(
            >>>     person_id="A123456789",
            >>>     passwd="your_password"
            >>> )
            >>> 
            >>> # 完整登入 (包含下單功能)
            >>> success = connector.login(
            >>>     person_id="A123456789",
            >>>     passwd="your_password",
            >>>     ca_path="/path/to/cert.pfx",
            >>>     ca_passwd="cert_password"
            >>> )
            
        Note:
            - 僅使用帳號密碼登入只能進行查詢操作
            - 需要下單功能必須提供憑證
            - 憑證檔案(.pfx)需要從永豐金證券官網下載
        """
        if not person_id or not passwd:
            raise ValueError("person_id 和 passwd 不能為空")
        
        if self.sj is None:
            raise ConnectionError("Shioaji API 未初始化")
        
        try:
            # 執行登入
            self.logger.info(f"開始登入 Shioaji API (使用者: {person_id})")
            
            accounts = self.sj.login(
                api_key=self.api_key,
                secret_key=self.secret_key,
                person_id=person_id,
                passwd=passwd,
                fetch_contract=fetch_contract
            )
            
            self.is_connected = True
            self.login_time = datetime.now()
            self.logger.info(f"登入成功！帳戶資訊: {accounts}")
            
            # 如果提供憑證，則啟用下單功能
            if ca_path and ca_passwd:
                self._activate_ca(ca_path, ca_passwd)
            
            return True
            
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"登入失敗: {str(e)}")
            raise ConnectionError(f"Shioaji 登入失敗: {str(e)}")
    
    def _activate_ca(self, ca_path: str, ca_passwd: str) -> None:
        """
        啟用憑證認證
        
        啟用憑證以取得下單權限。此為私有方法，在 login 方法中調用。
        
        Args:
            ca_path (str): 憑證檔案路徑
            ca_passwd (str): 憑證密碼
            
        Raises:
            FileNotFoundError: 當憑證檔案不存在時拋出
            ValueError: 當憑證密碼錯誤時拋出
        """
        try:
            self.logger.info("開始啟用憑證...")
            self.sj.activate_ca(
                ca_path=ca_path,
                ca_passwd=ca_passwd,
                person_id=self.sj.person_id
            )
            self.logger.info("憑證啟用成功，已取得下單權限")
        except Exception as e:
            self.logger.error(f"憑證啟用失敗: {str(e)}")
            raise
    
    def logout(self) -> bool:
        """
        登出 Shioaji API
        
        結束與永豐金證券的連線，釋放資源。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
            
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> # ... 進行交易操作 ...
            >>> connector.logout()
            
        Note:
            - 登出後需要重新登入才能繼續使用
            - 建議在程式結束前呼叫此方法以正常釋放連線
        """
        if self.sj is None:
            self.logger.warning("API 未初始化，無需登出")
            return False
        
        if not self.is_connected:
            self.logger.warning("尚未登入，無需登出")
            return False
        
        try:
            self.logger.info("開始登出 Shioaji API...")
            self.sj.logout()
            self.is_connected = False
            self.logger.info("登出成功")
            return True
        except Exception as e:
            self.logger.error(f"登出失敗: {str(e)}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        取得連線狀態資訊
        
        Returns:
            Dict[str, Any]: 包含連線狀態的字典，包括:
                - is_connected (bool): 是否已連線
                - login_time (str): 登入時間
                - simulation (bool): 是否為模擬環境
                - api_initialized (bool): API 是否已初始化
                
        Examples:
            >>> connector = ShioajiConnector()
            >>> connector.login(person_id="A123456789", passwd="password")
            >>> status = connector.get_connection_status()
            >>> print(status)
            {
                'is_connected': True,
                'login_time': '2025-10-06 10:30:00',
                'simulation': False,
                'api_initialized': True
            }
        """
        return {
            'is_connected': self.is_connected,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S') if self.login_time else None,
            'simulation': self.simulation,
            'api_initialized': self.sj is not None
        }
    
    def __enter__(self):
        """
        支援 context manager (with 語句)
        
        Examples:
            >>> with ShioajiConnector() as connector:
            >>>     connector.login(person_id="A123456789", passwd="password")
            >>>     # 進行交易操作
            >>>     # 離開 with 區塊時自動登出
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出 context manager 時自動登出
        """
        if self.is_connected:
            self.logout()
        return False
    
    def __repr__(self) -> str:
        """
        物件的字串表示
        
        Returns:
            str: 物件的描述字串
        """
        status = "已連線" if self.is_connected else "未連線"
        env = "模擬" if self.simulation else "正式"
        return f"ShioajiConnector(狀態={status}, 環境={env})"


# 模組層級的便利函數
def create_connector(
    api_key: str = "",
    secret_key: str = "",
    simulation: bool = False
) -> ShioajiConnector:
    """
    建立 ShioajiConnector 實例的便利函數
    
    Args:
        api_key (str, optional): API 金鑰
        secret_key (str, optional): 密鑰
        simulation (bool, optional): 是否使用模擬環境
        
    Returns:
        ShioajiConnector: Shioaji 連線器實例
        
    Examples:
        >>> connector = create_connector(simulation=True)
        >>> connector.login(person_id="A123456789", passwd="password")
    """
    return ShioajiConnector(
        api_key=api_key,
        secret_key=secret_key,
        simulation=simulation
    )


if __name__ == "__main__":
    # 使用範例
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Shioaji 連線器使用範例")
    print("=" * 60)
    
    # 示範 1: 基本使用
    print("\n示範 1: 建立連線器實例")
    try:
        connector = ShioajiConnector(simulation=True)
        print(f"連線器已建立: {connector}")
        print(f"連線狀態: {connector.get_connection_status()}")
    except ImportError as e:
        print(f"錯誤: {e}")
        print("請先安裝 shioaji: pip install shioaji")
    
    # 示範 2: Context Manager 使用
    print("\n示範 2: 使用 Context Manager")
    print("with ShioajiConnector(simulation=True) as connector:")
    print("    # 在此進行登入和交易操作")
    print("    # 離開 with 區塊時自動登出")
    
    print("\n" + "=" * 60)
    print("請參考類別文件以了解完整功能")
    print("=" * 60)
