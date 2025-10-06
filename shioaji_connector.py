"""
Shioaji 連線器模組

此模組提供與永豐證券 Shioaji API 的連線功能。
"""

import shioaji as sj
from typing import Optional


class ShioajiConnector:
    """
    Shioaji 連線器類別，負責管理與永豐證券 API 的連線。
    
    此類別遵循單一職責原則，專注於處理 Shioaji 的登入與連線管理。
    
    Attributes:
        api_key (str): API 金鑰
        secret_key (str): 密鑰
        sj (Optional[sj.Shioaji]): Shioaji 連線實例
    """
    
    def __init__(self, api_key: str, secret_key: str):
        """
        初始化 Shioaji 連線器。
        
        Args:
            api_key (str): 永豐證券提供的 API 金鑰
            secret_key (str): 永豐證券提供的密鑰
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空字串時
        """
        if not api_key:
            raise ValueError("api_key cannot be empty")
        if not secret_key:
            raise ValueError("secret_key cannot be empty")
        
        self.api_key = api_key
        self.secret_key = secret_key
        self.sj: Optional[sj.Shioaji] = None
    
    def login(self) -> sj.Shioaji:
        """
        執行登入操作並建立 Shioaji 連線。
        
        Returns:
            sj.Shioaji: 登入成功後的 Shioaji 實例
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> api = connector.login()
            >>> print(api)
            <shioaji.Shioaji object>
        
        Raises:
            ConnectionError: 當無法連線到 Shioaji 伺服器時
            ValueError: 當 API 金鑰或密鑰無效時
        """
        # 創建 Shioaji 實例
        self.sj = sj.Shioaji()
        
        try:
            # 執行登入
            self.sj.login(
                api_key=self.api_key,
                secret_key=self.secret_key
            )
            
            return self.sj
        
        except ValueError as e:
            self.sj = None
            raise ValueError(f"Invalid API credentials: {e}")
        except ConnectionError as e:
            self.sj = None
            raise ConnectionError(f"Failed to connect to Shioaji server: {e}")
    
    def logout(self) -> None:
        """
        登出並關閉 Shioaji 連線。
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.login()
            >>> connector.logout()
        
        Raises:
            RuntimeError: 當尚未登入就嘗試登出時
        """
        if self.sj is None:
            raise RuntimeError("Not logged in. Please login first.")
        
        self.sj.logout()
        self.sj = None
    
    def is_connected(self) -> bool:
        """
        檢查是否已建立連線。
        
        Returns:
            bool: 如果已連線則返回 True，否則返回 False
        
        Examples:
            >>> connector = ShioajiConnector("your_api_key", "your_secret_key")
            >>> connector.is_connected()
            False
            >>> connector.login()
            >>> connector.is_connected()
            True
        """
        return self.sj is not None
