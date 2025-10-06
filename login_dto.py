"""Data Transfer Objects for login operations.

This module defines DTOs (Data Transfer Objects) for login request
and response, providing a stable data model that isolates the application
from SDK implementation details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LoginRequestDTO:
    """Data Transfer Object for login request.
    
    This DTO encapsulates all information needed to perform a login operation.
    It provides a stable interface that doesn't change even if the underlying
    SDK implementation changes.
    
    Attributes:
        api_key: API key for authentication
        secret_key: Secret key for authentication
        person_id: Person ID (identity number) for the trading account
        ca_password: Certificate password for secure connection
    
    Examples:
        >>> request = LoginRequestDTO(
        ...     api_key="your_api_key",
        ...     secret_key="your_secret",
        ...     person_id="A123456789",
        ...     ca_password="password123"
        ... )
        >>> print(request.api_key)
        'your_api_key'
    """
    
    api_key: str
    secret_key: str
    person_id: str
    ca_password: str
    
    def __post_init__(self):
        """Validate required fields after initialization.
        
        Raises:
            ValueError: If any required field is empty or None
        
        Examples:
            >>> LoginRequestDTO("", "secret", "id", "pass")
            Traceback (most recent call last):
                ...
            ValueError: api_key cannot be empty
        """
        if not self.api_key:
            raise ValueError("api_key cannot be empty")
        if not self.secret_key:
            raise ValueError("secret_key cannot be empty")
        if not self.person_id:
            raise ValueError("person_id cannot be empty")
        if not self.ca_password:
            raise ValueError("ca_password cannot be empty")


@dataclass
class LoginResponseDTO:
    """Data Transfer Object for login response.
    
    This DTO encapsulates the result of a successful login operation.
    It provides a stable interface for accessing login session information.
    
    Attributes:
        success: Whether login was successful
        token: Authentication token for subsequent API calls
        session_id: Session identifier
        user_id: User identifier
        login_time: Timestamp of login
        message: Additional message from server
    
    Examples:
        >>> response = LoginResponseDTO(
        ...     success=True,
        ...     token="abc123token",
        ...     session_id="session_001",
        ...     user_id="A123456789",
        ...     login_time=datetime.now(),
        ...     message="Login successful"
        ... )
        >>> print(response.success)
        True
        >>> print(response.token)
        'abc123token'
    """
    
    success: bool
    token: str
    session_id: str
    user_id: str
    login_time: datetime
    message: Optional[str] = None
    
    def __post_init__(self):
        """Validate response data after initialization.
        
        Raises:
            ValueError: If required fields are empty or invalid
        
        Examples:
            >>> LoginResponseDTO(True, "", "session", "user", datetime.now())
            Traceback (most recent call last):
                ...
            ValueError: token cannot be empty when success is True
        """
        if self.success and not self.token:
            raise ValueError("token cannot be empty when success is True")
        if self.success and not self.session_id:
            raise ValueError("session_id cannot be empty when success is True")
        if self.success and not self.user_id:
            raise ValueError("user_id cannot be empty when success is True")
