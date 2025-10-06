"""Unit tests for Client class.

This module contains comprehensive unit tests for the Client class,
using mocks to avoid dependency on actual config files and adapters.
"""

from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest

from client import Client
from config import Config
from login_dto import LoginResponseDTO
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    LoginException
)


class TestClientUnit:
    """Unit test suite for Client class.
    
    These tests use mocks to isolate the Client class from its dependencies,
    ensuring that we test only the Client's behavior without relying on
    external components like Config or LoginAdapter.
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock config
        self.mock_config = Mock(spec=Config)
        self.mock_config.api_key = "test_api_key"
        self.mock_config.secret_key = "test_secret_key"
        self.mock_config.person_id = "A123456789"
        self.mock_config.ca_password = "test_password"
        
        # Create mock login adapter
        self.mock_adapter = Mock()
        
        # Create mock login response
        self.mock_response = LoginResponseDTO(
            success=True,
            token="test_token_123",
            session_id="test_session_001",
            user_id="A123456789",
            login_time=datetime.now(),
            message="Login successful"
        )
    
    def test_client_initialization_with_config_object(self):
        """Test Client initialization with Config object.
        
        This test verifies that Client can be initialized with a Config object
        and that the config and adapter are properly set.
        
        Expected behavior:
            - Client should accept Config object
            - Client should store config
            - Client should use provided or default adapter
            - Initial login status should be False
            - Initial sj should be None
        """
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        
        assert client.config == self.mock_config
        assert client.login_adapter == self.mock_adapter
        assert client.is_logged_in is False
        assert client.sj is None
    
    @patch('client.Config')
    def test_client_initialization_with_config_path(self, mock_config_class):
        """Test Client initialization with config file path.
        
        This test verifies that Client can be initialized with a config
        file path string and properly creates a Config object.
        
        Expected behavior:
            - Client should accept string path
            - Client should create Config object from path
            - Config class should be instantiated with the path
        """
        mock_config_class.return_value = self.mock_config
        
        client = Client("config.yaml", login_adapter=self.mock_adapter)
        
        mock_config_class.assert_called_once_with("config.yaml")
        assert client.config == self.mock_config
    
    def test_client_initialization_with_invalid_config_type(self):
        """Test Client initialization with invalid config type.
        
        This test verifies that Client raises ValueError when initialized
        with an invalid config type (not string or Config object).
        
        Expected behavior:
            - Should raise ValueError
            - Error message should indicate invalid type
        """
        with pytest.raises(ValueError) as exc_info:
            Client(123)  # Invalid type
        
        assert "must be either a file path string or Config object" in str(exc_info.value)
    
    def test_login_calls_adapter(self):
        """Test that login method calls the login adapter.
        
        This test verifies that when login() is called, the Client properly
        calls the login adapter's login method with correct parameters.
        
        Expected behavior:
            - Should call adapter.login()
            - Should pass LoginRequestDTO with config credentials
            - Should call adapter exactly once
        """
        self.mock_adapter.login.return_value = self.mock_response
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        client.login()
        
        # Verify adapter was called
        self.mock_adapter.login.assert_called_once()
        
        # Verify the LoginRequestDTO was created with correct values
        call_args = self.mock_adapter.login.call_args
        login_request = call_args[0][0]
        
        assert login_request.api_key == self.mock_config.api_key
        assert login_request.secret_key == self.mock_config.secret_key
        assert login_request.person_id == self.mock_config.person_id
        assert login_request.ca_password == self.mock_config.ca_password
    
    def test_login_failure_raises_exception(self):
        """Test that login failure raises appropriate exception.
        
        This test verifies that when the login adapter raises an exception,
        the Client properly propagates the exception and maintains correct state.
        
        Expected behavior:
            - Should raise AuthenticationError when adapter raises it
            - Should set is_logged_in to False
            - Should set sj to None
        """
        # Configure mock to raise AuthenticationError
        self.mock_adapter.login.side_effect = AuthenticationError("Invalid credentials")
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.login()
        
        assert "invalid credentials" in str(exc_info.value).lower()
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_login_connection_error_raises_exception(self):
        """Test that connection error during login raises exception.
        
        This test verifies that when the adapter raises a ConnectionError,
        the Client properly handles it.
        
        Expected behavior:
            - Should raise ConnectionError when adapter raises it
            - Should maintain proper state
        """
        self.mock_adapter.login.side_effect = ConnectionError("Connection failed")
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        
        with pytest.raises(ConnectionError) as exc_info:
            client.login()
        
        assert "connection failed" in str(exc_info.value).lower()
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_login_success_stores_result_in_sj(self):
        """Test that successful login stores result in sj attribute.
        
        This test verifies that when login succeeds, the Client stores
        the login response in the 'sj' attribute and updates login status.
        
        Expected behavior:
            - Should store LoginResponseDTO in sj attribute
            - Should set is_logged_in to True
            - Should return the LoginResponseDTO
            - sj should contain all response data (token, session_id, user_id)
        """
        self.mock_adapter.login.return_value = self.mock_response
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        response = client.login()
        
        # Verify response is returned
        assert response == self.mock_response
        
        # Verify sj is set correctly
        assert client.sj == self.mock_response
        assert client.sj.token == "test_token_123"
        assert client.sj.session_id == "test_session_001"
        assert client.sj.user_id == "A123456789"
        
        # Verify login status
        assert client.is_logged_in is True
    
    def test_login_unexpected_error_wraps_exception(self):
        """Test that unexpected errors during login are wrapped.
        
        This test verifies that when an unexpected (non-LoginException)
        error occurs during login, it's wrapped in a LoginException.
        
        Expected behavior:
            - Should wrap unexpected exceptions in LoginException
            - Should preserve original exception
            - Should maintain proper state
        """
        self.mock_adapter.login.side_effect = RuntimeError("Unexpected error")
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        
        with pytest.raises(LoginException) as exc_info:
            client.login()
        
        assert "unexpected error during login" in str(exc_info.value).lower()
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_logout_clears_session(self):
        """Test that logout clears session and login status.
        
        This test verifies that the logout method properly clears
        the sj attribute and resets the login status.
        
        Expected behavior:
            - Should set sj to None
            - Should set is_logged_in to False
        """
        self.mock_adapter.login.return_value = self.mock_response
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        client.login()
        
        # Verify logged in
        assert client.is_logged_in is True
        assert client.sj is not None
        
        # Logout
        client.logout()
        
        # Verify logged out
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_repr_before_login(self):
        """Test string representation before login.
        
        This test verifies that the __repr__ method returns appropriate
        string representation when client is not logged in.
        
        Expected behavior:
            - Should show is_logged_in=False
            - Should not show user_id
        """
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        repr_str = repr(client)
        
        assert "Client(" in repr_str
        assert "is_logged_in=False" in repr_str
        assert "user_id" not in repr_str
    
    def test_repr_after_login(self):
        """Test string representation after login.
        
        This test verifies that the __repr__ method returns appropriate
        string representation when client is logged in.
        
        Expected behavior:
            - Should show is_logged_in=True
            - Should show user_id
        """
        self.mock_adapter.login.return_value = self.mock_response
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        client.login()
        repr_str = repr(client)
        
        assert "Client(" in repr_str
        assert "is_logged_in=True" in repr_str
        assert "user_id='A123456789'" in repr_str
    
    def test_context_manager_login_and_logout(self):
        """Test Client as context manager.
        
        This test verifies that Client can be used as a context manager
        and automatically logs out when exiting the context.
        
        Expected behavior:
            - Should support 'with' statement
            - Should return client instance
            - Should automatically logout on exit
        """
        self.mock_adapter.login.return_value = self.mock_response
        
        with Client(self.mock_config, login_adapter=self.mock_adapter) as client:
            client.login()
            assert client.is_logged_in is True
            assert client.sj is not None
            stored_client = client
        
        # After exiting context, should be logged out
        assert stored_client.is_logged_in is False
        assert stored_client.sj is None
    
    def test_multiple_login_calls_update_sj(self):
        """Test that multiple login calls update sj attribute.
        
        This test verifies that calling login() multiple times
        updates the sj attribute with the latest response.
        
        Expected behavior:
            - First login should set sj
            - Second login should update sj with new response
        """
        response1 = LoginResponseDTO(
            success=True,
            token="token_1",
            session_id="session_1",
            user_id="A123456789",
            login_time=datetime.now()
        )
        
        response2 = LoginResponseDTO(
            success=True,
            token="token_2",
            session_id="session_2",
            user_id="A123456789",
            login_time=datetime.now()
        )
        
        self.mock_adapter.login.side_effect = [response1, response2]
        
        client = Client(self.mock_config, login_adapter=self.mock_adapter)
        
        # First login
        client.login()
        assert client.sj.token == "token_1"
        assert client.sj.session_id == "session_1"
        
        # Second login
        client.login()
        assert client.sj.token == "token_2"
        assert client.sj.session_id == "session_2"
    
    def test_default_adapter_when_none_provided(self):
        """Test that Client uses default adapter when none provided.
        
        This test verifies that when no adapter is provided,
        Client creates a default SinopacLoginAdapter.
        
        Expected behavior:
            - Should create SinopacLoginAdapter by default
            - Should not be None
        """
        with patch('client.SinopacLoginAdapter') as mock_adapter_class:
            mock_adapter_instance = Mock()
            mock_adapter_class.return_value = mock_adapter_instance
            
            client = Client(self.mock_config)
            
            mock_adapter_class.assert_called_once()
            assert client.login_adapter == mock_adapter_instance
