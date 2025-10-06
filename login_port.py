"""Port (interface) for login operations.

This module defines the LoginPort interface that all login adapters
must implement, following the Ports and Adapters (Hexagonal) architecture.
"""

from abc import ABC, abstractmethod

from login_dto import LoginRequestDTO, LoginResponseDTO


class LoginPort(ABC):
    """Abstract interface for login operations.
    
    This port defines the contract that all login adapters must implement.
    It follows the Dependency Inversion Principle, allowing the application
    to depend on abstractions rather than concrete implementations.
    
    Examples:
        >>> class MyLoginAdapter(LoginPort):
        ...     def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        ...         # Implementation here
        ...         pass
    """
    
    @abstractmethod
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """Perform login operation.
        
        This method authenticates the user with the provided credentials
        and returns a LoginResponseDTO containing session information.
        
        Args:
            request: LoginRequestDTO containing login credentials
        
        Returns:
            LoginResponseDTO containing authentication token and session info
        
        Raises:
            AuthenticationError: When credentials are invalid
            ConnectionError: When connection to server fails
            DataFormatError: When response format is invalid
            ParameterError: When input parameters are invalid
            ServerError: When server returns error status code
        
        Examples:
            >>> adapter = SinopacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     api_key="key",
            ...     secret_key="secret",
            ...     person_id="A123456789",
            ...     ca_password="pass"
            ... )
            >>> response = adapter.login(request)
            >>> print(response.success)
            True
        """
        pass
