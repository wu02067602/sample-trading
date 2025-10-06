"""Integration tests for Client class.

This module contains integration tests for the Client class,
testing the integration between Client, Config, and LoginAdapter
without mocking those components (but still mocking HTTP calls).
"""

import tempfile
from datetime import datetime
from unittest.mock import Mock

import pytest
import yaml

from client import Client
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    ServerError
)
from sinopac_login_adapter import SinopacLoginAdapter


class TestClientIntegration:
    """Integration test suite for Client class.
    
    These tests verify the integration between Client, Config, and LoginAdapter,
    using real instances of these classes but mocking external HTTP calls.
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary config file
        self.config_data = {
            'api_key': 'integration_test_api_key',
            'secret_key': 'integration_test_secret_key',
            'person_id': 'A123456789',
            'ca_password': 'integration_test_password'
        }
        
        self.temp_config_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )
        yaml.dump(self.config_data, self.temp_config_file)
        self.temp_config_file.close()
        self.config_path = self.temp_config_file.name
    
    def teardown_method(self):
        """Clean up after each test method."""
        import os
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
    
    def test_client_with_real_config_calls_adapter(self):
        """Test Client with real Config calls the login adapter.
        
        This integration test verifies that:
        1. Client can load real Config from YAML file
        2. Client creates LoginRequestDTO with config values
        3. Client calls the login adapter
        4. The entire flow works end-to-end
        
        Expected behavior:
            - Client should load config from file
            - Client should call adapter with correct parameters
            - Adapter should be called exactly once
        """
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {
            "token": "integration_test_token",
            "session_id": "integration_test_session",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:00:00",
            "message": "Integration test login successful"
        }
        
        # Create mock HTTP client
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client with real config and mocked adapter
        client = Client(self.config_path, login_adapter=adapter)
        
        # Perform login
        response = client.login()
        
        # Verify HTTP client was called
        mock_http_client.post.assert_called_once()
        
        # Verify call parameters
        call_args = mock_http_client.post.call_args
        body = call_args[1]['json']
        
        assert body['api_key'] == 'integration_test_api_key'
        assert body['secret_key'] == 'integration_test_secret_key'
        assert body['person_id'] == 'A123456789'
        assert body['ca_password'] == 'integration_test_password'
        
        # Verify response
        assert response.token == "integration_test_token"
        assert response.session_id == "integration_test_session"
    
    def test_client_integration_login_failure_raises_exception(self):
        """Test Client with real adapter raises exception on login failure.
        
        This integration test verifies that when authentication fails,
        the exception properly propagates through the entire stack:
        Adapter -> Client -> Test
        
        Expected behavior:
            - Should raise AuthenticationError
            - Client state should be properly maintained
        """
        # Create mock HTTP response for authentication failure
        mock_http_response = Mock()
        mock_http_response.status_code = 401
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client
        client = Client(self.config_path, login_adapter=adapter)
        
        # Attempt login and expect exception
        with pytest.raises(AuthenticationError) as exc_info:
            client.login()
        
        assert "401" in str(exc_info.value)
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_client_integration_connection_error_raises_exception(self):
        """Test Client with real adapter raises exception on connection error.
        
        This integration test verifies that connection errors properly
        propagate through the entire stack.
        
        Expected behavior:
            - Should raise ConnectionError
            - Client state should be properly maintained
        """
        from requests.exceptions import Timeout
        
        # Configure mock to raise Timeout
        mock_http_client = Mock()
        mock_http_client.post.side_effect = Timeout("Connection timeout")
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client
        client = Client(self.config_path, login_adapter=adapter)
        
        # Attempt login and expect exception
        with pytest.raises(ConnectionError) as exc_info:
            client.login()
        
        assert "timeout" in str(exc_info.value).lower()
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_client_integration_server_error_raises_exception(self):
        """Test Client with real adapter raises exception on server error.
        
        This integration test verifies that server errors (5xx) properly
        propagate through the entire stack.
        
        Expected behavior:
            - Should raise ServerError
            - Should include status code
            - Client state should be properly maintained
        """
        # Create mock HTTP response for server error
        mock_http_response = Mock()
        mock_http_response.status_code = 500
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client
        client = Client(self.config_path, login_adapter=adapter)
        
        # Attempt login and expect exception
        with pytest.raises(ServerError) as exc_info:
            client.login()
        
        assert exc_info.value.status_code == 500
        assert "500" in str(exc_info.value)
        assert client.is_logged_in is False
        assert client.sj is None
    
    def test_client_integration_successful_login_stores_sj(self):
        """Test Client with real config and adapter successfully logs in.
        
        This integration test verifies the complete successful login flow:
        1. Client loads config from YAML
        2. Client creates LoginRequestDTO
        3. Adapter processes the request
        4. Adapter calls HTTP client
        5. Adapter parses response
        6. Client stores result in sj
        
        Expected behavior:
            - Should successfully complete entire login flow
            - Should store LoginResponseDTO in sj
            - Should set is_logged_in to True
            - sj should contain all expected data
        """
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {
            "token": "full_integration_token_xyz",
            "session_id": "full_integration_session_123",
            "user_id": "A123456789",
            "login_time": "2025-10-06T15:30:00",
            "message": "Full integration test successful"
        }
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client with real config and adapter
        client = Client(self.config_path, login_adapter=adapter)
        
        # Perform login
        response = client.login()
        
        # Verify client state
        assert client.is_logged_in is True
        assert client.sj is not None
        
        # Verify sj contains expected data
        assert client.sj.success is True
        assert client.sj.token == "full_integration_token_xyz"
        assert client.sj.session_id == "full_integration_session_123"
        assert client.sj.user_id == "A123456789"
        assert client.sj.message == "Full integration test successful"
        
        # Verify returned response matches sj
        assert response == client.sj
    
    def test_client_integration_with_yaml_sample(self):
        """Test Client with yaml_sample.yaml file.
        
        This integration test verifies that Client can work with
        the actual yaml_sample.yaml file in the project.
        
        Expected behavior:
            - Should load config from yaml_sample.yaml
            - Should successfully call adapter
            - Should store result in sj
        """
        import os
        
        # Check if yaml_sample.yaml exists
        if not os.path.exists("yaml_sample.yaml"):
            pytest.skip("yaml_sample.yaml not found")
        
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {
            "token": "yaml_sample_token",
            "session_id": "yaml_sample_session",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:00:00"
        }
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        # Create adapter with mocked HTTP client
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Create client with yaml_sample.yaml
        client = Client("yaml_sample.yaml", login_adapter=adapter)
        
        # Perform login
        response = client.login()
        
        # Verify success
        assert client.is_logged_in is True
        assert client.sj is not None
        assert client.sj.token == "yaml_sample_token"
    
    def test_client_integration_context_manager(self):
        """Test Client as context manager in integration scenario.
        
        This integration test verifies that Client works properly as
        a context manager with real Config and Adapter.
        
        Expected behavior:
            - Should work as context manager
            - Should login successfully within context
            - Should auto-logout when exiting context
        """
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {
            "token": "context_test_token",
            "session_id": "context_test_session",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:00:00"
        }
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Use client as context manager
        with Client(self.config_path, login_adapter=adapter) as client:
            client.login()
            
            # Inside context: should be logged in
            assert client.is_logged_in is True
            assert client.sj is not None
            assert client.sj.token == "context_test_token"
            
            # Store reference for verification after context
            client_ref = client
        
        # Outside context: should be logged out
        assert client_ref.is_logged_in is False
        assert client_ref.sj is None
    
    def test_client_integration_multiple_logins(self):
        """Test Client can perform multiple logins.
        
        This integration test verifies that Client can perform
        multiple login operations and properly updates sj each time.
        
        Expected behavior:
            - First login should set sj
            - Second login should update sj with new values
            - Both logins should complete successfully
        """
        mock_http_client = Mock()
        
        # Configure different responses for each login
        response1 = Mock()
        response1.status_code = 200
        response1.json.return_value = {
            "token": "token_first",
            "session_id": "session_first",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:00:00"
        }
        
        response2 = Mock()
        response2.status_code = 200
        response2.json.return_value = {
            "token": "token_second",
            "session_id": "session_second",
            "user_id": "A123456789",
            "login_time": "2025-10-06T11:00:00"
        }
        
        mock_http_client.post.side_effect = [response1, response2]
        
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        client = Client(self.config_path, login_adapter=adapter)
        
        # First login
        client.login()
        assert client.sj.token == "token_first"
        assert client.sj.session_id == "session_first"
        
        # Second login
        client.login()
        assert client.sj.token == "token_second"
        assert client.sj.session_id == "session_second"
        
        # Verify both calls were made
        assert mock_http_client.post.call_count == 2
    
    def test_client_integration_logout_after_login(self):
        """Test Client logout functionality in integration scenario.
        
        This integration test verifies that logout properly clears
        the session after a successful login.
        
        Expected behavior:
            - Login should succeed and set sj
            - Logout should clear sj and login status
        """
        # Create mock HTTP response
        mock_http_response = Mock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = {
            "token": "logout_test_token",
            "session_id": "logout_test_session",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:00:00"
        }
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_http_response
        
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        client = Client(self.config_path, login_adapter=adapter)
        
        # Login
        client.login()
        assert client.is_logged_in is True
        assert client.sj is not None
        
        # Logout
        client.logout()
        assert client.is_logged_in is False
        assert client.sj is None
