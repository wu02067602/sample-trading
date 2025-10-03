"""
控制器模組

此模組提供永豐 Shioaji API 的高層次控制介面，整合配置管理和登入功能。
"""

from typing import Optional, Union
from pathlib import Path
from .config import Config, ConfigError
from .login import Login, LoginError


class ControllerError(Exception):
    """控制器錯誤異常"""
    pass


class Controller:
    """
    永豐 Shioaji API 控制器類別
    
    提供高層次的 API 介面，整合配置管理和登入功能，簡化使用流程。
    
    屬性：
        config (Config): 配置物件
        login (Login): 登入物件
        sj (Optional): Shioaji API 實例（登入後可用）
    
    範例：
        >>> # 方法 1：使用配置檔案路徑
        >>> controller = Controller("config.yaml")
        >>> controller.connect()
        >>> 
        >>> # 方法 2：使用 Config 物件
        >>> config = Config("config.yaml")
        >>> controller = Controller(config)
        >>> controller.connect()
        >>> 
        >>> # 使用 Context Manager（推薦）
        >>> with Controller("config.yaml") as ctrl:
        ...     if ctrl.is_connected():
        ...         # 使用 ctrl.sj 進行交易
        ...         pass
    """
    
    def __init__(self, config: Union[str, Path, Config]):
        """
        初始化控制器
        
        Args:
            config: 配置檔案路徑（str/Path）或 Config 物件
            
        Raises:
            TypeError: 當 config 類型不正確時
            ConfigError: 當配置載入或驗證失敗時
        
        範例：
            >>> # 使用路徑
            >>> ctrl = Controller("config.yaml")
            >>> 
            >>> # 使用 Config 物件
            >>> config = Config("config.yaml")
            >>> ctrl = Controller(config)
        """
        # 處理不同類型的 config 輸入
        if isinstance(config, (str, Path)):
            self.config = Config(config)
        elif isinstance(config, Config):
            self.config = config
        else:
            raise TypeError(
                f"config 必須是 str、Path 或 Config 類型，收到: {type(config)}"
            )
        
        # 初始化 Login 物件
        self.login = Login(self.config)
        
        # Shioaji API 實例（登入後設定）
        self.sj = None
    
    def connect(self) -> bool:
        """
        連線到永豐 API（執行登入）
        
        執行登入流程並將 Shioaji API 實例儲存到 self.sj。
        
        Returns:
            bool: 連線成功返回 True
            
        Raises:
            ControllerError: 當已經連線時
            LoginError: 當登入失敗時
        
        範例：
            >>> controller = Controller("config.yaml")
            >>> controller.connect()
            True
            >>> controller.is_connected()
            True
        """
        if self.is_connected():
            raise ControllerError("已經連線，請勿重複連線")
        
        try:
            # 執行登入
            self.login.login()
            
            # 儲存 Shioaji API 實例
            self.sj = self.login.api
            
            return True
            
        except LoginError as e:
            raise LoginError(f"連線失敗: {e}")
        except Exception as e:
            raise ControllerError(f"連線時發生未預期的錯誤: {e}")
    
    def disconnect(self) -> bool:
        """
        中斷連線（執行登出）
        
        Returns:
            bool: 中斷連線成功返回 True
            
        Raises:
            ControllerError: 當尚未連線時
            LoginError: 當登出失敗時
        
        範例：
            >>> controller.disconnect()
            True
            >>> controller.is_connected()
            False
        """
        if not self.is_connected():
            raise ControllerError("尚未連線")
        
        try:
            # 執行登出
            self.login.logout()
            
            # 清除 Shioaji API 實例
            self.sj = None
            
            return True
            
        except LoginError as e:
            raise LoginError(f"中斷連線失敗: {e}")
        except Exception as e:
            raise ControllerError(f"中斷連線時發生未預期的錯誤: {e}")
    
    def is_connected(self) -> bool:
        """
        檢查是否已連線
        
        Returns:
            bool: 已連線返回 True，未連線返回 False
        
        範例：
            >>> controller = Controller("config.yaml")
            >>> controller.is_connected()
            False
            >>> controller.connect()
            >>> controller.is_connected()
            True
        """
        return self.login.is_logged_in and self.sj is not None
    
    def get_status(self) -> dict:
        """
        取得控制器狀態資訊
        
        Returns:
            dict: 包含狀態資訊的字典
        
        範例：
            >>> status = controller.get_status()
            >>> print(status['connected'])
            True
            >>> print(status['person_id'])
            'A123456789'
        """
        return {
            "connected": self.is_connected(),
            "person_id": self.config.person_id,
            "simulation": self.config.simulation,
            "has_certificate": self.config.ca_path is not None,
        }
    
    def __repr__(self) -> str:
        """返回控制器物件的字串表示"""
        status = "已連線" if self.is_connected() else "未連線"
        return (
            f"Controller(person_id='{self.config.person_id}', "
            f"status='{status}', "
            f"simulation={self.config.simulation})"
        )
    
    def __enter__(self):
        """Context manager 進入"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        if self.is_connected():
            self.disconnect()
        return False
