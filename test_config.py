"""
Config 類別的單元測試模組。

此模組包含對 Config 類別各種情境的測試案例，
確保配置管理功能正確運作。
"""

import os
import tempfile
import pytest
from config import (
    Config,
    ConfigError,
    ConfigFileNotFoundError,
    ConfigReadError,
    ConfigValidationError
)


class TestConfig:
    """Config 類別的測試案例集合。"""
    
    def test_yaml_file_not_exists_should_raise_exception(self):
        """
        測試當 YAML 檔案不存在時，應該要 raise ConfigFileNotFoundError 例外。
        
        此測試確保當指定的配置檔案路徑不存在時，
        Config 類別會正確地拋出 ConfigFileNotFoundError 異常。
        """
        non_existent_file = "non_existent_config.yaml"
        
        # 確保檔案不存在
        if os.path.exists(non_existent_file):
            os.remove(non_existent_file)
        
        with pytest.raises(ConfigFileNotFoundError) as exc_info:
            Config(non_existent_file)
        
        assert "配置檔案不存在" in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)
    
    def test_yaml_file_exists_should_read_successfully(self):
        """
        測試當 YAML 檔案存在時，應該要成功讀取 YAML 檔案。
        
        此測試使用 yaml_sample.yaml 檔案，
        確保 Config 類別能夠成功讀取並初始化。
        """
        config = Config("yaml_sample.yaml")
        
        # 驗證 Config 物件已成功建立
        assert config is not None
        assert isinstance(config, Config)
    
    def test_yaml_file_exists_should_validate_schema(self):
        """
        測試當 YAML 檔案存在時，應該要驗證 YAML 檔案的格式是否符合 schema。
        
        此測試建立一個格式不正確的 YAML 檔案（缺少必要欄位），
        確保 Config 類別會正確地進行 schema 驗證並拋出異常。
        """
        # 建立一個缺少必要欄位的測試檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("person_id: 'A123456789'\n")
            f.write("account: '1234567'\n")
            # 故意缺少 password 和 ca_password
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                Config(temp_file_path)
            
            assert "配置缺少必要欄位" in str(exc_info.value)
        finally:
            # 清理測試檔案
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def test_config_attributes_should_be_set_when_validation_passes(self):
        """
        測試當驗證參數通過時，最終初始化而成的 config 屬性應該要存成類別中的屬性。
        
        此測試使用 yaml_sample.yaml 檔案，
        確保所有配置參數都正確地設定為 Config 物件的屬性。
        """
        config = Config("yaml_sample.yaml")
        
        # 驗證所有必要屬性都已設定
        assert hasattr(config, 'person_id')
        assert hasattr(config, 'account')
        assert hasattr(config, 'password')
        assert hasattr(config, 'ca_password')
        
        # 驗證屬性值正確
        assert config.person_id == "A123456789"
        assert config.account == "1234567"
        assert config.password == "test_password"
        assert config.ca_password == "test_ca_password"
        
        # 驗證屬性值為字串類型
        assert isinstance(config.person_id, str)
        assert isinstance(config.account, str)
        assert isinstance(config.password, str)
        assert isinstance(config.ca_password, str)
    
    def test_should_raise_exception_when_validation_fails(self):
        """
        測試當驗證參數失敗時，應該要 raise ConfigValidationError 例外。
        
        此測試涵蓋多種驗證失敗的情境：
        1. 欄位值為空字串
        2. 欄位值不是字串類型
        3. 配置資料不是字典格式
        """
        # 測試情境 1: 欄位值為空字串
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("person_id: ''\n")
            f.write("account: '1234567'\n")
            f.write("password: 'test_password'\n")
            f.write("ca_password: 'test_ca_password'\n")
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                Config(temp_file_path)
            assert "配置欄位值無效" in str(exc_info.value)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        # 測試情境 2: 欄位值不是字串類型
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("person_id: 'A123456789'\n")
            f.write("account: 1234567\n")  # 數字而非字串
            f.write("password: 'test_password'\n")
            f.write("ca_password: 'test_ca_password'\n")
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                Config(temp_file_path)
            assert "配置欄位值無效" in str(exc_info.value)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        # 測試情境 3: 配置資料不是字典格式（YAML 為純文字）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("just a plain string\n")
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigValidationError) as exc_info:
                Config(temp_file_path)
            assert "配置資料格式錯誤" in str(exc_info.value)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def test_should_raise_exception_when_yaml_read_fails(self):
        """
        測試當 YAML 檔案存在且讀取失敗，應該要 raise ConfigReadError 例外。
        
        此測試建立一個格式錯誤的 YAML 檔案，
        確保 Config 類別會正確地拋出 ConfigReadError 異常。
        """
        # 建立一個格式錯誤的 YAML 檔案（無效的 YAML 語法）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("person_id: 'A123456789'\n")
            f.write("account: [\n")  # 不完整的陣列語法
            f.write("  - item1\n")
            f.write("password: 'test'\n")
            # 缺少陣列結尾括號，造成 YAML 解析錯誤
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigReadError) as exc_info:
                Config(temp_file_path)
            
            assert "讀取配置檔案失敗" in str(exc_info.value)
        finally:
            # 清理測試檔案
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        # 測試空檔案的情況
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # 建立一個空檔案
            temp_file_path = f.name
        
        try:
            with pytest.raises(ConfigReadError) as exc_info:
                Config(temp_file_path)
            
            assert "配置檔案為空或格式不正確" in str(exc_info.value)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


class TestConfigRepresentation:
    """測試 Config 類別的字串表示功能。"""
    
    def test_repr_should_mask_passwords(self):
        """
        測試 Config 物件的字串表示應該要遮蔽密碼。
        
        確保在輸出 Config 物件資訊時，密碼欄位會被遮蔽，
        避免敏感資訊外洩。
        """
        config = Config("yaml_sample.yaml")
        repr_str = repr(config)
        
        # 驗證 repr 包含非敏感資訊
        assert "A123456789" in repr_str
        assert "1234567" in repr_str
        
        # 驗證密碼被遮蔽
        assert "test_password" not in repr_str
        assert "test_ca_password" not in repr_str
        assert "***" in repr_str
