"""登入模組

此模組負責處理永豐 Shioaji API 的身份驗證與登入功能。
"""

import shioaji as sj
from typing import Optional


class Login:
    """負責使用者驗證與身份認證
    
    此類別封裝了永豐 Shioaji API 的登入流程，支援 Token 驗證方式。
    登入成功後，API 物件會被保存為實例屬性供後續使用。
    """
    
    def __init__(self) -> None:
        """初始化登入物件"""
        self.sj: Optional[sj.Shioaji] = None
    
    def login(self, api_key: str, secret_key: str) -> sj.Shioaji:
        """執行登入操作
        
        使用 API Key 和 Secret Key 進行身份驗證，並建立 Shioaji API 連線。
        
        Args:
            api_key (str): API 金鑰，需從永豐證券申請
            secret_key (str): API 密鑰，需從永豐證券申請
        
        Returns:
            sj.Shioaji: 已登入的 Shioaji API 物件
        
        Examples:
            >>> login_service = Login()
            >>> api = login_service.login(
            ...     api_key="YOUR_API_KEY",
            ...     secret_key="YOUR_SECRET_KEY"
            ... )
            >>> print(f"登入成功: {api.login}")
        
        Raises:
            ValueError: 當 api_key 或 secret_key 為空字串時
            ConnectionError: 當無法連線到永豐 API 伺服器時
            AuthenticationError: 當 API Key 或 Secret Key 驗證失敗時
        """
        if not api_key:
            raise ValueError("API Key 不可為空")
        if not secret_key:
            raise ValueError("Secret Key 不可為空")
        
        try:
            # 建立 Shioaji API 物件
            self.sj = sj.Shioaji()
            
            # 執行登入
            self.sj.login(
                api_key=api_key,
                secret_key=secret_key
            )
            
            return self.sj
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except (ValueError, KeyError) as e:
            # Shioaji 在驗證失敗時可能拋出 ValueError 或 KeyError
            raise AuthenticationError(f"API Key 或 Secret Key 驗證失敗: {e}")
        except OSError as e:
            # 網路相關錯誤
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def is_logged_in(self) -> bool:
        """檢查是否已登入
        
        Returns:
            bool: 如果已成功登入則返回 True，否則返回 False
        
        Examples:
            >>> login_service = Login()
            >>> login_service.is_logged_in()
            False
            >>> login_service.login(api_key="...", secret_key="...")
            >>> login_service.is_logged_in()
            True
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self.sj is not None
    
    def logout(self) -> None:
        """登出並清理資源
        
        執行登出操作並釋放 API 連線資源。
        
        Examples:
            >>> login_service = Login()
            >>> login_service.login(api_key="...", secret_key="...")
            >>> login_service.logout()
            >>> login_service.is_logged_in()
            False
        
        Raises:
            RuntimeError: 當尚未登入就嘗試登出時
        """
        if not self.is_logged_in():
            raise RuntimeError("尚未登入，無法執行登出操作")
        
        try:
            if self.sj is not None:
                self.sj.logout()
                self.sj = None
        except ConnectionError as e:
            # 登出時的連線錯誤
            raise RuntimeError(f"登出失敗 - 連線錯誤: {e}")
        except OSError as e:
            # 網路相關錯誤
            raise RuntimeError(f"登出失敗 - 網路錯誤: {e}")


class AuthenticationError(Exception):
    """身份驗證錯誤
    
    當 API Key 或 Secret Key 驗證失敗時拋出此錯誤。
    """
    pass
