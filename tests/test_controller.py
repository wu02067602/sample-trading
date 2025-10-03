"""
Controller 類別整合測試

測試 Controller 如何整合 Config 和 Login 類別
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from src.config import Config, ConfigError
from src.login import Login, LoginError
from src.controller import Controller, ControllerError


class TestController:
    """Controller 類別測試集"""
    
    @pytest.fixture
    def mock_config(self):
        """模擬的 Config 物件"""
        config = Mock(spec=Config)
        config.api_key = "test_api_key_12345"
        config.secret_key = "test_secret_key_67890"
        config.person_id = "A123456789"
        config.ca_path = None
        config.ca_passwd = None
        config.simulation = True
        config.contracts_timeout = 30
        return config
    
    @pytest.fixture
    def mock_shioaji(self):
        """模擬的 shioaji 模組"""
        mock_sj_module = MagicMock()
        mock_api_instance = MagicMock()
        mock_sj_module.Shioaji.return_value = mock_api_instance
        return mock_sj_module, mock_api_instance
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """創建臨時配置檔案"""
        config_data = {
            "api_key": "test_api_key_12345",
            "secret_key": "test_secret_key_67890",
            "person_id": "A123456789",
            "simulation": True,
        }
        config_file = tmp_path / "test_config.yaml"
        import yaml
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return config_file
    
    # === 初始化測試 ===
    
    def test_init_with_config_object(self, mock_config):
        """測試使用 Config 物件初始化"""
        controller = Controller(mock_config)
        
        assert controller.config == mock_config
        assert isinstance(controller.login, Login)
        assert controller.sj is None
        assert not controller.is_connected()
    
    def test_init_with_config_path_string(self, temp_config_file):
        """測試使用字串路徑初始化"""
        controller = Controller(str(temp_config_file))
        
        assert isinstance(controller.config, Config)
        assert isinstance(controller.login, Login)
        assert controller.sj is None
    
    def test_init_with_config_path_object(self, temp_config_file):
        """測試使用 Path 物件初始化"""
        controller = Controller(Path(temp_config_file))
        
        assert isinstance(controller.config, Config)
        assert isinstance(controller.login, Login)
        assert controller.sj is None
    
    def test_init_with_invalid_type(self):
        """測試使用無效類型初始化"""
        with pytest.raises(TypeError, match="config 必須是 str、Path 或 Config 類型"):
            Controller(123)
    
    def test_init_with_invalid_config_file(self, tmp_path):
        """測試使用不存在的配置檔案初始化"""
        with pytest.raises(ConfigError):
            Controller(tmp_path / "non_existent.yaml")
    
    # === 連線測試 ===
    
    def test_connect_success(self, mock_config, mock_shioaji):
        """測試連線成功"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            result = controller.connect()
            
            # 驗證
            assert result is True
            assert controller.is_connected()
            assert controller.sj is not None
            assert controller.sj == mock_api_instance
    
    def test_connect_already_connected(self, mock_config, mock_shioaji):
        """測試重複連線"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            # 第二次連線應該失敗
            with pytest.raises(ControllerError, match="已經連線，請勿重複連線"):
                controller.connect()
    
    def test_connect_login_failure(self, mock_config, mock_shioaji):
        """測試連線失敗"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = Exception("Invalid api_key")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            
            with pytest.raises(LoginError, match="連線失敗"):
                controller.connect()
            
            assert not controller.is_connected()
            assert controller.sj is None
    
    # === 中斷連線測試 ===
    
    def test_disconnect_success(self, mock_config, mock_shioaji):
        """測試中斷連線成功"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            # 中斷連線
            result = controller.disconnect()
            
            # 驗證
            assert result is True
            assert not controller.is_connected()
            assert controller.sj is None
    
    def test_disconnect_not_connected(self, mock_config):
        """測試未連線時中斷連線"""
        controller = Controller(mock_config)
        
        with pytest.raises(ControllerError, match="尚未連線"):
            controller.disconnect()
    
    def test_disconnect_logout_failure(self, mock_config, mock_shioaji):
        """測試登出失敗"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        mock_api_instance.logout.side_effect = Exception("登出錯誤")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            with pytest.raises(LoginError, match="中斷連線失敗"):
                controller.disconnect()
    
    # === 連線狀態檢查測試 ===
    
    def test_is_connected_before_connect(self, mock_config):
        """測試連線前的狀態"""
        controller = Controller(mock_config)
        assert not controller.is_connected()
    
    def test_is_connected_after_connect(self, mock_config, mock_shioaji):
        """測試連線後的狀態"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            assert controller.is_connected()
    
    def test_is_connected_after_disconnect(self, mock_config, mock_shioaji):
        """測試中斷連線後的狀態"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            controller.disconnect()
            
            assert not controller.is_connected()
    
    # === 狀態資訊測試 ===
    
    def test_get_status_not_connected(self, mock_config):
        """測試取得未連線狀態"""
        controller = Controller(mock_config)
        status = controller.get_status()
        
        assert status["connected"] is False
        assert status["person_id"] == "A123456789"
        assert status["simulation"] is True
        assert status["has_certificate"] is False
    
    def test_get_status_connected(self, mock_config, mock_shioaji):
        """測試取得已連線狀態"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            status = controller.get_status()
            
            assert status["connected"] is True
            assert status["person_id"] == "A123456789"
            assert status["simulation"] is True
    
    def test_get_status_with_certificate(self, mock_config, mock_shioaji):
        """測試有憑證的狀態"""
        mock_config.ca_path = "/path/to/cert.pfx"
        
        controller = Controller(mock_config)
        status = controller.get_status()
        
        assert status["has_certificate"] is True
    
    # === __repr__ 測試 ===
    
    def test_repr_not_connected(self, mock_config):
        """測試未連線的字串表示"""
        controller = Controller(mock_config)
        repr_str = repr(controller)
        
        assert "Controller" in repr_str
        assert "A123456789" in repr_str
        assert "未連線" in repr_str
        assert "simulation=True" in repr_str
    
    def test_repr_connected(self, mock_config, mock_shioaji):
        """測試已連線的字串表示"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            controller = Controller(mock_config)
            controller.connect()
            
            repr_str = repr(controller)
            
            assert "Controller" in repr_str
            assert "已連線" in repr_str
    
    # === Context Manager 測試 ===
    
    def test_context_manager(self, mock_config, mock_shioaji):
        """測試 Context Manager 功能"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 使用 with 語句
            with Controller(mock_config) as controller:
                assert controller.is_connected()
                assert controller.sj is not None
            
            # 離開後應該自動中斷連線
            # 注意：這裡的 controller 變數已經離開 context，無法直接檢查
            mock_api_instance.logout.assert_called_once()
    
    def test_context_manager_with_exception(self, mock_config, mock_shioaji):
        """測試 Context Manager 遇到異常時的處理"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 使用 with 語句並拋出異常
            with pytest.raises(ValueError):
                with Controller(mock_config) as controller:
                    assert controller.is_connected()
                    raise ValueError("測試異常")
            
            # 即使有異常，也應該自動中斷連線
            mock_api_instance.logout.assert_called_once()
    
    # === 整合測試 ===
    
    def test_full_lifecycle(self, mock_config, mock_shioaji):
        """測試完整的生命週期"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 1. 初始化
            controller = Controller(mock_config)
            assert not controller.is_connected()
            
            # 2. 連線
            controller.connect()
            assert controller.is_connected()
            assert controller.sj is not None
            
            # 3. 取得狀態
            status = controller.get_status()
            assert status["connected"] is True
            
            # 4. 中斷連線
            controller.disconnect()
            assert not controller.is_connected()
            assert controller.sj is None
    
    def test_integration_with_real_config_file(self, temp_config_file, mock_shioaji):
        """測試與真實配置檔案的整合"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 使用真實的配置檔案
            controller = Controller(temp_config_file)
            
            # 驗證配置被正確載入
            assert controller.config.api_key == "test_api_key_12345"
            assert controller.config.person_id == "A123456789"
            
            # 測試連線
            controller.connect()
            assert controller.is_connected()
            
            # 測試中斷連線
            controller.disconnect()
            assert not controller.is_connected()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
