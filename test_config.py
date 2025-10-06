"""Unit tests for Config class.

This module contains comprehensive tests for the Config class, including:
- File existence validation
- YAML file reading
- Schema validation
- Attribute storage
- Error handling
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from config import Config


class TestConfig:
    """Test suite for Config class."""
    
    def test_config_file_not_found(self):
        """Test that FileNotFoundError is raised when YAML file does not exist.
        
        This test verifies that the Config class properly handles the case
        when the specified configuration file does not exist.
        
        Expected behavior:
            - Should raise FileNotFoundError
            - Error message should contain the file path
        """
        non_existent_file = "non_existent_config.yaml"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            Config(non_existent_file)
        
        assert non_existent_file in str(exc_info.value)
    
    def test_config_reads_existing_yaml_file(self):
        """Test that Config successfully reads an existing YAML file.
        
        This test verifies that the Config class can read and parse
        a valid YAML configuration file.
        
        Expected behavior:
            - Should successfully read yaml_sample.yaml
            - Should create Config instance without errors
            - Should have all required attributes
        """
        config = Config("yaml_sample.yaml")
        
        assert config is not None
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'secret_key')
        assert hasattr(config, 'person_id')
        assert hasattr(config, 'ca_password')
    
    def test_config_validates_yaml_schema(self):
        """Test that Config validates YAML file format against schema.
        
        This test verifies that the Config class properly validates
        the structure and content of the YAML file against the expected schema.
        
        Expected behavior:
            - Should successfully validate yaml_sample.yaml
            - Should accept all required fields: api_key, secret_key, person_id, ca_password
            - Should store validated data as attributes
        """
        config = Config("yaml_sample.yaml")
        
        # Verify all required fields are present and have correct types
        assert isinstance(config.api_key, str)
        assert isinstance(config.secret_key, str)
        assert isinstance(config.person_id, str)
        assert isinstance(config.ca_password, str)
        
        # Verify values are not empty
        assert len(config.api_key) > 0
        assert len(config.secret_key) > 0
        assert len(config.person_id) > 0
        assert len(config.ca_password) > 0
    
    def test_config_stores_validated_attributes(self):
        """Test that validated config properties are stored as class attributes.
        
        This test verifies that after successful validation, all configuration
        parameters are properly stored as instance attributes of the Config class.
        
        Expected behavior:
            - All parameters should be accessible as instance attributes
            - Attribute values should match the values in yaml_sample.yaml
        """
        config = Config("yaml_sample.yaml")
        
        # Verify attributes match expected values from yaml_sample.yaml
        assert config.api_key == "test_api_key_123"
        assert config.secret_key == "test_secret_key_456"
        assert config.person_id == "A123456789"
        assert config.ca_password == "test_password"
    
    def test_config_validation_failure_raises_exception(self):
        """Test that ValueError is raised when validation fails.
        
        This test verifies that the Config class properly handles invalid
        configuration data by raising appropriate exceptions.
        
        Expected behavior:
            - Should raise ValueError for missing required fields
            - Should raise ValueError for empty strings
            - Should raise ValueError for wrong data types
        """
        # Test case 1: Missing required field
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'api_key': 'test_key',
                'secret_key': 'test_secret',
                # person_id is missing
                'ca_password': 'test_password'
            }, f)
            temp_file_1 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_1)
            assert "validation failed" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_1)
        
        # Test case 2: Empty string value
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'api_key': '',  # Empty string
                'secret_key': 'test_secret',
                'person_id': 'A123456789',
                'ca_password': 'test_password'
            }, f)
            temp_file_2 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_2)
            assert "validation failed" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_2)
        
        # Test case 3: Wrong data type
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'api_key': 123,  # Should be string, not int
                'secret_key': 'test_secret',
                'person_id': 'A123456789',
                'ca_password': 'test_password'
            }, f)
            temp_file_3 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_3)
            assert "validation failed" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_3)
    
    def test_config_yaml_read_failure_raises_exception(self):
        """Test that ValueError is raised when YAML file exists but cannot be read.
        
        This test verifies that the Config class properly handles errors
        during YAML file parsing, such as invalid YAML syntax.
        
        Expected behavior:
            - Should raise ValueError for invalid YAML syntax
            - Should raise ValueError for corrupted files
            - Error message should indicate parsing failure
        """
        # Test case 1: Invalid YAML syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed bracket")
            temp_file_1 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_1)
            assert "parse" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_1)
        
        # Test case 2: Empty YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_file_2 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_2)
            assert "empty" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_2)
        
        # Test case 3: YAML contains non-dict content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- item1\n- item2\n- item3")
            temp_file_3 = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                Config(temp_file_3)
            assert "dictionary" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file_3)
    
    def test_config_repr(self):
        """Test that Config has a proper string representation.
        
        This test verifies that the __repr__ method returns a useful
        string representation with masked sensitive information.
        
        Expected behavior:
            - Should mask sensitive fields (api_key, secret_key, ca_password)
            - Should show non-sensitive fields (person_id)
        """
        config = Config("yaml_sample.yaml")
        repr_str = repr(config)
        
        assert "Config(" in repr_str
        assert "***" in repr_str  # Sensitive data should be masked
        assert config.person_id in repr_str  # Non-sensitive data can be shown
        # Ensure actual sensitive values are NOT in the repr
        assert config.api_key not in repr_str
        assert config.secret_key not in repr_str
        assert config.ca_password not in repr_str
