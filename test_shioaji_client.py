"""
Shioaji 客戶端單元測試

此測試展示了如何透過抽象介面進行測試，遵循依賴反轉原則。
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from trading_interface import ITradingClient, IConfigValidator
from shioaji_client import ShioajiClient, LoginConfig


class MockTradingClient(ITradingClient):
    """
    模擬交易客戶端，用於測試
    
    此類別展示了抽象介面的價值：我們可以輕鬆創建模擬實作進行測試。
    """
    
    def __init__(self):
        self._connected = False
        self._accounts = {
            'stock_account': 'MOCK_STOCK_ACCOUNT',
            'futopt_account': 'MOCK_FUTOPT_ACCOUNT'
        }
    
    def connect(self, config: Any) -> bool:
        """模擬連線"""
        self._connected = True
        return True
    
    def disconnect(self) -> bool:
        """模擬斷線"""
        self._connected = False
        return True
    
    def get_accounts(self) -> Dict[str, Any]:
        """模擬取得帳戶"""
        if not self._connected:
            raise RuntimeError("尚未連線")
        return self._accounts
    
    def is_connected(self) -> bool:
        """檢查連線狀態"""
        return self._connected


class TestLoginConfig(unittest.TestCase):
    """測試 LoginConfig 類別"""
    
    def test_valid_config(self):
        """測試有效的配置"""
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123"
        )
        # 不應該拋出異常
        config.validate()
    
    def test_empty_person_id(self):
        """測試空的 person_id"""
        config = LoginConfig(
            person_id="",
            passwd="password123"
        )
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("person_id", str(context.exception))
    
    def test_empty_passwd(self):
        """測試空的 passwd"""
        config = LoginConfig(
            person_id="A123456789",
            passwd=""
        )
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("passwd", str(context.exception))
    
    def test_ca_path_without_passwd(self):
        """測試只提供 ca_path 但沒有 ca_passwd"""
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123",
            ca_path="/path/to/cert.pfx"
        )
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("ca_passwd", str(context.exception))
    
    def test_ca_passwd_without_path(self):
        """測試只提供 ca_passwd 但沒有 ca_path"""
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123",
            ca_passwd="cert_password"
        )
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("ca_path", str(context.exception))
    
    def test_valid_ca_config(self):
        """測試有效的 CA 配置"""
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123",
            ca_path="/path/to/cert.pfx",
            ca_passwd="cert_password"
        )
        # 不應該拋出異常
        config.validate()


class TestShioajiClient(unittest.TestCase):
    """測試 ShioajiClient 類別"""
    
    @patch('shioaji_client.sj.Shioaji')
    def test_login_success(self, mock_shioaji_class):
        """測試成功登入"""
        # 設定 mock
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1', 'account2']
        mock_shioaji_class.return_value = mock_api
        
        # 執行測試
        client = ShioajiClient()
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123"
        )
        
        result = client.login(config)
        
        # 驗證結果
        self.assertTrue(result)
        self.assertTrue(client.is_logged_in)
        self.assertTrue(client.is_connected())
        mock_api.login.assert_called_once_with(
            person_id="A123456789",
            passwd="password123"
        )
    
    @patch('shioaji_client.sj.Shioaji')
    def test_login_with_ca(self, mock_shioaji_class):
        """測試使用 CA 憑證登入"""
        # 設定 mock
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1']
        mock_shioaji_class.return_value = mock_api
        
        # 執行測試
        client = ShioajiClient()
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123",
            ca_path="/path/to/cert.pfx",
            ca_passwd="cert_password"
        )
        
        result = client.login(config)
        
        # 驗證結果
        self.assertTrue(result)
        mock_api.activate_ca.assert_called_once_with(
            ca_path="/path/to/cert.pfx",
            ca_passwd="cert_password",
            person_id="A123456789"
        )
    
    @patch('shioaji_client.sj.Shioaji')
    def test_connect_method(self, mock_shioaji_class):
        """測試 connect 方法（ITradingClient 介面）"""
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1']
        mock_shioaji_class.return_value = mock_api
        
        client = ShioajiClient()
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123"
        )
        
        # 測試 connect 方法（應該調用 login）
        result = client.connect(config)
        
        self.assertTrue(result)
        self.assertTrue(client.is_connected())
    
    @patch('shioaji_client.sj.Shioaji')
    def test_logout_success(self, mock_shioaji_class):
        """測試成功登出"""
        # 設定 mock
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1']
        mock_api.logout.return_value = True
        mock_shioaji_class.return_value = mock_api
        
        # 先登入
        client = ShioajiClient()
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123"
        )
        client.login(config)
        
        # 執行登出
        result = client.logout()
        
        # 驗證結果
        self.assertTrue(result)
        self.assertFalse(client.is_logged_in)
        self.assertFalse(client.is_connected())
        mock_api.logout.assert_called_once()
    
    def test_logout_without_login(self):
        """測試未登入時執行登出"""
        client = ShioajiClient()
        
        with self.assertRaises(RuntimeError) as context:
            client.logout()
        self.assertIn("尚未登入", str(context.exception))
    
    @patch('shioaji_client.sj.Shioaji')
    def test_get_accounts(self, mock_shioaji_class):
        """測試取得帳戶資訊"""
        # 設定 mock
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1']
        mock_api.stock_account = 'STOCK_ACCOUNT'
        mock_api.futopt_account = 'FUTOPT_ACCOUNT'
        mock_shioaji_class.return_value = mock_api
        
        # 先登入
        client = ShioajiClient()
        config = LoginConfig(
            person_id="A123456789",
            passwd="password123"
        )
        client.login(config)
        
        # 取得帳戶
        accounts = client.get_accounts()
        
        # 驗證結果
        self.assertEqual(accounts['stock_account'], 'STOCK_ACCOUNT')
        self.assertEqual(accounts['futopt_account'], 'FUTOPT_ACCOUNT')
    
    def test_get_accounts_without_login(self):
        """測試未登入時取得帳戶"""
        client = ShioajiClient()
        
        with self.assertRaises(RuntimeError) as context:
            client.get_accounts()
        self.assertIn("尚未登入", str(context.exception))
    
    @patch('shioaji_client.sj.Shioaji')
    def test_context_manager(self, mock_shioaji_class):
        """測試 context manager 功能"""
        # 設定 mock
        mock_api = MagicMock()
        mock_api.login.return_value = ['account1']
        mock_api.logout.return_value = True
        mock_shioaji_class.return_value = mock_api
        
        # 使用 with 語句
        with ShioajiClient() as client:
            config = LoginConfig(
                person_id="A123456789",
                passwd="password123"
            )
            client.login(config)
            self.assertTrue(client.is_logged_in)
        
        # 離開 with 區塊後應該自動登出
        mock_api.logout.assert_called_once()


class TestMockTradingClient(unittest.TestCase):
    """測試模擬交易客戶端"""
    
    def test_implements_interface(self):
        """測試是否正確實作介面"""
        client = MockTradingClient()
        self.assertIsInstance(client, ITradingClient)
    
    def test_connect_disconnect(self):
        """測試連線和斷線"""
        client = MockTradingClient()
        
        # 初始狀態應該未連線
        self.assertFalse(client.is_connected())
        
        # 連線
        result = client.connect(None)
        self.assertTrue(result)
        self.assertTrue(client.is_connected())
        
        # 斷線
        result = client.disconnect()
        self.assertTrue(result)
        self.assertFalse(client.is_connected())
    
    def test_get_accounts(self):
        """測試取得帳戶"""
        client = MockTradingClient()
        
        # 未連線時應該拋出異常
        with self.assertRaises(RuntimeError):
            client.get_accounts()
        
        # 連線後應該能取得帳戶
        client.connect(None)
        accounts = client.get_accounts()
        self.assertIn('stock_account', accounts)
        self.assertIn('futopt_account', accounts)


def test_polymorphism():
    """
    測試多型性：展示如何透過抽象介面使用不同的實作
    
    這個測試展示了依賴反轉原則的價值：
    高層模組依賴於抽象介面，而非具體實作。
    """
    def use_trading_client(client: ITradingClient, config: Any = None):
        """
        使用交易客戶端的範例函數
        
        此函數接受 ITradingClient 介面，可以使用任何實作該介面的類別。
        """
        client.connect(config)
        assert client.is_connected()
        accounts = client.get_accounts()
        assert accounts is not None
        client.disconnect()
        assert not client.is_connected()
    
    # 使用模擬客戶端
    mock_client = MockTradingClient()
    use_trading_client(mock_client)
    
    print("多型性測試通過：可以透過抽象介面使用不同的實作")


if __name__ == '__main__':
    # 執行單元測試
    print("=== 執行單元測試 ===\n")
    unittest.main(verbosity=2, exit=False)
    
    # 執行多型性測試
    print("\n=== 執行多型性測試 ===\n")
    test_polymorphism()
