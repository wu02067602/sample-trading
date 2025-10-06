"""
交易介面抽象層

此模組定義了交易系統的抽象介面，遵循依賴反轉原則 (DIP)。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


class ITradingClient(ABC):
    """
    交易客戶端抽象介面
    
    此介面定義了所有交易客戶端必須實作的基本方法，
    遵循依賴反轉原則，讓高層模組不依賴於低層模組的具體實作。
    
    Examples:
        >>> class MyTradingClient(ITradingClient):
        ...     def connect(self, config: Any) -> bool:
        ...         # 實作連線邏輯
        ...         pass
        ...     def disconnect(self) -> bool:
        ...         # 實作斷線邏輯
        ...         pass
        ...     def get_accounts(self) -> Dict[str, Any]:
        ...         # 實作取得帳戶邏輯
        ...         pass
        ...     def is_connected(self) -> bool:
        ...         # 實作檢查連線狀態邏輯
        ...         pass
    """
    
    @abstractmethod
    def connect(self, config: Any) -> bool:
        """
        連接到交易系統
        
        Args:
            config: 連線配置物件
        
        Returns:
            bool: 連線成功返回 True，失敗返回 False
        
        Raises:
            ValueError: 當配置參數無效時
            ConnectionError: 當連線失敗時
            RuntimeError: 當發生其他錯誤時
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        斷開與交易系統的連線
        
        Returns:
            bool: 斷線成功返回 True，失敗返回 False
        
        Raises:
            RuntimeError: 當尚未連線或斷線過程發生錯誤時
        """
        pass
    
    @abstractmethod
    def get_accounts(self) -> Dict[str, Any]:
        """
        取得帳戶資訊
        
        Returns:
            Dict[str, Any]: 帳戶資訊字典
        
        Raises:
            RuntimeError: 當尚未連線時
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        檢查是否已連線
        
        Returns:
            bool: 已連線返回 True，未連線返回 False
        """
        pass


class IConfigValidator(ABC):
    """
    配置驗證器抽象介面
    
    此介面定義了配置驗證的標準方法。
    """
    
    @abstractmethod
    def validate(self) -> None:
        """
        驗證配置的有效性
        
        Raises:
            ValueError: 當配置無效時
        """
        pass
