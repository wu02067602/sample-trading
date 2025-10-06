"""登录相关的例外定义。

此模块定义了登录过程中可能发生的各种例外类型。
"""


class LoginError(Exception):
    """登录错误的基类。
    
    所有登录相关的例外都继承自此类。
    
    Attributes:
        message (str): 错误信息
        original_error (Exception): 原始错误（可选）
    
    Examples:
        >>> raise LoginError("登录失败")
        Traceback (most recent call last):
            ...
        LoginError: 登录失败
    
    Raises:
        None
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        """初始化登录错误。
        
        Args:
            message (str): 错误信息
            original_error (Exception): 原始错误（可选）
        
        Examples:
            >>> error = LoginError("测试错误")
            >>> str(error)
            '测试错误'
        
        Raises:
            None
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class LoginAuthenticationError(LoginError):
    """身份验证失败错误。
    
    当账号密码错误或身份验证失败时抛出。
    
    Examples:
        >>> raise LoginAuthenticationError("账号或密码错误")
        Traceback (most recent call last):
            ...
        LoginAuthenticationError: 账号或密码错误
    
    Raises:
        None
    """
    pass


class LoginConnectionError(LoginError):
    """连线错误。
    
    当 API 连线失败或超时时抛出。
    
    Examples:
        >>> raise LoginConnectionError("连线超时")
        Traceback (most recent call last):
            ...
        LoginConnectionError: 连线超时
    
    Raises:
        None
    """
    pass


class LoginDataFormatError(LoginError):
    """数据格式错误。
    
    当 API 响应格式错误或缺少必要字段时抛出。
    
    Examples:
        >>> raise LoginDataFormatError("响应缺少 token 字段")
        Traceback (most recent call last):
            ...
        LoginDataFormatError: 响应缺少 token 字段
    
    Raises:
        None
    """
    pass


class LoginParameterError(LoginError):
    """参数错误。
    
    当输入参数不完整或无效时抛出。
    
    Examples:
        >>> raise LoginParameterError("缺少必要的登录信息")
        Traceback (most recent call last):
            ...
        LoginParameterError: 缺少必要的登录信息
    
    Raises:
        None
    """
    pass


class LoginServerError(LoginError):
    """服务器错误。
    
    当 API 返回服务器错误（5xx）时抛出。
    
    Attributes:
        status_code (int): HTTP 状态码
    
    Examples:
        >>> error = LoginServerError("服务器内部错误", status_code=500)
        >>> error.status_code
        500
    
    Raises:
        None
    """
    
    def __init__(self, message: str, status_code: int = None, original_error: Exception = None):
        """初始化服务器错误。
        
        Args:
            message (str): 错误信息
            status_code (int): HTTP 状态码（可选）
            original_error (Exception): 原始错误（可选）
        
        Examples:
            >>> error = LoginServerError("服务不可用", status_code=503)
            >>> error.status_code
            503
        
        Raises:
            None
        """
        super().__init__(message, original_error)
        self.status_code = status_code


class LoginHTTPError(LoginError):
    """HTTP 错误。
    
    当 API 返回其他 HTTP 错误时抛出。
    
    Attributes:
        status_code (int): HTTP 状态码
    
    Examples:
        >>> error = LoginHTTPError("请求错误", status_code=400)
        >>> error.status_code
        400
    
    Raises:
        None
    """
    
    def __init__(self, message: str, status_code: int = None, original_error: Exception = None):
        """初始化 HTTP 错误。
        
        Args:
            message (str): 错误信息
            status_code (int): HTTP 状态码（可选）
            original_error (Exception): 原始错误（可选）
        
        Examples:
            >>> error = LoginHTTPError("未找到资源", status_code=404)
            >>> error.status_code
            404
        
        Raises:
            None
        """
        super().__init__(message, original_error)
        self.status_code = status_code
