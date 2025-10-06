"""Client 类的单元测试。

此模块包含 Client 类的所有单元测试，使用 mock 避免依赖真实实现。
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from client import Client
from config import Config
from login_port import LoginPort
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import (
    LoginAuthenticationError,
    LoginConnectionError,
    LoginDataFormatError,
    LoginError
)


class TestClientUnitTests:
    """Client 类的单元测试套件。
    
    使用 mock 对象进行隔离测试，不依赖真实的 Config 和 Adapter 实现。
    """
    
    def test_client_should_call_login_adapter(self):
        """测试当调用 Client.login() 时，应该调用登录适配器的 login 方法。
        
        验证 Client 正确调用了注入的登录适配器。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> client = Client(config, adapter)
            >>> client.login()
            >>> adapter.login.assert_called_once()
        
        Raises:
            None
        """
        # Arrange - 创建 mock 对象
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        mock_response = LoginResponseDTO(
            token='abc123token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() + timedelta(hours=1)
        )
        mock_adapter.login.return_value = mock_response
        
        client = Client(mock_config, mock_adapter)
        
        # Act
        client.login()
        
        # Assert - 验证调用了适配器的 login 方法
        mock_adapter.login.assert_called_once()
        
        # 验证传递的参数正确
        call_args = mock_adapter.login.call_args[0][0]
        assert isinstance(call_args, LoginRequestDTO)
        assert call_args.person_id == 'A123456789'
        assert call_args.api_key == 'test_key'
        assert call_args.api_secret == 'test_secret'
    
    def test_client_should_raise_exception_when_login_fails(self):
        """测试当登录适配器抛出异常时，Client 应该向上传播该异常。
        
        验证 Client 正确处理登录失败的情况。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> adapter.login.side_effect = LoginAuthenticationError("认证失败")
            >>> client = Client(config, adapter)
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginAuthenticationError: 认证失败
        
        Raises:
            LoginAuthenticationError: 当身份验证失败时
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'wrong_key'
        mock_config.api_secret = 'wrong_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        mock_adapter.login.side_effect = LoginAuthenticationError("身份验证失败")
        
        client = Client(mock_config, mock_adapter)
        
        # Act & Assert
        with pytest.raises(LoginAuthenticationError) as exc_info:
            client.login()
        
        assert '身份验证失败' in str(exc_info.value)
        
        # 验证 sj 属性没有被设置
        assert client.sj is None
    
    def test_client_should_raise_connection_error_when_connection_fails(self):
        """测试当连线失败时，Client 应该抛出 LoginConnectionError。
        
        验证 Client 正确处理连线错误。
        
        Examples:
            >>> adapter.login.side_effect = LoginConnectionError("连线超时")
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginConnectionError: 连线超时
        
        Raises:
            LoginConnectionError: 当连线失败时
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        mock_adapter.login.side_effect = LoginConnectionError("连线超时")
        
        client = Client(mock_config, mock_adapter)
        
        # Act & Assert
        with pytest.raises(LoginConnectionError) as exc_info:
            client.login()
        
        assert '连线超时' in str(exc_info.value)
    
    def test_client_should_raise_data_format_error_when_response_invalid(self):
        """测试当响应格式错误时，Client 应该抛出 LoginDataFormatError。
        
        验证 Client 正确处理数据格式错误。
        
        Examples:
            >>> adapter.login.side_effect = LoginDataFormatError("响应缺少必要字段")
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: 响应缺少必要字段
        
        Raises:
            LoginDataFormatError: 当响应格式错误时
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        mock_adapter.login.side_effect = LoginDataFormatError("响应缺少必要字段")
        
        client = Client(mock_config, mock_adapter)
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            client.login()
        
        assert '响应缺少必要字段' in str(exc_info.value)
    
    def test_client_should_store_response_in_sj_when_login_succeeds(self):
        """测试当登录成功时，Client 应该将响应存储在 sj 属性中。
        
        验证 Client 正确存储登录响应结果。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> client = Client(config, adapter)
            >>> response = client.login()
            >>> client.sj == response
            True
            >>> client.sj.token
            'abc123token'
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = '/path/to/cert'
        
        mock_adapter = Mock(spec=LoginPort)
        expected_response = LoginResponseDTO(
            token='abc123token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() + timedelta(hours=1),
            account_id='account_001'
        )
        mock_adapter.login.return_value = expected_response
        
        client = Client(mock_config, mock_adapter)
        
        # Act
        response = client.login()
        
        # Assert - 验证返回值和 sj 属性
        assert response == expected_response
        assert client.sj == expected_response
        assert client.sj.token == 'abc123token'
        assert client.sj.person_id == 'A123456789'
        assert client.sj.session_id == 'session_xyz'
        assert client.sj.account_id == 'account_001'
    
    def test_client_sj_should_be_none_initially(self):
        """测试 Client 初始化时，sj 属性应该为 None。
        
        验证 Client 的初始状态正确。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> client = Client(config, adapter)
            >>> client.sj is None
            True
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_adapter = Mock(spec=LoginPort)
        
        # Act
        client = Client(mock_config, mock_adapter)
        
        # Assert
        assert client.sj is None
    
    def test_client_is_logged_in_should_return_false_initially(self):
        """测试 Client 初始化时，is_logged_in() 应该返回 False。
        
        验证 Client 的登录状态检查功能。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> client = Client(config, adapter)
            >>> client.is_logged_in()
            False
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_adapter = Mock(spec=LoginPort)
        client = Client(mock_config, mock_adapter)
        
        # Act & Assert
        assert client.is_logged_in() is False
    
    def test_client_is_logged_in_should_return_true_after_successful_login(self):
        """测试登录成功后，is_logged_in() 应该返回 True。
        
        验证 Client 的登录状态在登录后正确更新。
        
        Examples:
            >>> client.login()
            >>> client.is_logged_in()
            True
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        mock_response = LoginResponseDTO(
            token='abc123token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() + timedelta(hours=1)
        )
        mock_adapter.login.return_value = mock_response
        
        client = Client(mock_config, mock_adapter)
        
        # Act
        client.login()
        
        # Assert
        assert client.is_logged_in() is True
    
    def test_client_is_logged_in_should_return_false_when_token_expired(self):
        """测试当 token 过期时，is_logged_in() 应该返回 False。
        
        验证 Client 能够检测过期的 token。
        
        Examples:
            >>> # 模拟已过期的 token
            >>> client.sj.expires_at < datetime.now()
            True
            >>> client.is_logged_in()
            False
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_adapter = Mock(spec=LoginPort)
        # 创建一个已过期的响应
        expired_response = LoginResponseDTO(
            token='expired_token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() - timedelta(hours=1)  # 过期的 token
        )
        mock_adapter.login.return_value = expired_response
        
        client = Client(mock_config, mock_adapter)
        client.login()
        
        # Act & Assert
        assert client.is_logged_in() is False
    
    def test_client_repr_should_show_login_status(self):
        """测试 Client 的 __repr__ 方法应该显示登录状态。
        
        验证 Client 的字符串表示正确。
        
        Examples:
            >>> config = Mock(spec=Config)
            >>> adapter = Mock(spec=LoginPort)
            >>> client = Client(config, adapter)
            >>> repr(client)
            'Client(logged_in=False)'
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_adapter = Mock(spec=LoginPort)
        
        # Test before login
        client = Client(mock_config, mock_adapter)
        assert repr(client) == 'Client(logged_in=False)'
        
        # Test after login
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = None
        
        mock_response = LoginResponseDTO(
            token='abc123token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() + timedelta(hours=1)
        )
        mock_adapter.login.return_value = mock_response
        
        client.login()
        assert repr(client) == 'Client(logged_in=True)'
    
    def test_client_should_pass_ca_path_to_adapter(self):
        """测试 Client 应该正确传递 ca_path 参数给适配器。
        
        验证 Client 正确处理可选的 ca_path 参数。
        
        Examples:
            >>> config.ca_path = '/path/to/cert'
            >>> client.login()
            >>> call_args.ca_path
            '/path/to/cert'
        
        Raises:
            None
        """
        # Arrange
        mock_config = Mock(spec=Config)
        mock_config.person_id = 'A123456789'
        mock_config.api_key = 'test_key'
        mock_config.api_secret = 'test_secret'
        mock_config.ca_path = '/custom/path/to/cert'
        
        mock_adapter = Mock(spec=LoginPort)
        mock_response = LoginResponseDTO(
            token='abc123token',
            person_id='A123456789',
            session_id='session_xyz',
            expires_at=datetime.now() + timedelta(hours=1)
        )
        mock_adapter.login.return_value = mock_response
        
        client = Client(mock_config, mock_adapter)
        
        # Act
        client.login()
        
        # Assert
        call_args = mock_adapter.login.call_args[0][0]
        assert call_args.ca_path == '/custom/path/to/cert'
