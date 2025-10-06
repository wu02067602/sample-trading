"""
Shioaji 交易客戶端模組

此模組提供與永豐 Shioaji API 交互的客戶端類別。
"""

import shioaji as sj
from typing import Optional


class ShioajiClient:
    """
    Shioaji 交易客戶端類別
    
    此類別負責處理與永豐 Shioaji API 的連線和認證。
    
    Attributes:
        sj (Optional[sj.Shioaji]): Shioaji API 實例，登入成功後可用
    """
    
    def __init__(self):
        """初始化 ShioajiClient 實例。"""
        self.sj: Optional[sj.Shioaji] = None
    
    def login(
        self,
        api_key: str,
        secret_key: str,
        contracts_timeout: int = 30000
    ) -> bool:
        """
        使用 API Key 和 Secret Key 登入永豐 Shioaji。
        
        Args:
            api_key (str): 永豐提供的 API Key
            secret_key (str): 永豐提供的 Secret Key
            contracts_timeout (int): 合約下載逾時時間（毫秒），預設 30000
        
        Returns:
            bool: 登入成功返回 True，失敗返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.sj.stock_account
            Account(...)
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空字串時
            ConnectionError: 當無法連線到 Shioaji 伺服器時
            AuthenticationError: 當認證失敗時（無效的 API Key 或 Secret Key）
        """
        if not api_key or not api_key.strip():
            raise ValueError("API Key 不可為空")
        
        if not secret_key or not secret_key.strip():
            raise ValueError("Secret Key 不可為空")
        
        try:
            # 建立 Shioaji 實例
            self.sj = sj.Shioaji()
            
            # 執行登入
            result = self.sj.login(
                api_key=api_key,
                secret_key=secret_key,
                contracts_timeout=contracts_timeout
            )
            
            if result:
                return True
            else:
                self.sj = None
                raise AuthenticationError("登入失敗：認證未通過")
                
        except ConnectionError as e:
            self.sj = None
            raise ConnectionError(f"無法連線到 Shioaji 伺服器: {e}")
        except AuthenticationError:
            # 重新拋出已處理的認證錯誤
            raise
        except (ValueError, TypeError) as e:
            # 處理參數相關錯誤
            self.sj = None
            raise ValueError(f"登入參數錯誤: {e}")
        except OSError as e:
            # 處理網路相關錯誤
            self.sj = None
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def logout(self) -> bool:
        """
        登出 Shioaji 連線。
        
        Returns:
            bool: 登出成功返回 True
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.logout()
            True
        
        Raises:
            RuntimeError: 當尚未登入時嘗試登出
        """
        if self.sj is None:
            raise RuntimeError("尚未登入，無法執行登出操作")
        
        try:
            result = self.sj.logout()
            self.sj = None
            return result
        except (ConnectionError, OSError) as e:
            # 即使登出失敗，也清理本地狀態
            self.sj = None
            raise RuntimeError(f"登出時發生網路錯誤: {e}")
        except AttributeError as e:
            # Shioaji 物件可能已損壞
            self.sj = None
            raise RuntimeError(f"登出時發生錯誤，API 物件狀態異常: {e}")
    
    def is_logged_in(self) -> bool:
        """
        檢查是否已登入。
        
        Returns:
            bool: 已登入返回 True，否則返回 False
        
        Examples:
            >>> client = ShioajiClient()
            >>> client.is_logged_in()
            False
            >>> client.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")
            True
            >>> client.is_logged_in()
            True
        
        Raises:
            None
        """
        return self.sj is not None


class AuthenticationError(Exception):
    """
    認證錯誤異常
    
    當 Shioaji 認證失敗時拋出此異常。
    """
    pass
