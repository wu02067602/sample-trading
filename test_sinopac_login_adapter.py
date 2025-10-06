"""永丰证券登录适配器的单元测试。

此模块包含 SinoPacLoginAdapter 的所有单元测试，使用 mock 避免依赖真实 API。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import requests
from sinopac_login_adapter import SinoPacLoginAdapter
from login_dto import LoginRequestDTO, LoginResponseDTO
from login_exceptions import (
    LoginAuthenticationError,
    LoginConnectionError,
    LoginDataFormatError,
    LoginParameterError,
    LoginServerError,
    LoginHTTPError
)


class TestSinoPacLoginAdapterSuccess:
    """测试成功登录的场景。"""
    
    def test_successful_login_should_return_valid_dto(self):
        """测试当 API 响应成功登录时，应该正确解析响应并返回包含 token 和必要信息的 DTO。
        
        验证 Adapter 能够正确处理成功的 API 响应，并将其转换为 LoginResponseDTO。
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='test_key',
            ...     api_secret='test_secret'
            ... )
            >>> response = adapter.login(request)
            >>> isinstance(response, LoginResponseDTO)
            True
        
        Raises:
            None
        """
        # Arrange - 创建 mock HTTP 客户端
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600,
            'account_id': 'account_001'
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act
        response = adapter.login(request)
        
        # Assert
        assert isinstance(response, LoginResponseDTO)
        assert response.token == 'abc123token'
        assert response.person_id == 'A123456789'
        assert response.session_id == 'session_xyz'
        assert response.account_id == 'account_001'
        assert isinstance(response.expires_at, datetime)
        assert response.expires_at > datetime.now()
    
    def test_successful_login_without_optional_fields(self):
        """测试成功登录但不包含可选字段。
        
        验证 Adapter 能够处理缺少可选字段（如 account_id）的响应。
        
        Examples:
            >>> # 响应不包含 account_id
            >>> response = adapter.login(request)
            >>> response.account_id is None
            True
        
        Raises:
            None
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 7200
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act
        response = adapter.login(request)
        
        # Assert
        assert response.token == 'abc123token'
        assert response.account_id is None


class TestSinoPacLoginAdapterAuthenticationFailure:
    """测试身份验证失败的场景。"""
    
    def test_login_failure_401_should_raise_authentication_error(self):
        """测试当 API 返回 401（账号密码错误）时，应该抛出 LoginAuthenticationError。
        
        验证 Adapter 能够正确识别并处理身份验证失败的情况。
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='wrong_key',
            ...     api_secret='wrong_secret'
            ... )
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginAuthenticationError: 身份验证失败，账号或密码错误
        
        Raises:
            LoginAuthenticationError: 当 API 返回 401 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='wrong_key',
            api_secret='wrong_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginAuthenticationError) as exc_info:
            adapter.login(request)
        
        assert '身份验证失败' in str(exc_info.value)
    
    def test_login_failure_403_should_raise_authentication_error(self):
        """测试当 API 返回 403（权限不足）时，应该抛出 LoginAuthenticationError。
        
        验证 Adapter 能够正确处理权限不足的情况。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginAuthenticationError: 权限不足，无法访问
        
        Raises:
            LoginAuthenticationError: 当 API 返回 403 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginAuthenticationError) as exc_info:
            adapter.login(request)
        
        assert '权限不足' in str(exc_info.value)


class TestSinoPacLoginAdapterConnectionFailure:
    """测试连线失败的场景。"""
    
    def test_connection_timeout_should_raise_connection_error(self):
        """测试当 API 连线超时时，应该抛出 LoginConnectionError。
        
        验证 Adapter 能够正确处理连线超时的情况。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginConnectionError: 连线超时
        
        Raises:
            LoginConnectionError: 当连线超时时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_http_client.post.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginConnectionError) as exc_info:
            adapter.login(request)
        
        assert '连线超时' in str(exc_info.value)
        assert exc_info.value.original_error is not None
    
    def test_connection_error_should_raise_connection_error(self):
        """测试当 API 连线失败时，应该抛出 LoginConnectionError。
        
        验证 Adapter 能够正确处理网络连线错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginConnectionError: 连线失败
        
        Raises:
            LoginConnectionError: 当连线失败时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_http_client.post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginConnectionError) as exc_info:
            adapter.login(request)
        
        assert '连线失败' in str(exc_info.value)
    
    def test_request_exception_should_raise_connection_error(self):
        """测试当发生其他请求异常时，应该抛出 LoginConnectionError。
        
        验证 Adapter 能够正确处理其他类型的请求错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginConnectionError: 请求失败: ...
        
        Raises:
            LoginConnectionError: 当请求失败时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_http_client.post.side_effect = requests.exceptions.RequestException("Unknown error")
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginConnectionError) as exc_info:
            adapter.login(request)
        
        assert '请求失败' in str(exc_info.value)


class TestSinoPacLoginAdapterDataFormatError:
    """测试数据格式错误的场景。"""
    
    def test_invalid_json_response_should_raise_data_format_error(self):
        """测试当 API 响应不是有效的 JSON 格式时，应该抛出 LoginDataFormatError。
        
        验证 Adapter 能够正确处理 JSON 解析错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: 响应数据不是有效的 JSON 格式
        
        Raises:
            LoginDataFormatError: 当响应不是有效 JSON 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            adapter.login(request)
        
        assert '响应数据不是有效的 JSON 格式' in str(exc_info.value)
    
    def test_missing_required_field_token_should_raise_data_format_error(self):
        """测试当响应缺少 token 字段时，应该抛出 LoginDataFormatError。
        
        验证 Adapter 能够检测缺少必要字段的情况。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: 响应缺少必要字段: token
        
        Raises:
            LoginDataFormatError: 当响应缺少 token 字段时
        """
        # Arrange
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
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            adapter.login(request)
        
        assert '响应缺少必要字段' in str(exc_info.value)
        assert 'token' in str(exc_info.value)
    
    def test_missing_multiple_required_fields_should_raise_data_format_error(self):
        """测试当响应缺少多个必要字段时，应该抛出 LoginDataFormatError。
        
        验证 Adapter 能够识别所有缺少的必要字段。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: 响应缺少必要字段: token, session_id
        
        Raises:
            LoginDataFormatError: 当响应缺少多个必要字段时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'person_id': 'A123456789'
            # 缺少 token 和 session_id
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            adapter.login(request)
        
        assert '响应缺少必要字段' in str(exc_info.value)
    
    def test_empty_token_should_raise_data_format_error(self):
        """测试当 token 为空字符串时，应该抛出 LoginDataFormatError。
        
        验证 Adapter 能够检测空的必要字段。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: token 字段必须是非空字符串
        
        Raises:
            LoginDataFormatError: 当 token 为空时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': '',  # 空字符串
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            adapter.login(request)
        
        assert 'token 字段必须是非空字符串' in str(exc_info.value)
    
    def test_invalid_field_type_should_raise_data_format_error(self):
        """测试当字段类型不正确时，应该抛出 LoginDataFormatError。
        
        验证 Adapter 能够检测字段类型错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginDataFormatError: token 字段必须是非空字符串
        
        Raises:
            LoginDataFormatError: 当字段类型不正确时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 123,  # 应该是字符串
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginDataFormatError) as exc_info:
            adapter.login(request)
        
        assert 'token 字段必须是非空字符串' in str(exc_info.value)


class TestSinoPacLoginAdapterParameterError:
    """测试参数错误的场景。"""
    
    def test_empty_person_id_should_raise_parameter_error(self):
        """测试当 person_id 为空时，应该抛出 ValueError（在 DTO 层面）。
        
        验证输入参数在 DTO 层面就被正确验证。
        
        Examples:
            >>> request = LoginRequestDTO(
            ...     person_id='',
            ...     api_key='test_key',
            ...     api_secret='test_secret'
            ... )
            Traceback (most recent call last):
                ...
            ValueError: person_id 不能为空
        
        Raises:
            ValueError: 当 person_id 为空时
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            LoginRequestDTO(
                person_id='',
                api_key='test_key',
                api_secret='test_secret'
            )
        
        assert 'person_id 不能为空' in str(exc_info.value)
    
    def test_empty_api_key_should_raise_parameter_error(self):
        """测试当 api_key 为空时，应该抛出 ValueError。
        
        验证 api_key 参数被正确验证。
        
        Examples:
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='',
            ...     api_secret='test_secret'
            ... )
            Traceback (most recent call last):
                ...
            ValueError: api_key 不能为空
        
        Raises:
            ValueError: 当 api_key 为空时
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            LoginRequestDTO(
                person_id='A123456789',
                api_key='',
                api_secret='test_secret'
            )
        
        assert 'api_key 不能为空' in str(exc_info.value)
    
    def test_empty_api_secret_should_raise_parameter_error(self):
        """测试当 api_secret 为空时，应该抛出 ValueError。
        
        验证 api_secret 参数被正确验证。
        
        Examples:
            >>> request = LoginRequestDTO(
            ...     person_id='A123456789',
            ...     api_key='test_key',
            ...     api_secret=''
            ... )
            Traceback (most recent call last):
                ...
            ValueError: api_secret 不能为空
        
        Raises:
            ValueError: 当 api_secret 为空时
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            LoginRequestDTO(
                person_id='A123456789',
                api_key='test_key',
                api_secret=''
            )
        
        assert 'api_secret 不能为空' in str(exc_info.value)


class TestSinoPacLoginAdapterHTTPError:
    """测试 HTTP 错误的场景。"""
    
    def test_500_internal_server_error_should_raise_server_error(self):
        """测试当 API 返回 500 错误时，应该抛出 LoginServerError。
        
        验证 Adapter 能够正确处理服务器内部错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginServerError: 服务器错误: 500
        
        Raises:
            LoginServerError: 当 API 返回 500 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginServerError) as exc_info:
            adapter.login(request)
        
        assert '服务器错误: 500' in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    def test_503_service_unavailable_should_raise_server_error(self):
        """测试当 API 返回 503 错误时，应该抛出 LoginServerError。
        
        验证 Adapter 能够正确处理服务不可用错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginServerError: 服务器错误: 503
        
        Raises:
            LoginServerError: 当 API 返回 503 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 503
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginServerError) as exc_info:
            adapter.login(request)
        
        assert '服务器错误: 503' in str(exc_info.value)
        assert exc_info.value.status_code == 503
    
    def test_400_bad_request_should_raise_http_error(self):
        """测试当 API 返回 400 错误时，应该抛出 LoginHTTPError。
        
        验证 Adapter 能够正确处理客户端请求错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginHTTPError: HTTP 错误: 400
        
        Raises:
            LoginHTTPError: 当 API 返回 400 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 400
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginHTTPError) as exc_info:
            adapter.login(request)
        
        assert 'HTTP 错误: 400' in str(exc_info.value)
        assert exc_info.value.status_code == 400
    
    def test_404_not_found_should_raise_http_error(self):
        """测试当 API 返回 404 错误时，应该抛出 LoginHTTPError。
        
        验证 Adapter 能够正确处理资源未找到错误。
        
        Examples:
            >>> adapter.login(request)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            LoginHTTPError: HTTP 错误: 404
        
        Raises:
            LoginHTTPError: 当 API 返回 404 时
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act & Assert
        with pytest.raises(LoginHTTPError) as exc_info:
            adapter.login(request)
        
        assert 'HTTP 错误: 404' in str(exc_info.value)
        assert exc_info.value.status_code == 404


class TestSinoPacLoginAdapterHTTPClientCall:
    """测试 HTTP 客户端调用的场景。"""
    
    def test_adapter_should_call_http_client_with_correct_url(self):
        """测试 Adapter 是否使用正确的 URL 调用 HTTP 客户端。
        
        验证 Adapter 构建了正确的 API URL。
        
        Examples:
            >>> adapter.login(request)
            >>> mock_http_client.post.assert_called_once()
            >>> args, kwargs = mock_http_client.post.call_args
            >>> args[0]  # URL
            'https://openapi.sinotrade.com.tw/v1/login'
        
        Raises:
            None
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act
        adapter.login(request)
        
        # Assert
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == 'https://openapi.sinotrade.com.tw/v1/login'
    
    def test_adapter_should_call_http_client_with_correct_headers(self):
        """测试 Adapter 是否使用正确的 headers 调用 HTTP 客户端。
        
        验证 Adapter 设置了正确的 HTTP 请求头。
        
        Examples:
            >>> adapter.login(request)
            >>> kwargs = mock_http_client.post.call_args.kwargs
            >>> kwargs['headers']['Content-Type']
            'application/json'
        
        Raises:
            None
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act
        adapter.login(request)
        
        # Assert
        call_kwargs = mock_http_client.post.call_args.kwargs
        headers = call_kwargs['headers']
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
        assert 'User-Agent' in headers
    
    def test_adapter_should_call_http_client_with_correct_body(self):
        """测试 Adapter 是否使用正确的 body 调用 HTTP 客户端。
        
        验证 Adapter 构建了正确的请求体。
        
        Examples:
            >>> adapter.login(request)
            >>> kwargs = mock_http_client.post.call_args.kwargs
            >>> kwargs['json']['person_id']
            'A123456789'
        
        Raises:
            None
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        adapter = SinoPacLoginAdapter(http_client=mock_http_client)
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret',
            ca_path='/path/to/cert'
        )
        
        # Act
        adapter.login(request)
        
        # Assert
        call_kwargs = mock_http_client.post.call_args.kwargs
        body = call_kwargs['json']
        assert body['person_id'] == 'A123456789'
        assert body['api_key'] == 'test_key'
        assert body['api_secret'] == 'test_secret'
        assert body['ca_path'] == '/path/to/cert'
    
    def test_adapter_should_call_http_client_with_timeout(self):
        """测试 Adapter 是否设置了正确的超时时间。
        
        验证 Adapter 传递了超时参数给 HTTP 客户端。
        
        Examples:
            >>> adapter = SinoPacLoginAdapter(timeout=60)
            >>> adapter.login(request)
            >>> kwargs = mock_http_client.post.call_args.kwargs
            >>> kwargs['timeout']
            60
        
        Raises:
            None
        """
        # Arrange
        mock_http_client = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'abc123token',
            'person_id': 'A123456789',
            'session_id': 'session_xyz',
            'expires_in': 3600
        }
        mock_http_client.post.return_value = mock_response
        
        custom_timeout = 60
        adapter = SinoPacLoginAdapter(
            http_client=mock_http_client,
            timeout=custom_timeout
        )
        request = LoginRequestDTO(
            person_id='A123456789',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        # Act
        adapter.login(request)
        
        # Assert
        call_kwargs = mock_http_client.post.call_args.kwargs
        assert call_kwargs['timeout'] == custom_timeout


class TestSinoPacLoginAdapterInitialization:
    """测试 Adapter 初始化的场景。"""
    
    def test_adapter_initialization_with_default_values(self):
        """测试使用默认值初始化 Adapter。
        
        验证 Adapter 的默认配置是否正确。
        
        Examples:
            >>> adapter = SinoPacLoginAdapter()
            >>> adapter.base_url
            'https://openapi.sinotrade.com.tw'
            >>> adapter.timeout
            30
        
        Raises:
            None
        """
        # Act
        adapter = SinoPacLoginAdapter()
        
        # Assert
        assert adapter.base_url == 'https://openapi.sinotrade.com.tw'
        assert adapter.timeout == 30
        assert isinstance(adapter.http_client, requests.Session)
    
    def test_adapter_initialization_with_custom_values(self):
        """测试使用自定义值初始化 Adapter。
        
        验证 Adapter 能够接受自定义配置。
        
        Examples:
            >>> adapter = SinoPacLoginAdapter(
            ...     base_url='https://custom.api.com',
            ...     timeout=60
            ... )
            >>> adapter.base_url
            'https://custom.api.com'
            >>> adapter.timeout
            60
        
        Raises:
            None
        """
        # Arrange
        custom_base_url = 'https://custom.api.com'
        custom_timeout = 60
        mock_http_client = Mock(spec=requests.Session)
        
        # Act
        adapter = SinoPacLoginAdapter(
            base_url=custom_base_url,
            timeout=custom_timeout,
            http_client=mock_http_client
        )
        
        # Assert
        assert adapter.base_url == 'https://custom.api.com'
        assert adapter.timeout == 60
        assert adapter.http_client == mock_http_client
