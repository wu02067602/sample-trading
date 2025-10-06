"""交易系统客户端类。

此模块提供 Client 类，用于管理与永丰 API 的交互。
"""

from typing import Optional
from config import Config
from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import LoginError


class Client:
    """交易系统客户端类。
    
    此类负责调用永丰 API 登录功能的 Adapter，并将登录结果存储为实例属性。
    采用依赖注入模式，接受 Config 和 LoginPort 作为依赖。
    
    Attributes:
        config (Config): 配置对象，包含登录所需的参数
        login_adapter (LoginPort): 登录适配器，实现登录功能
        sj (Optional[LoginResponseDTO]): 登录响应结果，登录成功后存储
    
    Examples:
        >>> from config import Config
        >>> from sinopac_login_adapter import SinoPacLoginAdapter
        >>> config = Config('config.yaml')
        >>> adapter = SinoPacLoginAdapter()
        >>> client = Client(config, adapter)
        >>> client.login()
        >>> print(client.sj.token)
        'abc123token'
    
    Raises:
        LoginError: 当登录失败时抛出相关的登录错误
    """
    
    def __init__(self, config: Config, login_adapter: LoginPort) -> None:
        """初始化 Client 类。
        
        Args:
            config (Config): 配置对象，包含登录所需的参数
            login_adapter (LoginPort): 登录适配器，实现登录功能
        
        Examples:
            >>> config = Config('config.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> client.sj is None
            True
        
        Raises:
            None
        """
        self.config = config
        self.login_adapter = login_adapter
        self.sj: Optional[LoginResponseDTO] = None
    
    def login(self) -> LoginResponseDTO:
        """执行登录操作。
        
        调用登录适配器执行登录，并将登录结果存储在 sj 属性中。
        
        Returns:
            LoginResponseDTO: 登录响应数据传输对象
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> response = client.login()
            >>> isinstance(response, LoginResponseDTO)
            True
            >>> client.sj is not None
            True
            >>> client.sj == response
            True
        
        Raises:
            LoginAuthenticationError: 当身份验证失败时（账号密码错误）
            LoginConnectionError: 当连线失败或超时时
            LoginDataFormatError: 当 API 响应格式错误或缺少必要字段时
            LoginParameterError: 当输入参数不完整或无效时
            LoginServerError: 当 API 返回服务器错误（5xx）时
            LoginHTTPError: 当 API 返回其他 HTTP 错误时
            LoginError: 当发生其他登录相关错误时
        """
        # 构建登录请求 DTO
        request = LoginRequestDTO(
            person_id=self.config.person_id,
            api_key=self.config.api_key,
            api_secret=self.config.api_secret,
            ca_path=self.config.ca_path
        )
        
        # 调用登录适配器
        response = self.login_adapter.login(request)
        
        # 将结果存储在 sj 属性中
        self.sj = response
        
        return response
    
    def is_logged_in(self) -> bool:
        """检查是否已登录。
        
        Returns:
            bool: 如果已登录且 token 未过期返回 True，否则返回 False
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> client.is_logged_in()
            False
            >>> client.login()
            >>> client.is_logged_in()
            True
        
        Raises:
            None
        """
        if self.sj is None:
            return False
        return not self.sj.is_expired()
    
    def __repr__(self) -> str:
        """返回 Client 对象的字符串表示。
        
        Returns:
            str: Client 对象的字符串表示
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> repr(client)
            'Client(logged_in=False)'
        
        Raises:
            None
        """
        logged_in = self.is_logged_in()
        return f"Client(logged_in={logged_in})"
