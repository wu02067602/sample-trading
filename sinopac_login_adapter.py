"""Sinopac Login Adapter implementation.

This module provides a concrete implementation of the LoginPort interface
for Sinopac (永豐) trading system, following the Ports and Adapters pattern.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError

from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    DataFormatError,
    ParameterError,
    ServerError
)


class SinopacLoginAdapter(LoginPort):
    """Adapter for Sinopac SDK login operations.
    
    This adapter implements the LoginPort interface and provides
    integration with Sinopac (永豐) trading system API.
    
    Attributes:
        base_url: Base URL for Sinopac API
        timeout: Request timeout in seconds
        http_client: HTTP client for making requests (injectable for testing)
    
    Examples:
        >>> adapter = SinopacLoginAdapter()
        >>> request = LoginRequestDTO(
        ...     api_key="key",
        ...     secret_key="secret",
        ...     person_id="A123456789",
        ...     ca_password="pass"
        ... )
        >>> response = adapter.login(request)
        >>> print(response.token)
    """
    
    def __init__(
        self,
        base_url: str = "https://api.sinopac.com",
        timeout: int = 30,
        http_client: Optional[Any] = None
    ):
        """Initialize SinopacLoginAdapter.
        
        Args:
            base_url: Base URL for Sinopac API
            timeout: Request timeout in seconds
            http_client: Optional HTTP client (for testing with mocks)
        
        Examples:
            >>> adapter = SinopacLoginAdapter()
            >>> adapter = SinopacLoginAdapter(base_url="https://test.api.com")
            >>> adapter = SinopacLoginAdapter(timeout=60)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.http_client = http_client or requests
    
    def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """Perform login operation with Sinopac API.
        
        This method sends login credentials to Sinopac API and processes
        the response, converting it to a standardized LoginResponseDTO.
        
        Args:
            request: LoginRequestDTO containing login credentials
        
        Returns:
            LoginResponseDTO containing authentication token and session info
        
        Raises:
            ParameterError: When input parameters are invalid
            ConnectionError: When connection to server fails
            AuthenticationError: When credentials are invalid
            ServerError: When server returns error status code
            DataFormatError: When response format is invalid
        
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
        # Validate input parameters
        self._validate_request(request)
        
        # Prepare request
        url = f"{self.base_url}/v1/auth/login"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        body = {
            "api_key": request.api_key,
            "secret_key": request.secret_key,
            "person_id": request.person_id,
            "ca_password": request.ca_password
        }
        
        # Make HTTP request
        try:
            response = self.http_client.post(
                url,
                headers=headers,
                json=body,
                timeout=self.timeout
            )
        except Timeout as e:
            raise ConnectionError(
                "Connection timeout while connecting to Sinopac API",
                original_error=e
            )
        except RequestsConnectionError as e:
            raise ConnectionError(
                "Failed to connect to Sinopac API",
                original_error=e
            )
        except RequestException as e:
            raise ConnectionError(
                f"Request failed: {str(e)}",
                original_error=e
            )
        
        # Handle HTTP status codes
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(
                f"Authentication failed: Invalid credentials (status code: {response.status_code})"
            )
        
        if response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code
            )
        
        if response.status_code >= 400:
            raise ServerError(
                f"Client error: {response.status_code}",
                status_code=response.status_code
            )
        
        if response.status_code != 200:
            raise ServerError(
                f"Unexpected status code: {response.status_code}",
                status_code=response.status_code
            )
        
        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise DataFormatError(
                "Failed to parse JSON response",
                original_error=e
            )
        
        # Validate and extract response data
        return self._parse_response(response_data)
    
    def _validate_request(self, request: LoginRequestDTO) -> None:
        """Validate login request parameters.
        
        Args:
            request: LoginRequestDTO to validate
        
        Raises:
            ParameterError: When required parameters are missing or invalid
        
        Examples:
            >>> adapter = SinopacLoginAdapter()
            >>> request = LoginRequestDTO("", "secret", "id", "pass")
            >>> adapter._validate_request(request)
            Traceback (most recent call last):
                ...
            ParameterError: api_key cannot be empty
        """
        if not request:
            raise ParameterError("Login request cannot be None")
        
        if not isinstance(request, LoginRequestDTO):
            raise ParameterError("Request must be a LoginRequestDTO instance")
        
        # Note: LoginRequestDTO already validates non-empty fields in __post_init__
        # But we add extra validation here for clarity
        if not request.api_key or not request.api_key.strip():
            raise ParameterError("api_key cannot be empty")
        
        if not request.secret_key or not request.secret_key.strip():
            raise ParameterError("secret_key cannot be empty")
        
        if not request.person_id or not request.person_id.strip():
            raise ParameterError("person_id cannot be empty")
        
        if not request.ca_password or not request.ca_password.strip():
            raise ParameterError("ca_password cannot be empty")
    
    def _parse_response(self, response_data: Dict[str, Any]) -> LoginResponseDTO:
        """Parse and validate API response data.
        
        Args:
            response_data: Raw response data from API
        
        Returns:
            LoginResponseDTO with parsed data
        
        Raises:
            DataFormatError: When response format is invalid or missing required fields
        
        Examples:
            >>> adapter = SinopacLoginAdapter()
            >>> data = {
            ...     "success": True,
            ...     "token": "abc123",
            ...     "session_id": "session_001",
            ...     "user_id": "A123456789",
            ...     "login_time": "2025-10-06T10:00:00"
            ... }
            >>> response = adapter._parse_response(data)
            >>> print(response.token)
            'abc123'
        """
        if not isinstance(response_data, dict):
            raise DataFormatError("Response data must be a dictionary")
        
        # Check for authentication failure in response
        if "success" in response_data and not response_data["success"]:
            error_message = response_data.get("message", "Authentication failed")
            raise AuthenticationError(error_message)
        
        # Validate required fields
        required_fields = ["token", "session_id", "user_id"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if missing_fields:
            raise DataFormatError(
                f"Missing required fields in response: {', '.join(missing_fields)}"
            )
        
        # Extract and validate token
        token = response_data.get("token")
        if not token or not isinstance(token, str) or not token.strip():
            raise DataFormatError("Invalid or empty token in response")
        
        # Extract session_id
        session_id = response_data.get("session_id")
        if not session_id or not isinstance(session_id, str):
            raise DataFormatError("Invalid or empty session_id in response")
        
        # Extract user_id
        user_id = response_data.get("user_id")
        if not user_id or not isinstance(user_id, str):
            raise DataFormatError("Invalid or empty user_id in response")
        
        # Parse login time
        login_time_str = response_data.get("login_time")
        if login_time_str:
            try:
                login_time = datetime.fromisoformat(login_time_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                raise DataFormatError(
                    f"Invalid login_time format: {login_time_str}",
                    original_error=e
                )
        else:
            login_time = datetime.now()
        
        # Extract optional message
        message = response_data.get("message", "Login successful")
        
        # Create and return DTO
        return LoginResponseDTO(
            success=True,
            token=token,
            session_id=session_id,
            user_id=user_id,
            login_time=login_time,
            message=message
        )
