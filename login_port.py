"""登录功能的端口定义 (Port)。

此模块定义了登录功能的抽象接口，遵循 Ports and Adapters 架构模式。
"""

from abc import ABC, abstractmethod
from login_dto import LoginRequestDTO, LoginResponseDTO


class LoginPort(ABC):
    """登录功能的端口（接口）。
    
    定义登录操作的契约，任何登录适配器都必须实现此接口。
    这是 Ports and Adapters 架构中的 Port 层。
    
    Examples:
        >>> class MyLoginAdapter(LoginPort):
        ...     def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        ...         # 实现登录逻辑
        ...         pass
    
    Raises:
        NotImplementedError: 当子类未实现抽象方法时
    """
    
    @abstractmethod
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """执行登录操作。
        
        Args:
            request (LoginRequestDTO): 登录请求数据传输对象
        
        Returns:
            LoginResponseDTO: 登录响应数据传输对象
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='test_key',
            ...     api_secret='test_secret'
            ... )
            >>> response = adapter.login(request)
            >>> isinstance(response, LoginResponseDTO)
            True
        
        Raises:
            LoginAuthenticationError: 当身份验证失败时（账号密码错误）
            LoginConnectionError: 当连线失败或超时时
            LoginDataFormatError: 当 API 响应格式错误或缺少必要字段时
            LoginParameterError: 当输入参数不完整或无效时
            LoginServerError: 当 API 返回服务器错误（5xx）时
            LoginHTTPError: 当 API 返回其他 HTTP 错误时
        """
        pass
