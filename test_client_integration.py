"""Client 类的整合测试。

此模块包含 Client 类的整合测试，使用真实的 Config 和 Adapter，
但 mock HTTP 客户端以避免依赖真实的永丰 API。
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
import tempfile
import os
import yaml
import requests
from client import Client
from config import Config
from sinopac_login_adapter import SinoPacLoginAdapter
from login_exceptions import (
    LoginAuthenticationError,
    LoginConnectionError,
    LoginDataFormatError
)


class TestClientIntegrationTests:
    """Client 类的整合测试套件。
    
    使用真实的 Config 和 SinoPacLoginAdapter，但 mock HTTP 客户端。
    """
    
    def test_client_should_call_login_adapter_integration(self):
        """整合测试：当调用 Client.login() 时，应该调用真实的登录适配器。
        
        验证 Client 与真实的 Config 和 Adapter 正确集成。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> response = client.login()
            >>> isinstance(response, LoginResponseDTO)
            True
        
        Raises:
            None
        """
        # Arrange - 创建真实的配置文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret',
                'ca_path': '/test/path'
            }, f)
            config_file = f.name
        
        try:
            # 使用真实的 Config 和 Adapter
            config = Config(config_file)
            
            # 创建 mock HTTP 客户端
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token': 'integration_test_token',
                'person_id': 'A123456789',
                'session_id': 'integration_session',
                'expires_in': 3600,
                'account_id': 'integration_account'
            }
            mock_http_client.post.return_value = mock_response
            
            # 注入 mock HTTP 客户端到适配器
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            
            # 创建 Client
            client = Client(config, adapter)
            
            # Act
            response = client.login()
            
            # Assert - 验证 HTTP 客户端被调用
            mock_http_client.post.assert_called_once()
            
            # 验证调用参数
            call_kwargs = mock_http_client.post.call_args.kwargs
            assert 'json' in call_kwargs
            body = call_kwargs['json']
            assert body['person_id'] == 'A123456789'
            assert body['api_key'] == 'test_api_key'
            assert body['api_secret'] == 'test_api_secret'
            
            # 验证响应
            assert response.token == 'integration_test_token'
            assert response.person_id == 'A123456789'
            assert response.session_id == 'integration_session'
            
        finally:
            os.unlink(config_file)
    
    def test_client_should_raise_exception_when_adapter_fails_integration(self):
        """整合测试：当登录适配器失败时，Client 应该抛出相应的异常。
        
        验证 Client 与真实适配器在错误情况下的集成。
        
        Examples:
            >>> # 模拟 401 错误
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginAuthenticationError: 身份验证失败，账号或密码错误
        
        Raises:
            LoginAuthenticationError: 当身份验证失败时
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'wrong_key',
                'api_secret': 'wrong_secret'
            }, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            # Mock HTTP 客户端返回 401 错误
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 401
            mock_http_client.post.return_value = mock_response
            
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            client = Client(config, adapter)
            
            # Act & Assert
            with pytest.raises(LoginAuthenticationError) as exc_info:
                client.login()
            
            assert '身份验证失败' in str(exc_info.value)
            
            # 验证 sj 属性没有被设置
            assert client.sj is None
            
        finally:
            os.unlink(config_file)
    
    def test_client_should_raise_connection_error_integration(self):
        """整合测试：当连线失败时，Client 应该抛出 LoginConnectionError。
        
        验证 Client 与真实适配器在连线错误时的集成。
        
        Examples:
            >>> # 模拟连线超时
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginConnectionError: 连线超时
        
        Raises:
            LoginConnectionError: 当连线失败时
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            }, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            # Mock HTTP 客户端抛出超时异常
            mock_http_client = Mock(spec=requests.Session)
            mock_http_client.post.side_effect = requests.exceptions.Timeout("Connection timeout")
            
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            client = Client(config, adapter)
            
            # Act & Assert
            with pytest.raises(LoginConnectionError) as exc_info:
                client.login()
            
            assert '连线超时' in str(exc_info.value)
            
        finally:
            os.unlink(config_file)
    
    def test_client_should_store_response_in_sj_integration(self):
        """整合测试：当登录成功时，Client 应该将响应存储在 sj 属性中。
        
        验证 Client 与真实 Config 和 Adapter 的完整集成流程。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> response = client.login()
            >>> client.sj == response
            True
            >>> client.sj.token
            'integration_test_token'
        
        Raises:
            None
        """
        # Arrange - 创建配置文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'test_api_key',
                'api_secret': 'test_api_secret',
                'ca_path': '/custom/cert/path'
            }, f)
            config_file = f.name
        
        try:
            # 使用真实的 Config
            config = Config(config_file)
            
            # Mock HTTP 客户端
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token': 'full_integration_token',
                'person_id': 'A123456789',
                'session_id': 'full_integration_session',
                'expires_in': 7200,
                'account_id': 'full_integration_account'
            }
            mock_http_client.post.return_value = mock_response
            
            # 使用真实的 Adapter
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            
            # 创建 Client
            client = Client(config, adapter)
            
            # 验证初始状态
            assert client.sj is None
            assert not client.is_logged_in()
            
            # Act
            response = client.login()
            
            # Assert - 验证响应和 sj 属性
            assert client.sj is not None
            assert client.sj == response
            assert client.sj.token == 'full_integration_token'
            assert client.sj.person_id == 'A123456789'
            assert client.sj.session_id == 'full_integration_session'
            assert client.sj.account_id == 'full_integration_account'
            
            # 验证登录状态
            assert client.is_logged_in()
            
            # 验证 ca_path 被正确传递
            call_kwargs = mock_http_client.post.call_args.kwargs
            body = call_kwargs['json']
            assert body['ca_path'] == '/custom/cert/path'
            
        finally:
            os.unlink(config_file)
    
    def test_client_integration_with_yaml_sample(self):
        """整合测试：使用 yaml_sample.yaml 进行完整的集成测试。
        
        验证 Client 能够使用项目提供的示例配置文件。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> response = client.login()
            >>> client.sj is not None
            True
        
        Raises:
            None
        """
        # Arrange - 使用项目的 yaml_sample.yaml
        config = Config('yaml_sample.yaml')
        
        # Mock HTTP 客户端
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'sample_yaml_token',
            'person_id': config.person_id,
            'session_id': 'sample_yaml_session',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        client = Client(config, adapter)
        
        # Act
        response = client.login()
        
        # Assert
        assert client.sj is not None
        assert client.sj.token == 'sample_yaml_token'
        assert client.sj.person_id == config.person_id
        assert client.is_logged_in()
        
        # 验证配置正确传递
        call_kwargs = mock_http_client.post.call_args.kwargs
        body = call_kwargs['json']
        assert body['person_id'] == config.person_id
        assert body['api_key'] == config.api_key
        assert body['api_secret'] == config.api_secret
    
    def test_client_integration_handles_server_errors(self):
        """整合测试：验证 Client 能正确处理服务器错误（500, 503）。
        
        验证完整的错误处理流程。
        
        Examples:
            >>> # 模拟 500 错误
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginServerError: 服务器错误: 500
        
        Raises:
            LoginServerError: 当服务器错误时
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            }, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            # Mock HTTP 客户端返回 500 错误
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 500
            mock_http_client.post.return_value = mock_response
            
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            client = Client(config, adapter)
            
            # Act & Assert
            from login_exceptions import LoginServerError
            with pytest.raises(LoginServerError) as exc_info:
                client.login()
            
            assert exc_info.value.status_code == 500
            assert '服务器错误' in str(exc_info.value)
            
        finally:
            os.unlink(config_file)
    
    def test_client_integration_handles_data_format_errors(self):
        """整合测试：验证 Client 能正确处理数据格式错误。
        
        验证当 API 返回格式错误的数据时的处理。
        
        Examples:
            >>> # API 返回缺少必要字段的响应
            >>> client.login()  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: 响应缺少必要字段: token
        
        Raises:
            LoginDataFormatError: 当数据格式错误时
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            }, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            # Mock HTTP 客户端返回格式错误的数据（缺少 token）
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'person_id': 'A123456789',
                'session_id': 'session_xyz'
                # 缺少 token 字段
            }
            mock_http_client.post.return_value = mock_response
            
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            client = Client(config, adapter)
            
            # Act & Assert
            with pytest.raises(LoginDataFormatError) as exc_info:
                client.login()
            
            assert '响应缺少必要字段' in str(exc_info.value)
            assert 'token' in str(exc_info.value)
            
        finally:
            os.unlink(config_file)
    
    def test_client_integration_full_workflow(self):
        """整合测试：验证完整的登录工作流程。
        
        从创建配置、初始化客户端、执行登录到检查状态的完整流程。
        
        Examples:
            >>> # 完整的工作流程
            >>> config = Config('config.yaml')
            >>> adapter = SinoPacLoginAdapter()
            >>> client = Client(config, adapter)
            >>> client.is_logged_in()
            False
            >>> client.login()
            >>> client.is_logged_in()
            True
        
        Raises:
            None
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 'A123456789',
                'api_key': 'workflow_key',
                'api_secret': 'workflow_secret',
                'ca_path': '/workflow/cert'
            }, f)
            config_file = f.name
        
        try:
            # Step 1: 创建配置
            config = Config(config_file)
            assert config.person_id == 'A123456789'
            
            # Step 2: 创建适配器
            mock_http_client = Mock(spec=requests.Session)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'token': 'workflow_token',
                'person_id': 'A123456789',
                'session_id': 'workflow_session',
                'expires_in': 3600,
                'account_id': 'workflow_account'
            }
            mock_http_client.post.return_value = mock_response
            adapter = SinoPacLoginAdapter(http_client=mock_http_client)
            
            # Step 3: 创建客户端
            client = Client(config, adapter)
            assert client.sj is None
            assert not client.is_logged_in()
            assert repr(client) == 'Client(logged_in=False)'
            
            # Step 4: 执行登录
            response = client.login()
            
            # Step 5: 验证结果
            assert response.token == 'workflow_token'
            assert client.sj == response
            assert client.is_logged_in()
            assert repr(client) == 'Client(logged_in=True)'
            
            # Step 6: 验证可以访问所有属性
            assert client.sj.token == 'workflow_token'
            assert client.sj.person_id == 'A123456789'
            assert client.sj.session_id == 'workflow_session'
            assert client.sj.account_id == 'workflow_account'
            
        finally:
            os.unlink(config_file)
