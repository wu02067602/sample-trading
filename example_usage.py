"""Example usage of the Sinopac Login Adapter.

This module demonstrates how to use the Ports and Adapters architecture
for Sinopac login operations.
"""

from config import Config
from login_dto import LoginRequestDTO
from sinopac_login_adapter import SinopacLoginAdapter
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    DataFormatError,
    ParameterError,
    ServerError
)


def main():
    """Main function demonstrating login adapter usage.
    
    This function shows how to:
    1. Load configuration from YAML file
    2. Create login request DTO
    3. Initialize the adapter
    4. Perform login operation
    5. Handle various exceptions
    
    Examples:
        >>> python example_usage.py
    """
    try:
        # Step 1: Load configuration from YAML file
        print("Loading configuration...")
        config = Config("config.yaml")
        
        # Step 2: Create login request DTO
        print("Creating login request...")
        login_request = LoginRequestDTO(
            api_key=config.api_key,
            secret_key=config.secret_key,
            person_id=config.person_id,
            ca_password=config.ca_password
        )
        
        # Step 3: Initialize the adapter
        print("Initializing Sinopac login adapter...")
        adapter = SinopacLoginAdapter(
            base_url="https://api.sinopac.com",
            timeout=30
        )
        
        # Step 4: Perform login operation
        print("Attempting to login...")
        response = adapter.login(login_request)
        
        # Step 5: Handle successful login
        if response.success:
            print("\n✅ Login successful!")
            print(f"Token: {response.token[:20]}...")  # Show first 20 chars
            print(f"Session ID: {response.session_id}")
            print(f"User ID: {response.user_id}")
            print(f"Login Time: {response.login_time}")
            print(f"Message: {response.message}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Configuration file not found: {e}")
        
    except ParameterError as e:
        print(f"\n❌ Parameter error: {e}")
        print("Please check your configuration file for missing or invalid parameters.")
        
    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("Please check your credentials.")
        
    except ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print("Please check your network connection and server availability.")
        
    except DataFormatError as e:
        print(f"\n❌ Data format error: {e}")
        print("The server response was invalid or incomplete.")
        
    except ServerError as e:
        print(f"\n❌ Server error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        print("The server encountered an error. Please try again later.")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def example_with_custom_adapter():
    """Example showing how to use adapter with dependency injection.
    
    This demonstrates how the Ports and Adapters pattern allows
    for easy testing and swapping of implementations.
    
    Examples:
        >>> example_with_custom_adapter()
    """
    # You can inject a custom HTTP client for testing
    from unittest.mock import Mock
    
    # Create a mock HTTP client
    mock_http_client = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token": "test_token_123",
        "session_id": "test_session_001",
        "user_id": "A123456789",
        "login_time": "2025-10-06T10:30:00",
        "message": "Test login successful"
    }
    mock_http_client.post.return_value = mock_response
    
    # Create adapter with mocked client
    adapter = SinopacLoginAdapter(http_client=mock_http_client)
    
    # Create login request
    request = LoginRequestDTO(
        api_key="test_api_key",
        secret_key="test_secret_key",
        person_id="A123456789",
        ca_password="test_password"
    )
    
    # Perform login
    response = adapter.login(request)
    
    print("\n🧪 Testing with mock adapter:")
    print(f"Success: {response.success}")
    print(f"Token: {response.token}")
    print(f"Session ID: {response.session_id}")
    print(f"User ID: {response.user_id}")


if __name__ == "__main__":
    print("=" * 60)
    print("Sinopac Login Adapter - Example Usage")
    print("=" * 60)
    print()
    
    # Run main example
    main()
    
    print("\n" + "=" * 60)
    print()
    
    # Run mock example
    example_with_custom_adapter()
    
    print("\n" + "=" * 60)
