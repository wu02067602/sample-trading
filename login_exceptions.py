"""Custom exceptions for login operations.

This module defines all custom exceptions that can be raised during
the login process, providing clear error handling and reporting.
"""


class LoginException(Exception):
    """Base exception for all login-related errors.
    
    This is the parent class for all login exceptions, allowing
    catch-all exception handling when needed.
    
    Attributes:
        message: Description of the error
        original_error: Original exception that caused this error (optional)
    
    Examples:
        >>> raise LoginException("Login failed")
        >>> try:
        ...     # some operation
        ... except SomeError as e:
        ...     raise LoginException("Operation failed", original_error=e)
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        """Initialize LoginException.
        
        Args:
            message: Description of the error
            original_error: Original exception that caused this error
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class AuthenticationError(LoginException):
    """Exception raised when authentication fails.
    
    This exception is raised when login credentials are incorrect
    or authentication is rejected by the server.
    
    Examples:
        >>> raise AuthenticationError("Invalid username or password")
        >>> raise AuthenticationError("Account locked")
    """
    pass


class ConnectionError(LoginException):
    """Exception raised when connection to server fails.
    
    This exception is raised when the client cannot establish
    connection to the server or when connection times out.
    
    Examples:
        >>> raise ConnectionError("Cannot connect to server")
        >>> raise ConnectionError("Connection timeout")
    """
    pass


class DataFormatError(LoginException):
    """Exception raised when response data format is invalid.
    
    This exception is raised when the server response cannot be parsed
    or when required fields are missing from the response.
    
    Examples:
        >>> raise DataFormatError("Missing 'token' field in response")
        >>> raise DataFormatError("Invalid JSON response")
    """
    pass


class ParameterError(LoginException):
    """Exception raised when input parameters are invalid.
    
    This exception is raised when required parameters are missing
    or when parameter values are invalid.
    
    Examples:
        >>> raise ParameterError("Missing required parameter: api_key")
        >>> raise ParameterError("Invalid parameter type")
    """
    pass


class ServerError(LoginException):
    """Exception raised when server returns error status code.
    
    This exception is raised when the server returns HTTP error
    status codes (4xx, 5xx).
    
    Attributes:
        status_code: HTTP status code returned by server
    
    Examples:
        >>> raise ServerError("Internal server error", status_code=500)
        >>> raise ServerError("Service unavailable", status_code=503)
    """
    
    def __init__(self, message: str, status_code: int = None, original_error: Exception = None):
        """Initialize ServerError.
        
        Args:
            message: Description of the error
            status_code: HTTP status code returned by server
            original_error: Original exception that caused this error
        """
        super().__init__(message, original_error)
        self.status_code = status_code
