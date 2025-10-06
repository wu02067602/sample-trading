"""登录相关的数据传输对象 (DTOs)。

此模块定义了登录请求和响应的数据传输对象，用于稳定化数据模型。
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class LoginRequestDTO:
    """登录请求的数据传输对象。
    
    封装登录所需的所有参数，确保数据的不可变性和类型安全。
    
    Attributes:
        person_id (str): 身份证字号
        api_key (str): API Key
        api_secret (str): API Secret
        ca_path (Optional[str]): 凭证路径（可选）
    
    Examples:
        >>> request = LoginRequestDTO(
        ...     person_id='A123456789',
        ...     api_key='test_key',
        ...     api_secret='test_secret'
        ... )
        >>> request.person_id
        'A123456789'
    
    Raises:
        ValueError: 当必要字段为空时
    """
    
    person_id: str
    api_key: str
    api_secret: str
    ca_path: Optional[str] = None
    
    def __post_init__(self) -> None:
        """验证数据传输对象的字段。
        
        Raises:
            ValueError: 当必要字段为空或格式不正确时
        
        Examples:
            >>> LoginRequestDTO(person_id='', api_key='key', api_secret='secret')
            Traceback (most recent call last):
                ...
            ValueError: person_id 不能为空
        """
        if not self.person_id or not isinstance(self.person_id, str):
            raise ValueError("person_id 不能为空")
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("api_key 不能为空")
        if not self.api_secret or not isinstance(self.api_secret, str):
            raise ValueError("api_secret 不能为空")
        if self.ca_path is not None and not isinstance(self.ca_path, str):
            raise ValueError("ca_path 必须是字符串类型")


@dataclass(frozen=True)
class LoginResponseDTO:
    """登录响应的数据传输对象。
    
    封装登录成功后返回的所有信息，确保数据的不可变性。
    
    Attributes:
        token (str): 认证令牌
        person_id (str): 用户身份证字号
        session_id (str): 会话标识
        expires_at (datetime): 令牌过期时间
        account_id (Optional[str]): 账户 ID（可选）
    
    Examples:
        >>> from datetime import datetime, timedelta
        >>> response = LoginResponseDTO(
        ...     token='abc123token',
        ...     person_id='A123456789',
        ...     session_id='session_xyz',
        ...     expires_at=datetime.now() + timedelta(hours=1)
        ... )
        >>> response.token
        'abc123token'
    
    Raises:
        ValueError: 当必要字段为空时
    """
    
    token: str
    person_id: str
    session_id: str
    expires_at: datetime
    account_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """验证数据传输对象的字段。
        
        Raises:
            ValueError: 当必要字段为空或格式不正确时
        
        Examples:
            >>> from datetime import datetime
            >>> LoginResponseDTO(
            ...     token='',
            ...     person_id='A123456789',
            ...     session_id='session',
            ...     expires_at=datetime.now()
            ... )
            Traceback (most recent call last):
                ...
            ValueError: token 不能为空
        """
        if not self.token or not isinstance(self.token, str):
            raise ValueError("token 不能为空")
        if not self.person_id or not isinstance(self.person_id, str):
            raise ValueError("person_id 不能为空")
        if not self.session_id or not isinstance(self.session_id, str):
            raise ValueError("session_id 不能为空")
        if not isinstance(self.expires_at, datetime):
            raise ValueError("expires_at 必须是 datetime 类型")
        if self.account_id is not None and not isinstance(self.account_id, str):
            raise ValueError("account_id 必须是字符串类型")
    
    def is_expired(self) -> bool:
        """检查令牌是否已过期。
        
        Returns:
            bool: 如果令牌已过期返回 True，否则返回 False
        
        Examples:
            >>> from datetime import datetime, timedelta
            >>> response = LoginResponseDTO(
            ...     token='abc123',
            ...     person_id='A123456789',
            ...     session_id='session',
            ...     expires_at=datetime.now() - timedelta(hours=1)
            ... )
            >>> response.is_expired()
            True
        
        Raises:
            None
        """
        return datetime.now() >= self.expires_at
    
    def __repr__(self) -> str:
        """返回 LoginResponseDTO 对象的字符串表示。
        
        隐藏敏感信息（token）。
        
        Returns:
            str: LoginResponseDTO 对象的字符串表示
        
        Examples:
            >>> from datetime import datetime
            >>> response = LoginResponseDTO(
            ...     token='abc123token',
            ...     person_id='A123456789',
            ...     session_id='session_xyz',
            ...     expires_at=datetime(2025, 10, 6, 12, 0, 0)
            ... )
            >>> repr(response)
            "LoginResponseDTO(token='***', person_id='A***6789', session_id='session_xyz')"
        """
        person_id_masked = (
            f"{self.person_id[0]}***{self.person_id[-4:]}"
            if len(self.person_id) > 5 else "***"
        )
        return (
            f"LoginResponseDTO(token='***', "
            f"person_id='{person_id_masked}', "
            f"session_id='{self.session_id}')"
        )
