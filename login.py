"""登入模組

此模組負責處理永豐 Shioaji API 的身份驗證與登入功能。
"""

import shioaji as sj
from typing import Optional
from config import Config

class Login:
    """負責使用者驗證與身份認證
    
    此類別封裝了永豐 Shioaji API 的登入流程，支援 Token 驗證方式。
    登入成功後，API 物件會被保存為實例屬性供後續使用。
    """
    
    def __init__(self, config: Config) -> None:
        """初始化登入物件"""
        self.sj: Optional[sj.Shioaji] = None
        self.config = config
    
    def login(self) -> sj.Shioaji:
        """執行登入操作
        
        使用 API Key 和 Secret Key 進行身份驗證，並建立 Shioaji API 連線。
        
        Args:
            api_key (str): API 金鑰，需從永豐證券申請
            secret_key (str): API 密鑰，需從永豐證券申請
        
        Returns:
            sj.Shioaji: 已登入的 Shioaji API 物件
        
        Examples:
            >>> login_service = Login(config)
            >>> api = login_service.login()
            >>> print(f"登入成功: {api.login}")
        """
        try:
            self.sj = sj.Shioaji(simulation=self.config.simulation)
            
            self.sj.login(
                api_key=self.config.api_key,
                secret_key=self.config.api_secret
            )
            
            return self.sj
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except (ValueError, KeyError) as e:
            raise AuthenticationError(f"API Key 或 Secret Key 驗證失敗: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
    
    def is_logged_in(self) -> bool:
        return self.sj is not None
    
    def logout(self) -> None:
        """登出並清理資源
        
        執行登出操作並釋放 API 連線資源。
        
        Examples:
            >>> login_service = Login(config)
            >>> login_service.login()
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
