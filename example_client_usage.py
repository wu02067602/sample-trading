"""Example usage of the Client class.

This module demonstrates how to use the Client class for
Sinopac trading system login operations.
"""

from client import Client
from login_exceptions import (
    AuthenticationError,
    ConnectionError,
    DataFormatError,
    ServerError,
    LoginException
)


def basic_usage():
    """Basic usage of Client class.
    
    This example shows the simplest way to use the Client class
    for login operations.
    """
    print("=" * 60)
    print("Basic Usage Example")
    print("=" * 60)
    
    try:
        # Create client with config file path
        client = Client("config.yaml")
        
        # Perform login
        print("Attempting to login...")
        response = client.login()
        
        # Access login information
        print(f"\n✅ Login successful!")
        print(f"Token: {response.token[:20]}...")
        print(f"Session ID: {response.session_id}")
        print(f"User ID: {response.user_id}")
        print(f"Login Time: {response.login_time}")
        print(f"Message: {response.message}")
        
        # Access session through client.sj
        print(f"\nClient session (sj) is available:")
        print(f"client.sj.token: {client.sj.token[:20]}...")
        print(f"client.is_logged_in: {client.is_logged_in}")
        
        # Logout when done
        print("\nLogging out...")
        client.logout()
        print(f"client.is_logged_in: {client.is_logged_in}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Config file not found: {e}")
    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
    except ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def context_manager_usage():
    """Using Client as a context manager.
    
    This example shows how to use the Client class with
    Python's context manager (with statement) for automatic cleanup.
    """
    print("\n" + "=" * 60)
    print("Context Manager Usage Example")
    print("=" * 60)
    
    try:
        # Use Client as context manager
        with Client("config.yaml") as client:
            print("Inside context manager...")
            client.login()
            
            print(f"\n✅ Login successful!")
            print(f"Token: {client.sj.token[:20]}...")
            print(f"User ID: {client.sj.user_id}")
            print(f"Is logged in: {client.is_logged_in}")
            
            # Do your trading operations here...
            print("\nPerforming trading operations...")
            # ...
            
        # Automatically logged out when exiting context
        print("\nExited context manager (automatically logged out)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def comprehensive_error_handling():
    """Comprehensive error handling example.
    
    This example shows how to handle all possible exceptions
    that can occur during login operations.
    """
    print("\n" + "=" * 60)
    print("Comprehensive Error Handling Example")
    print("=" * 60)
    
    try:
        client = Client("config.yaml")
        response = client.login()
        
        print(f"✅ Login successful!")
        print(f"Session ID: {response.session_id}")
        
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        print("Please ensure config.yaml exists in the current directory.")
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Please check your credentials in config.yaml:")
        print("  - api_key")
        print("  - secret_key")
        print("  - person_id")
        print("  - ca_password")
        
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("Possible causes:")
        print("  - Network connection issues")
        print("  - Server is down or unreachable")
        print("  - Firewall blocking the connection")
        print("  - Request timeout")
        
    except DataFormatError as e:
        print(f"❌ Data format error: {e}")
        print("The server response was invalid or incomplete.")
        print("This might be a server-side issue. Please try again later.")
        
    except ServerError as e:
        print(f"❌ Server error: {e}")
        if hasattr(e, 'status_code'):
            print(f"HTTP Status Code: {e.status_code}")
        print("The server encountered an error. Please try again later.")
        
    except LoginException as e:
        print(f"❌ Login error: {e}")
        print("An unexpected error occurred during login.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("An unexpected error occurred. Please contact support.")


def using_config_object():
    """Using Client with Config object.
    
    This example shows how to use the Client class with
    a Config object instead of a file path.
    """
    print("\n" + "=" * 60)
    print("Using Config Object Example")
    print("=" * 60)
    
    try:
        from config import Config
        
        # Create Config object first
        config = Config("config.yaml")
        print(f"Config loaded for user: {config.person_id}")
        
        # Create Client with Config object
        client = Client(config)
        
        # Perform login
        client.login()
        print(f"\n✅ Login successful!")
        print(f"User ID: {client.sj.user_id}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def checking_login_status():
    """Checking login status example.
    
    This example shows how to check if the client is logged in
    and access session information.
    """
    print("\n" + "=" * 60)
    print("Checking Login Status Example")
    print("=" * 60)
    
    try:
        client = Client("config.yaml")
        
        # Before login
        print(f"Before login:")
        print(f"  is_logged_in: {client.is_logged_in}")
        print(f"  sj: {client.sj}")
        print(f"  repr: {repr(client)}")
        
        # Perform login
        client.login()
        
        # After login
        print(f"\nAfter login:")
        print(f"  is_logged_in: {client.is_logged_in}")
        print(f"  sj: {client.sj is not None}")
        print(f"  repr: {repr(client)}")
        
        # Check session details
        if client.is_logged_in:
            print(f"\nSession details:")
            print(f"  Token: {client.sj.token[:20]}...")
            print(f"  Session ID: {client.sj.session_id}")
            print(f"  User ID: {client.sj.user_id}")
            print(f"  Login Time: {client.sj.login_time}")
        
        # Logout
        client.logout()
        
        # After logout
        print(f"\nAfter logout:")
        print(f"  is_logged_in: {client.is_logged_in}")
        print(f"  sj: {client.sj}")
        print(f"  repr: {repr(client)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def mock_example_for_testing():
    """Example showing how to use Client with mocked adapter for testing.
    
    This example demonstrates dependency injection for testing purposes.
    """
    print("\n" + "=" * 60)
    print("Mock Example for Testing")
    print("=" * 60)
    
    from unittest.mock import Mock
    from datetime import datetime
    from login_dto import LoginResponseDTO
    
    # Create a mock login adapter
    mock_adapter = Mock()
    
    # Configure the mock to return a successful response
    mock_response = LoginResponseDTO(
        success=True,
        token="mock_token_123",
        session_id="mock_session_001",
        user_id="A123456789",
        login_time=datetime.now(),
        message="Mock login successful"
    )
    mock_adapter.login.return_value = mock_response
    
    # Create client with mocked adapter
    client = Client("yaml_sample.yaml", login_adapter=mock_adapter)
    
    # Perform login (uses mock, no actual network call)
    response = client.login()
    
    print("✅ Mock login successful!")
    print(f"Token: {response.token}")
    print(f"Session ID: {response.session_id}")
    print(f"User ID: {response.user_id}")
    print("\nNote: This used a mock adapter, no actual API call was made.")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Client Class Usage Examples")
    print("=" * 60)
    print()
    
    # Run basic usage (commented out to avoid actual API calls)
    # basic_usage()
    
    # Run context manager example (commented out)
    # context_manager_usage()
    
    # Show error handling patterns
    # comprehensive_error_handling()
    
    # Show config object usage (commented out)
    # using_config_object()
    
    # Show login status checking (commented out)
    # checking_login_status()
    
    # Run mock example (safe to run)
    mock_example_for_testing()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNote: Most examples are commented out to avoid actual API calls.")
    print("Uncomment them in the code to try with real credentials.")


if __name__ == "__main__":
    main()
