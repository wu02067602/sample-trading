"""
量化交易系統 - 身份驗證模組

此模組負責處理永豐金證券 API (Shioaji) 的使用者登入與身份驗證。
"""

import shioaji as sj
from typing import Optional, Callable


class Authentication:
    """
    負責處理使用者登入驗證與身份認證，管理使用者會話與授權。
    
    此類別封裝了永豐金證券 Shioaji API 的登入功能，並將登入後的 API 實例
    儲存為類別屬性供後續使用。
    
    Attributes:
        api (Optional[sj.Shioaji]): 登入成功後的 Shioaji API 實例
    
    Examples:
        >>> auth = Authentication()
        >>> auth.login(person_id="YOUR_ID", passwd="YOUR_PASSWORD")
        >>> # 登入成功後，可透過 auth.api 使用 Shioaji 功能
    """
    
    def __init__(self) -> None:
        """
        初始化 Authentication 實例。
        
        建立一個新的 Shioaji API 實例並將其儲存為 api 屬性。
        """
        self.api: Optional[sj.Shioaji] = sj.Shioaji()
    
    def login(
        self,
        person_id: str,
        passwd: str,
        contracts_cb: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        執行登入操作。
        
        使用提供的帳號密碼登入永豐金證券 API。登入成功後，API 實例會保存在
        self.api 屬性中，供其他模組使用。
        
        Args:
            person_id (str): 使用者的身分證字號或帳號
            passwd (str): 使用者密碼
            contracts_cb (Optional[Callable[[str], None]]): 
                合約下載完成時的回調函數，接收合約類型字串作為參數
        
        Returns:
            bool: 登入成功返回 True，失敗返回 False
        
        Examples:
            >>> auth = Authentication()
            >>> success = auth.login(
            ...     person_id="A123456789",
            ...     passwd="password123",
            ...     contracts_cb=lambda x: print(f"{x} 合約下載完成")
            ... )
            >>> if success:
            ...     print("登入成功")
        
        Raises:
            ValueError: 當 person_id 或 passwd 為空字串時
            ConnectionError: 當網路連線失敗時
            RuntimeError: 當 API 登入失敗時
        """
        if not person_id:
            raise ValueError("person_id 不可為空")
        if not passwd:
            raise ValueError("passwd 不可為空")
        
        try:
            # 執行登入
            result = self.api.login(
                person_id=person_id,
                passwd=passwd,
                contracts_cb=contracts_cb
            )
            
            # 檢查登入結果
            if result:
                return True
            else:
                raise RuntimeError("登入失敗：API 返回失敗狀態")
                
        except ConnectionError as e:
            raise ConnectionError(f"網路連線失敗：{e}") from e
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"登入失敗：{e}") from e
    
    def logout(self) -> bool:
        """
        執行登出操作。
        
        登出當前的 API 會話，釋放相關資源。
        
        Returns:
            bool: 登出成功返回 True，失敗返回 False
        
        Examples:
            >>> auth = Authentication()
            >>> auth.login(person_id="A123456789", passwd="password123")
            >>> auth.logout()
            True
        
        Raises:
            RuntimeError: 當 API 尚未登入或登出失敗時
        """
        if self.api is None:
            raise RuntimeError("API 尚未初始化")
        
        try:
            result = self.api.logout()
            return bool(result)
        except (RuntimeError, Exception) as e:
            raise RuntimeError(f"登出失敗：{e}") from e
    
    def is_logged_in(self) -> bool:
        """
        檢查當前是否已登入。
        
        Returns:
            bool: 已登入返回 True，未登入返回 False
        
        Examples:
            >>> auth = Authentication()
            >>> auth.is_logged_in()
            False
            >>> auth.login(person_id="A123456789", passwd="password123")
            >>> auth.is_logged_in()
            True
        """
        if self.api is None:
            return False
        
        # 透過檢查 API 的連線狀態來判斷是否已登入
        return hasattr(self.api, 'stock') and self.api.stock is not None
