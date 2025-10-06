"""Client class for Sinopac trading system.

This module provides a Client class that manages the login process
and maintains the session for Sinopac trading operations.
"""

from typing import Optional, Union

from config import Config
from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO
from sinopac_login_adapter import SinopacLoginAdapter
from login_exceptions import LoginException


class Client:
    """Client for Sinopac trading system.
    
    This class manages the trading system client, handling login operations
    and maintaining the session (sj) for subsequent trading operations.
    
    Attributes:
        config: Configuration object containing login credentials
        login_adapter: Login adapter for authentication (injectable for testing)
        sj: Session object after successful login (None before login)
        is_logged_in: Boolean indicating if client is logged in
    
    Examples:
        >>> # Using config file path
        >>> client = Client("config.yaml")
        >>> client.login()
        >>> print(client.is_logged_in)
        True
        
        >>> # Using Config object
        >>> config = Config("config.yaml")
        >>> client = Client(config)
        >>> client.login()
        
        >>> # Using custom adapter (for testing)
        >>> mock_adapter = MockLoginAdapter()
        >>> client = Client("config.yaml", login_adapter=mock_adapter)
        >>> client.login()
    """
    
    def __init__(
        self,
        config: Union[str, Config],
        login_adapter: Optional[LoginPort] = None
    ):
        """Initialize Client with configuration and optional login adapter.
        
        Args:
            config: Either a path to config YAML file or a Config object
            login_adapter: Optional login adapter for dependency injection.
                          If not provided, uses SinopacLoginAdapter by default.
        
        Raises:
            FileNotFoundError: When config file path doesn't exist
            ValueError: When config is invalid
        
        Examples:
            >>> client = Client("config.yaml")
            >>> client = Client(Config("config.yaml"))
            >>> client = Client("config.yaml", login_adapter=custom_adapter)
        """
        # Load configuration
        if isinstance(config, str):
            self.config = Config(config)
        elif isinstance(config, Config):
            self.config = config
        else:
            raise ValueError("config must be either a file path string or Config object")
        
        # Set login adapter (use injected one or default)
        self.login_adapter = login_adapter or SinopacLoginAdapter()
        
        # Initialize session-related attributes
        self.sj: Optional[LoginResponseDTO] = None
        self.is_logged_in: bool = False
    
    def login(self) -> LoginResponseDTO:
        """Perform login operation using the configured credentials.
        
        This method calls the login adapter with credentials from config
        and stores the result in the 'sj' attribute. After successful login,
        the 'is_logged_in' flag is set to True.
        
        Returns:
            LoginResponseDTO containing session information and token
        
        Raises:
            AuthenticationError: When login credentials are invalid
            ConnectionError: When connection to server fails
            DataFormatError: When response format is invalid
            ParameterError: When input parameters are invalid
            ServerError: When server returns error status code
            LoginException: For other login-related errors
        
        Examples:
            >>> client = Client("config.yaml")
            >>> response = client.login()
            >>> print(f"Logged in with token: {response.token}")
            >>> print(f"Session ID: {response.session_id}")
            >>> print(f"Client session: {client.sj}")
            >>> print(f"Is logged in: {client.is_logged_in}")
            True
        """
        # Create login request from config
        login_request = LoginRequestDTO(
            api_key=self.config.api_key,
            secret_key=self.config.secret_key,
            person_id=self.config.person_id,
            ca_password=self.config.ca_password
        )
        
        # Call login adapter
        try:
            response = self.login_adapter.login(login_request)
        except LoginException as e:
            # Re-raise login exceptions as-is
            self.is_logged_in = False
            self.sj = None
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            self.is_logged_in = False
            self.sj = None
            raise LoginException(
                f"Unexpected error during login: {str(e)}",
                original_error=e
            )
        
        # Store session and update login status
        self.sj = response
        self.is_logged_in = True
        
        return response
    
    def logout(self) -> None:
        """Logout and clear session.
        
        This method clears the session (sj) and sets is_logged_in to False.
        Note: This is a local logout and doesn't call any server-side logout API.
        
        Examples:
            >>> client = Client("config.yaml")
            >>> client.login()
            >>> client.logout()
            >>> print(client.is_logged_in)
            False
            >>> print(client.sj)
            None
        """
        self.sj = None
        self.is_logged_in = False
    
    def __repr__(self) -> str:
        """Return string representation of Client.
        
        Returns:
            String representation showing login status
        
        Examples:
            >>> client = Client("config.yaml")
            >>> print(repr(client))
            Client(is_logged_in=False)
            >>> client.login()
            >>> print(repr(client))
            Client(is_logged_in=True, user_id='A123456789')
        """
        if self.is_logged_in and self.sj:
            return f"Client(is_logged_in={self.is_logged_in}, user_id='{self.sj.user_id}')"
        return f"Client(is_logged_in={self.is_logged_in})"
    
    def __enter__(self):
        """Context manager entry.
        
        Examples:
            >>> with Client("config.yaml") as client:
            ...     client.login()
            ...     # Do trading operations
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.
        
        Automatically logout when exiting context.
        """
        self.logout()
        return False
