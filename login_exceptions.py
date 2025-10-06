"""
登入功能的例外類別定義。

此模組定義了登入過程中可能發生的各種例外，
提供清楚的錯誤分類和訊息。
"""


class LoginError(Exception):
    """登入相關的異常基礎類別。"""
    pass


class LoginAuthenticationError(LoginError):
    """
    當登入認證失敗時拋出的異常（帳號密碼錯誤）。
    
    Examples:
        >>> raise LoginAuthenticationError("帳號或密碼錯誤")
    """
    pass


class LoginConnectionError(LoginError):
    """
    當連線失敗或逾時時拋出的異常。
    
    Examples:
        >>> raise LoginConnectionError("連線逾時")
    """
    pass


class LoginDataFormatError(LoginError):
    """
    當回應資料格式錯誤或缺少必要欄位時拋出的異常。
    
    Examples:
        >>> raise LoginDataFormatError("回應缺少必要欄位: token")
    """
    pass


class LoginParameterError(LoginError):
    """
    當輸入參數不完整或格式錯誤時拋出的異常。
    
    Examples:
        >>> raise LoginParameterError("缺少必要參數: person_id")
    """
    pass


class LoginHTTPError(LoginError):
    """
    當 HTTP 請求返回錯誤狀態碼時拋出的異常。
    
    Attributes:
        status_code (int): HTTP 狀態碼
    
    Examples:
        >>> raise LoginHTTPError("伺服器錯誤", status_code=500)
    """
    
    def __init__(self, message: str, status_code: int = None):
        """
        初始化 LoginHTTPError。
        
        Args:
            message (str): 錯誤訊息
            status_code (int, optional): HTTP 狀態碼
        """
        super().__init__(message)
        self.status_code = status_code
    
    def __str__(self):
        """返回包含狀態碼的錯誤訊息。"""
        if self.status_code:
            return f"{super().__str__()} (HTTP {self.status_code})"
        return super().__str__()
