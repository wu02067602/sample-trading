"""
Login 類別單元測試

使用 mock 模擬 Shioaji API 行為
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from src.config import Config
from src.login import Login, LoginError


class TestLogin:
    """Login 類別測試集"""
    
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
    def mock_config_with_cert(self):
        """模擬帶憑證的 Config 物件"""
        config = Mock(spec=Config)
        config.api_key = "test_api_key_12345"
        config.secret_key = "test_secret_key_67890"
        config.person_id = "A123456789"
        config.ca_path = "/path/to/cert.pfx"
        config.ca_passwd = "cert_password"
        config.simulation = False
        config.contracts_timeout = 0
        return config
    
    @pytest.fixture
    def mock_shioaji(self):
        """模擬的 shioaji 模組"""
        mock_sj_module = MagicMock()
        mock_api_instance = MagicMock()
        mock_sj_module.Shioaji.return_value = mock_api_instance
        return mock_sj_module, mock_api_instance
    
    def test_init_with_valid_config(self, mock_config):
        """測試使用有效 Config 初始化"""
        login = Login(mock_config)
        
        assert login.config == mock_config
        assert login.api is None
        assert login.is_logged_in is False
    
    def test_init_with_invalid_config(self):
        """測試使用無效 Config 初始化"""
        with pytest.raises(TypeError, match="config 必須是 Config 類型"):
            Login("not_a_config")
    
    def test_login_success(self, mock_config, mock_shioaji):
        """測試登入成功"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        # 將 mock 模組加入 sys.modules
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config)
            result = login.login()
            
            # 驗證
            assert result is True
            assert login.is_logged_in is True
            assert login.api is not None
            
            # 驗證呼叫參數
            mock_api_instance.login.assert_called_once_with(
                api_key="test_api_key_12345",
                secret_key="test_secret_key_67890",
                contracts_timeout=30
            )
    
    def test_login_with_certificate(self, mock_config_with_cert, mock_shioaji):
        """測試使用憑證登入"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config_with_cert)
            result = login.login()
            
            # 驗證
            assert result is True
            assert login.is_logged_in is True
            
            # 驗證呼叫參數（包含憑證）
            mock_api_instance.login.assert_called_once_with(
                api_key="test_api_key_12345",
                secret_key="test_secret_key_67890",
                contracts_timeout=0,
                ca_path="/path/to/cert.pfx",
                ca_passwd="cert_password"
            )
    
    def test_login_already_logged_in(self, mock_config, mock_shioaji):
        """測試重複登入"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 第一次登入
            login = Login(mock_config)
            login.login()
            
            # 第二次登入應該失敗
            with pytest.raises(LoginError, match="已經登入，請勿重複登入"):
                login.login()
    
    def test_login_shioaji_not_installed(self, mock_config):
        """測試 shioaji 未安裝"""
        # 確保 shioaji 不在 sys.modules 中
        with patch.dict('sys.modules', {'shioaji': None}):
            login = Login(mock_config)
            
            with pytest.raises(LoginError, match="shioaji 套件未安裝"):
                login.login()
    
    def test_login_connection_error(self, mock_config, mock_shioaji):
        """測試連線失敗"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = ConnectionError("無法連線到伺服器")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config)
            
            with pytest.raises(LoginError, match="連線失敗"):
                login.login()
            
            assert login.is_logged_in is False
    
    def test_login_authentication_error(self, mock_config, mock_shioaji):
        """測試認證失敗"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = Exception("Invalid api_key")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config)
            
            with pytest.raises(LoginError, match="認證失敗.*API 金鑰或密鑰錯誤"):
                login.login()
            
            assert login.is_logged_in is False
    
    def test_login_certificate_error(self, mock_config_with_cert, mock_shioaji):
        """測試憑證錯誤"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = Exception("Invalid certificate")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config_with_cert)
            
            with pytest.raises(LoginError, match="憑證錯誤"):
                login.login()
            
            assert login.is_logged_in is False
    
    def test_login_timeout_error(self, mock_config, mock_shioaji):
        """測試連線逾時"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = Exception("Connection timeout")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config)
            
            with pytest.raises(LoginError, match="連線逾時"):
                login.login()
            
            assert login.is_logged_in is False
    
    def test_login_generic_error(self, mock_config, mock_shioaji):
        """測試一般錯誤"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.side_effect = Exception("Unknown error")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login = Login(mock_config)
            
            with pytest.raises(LoginError, match="登入失敗"):
                login.login()
            
            assert login.is_logged_in is False
    
    def test_logout_success(self, mock_config, mock_shioaji):
        """測試登出成功"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 先登入
            login = Login(mock_config)
            login.login()
            
            # 執行登出
            result = login.logout()
            
            # 驗證
            assert result is True
            assert login.is_logged_in is False
            assert login.api is None
            mock_api_instance.logout.assert_called_once()
    
    def test_logout_not_logged_in(self, mock_config):
        """測試未登入時登出"""
        login = Login(mock_config)
        
        with pytest.raises(LoginError, match="尚未登入"):
            login.logout()
    
    def test_logout_error(self, mock_config, mock_shioaji):
        """測試登出失敗"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        mock_api_instance.logout.side_effect = Exception("登出錯誤")
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 先登入
            login = Login(mock_config)
            login.login()
            
            # 執行登出
            with pytest.raises(LoginError, match="登出失敗"):
                login.logout()
    
    def test_repr(self, mock_config, mock_shioaji):
        """測試 __repr__ 方法"""
        # 未登入狀態
        login = Login(mock_config)
        repr_str = repr(login)
        
        assert "Login" in repr_str
        assert "A123456789" in repr_str
        assert "未登入" in repr_str
        
        # 登入狀態
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            login.login()
            repr_str = repr(login)
            
            assert "已登入" in repr_str
    
    def test_context_manager(self, mock_config, mock_shioaji):
        """測試 context manager 功能"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 使用 context manager
            with Login(mock_config) as login:
                assert login.is_logged_in is True
            
            # 離開 context 後應該自動登出
            mock_api_instance.logout.assert_called_once()
    
    def test_context_manager_with_exception(self, mock_config, mock_shioaji):
        """測試 context manager 遇到異常時的處理"""
        mock_sj_module, mock_api_instance = mock_shioaji
        mock_api_instance.login.return_value = True
        
        with patch.dict('sys.modules', {'shioaji': mock_sj_module}):
            # 使用 context manager 並拋出異常
            with pytest.raises(ValueError):
                with Login(mock_config) as login:
                    assert login.is_logged_in is True
                    raise ValueError("測試異常")
            
            # 即使有異常，也應該自動登出
            mock_api_instance.logout.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
