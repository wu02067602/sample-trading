"""Config 类的单元测试。

此模块包含 Config 类的所有单元测试，测试配置读取、验证和错误处理。
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from config import Config, ConfigError


class TestConfig:
    """Config 类的测试套件。"""
    
    def test_file_not_exists_should_raise_exception(self):
        """测试当 yaml 文件不存在时，应该要 raise 例外。
        
        验证当配置文件不存在时，Config 初始化会抛出 FileNotFoundError。
        
        Examples:
            >>> config = Config('nonexistent.yaml')
            Traceback (most recent call last):
                ...
            FileNotFoundError: 配置文件不存在: nonexistent.yaml
        
        Raises:
            FileNotFoundError: 当配置文件不存在时
        """
        # Arrange
        non_existent_file = 'non_existent_config.yaml'
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            Config(non_existent_file)
        
        assert '配置文件不存在' in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)
    
    def test_file_exists_should_read_yaml(self):
        """测试当 yaml 文件存在时，应该要读取 yaml 文件。
        
        验证当配置文件存在且格式正确时，Config 能成功读取文件。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> isinstance(config.person_id, str)
            True
        
        Raises:
            None
        """
        # Arrange
        yaml_file = 'yaml_sample.yaml'
        
        # Act
        config = Config(yaml_file)
        
        # Assert
        assert config is not None
        assert hasattr(config, 'person_id')
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'api_secret')
    
    def test_file_exists_should_validate_schema(self):
        """测试当 yaml 文件存在时，应该要验证 yaml 文件的格式是否符合 schema。
        
        验证 Config 类能够正确验证配置文件的格式，包括必需字段和字段类型。
        
        Examples:
            >>> # 缺少必需字段的配置
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     yaml.dump({'person_id': 'A123456789'}, f)
            ...     temp_file = f.name
            >>> config = Config(temp_file)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            ConfigError: 缺少必需的配置字段: api_key, api_secret
        
        Raises:
            ConfigError: 当配置格式不符合 schema 时
        """
        # Arrange - 创建一个缺少必需字段的临时配置文件
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({'person_id': 'A123456789'}, f)
            temp_file = f.name
        
        try:
            # Act & Assert
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file)
            
            assert '缺少必需的配置字段' in str(exc_info.value)
            assert 'api_key' in str(exc_info.value)
            assert 'api_secret' in str(exc_info.value)
        finally:
            # Cleanup
            os.unlink(temp_file)
    
    def test_valid_config_should_set_attributes(self):
        """测试当验证参数通过时，最终初始化而成的 config 属性应该要存成类别中的属性。
        
        验证当配置验证通过后，所有配置值都被正确设置为类的属性。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> config.person_id
            'A123456789'
            >>> config.api_key
            'test_api_key'
        
        Raises:
            None
        """
        # Arrange
        yaml_file = 'yaml_sample.yaml'
        
        # Act
        config = Config(yaml_file)
        
        # Assert - 验证所有必需字段都被设置为属性
        assert hasattr(config, 'person_id')
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'api_secret')
        assert hasattr(config, 'ca_path')
        
        # 验证属性值正确
        assert config.person_id == 'A123456789'
        assert config.api_key == 'test_api_key'
        assert config.api_secret == 'test_api_secret'
        assert config.ca_path == '/test/path/to/certificate'
    
    def test_invalid_schema_should_raise_exception(self):
        """测试当验证参数失败时，应该要 raise 例外。
        
        验证当配置格式不正确时，Config 初始化会抛出 ConfigError。
        包括以下场景：
        1. 缺少必需字段
        2. 字段值为空
        3. 字段类型不正确
        
        Examples:
            >>> # 缺少必需字段
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     yaml.dump({'person_id': 'A123456789'}, f)
            ...     temp_file = f.name
            >>> config = Config(temp_file)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            ConfigError: 缺少必需的配置字段: api_key, api_secret
        
        Raises:
            ConfigError: 当配置验证失败时
        """
        # Test Case 1: 缺少必需字段
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({'person_id': 'A123456789', 'api_key': 'test_key'}, f)
            temp_file1 = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file1)
            assert '缺少必需的配置字段' in str(exc_info.value)
        finally:
            os.unlink(temp_file1)
        
        # Test Case 2: 字段值为空
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': '',
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            }, f)
            temp_file2 = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file2)
            assert '配置字段不能为空' in str(exc_info.value)
        finally:
            os.unlink(temp_file2)
        
        # Test Case 3: 字段类型不正确
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump({
                'person_id': 123,  # 应该是字符串
                'api_key': 'test_key',
                'api_secret': 'test_secret'
            }, f)
            temp_file3 = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file3)
            assert '必须是字符串类型' in str(exc_info.value)
        finally:
            os.unlink(temp_file3)
    
    def test_yaml_read_failure_should_raise_exception(self):
        """测试当 yaml 文件存在且读取失败，应该要 raise 例外。
        
        验证当 YAML 文件存在但格式错误或读取失败时，Config 初始化会抛出异常。
        包括以下场景：
        1. YAML 格式错误
        2. 文件为空
        3. 文件不是有效的 YAML
        
        Examples:
            >>> # YAML 格式错误
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     f.write('invalid: yaml: content:')
            ...     temp_file = f.name
            >>> config = Config(temp_file)  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            yaml.YAMLError: YAML 文件格式错误: ...
        
        Raises:
            yaml.YAMLError: 当 YAML 格式错误时
            ConfigError: 当文件读取失败或为空时
        """
        # Test Case 1: YAML 格式错误
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write('invalid: yaml: content:\n  - bad\n  indentation')
            temp_file1 = f.name
        
        try:
            with pytest.raises(yaml.YAMLError) as exc_info:
                Config(temp_file1)
            assert 'YAML 文件格式错误' in str(exc_info.value)
        finally:
            os.unlink(temp_file1)
        
        # Test Case 2: 文件为空
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write('')  # 空文件
            temp_file2 = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file2)
            assert '配置文件为空' in str(exc_info.value)
        finally:
            os.unlink(temp_file2)
        
        # Test Case 3: 文件不是字典格式
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False,
            encoding='utf-8'
        ) as f:
            yaml.dump(['list', 'not', 'dict'], f)
            temp_file3 = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                Config(temp_file3)
            assert '配置数据必须是字典格式' in str(exc_info.value)
        finally:
            os.unlink(temp_file3)


class TestConfigEdgeCases:
    """Config 类的边界测试。"""
    
    def test_optional_fields_can_be_none(self):
        """测试可选字段可以为 None 或不存在。
        
        验证当可选字段不存在或为 None 时，Config 仍能正确初始化。
        
        Examples:
            >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            ...     yaml.dump({
            ...         'person_id': 'A123456789',
            ...         'api_key': 'test_key',
            ...         'api_secret': 'test_secret'
            ...     }, f)
            ...     temp_file = f.name
            >>> config = Config(temp_file)  # doctest: +SKIP
            >>> config.ca_path is None
            True
        
        Raises:
            None
        """
        # Arrange - 创建不包含可选字段的配置
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
            temp_file = f.name
        
        try:
            # Act
            config = Config(temp_file)
            
            # Assert
            assert config.person_id == 'A123456789'
            assert config.api_key == 'test_key'
            assert config.api_secret == 'test_secret'
            assert config.ca_path is None
        finally:
            os.unlink(temp_file)
    
    def test_config_repr_masks_sensitive_info(self):
        """测试 Config 的字符串表示会隐藏敏感信息。
        
        验证 repr() 输出会隐藏 API key、secret 等敏感信息。
        
        Examples:
            >>> config = Config('yaml_sample.yaml')
            >>> repr(config)
            "Config(person_id='A***6789', api_key='***', api_secret='***')"
        
        Raises:
            None
        """
        # Arrange
        yaml_file = 'yaml_sample.yaml'
        
        # Act
        config = Config(yaml_file)
        repr_str = repr(config)
        
        # Assert
        assert 'A***6789' in repr_str
        assert "api_key='***'" in repr_str
        assert "api_secret='***'" in repr_str
        assert 'test_api_key' not in repr_str
        assert 'test_api_secret' not in repr_str
