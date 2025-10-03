"""
登入管理模組

此模組提供永豐 Shioaji API 的登入功能。
"""

from typing import Optional, TYPE_CHECKING
from .config import Config

# 延遲導入 shioaji，避免測試時因未安裝而報錯
if TYPE_CHECKING:
    import shioaji as sj


class LoginError(Exception):
    """登入錯誤異常"""
    pass


class Login:
    """
    永豐 Shioaji API 登入類別
    
    負責處理與永豐證券 API 的連線和身份驗證。
    
    屬性：
        config (Config): 配置物件
        api (Optional[sj.Shioaji]): Shioaji API 實例
        is_logged_in (bool): 是否已登入
    
    範例：
        >>> from src.config import Config
        >>> from src.login import Login
        >>> 
        >>> config = Config("config.yaml")
        >>> login = Login(config)
        >>> 
        >>> # 執行登入
        >>> login.login()
        >>> 
        >>> # 檢查登入狀態
        >>> if login.is_logged_in:
        ...     print("登入成功！")
        >>> 
        >>> # 登出
        >>> login.logout()
    """
    
    def __init__(self, config: Config):
        """
        初始化登入物件
        
        Args:
            config: Config 配置物件，包含 API 金鑰和登入資訊
            
        Raises:
            TypeError: 當 config 不是 Config 類型時
        """
        if not isinstance(config, Config):
            raise TypeError("config 必須是 Config 類型")
        
        self.config = config
        self.api = None
        self.is_logged_in = False
    
    def login(self) -> bool:
        """
        執行登入操作
        
        使用配置中的憑證連線到永豐 Shioaji API。
        
        Returns:
            bool: 登入成功返回 True，失敗拋出異常
            
        Raises:
            LoginError: 當登入失敗時（連線失敗、認證失敗等）
            LoginError: 當已經登入時重複呼叫
        """
        # 檢查是否已登入
        if self.is_logged_in:
            raise LoginError("已經登入，請勿重複登入")
        
        try:
            # 動態導入 shioaji
            try:
                import shioaji as sj
            except ImportError:
                raise LoginError(
                    "shioaji 套件未安裝，請執行: pip install shioaji"
                )
            
            # 建立 Shioaji 實例
            self.api = sj.Shioaji()
            
            # 準備登入參數
            login_params = {
                "api_key": self.config.api_key,
                "secret_key": self.config.secret_key,
                "contracts_timeout": self.config.contracts_timeout,
            }
            
            # 如果有憑證，加入憑證參數
            if self.config.ca_path:
                login_params["ca_path"] = self.config.ca_path
                if self.config.ca_passwd:
                    login_params["ca_passwd"] = self.config.ca_passwd
            
            # 執行登入
            result = self.api.login(**login_params)
            
            # 標記為已登入
            self.is_logged_in = True
            
            return True
            
        except ConnectionError as e:
            raise LoginError(f"連線失敗: {e}")
        except Exception as e:
            error_msg = str(e)
            
            # 處理常見的認證錯誤
            if "api_key" in error_msg.lower() or "secret_key" in error_msg.lower():
                raise LoginError(f"認證失敗: API 金鑰或密鑰錯誤 - {error_msg}")
            elif "certificate" in error_msg.lower() or "ca_" in error_msg.lower():
                raise LoginError(f"憑證錯誤: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise LoginError(f"連線逾時: {error_msg}")
            else:
                raise LoginError(f"登入失敗: {error_msg}")
    
    def logout(self) -> bool:
        """
        執行登出操作
        
        Returns:
            bool: 登出成功返回 True
            
        Raises:
            LoginError: 當尚未登入時
        """
        if not self.is_logged_in:
            raise LoginError("尚未登入")
        
        try:
            if self.api:
                self.api.logout()
            
            self.is_logged_in = False
            self.api = None
            
            return True
            
        except Exception as e:
            raise LoginError(f"登出失敗: {e}")
    
    def __repr__(self) -> str:
        """返回登入物件的字串表示"""
        status = "已登入" if self.is_logged_in else "未登入"
        return f"Login(person_id='{self.config.person_id}', status='{status}')"
    
    def __enter__(self):
        """Context manager 進入"""
        self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        if self.is_logged_in:
            self.logout()
        return False
