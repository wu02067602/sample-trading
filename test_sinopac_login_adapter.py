"""Unit tests for SinopacLoginAdapter.

This module contains comprehensive tests for the SinopacLoginAdapter class,
using mocks to avoid dependency on the actual Sinopac SDK.
"""

import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError

from sinopac_login_adapter import SinopacLoginAdapter
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    DataFormatError,
    ParameterError,
    ServerError
)


class TestSinopacLoginAdapter:
    """Test suite for SinopacLoginAdapter."""
    
    def setup_method(self):
        """Set up test fixtures before each test method.
        
        This method is called before each test to create fresh instances
        of test objects.
        """
        self.adapter = SinopacLoginAdapter()
        self.valid_request = LoginRequestDTO(
            api_key="test_api_key",
            secret_key="test_secret_key",
            person_id="A123456789",
            ca_password="test_password"
        )
    
    def test_successful_login_returns_dto_with_token(self):
        """Test successful login returns DTO with token and necessary information.
        
        This test verifies that when the SDK responds with a successful login,
        the adapter correctly parses the response and returns a LoginResponseDTO
        containing the token and all necessary session information.
        
        Expected behavior:
            - Should return LoginResponseDTO instance
            - Response should have success=True
            - Response should contain valid token
            - Response should contain session_id and user_id
            - Response should contain login_time
        """
        # Arrange: Create mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "abc123token456",
            "session_id": "session_20251006_001",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:30:00",
            "message": "Login successful"
        }
        
        # Create mock HTTP client
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_response
        
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Act: Perform login
        response = adapter.login(self.valid_request)
        
        # Assert: Verify response
        assert isinstance(response, LoginResponseDTO)
        assert response.success is True
        assert response.token == "abc123token456"
        assert response.session_id == "session_20251006_001"
        assert response.user_id == "A123456789"
        assert isinstance(response.login_time, datetime)
        assert response.message == "Login successful"
    
    def test_authentication_failure_raises_authentication_error(self):
        """Test authentication failure raises AuthenticationError.
        
        This test verifies that when the SDK responds with authentication
        failure (invalid credentials), the adapter raises an appropriate
        AuthenticationError exception.
        
        Expected behavior:
            - Should raise AuthenticationError
            - Error message should indicate authentication failure
        """
        # Test case 1: 401 Unauthorized
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.json.return_value = {"error": "Invalid credentials"}
        
        mock_http_client_401 = Mock()
        mock_http_client_401.post.return_value = mock_response_401
        
        adapter_401 = SinopacLoginAdapter(http_client=mock_http_client_401)
        
        with pytest.raises(AuthenticationError) as exc_info:
            adapter_401.login(self.valid_request)
        
        assert "authentication failed" in str(exc_info.value).lower()
        assert "401" in str(exc_info.value)
        
        # Test case 2: 403 Forbidden
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        
        mock_http_client_403 = Mock()
        mock_http_client_403.post.return_value = mock_response_403
        
        adapter_403 = SinopacLoginAdapter(http_client=mock_http_client_403)
        
        with pytest.raises(AuthenticationError) as exc_info:
            adapter_403.login(self.valid_request)
        
        assert "403" in str(exc_info.value)
        
        # Test case 3: Response with success=False
        mock_response_false = Mock()
        mock_response_false.status_code = 200
        mock_response_false.json.return_value = {
            "success": False,
            "message": "Invalid username or password"
        }
        
        mock_http_client_false = Mock()
        mock_http_client_false.post.return_value = mock_response_false
        
        adapter_false = SinopacLoginAdapter(http_client=mock_http_client_false)
        
        with pytest.raises(AuthenticationError) as exc_info:
            adapter_false.login(self.valid_request)
        
        assert "invalid username or password" in str(exc_info.value).lower()
    
    def test_connection_failure_raises_connection_error(self):
        """Test connection failure or timeout raises ConnectionError.
        
        This test verifies that when the SDK cannot connect to the server
        or when connection times out, the adapter raises a ConnectionError.
        
        Expected behavior:
            - Should raise ConnectionError for timeout
            - Should raise ConnectionError for connection failure
            - Error message should indicate connection issue
        """
        # Test case 1: Connection timeout
        mock_http_client_timeout = Mock()
        mock_http_client_timeout.post.side_effect = Timeout("Connection timed out")
        
        adapter_timeout = SinopacLoginAdapter(http_client=mock_http_client_timeout)
        
        with pytest.raises(ConnectionError) as exc_info:
            adapter_timeout.login(self.valid_request)
        
        assert "timeout" in str(exc_info.value).lower()
        
        # Test case 2: Connection error
        mock_http_client_conn = Mock()
        mock_http_client_conn.post.side_effect = RequestsConnectionError("Cannot connect to server")
        
        adapter_conn = SinopacLoginAdapter(http_client=mock_http_client_conn)
        
        with pytest.raises(ConnectionError) as exc_info:
            adapter_conn.login(self.valid_request)
        
        assert "connect" in str(exc_info.value).lower()
    
    def test_invalid_response_format_raises_data_format_error(self):
        """Test invalid response format raises DataFormatError.
        
        This test verifies that when the SDK response has invalid format
        or missing required fields, the adapter raises a DataFormatError.
        
        Expected behavior:
            - Should raise DataFormatError for invalid JSON
            - Should raise DataFormatError for missing required fields
            - Should raise DataFormatError for invalid field types
        """
        # Test case 1: Invalid JSON
        mock_response_invalid_json = Mock()
        mock_response_invalid_json.status_code = 200
        mock_response_invalid_json.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        mock_http_client_invalid = Mock()
        mock_http_client_invalid.post.return_value = mock_response_invalid_json
        
        adapter_invalid = SinopacLoginAdapter(http_client=mock_http_client_invalid)
        
        with pytest.raises(DataFormatError) as exc_info:
            adapter_invalid.login(self.valid_request)
        
        assert "parse" in str(exc_info.value).lower() or "json" in str(exc_info.value).lower()
        
        # Test case 2: Missing required field (token)
        mock_response_missing_token = Mock()
        mock_response_missing_token.status_code = 200
        mock_response_missing_token.json.return_value = {
            "session_id": "session_001",
            "user_id": "A123456789"
            # token is missing
        }
        
        mock_http_client_missing = Mock()
        mock_http_client_missing.post.return_value = mock_response_missing_token
        
        adapter_missing = SinopacLoginAdapter(http_client=mock_http_client_missing)
        
        with pytest.raises(DataFormatError) as exc_info:
            adapter_missing.login(self.valid_request)
        
        assert "token" in str(exc_info.value).lower()
        
        # Test case 3: Empty token
        mock_response_empty_token = Mock()
        mock_response_empty_token.status_code = 200
        mock_response_empty_token.json.return_value = {
            "token": "",
            "session_id": "session_001",
            "user_id": "A123456789"
        }
        
        mock_http_client_empty = Mock()
        mock_http_client_empty.post.return_value = mock_response_empty_token
        
        adapter_empty = SinopacLoginAdapter(http_client=mock_http_client_empty)
        
        with pytest.raises(DataFormatError) as exc_info:
            adapter_empty.login(self.valid_request)
        
        assert "token" in str(exc_info.value).lower()
        
        # Test case 4: Non-dict response
        mock_response_non_dict = Mock()
        mock_response_non_dict.status_code = 200
        mock_response_non_dict.json.return_value = ["invalid", "response"]
        
        mock_http_client_non_dict = Mock()
        mock_http_client_non_dict.post.return_value = mock_response_non_dict
        
        adapter_non_dict = SinopacLoginAdapter(http_client=mock_http_client_non_dict)
        
        with pytest.raises(DataFormatError) as exc_info:
            adapter_non_dict.login(self.valid_request)
        
        assert "dictionary" in str(exc_info.value).lower()
    
    def test_incomplete_parameters_raise_parameter_error(self):
        """Test incomplete input parameters raise ParameterError.
        
        This test verifies that when required login information is missing
        or invalid, the adapter raises a ParameterError.
        
        Expected behavior:
            - Should raise ParameterError for None request
            - Should raise ParameterError for invalid request type
            - LoginRequestDTO should raise ValueError for empty fields (in __post_init__)
        """
        # Test case 1: None request
        with pytest.raises(ParameterError) as exc_info:
            self.adapter.login(None)
        
        assert "cannot be none" in str(exc_info.value).lower()
        
        # Test case 2: Invalid request type
        with pytest.raises(ParameterError) as exc_info:
            self.adapter.login({"api_key": "test"})  # Dict instead of DTO
        
        assert "must be" in str(exc_info.value).lower() or "instance" in str(exc_info.value).lower()
        
        # Test case 3: Empty api_key (caught by DTO validation)
        with pytest.raises(ValueError) as exc_info:
            LoginRequestDTO(
                api_key="",
                secret_key="secret",
                person_id="A123456789",
                ca_password="pass"
            )
        
        assert "api_key" in str(exc_info.value).lower()
        
        # Test case 4: Empty secret_key
        with pytest.raises(ValueError) as exc_info:
            LoginRequestDTO(
                api_key="key",
                secret_key="",
                person_id="A123456789",
                ca_password="pass"
            )
        
        assert "secret_key" in str(exc_info.value).lower()
    
    def test_http_error_status_codes_raise_server_error(self):
        """Test HTTP error status codes raise ServerError.
        
        This test verifies that when the SDK responds with HTTP error
        status codes (4xx, 5xx), the adapter raises appropriate ServerError.
        
        Expected behavior:
            - Should raise ServerError for 500 Internal Server Error
            - Should raise ServerError for 503 Service Unavailable
            - Should raise ServerError for other 4xx/5xx codes
            - Exception should include status code
        """
        # Test case 1: 500 Internal Server Error
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        
        mock_http_client_500 = Mock()
        mock_http_client_500.post.return_value = mock_response_500
        
        adapter_500 = SinopacLoginAdapter(http_client=mock_http_client_500)
        
        with pytest.raises(ServerError) as exc_info:
            adapter_500.login(self.valid_request)
        
        assert exc_info.value.status_code == 500
        assert "500" in str(exc_info.value)
        
        # Test case 2: 503 Service Unavailable
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        
        mock_http_client_503 = Mock()
        mock_http_client_503.post.return_value = mock_response_503
        
        adapter_503 = SinopacLoginAdapter(http_client=mock_http_client_503)
        
        with pytest.raises(ServerError) as exc_info:
            adapter_503.login(self.valid_request)
        
        assert exc_info.value.status_code == 503
        assert "503" in str(exc_info.value)
        
        # Test case 3: 400 Bad Request
        mock_response_400 = Mock()
        mock_response_400.status_code = 400
        
        mock_http_client_400 = Mock()
        mock_http_client_400.post.return_value = mock_response_400
        
        adapter_400 = SinopacLoginAdapter(http_client=mock_http_client_400)
        
        with pytest.raises(ServerError) as exc_info:
            adapter_400.login(self.valid_request)
        
        assert exc_info.value.status_code == 400
        assert "400" in str(exc_info.value)
    
    def test_adapter_calls_http_client_with_correct_parameters(self):
        """Test Adapter correctly calls HTTP client with proper parameters.
        
        This test verifies that the adapter calls the underlying HTTP client
        with correct URL, headers, and body parameters.
        
        Expected behavior:
            - Should call POST method
            - Should use correct URL
            - Should include correct headers (Content-Type, Accept)
            - Should include all credentials in body
            - Should set timeout
        """
        # Arrange: Create mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token",
            "session_id": "test_session",
            "user_id": "A123456789",
            "login_time": "2025-10-06T10:30:00"
        }
        
        # Create mock HTTP client
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_response
        
        base_url = "https://test.api.sinopac.com"
        timeout = 45
        adapter = SinopacLoginAdapter(
            base_url=base_url,
            timeout=timeout,
            http_client=mock_http_client
        )
        
        # Act: Perform login
        adapter.login(self.valid_request)
        
        # Assert: Verify HTTP client was called with correct parameters
        mock_http_client.post.assert_called_once()
        
        call_args = mock_http_client.post.call_args
        
        # Verify URL
        assert call_args[0][0] == f"{base_url}/v1/auth/login"
        
        # Verify headers
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        
        # Verify body
        body = call_args[1]["json"]
        assert body["api_key"] == self.valid_request.api_key
        assert body["secret_key"] == self.valid_request.secret_key
        assert body["person_id"] == self.valid_request.person_id
        assert body["ca_password"] == self.valid_request.ca_password
        
        # Verify timeout
        assert call_args[1]["timeout"] == timeout
    
    def test_adapter_initialization_with_custom_parameters(self):
        """Test adapter initialization with custom parameters.
        
        This test verifies that the adapter can be initialized with
        custom base_url, timeout, and http_client parameters.
        
        Expected behavior:
            - Should accept custom base_url
            - Should accept custom timeout
            - Should accept custom http_client
        """
        custom_base_url = "https://custom.api.com"
        custom_timeout = 60
        custom_http_client = Mock()
        
        adapter = SinopacLoginAdapter(
            base_url=custom_base_url,
            timeout=custom_timeout,
            http_client=custom_http_client
        )
        
        assert adapter.base_url == custom_base_url
        assert adapter.timeout == custom_timeout
        assert adapter.http_client == custom_http_client
    
    def test_response_parsing_with_optional_fields(self):
        """Test response parsing handles optional fields correctly.
        
        This test verifies that the adapter can handle responses
        with or without optional fields like message and login_time.
        
        Expected behavior:
            - Should handle missing login_time (use current time)
            - Should handle missing message (use default)
            - Should still return valid LoginResponseDTO
        """
        # Arrange: Response without optional fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token",
            "session_id": "test_session",
            "user_id": "A123456789"
            # login_time and message are missing
        }
        
        mock_http_client = Mock()
        mock_http_client.post.return_value = mock_response
        
        adapter = SinopacLoginAdapter(http_client=mock_http_client)
        
        # Act
        response = adapter.login(self.valid_request)
        
        # Assert
        assert response.token == "test_token"
        assert response.session_id == "test_session"
        assert response.user_id == "A123456789"
        assert isinstance(response.login_time, datetime)
        assert response.message == "Login successful"  # Default message
