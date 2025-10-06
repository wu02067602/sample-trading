"""永丰证券 API 登录适配器。

此模块实现了永丰证券 API 的登录功能适配器，遵循 Ports and Adapters 架构。
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import (
    LoginAuthenticationError,
    LoginConnectionError,
    LoginDataFormatError,
    LoginParameterError,
    LoginServerError,
    LoginHTTPError
)


class SinoPacLoginAdapter(LoginPort):
    """永丰证券 API 登录适配器。
    
    实现 LoginPort 接口，提供永丰证券 API 的登录功能。
    这是 Ports and Adapters 架构中的 Adapter 层。
    
    Attributes:
        base_url (str): API 基础 URL
        timeout (int): 请求超时时间（秒）
        http_client: HTTP 客户端实例
    
    Examples:
        >>> adapter = SinoPacLoginAdapter(base_url='https://api.sinopac.com')
        >>> request = LoginRequestDTO(
        ...     person_id='A123456789',
        ...     api_key='test_key',
        ...     api_secret='test_secret'
        ... )
        >>> response = adapter.login(request)
        >>> isinstance(response, LoginResponseDTO)
        True
    
    Raises:
        LoginAuthenticationError: 当身份验证失败时
        LoginConnectionError: 当连线失败或超时时
        LoginDataFormatError: 当 API 响应格式错误时
        LoginParameterError: 当输入参数无效时
        LoginServerError: 当服务器错误时
        LoginHTTPError: 当其他 HTTP 错误时
    """
    
    def __init__(
        self,
        base_url: str = 'https://openapi.sinotrade.com.tw',
        timeout: int = 30,
        http_client: Optional[requests.Session] = None
    ):
        """初始化永丰证券登录适配器。
        
        Args:
            base_url (str): API 基础 URL，默认为永丰证券的 OpenAPI URL
            timeout (int): 请求超时时间（秒），默认 30 秒
            http_client (Optional[requests.Session]): HTTP 客户端实例，默认为 None
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> adapter.base_url
            'https://openapi.sinotrade.com.tw'
            >>> adapter.timeout
            30
        
        Raises:
            None
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.http_client = http_client or requests.Session()
    
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """执行永丰证券 API 登录操作。
        
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
            >>> response.token
            'abc123token'
        
        Raises:
            LoginAuthenticationError: 当身份验证失败时（401）
            LoginConnectionError: 当连线失败或超时时
            LoginDataFormatError: 当 API 响应格式错误或缺少必要字段时
            LoginParameterError: 当输入参数不完整或无效时
            LoginServerError: 当 API 返回服务器错误（5xx）时
            LoginHTTPError: 当 API 返回其他 HTTP 错误时
        """
        # 验证输入参数
        self._validate_request(request)
        
        # 构建请求
        url = f"{self.base_url}/v1/login"
        headers = self._build_headers()
        body = self._build_request_body(request)
        
        try:
            # 发送 HTTP 请求
            response = self.http_client.post(
                url,
                json=body,
                headers=headers,
                timeout=self.timeout
            )
            
            # 处理响应
            return self._handle_response(response)
            
        except requests.exceptions.Timeout as e:
            raise LoginConnectionError("连线超时", original_error=e)
        except requests.exceptions.ConnectionError as e:
            raise LoginConnectionError("连线失败", original_error=e)
        except requests.exceptions.RequestException as e:
            raise LoginConnectionError(f"请求失败: {str(e)}", original_error=e)
    
    def _validate_request(self, request: LoginRequestDTO) -> None:
        """验证登录请求参数。
        
        Args:
            request (LoginRequestDTO): 登录请求数据传输对象
        
        Raises:
            LoginParameterError: 当参数无效时
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     person_id='',
            ...     api_key='key',
            ...     api_secret='secret'
            ... )
            >>> adapter._validate_request(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            ValueError: person_id 不能为空
        """
        try:
            # LoginRequestDTO 的 __post_init__ 已经做了基本验证
            # 这里可以添加额外的业务逻辑验证
            pass
        except ValueError as e:
            raise LoginParameterError(str(e), original_error=e)
    
    def _build_headers(self) -> Dict[str, str]:
        """构建 HTTP 请求头。
        
        Returns:
            Dict[str, str]: HTTP 请求头字典
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> headers = adapter._build_headers()
            >>> headers['Content-Type']
            'application/json'
        
        Raises:
            None
        """
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SinoPacLoginAdapter/1.0'
        }
    
    def _build_request_body(self, request: LoginRequestDTO) -> Dict[str, Any]:
        """构建 HTTP 请求体。
        
        Args:
            request (LoginRequestDTO): 登录请求数据传输对象
        
        Returns:
            Dict[str, Any]: HTTP 请求体字典
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='test_key',
            ...     api_secret='test_secret'
            ... )
            >>> body = adapter._build_request_body(request)
            >>> body['person_id']
            'A123456789'
        
        Raises:
            None
        """
        body = {
            'person_id': request.person_id,
            'api_key': request.api_key,
            'api_secret': request.api_secret
        }
        
        if request.ca_path:
            body['ca_path'] = request.ca_path
        
        return body
    
    def _handle_response(self, response: requests.Response) -> LoginResponseDTO:
        """处理 API 响应。
        
        Args:
            response (requests.Response): HTTP 响应对象
        
        Returns:
            LoginResponseDTO: 登录响应数据传输对象
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> # 模拟响应对象
            >>> class MockResponse:
            ...     status_code = 200
            ...     def json(self):
            ...         return {
            ...             'token': 'abc123',
            ...             'person_id': 'A123456789',
            ...             'session_id': 'session_xyz',
            ...             'expires_in': 3600
            ...         }
            >>> response = MockResponse()
            >>> dto = adapter._handle_response(response)
            >>> dto.token
            'abc123'
        
        Raises:
            LoginAuthenticationError: 当状态码为 401 时
            LoginServerError: 当状态码为 5xx 时
            LoginHTTPError: 当状态码为其他错误码时
            LoginDataFormatError: 当响应格式错误时
        """
        # 检查 HTTP 状态码
        if response.status_code == 401:
            raise LoginAuthenticationError("身份验证失败，账号或密码错误")
        elif response.status_code == 403:
            raise LoginAuthenticationError("权限不足，无法访问")
        elif 500 <= response.status_code < 600:
            raise LoginServerError(
                f"服务器错误: {response.status_code}",
                status_code=response.status_code
            )
        elif response.status_code != 200:
            raise LoginHTTPError(
                f"HTTP 错误: {response.status_code}",
                status_code=response.status_code
            )
        
        # 解析响应数据
        try:
            data = response.json()
        except ValueError as e:
            raise LoginDataFormatError("响应数据不是有效的 JSON 格式", original_error=e)
        
        # 验证响应数据格式
        return self._parse_response_data(data)
    
    def _parse_response_data(self, data: Dict[str, Any]) -> LoginResponseDTO:
        """解析响应数据并转换为 DTO。
        
        Args:
            data (Dict[str, Any]): API 响应数据
        
        Returns:
            LoginResponseDTO: 登录响应数据传输对象
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> data = {
            ...     'token': 'abc123',
            ...     'person_id': 'A123456789',
            ...     'session_id': 'session_xyz',
            ...     'expires_in': 3600
            ... }
            >>> dto = adapter._parse_response_data(data)
            >>> dto.token
            'abc123'
        
        Raises:
            LoginDataFormatError: 当响应缺少必要字段或格式错误时
        """
        # 检查必要字段
        required_fields = ['token', 'person_id', 'session_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise LoginDataFormatError(
                f"响应缺少必要字段: {', '.join(missing_fields)}"
            )
        
        # 提取数据
        token = data.get('token')
        person_id = data.get('person_id')
        session_id = data.get('session_id')
        expires_in = data.get('expires_in', 3600)  # 默认 1 小时
        account_id = data.get('account_id')
        
        # 验证字段类型
        if not isinstance(token, str) or not token:
            raise LoginDataFormatError("token 字段必须是非空字符串")
        if not isinstance(person_id, str) or not person_id:
            raise LoginDataFormatError("person_id 字段必须是非空字符串")
        if not isinstance(session_id, str) or not session_id:
            raise LoginDataFormatError("session_id 字段必须是非空字符串")
        
        # 计算过期时间
        try:
            expires_at = datetime.now() + timedelta(seconds=int(expires_in))
        except (ValueError, TypeError) as e:
            raise LoginDataFormatError(
                "expires_in 字段必须是有效的整数",
                original_error=e
            )
        
        # 创建 DTO
        try:
            return LoginResponseDTO(
                token=token,
                person_id=person_id,
                session_id=session_id,
                expires_at=expires_at,
                account_id=account_id
            )
        except ValueError as e:
            raise LoginDataFormatError(f"创建响应 DTO 失败: {str(e)}", original_error=e)
