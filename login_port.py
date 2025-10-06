"""
登入功能的 Port（接口）定義。

此模組定義了登入功能的抽象接口，遵循 Ports and Adapters 架構模式。
具體的實作（如永豐 SDK）需要實作此接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginRequestDTO:
    """
    登入請求的資料傳輸物件（DTO）。
    
    此 DTO 封裝登入所需的所有參數，確保資料結構的穩定性。
    
    Attributes:
        person_id (str): 身份證字號
        account (str): 帳號
        password (str): 密碼
        ca_password (str): CA 密碼
    
    Examples:
        >>> request = LoginRequestDTO(
        ...     person_id="A123456789",
        ...     account="1234567",
        ...     password="password123",
        ...     ca_password="ca_password123"
        ... )
    """
    person_id: str
    account: str
    password: str
    ca_password: str
    
    def __post_init__(self):
        """
        驗證 DTO 中的所有欄位是否有效。
        
        Raises:
            ValueError: 當任何欄位為空或不是字串時
        """
        if not all([self.person_id, self.account, self.password, self.ca_password]):
            raise ValueError("所有登入參數都必須提供且不能為空")
        
        if not all([
            isinstance(self.person_id, str),
            isinstance(self.account, str),
            isinstance(self.password, str),
            isinstance(self.ca_password, str)
        ]):
            raise ValueError("所有登入參數都必須是字串類型")


@dataclass
class LoginResponseDTO:
    """
    登入回應的資料傳輸物件（DTO）。
    
    此 DTO 封裝登入成功後返回的資訊，提供穩定的資料結構。
    
    Attributes:
        success (bool): 登入是否成功
        token (Optional[str]): 登入成功後的 token
        account (Optional[str]): 帳號資訊
        person_id (Optional[str]): 身份證字號
        message (Optional[str]): 回應訊息（成功或失敗的說明）
    
    Examples:
        >>> response = LoginResponseDTO(
        ...     success=True,
        ...     token="abc123token",
        ...     account="1234567",
        ...     person_id="A123456789",
        ...     message="登入成功"
        ... )
    """
    success: bool
    token: Optional[str] = None
    account: Optional[str] = None
    person_id: Optional[str] = None
    message: Optional[str] = None


class LoginPort(ABC):
    """
    登入功能的抽象接口（Port）。
    
    此接口定義了登入功能的標準行為，具體的實作（Adapter）
    需要繼承此類別並實作 login 方法。
    
    Examples:
        >>> class MyLoginAdapter(LoginPort):
        ...     def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        ...         # 實作登入邏輯
        ...         pass
    """
    
    @abstractmethod
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """
        執行登入操作。
        
        Args:
            request (LoginRequestDTO): 登入請求資料
        
        Returns:
            LoginResponseDTO: 登入回應資料
        
        Raises:
            LoginAuthenticationError: 當帳號密碼錯誤時
            LoginConnectionError: 當連線失敗或逾時時
            LoginDataFormatError: 當回應資料格式錯誤時
            LoginParameterError: 當輸入參數不完整時
            LoginHTTPError: 當 HTTP 請求返回錯誤狀態碼時
        """
        pass
