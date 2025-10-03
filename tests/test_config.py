"""
Config 類別單元測試
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.config import Config, ConfigError


class TestConfig:
    """Config 類別測試集"""
    
    @pytest.fixture
    def valid_config_data(self):
        """有效的配置資料"""
        return {
            "api_key": "test_api_key_12345",
            "secret_key": "test_secret_key_67890",
            "person_id": "A123456789",
        }
    
    @pytest.fixture
    def full_config_data(self):
        """完整的配置資料（包含選填欄位）"""
        return {
            "api_key": "test_api_key_12345",
            "secret_key": "test_secret_key_67890",
            "person_id": "A123456789",
            "ca_path": "/path/to/cert.pfx",
            "ca_passwd": "cert_password",
            "simulation": True,
            "contracts_timeout": 30,
        }
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """創建臨時配置檔案的 fixture"""
        def _create_config(data: dict) -> Path:
            config_file = tmp_path / "test_config.yaml"
            import yaml
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f)
            return config_file
        return _create_config
    
    def test_load_valid_config(self, temp_config_file, valid_config_data):
        """測試讀取有效配置"""
        config_path = temp_config_file(valid_config_data)
        config = Config(config_path)
        
        assert config.api_key == "test_api_key_12345"
        assert config.secret_key == "test_secret_key_67890"
        assert config.person_id == "A123456789"
    
    def test_load_full_config(self, temp_config_file, full_config_data):
        """測試讀取完整配置（包含選填欄位）"""
        config_path = temp_config_file(full_config_data)
        config = Config(config_path)
        
        assert config.api_key == "test_api_key_12345"
        assert config.secret_key == "test_secret_key_67890"
        assert config.person_id == "A123456789"
        assert config.ca_path == "/path/to/cert.pfx"
        assert config.ca_passwd == "cert_password"
        assert config.simulation is True
        assert config.contracts_timeout == 30
    
    def test_default_values(self, temp_config_file, valid_config_data):
        """測試選填欄位的預設值"""
        config_path = temp_config_file(valid_config_data)
        config = Config(config_path)
        
        assert config.ca_path is None
        assert config.ca_passwd is None
        assert config.simulation is False
        assert config.contracts_timeout == 0
    
    def test_missing_required_field(self, temp_config_file):
        """測試缺少必填欄位"""
        incomplete_data = {
            "api_key": "test_api_key",
            # 缺少 secret_key 和 person_id
        }
        config_path = temp_config_file(incomplete_data)
        
        with pytest.raises(ConfigError, match="缺少必填欄位"):
            Config(config_path)
    
    def test_empty_required_field(self, temp_config_file):
        """測試必填欄位為空"""
        empty_data = {
            "api_key": "test_api_key",
            "secret_key": "",  # 空字串
            "person_id": "A123456789",
        }
        config_path = temp_config_file(empty_data)
        
        with pytest.raises(ConfigError, match="必填欄位不可為空"):
            Config(config_path)
    
    def test_whitespace_required_field(self, temp_config_file):
        """測試必填欄位只有空白"""
        whitespace_data = {
            "api_key": "test_api_key",
            "secret_key": "   ",  # 只有空白
            "person_id": "A123456789",
        }
        config_path = temp_config_file(whitespace_data)
        
        with pytest.raises(ConfigError, match="必填欄位不可為空"):
            Config(config_path)
    
    def test_file_not_exists(self, tmp_path):
        """測試配置檔案不存在"""
        non_existent_path = tmp_path / "non_existent.yaml"
        
        with pytest.raises(ConfigError, match="配置檔案不存在"):
            Config(non_existent_path)
    
    def test_invalid_yaml_format(self, tmp_path):
        """測試無效的 YAML 格式"""
        invalid_yaml_file = tmp_path / "invalid.yaml"
        with open(invalid_yaml_file, "w") as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(ConfigError, match="無法解析 YAML 檔案"):
            Config(invalid_yaml_file)
    
    def test_empty_yaml_file(self, tmp_path):
        """測試空的 YAML 檔案"""
        empty_file = tmp_path / "empty.yaml"
        empty_file.touch()
        
        with pytest.raises(ConfigError, match="缺少必填欄位"):
            Config(empty_file)
    
    def test_to_dict(self, temp_config_file, full_config_data):
        """測試 to_dict 方法"""
        config_path = temp_config_file(full_config_data)
        config = Config(config_path)
        
        config_dict = config.to_dict()
        
        assert config_dict["api_key"] == "test_api_key_12345"
        assert config_dict["secret_key"] == "test_secret_key_67890"
        assert config_dict["person_id"] == "A123456789"
        assert config_dict["ca_path"] == "/path/to/cert.pfx"
        assert config_dict["ca_passwd"] == "cert_password"
        assert config_dict["simulation"] is True
        assert config_dict["contracts_timeout"] == 30
    
    def test_repr(self, temp_config_file, valid_config_data):
        """測試 __repr__ 方法"""
        config_path = temp_config_file(valid_config_data)
        config = Config(config_path)
        
        repr_str = repr(config)
        
        assert "Config" in repr_str
        assert "test_api" in repr_str  # api_key 前8個字元
        assert "A123456789" in repr_str
        assert "simulation=False" in repr_str
    
    def test_config_with_path_object(self, temp_config_file, valid_config_data):
        """測試使用 Path 物件初始化"""
        config_path = temp_config_file(valid_config_data)
        path_obj = Path(config_path)
        
        config = Config(path_obj)
        
        assert config.api_key == "test_api_key_12345"
    
    def test_config_with_string_path(self, temp_config_file, valid_config_data):
        """測試使用字串路徑初始化"""
        config_path = temp_config_file(valid_config_data)
        str_path = str(config_path)
        
        config = Config(str_path)
        
        assert config.api_key == "test_api_key_12345"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
