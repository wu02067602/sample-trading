"""
回調處理器介面模組

定義回調處理器的抽象介面，符合依賴反轉原則。
"""

from abc import ABC, abstractmethod


class ICallbackHandler(ABC):
    """
    回調處理器介面
    
    定義處理委託回報的抽象介面。
    """
    
    @abstractmethod
    def handle_order_callback(self, stat: int, msg: dict) -> None:
        """
        處理委託回報回調
        
        Args:
            stat (int): 狀態碼
            msg (dict): 委託訊息字典
        """
        pass
    
    @abstractmethod
    def handle_deal_callback(self, stat: int, msg: dict) -> None:
        """
        處理成交回報回調
        
        Args:
            stat (int): 狀態碼
            msg (dict): 成交訊息字典
        """
        pass
