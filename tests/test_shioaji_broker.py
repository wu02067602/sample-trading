"""
永豐證券券商介面測試模組
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock shioaji module before importing ShioajiBroker
sys.modules['shioaji'] = MagicMock()

from src.broker.shioaji_broker import ShioajiBroker
from src.broker.order_callback_handler import OrderCallbackHandler


class TestShioajiBroker(unittest.TestCase):
    """永豐證券券商介面測試類別"""
    
    def setUp(self):
        """測試前準備"""
        self.broker = ShioajiBroker()
    
    def test_initial_state(self):
        """測試初始狀態"""
        self.assertFalse(self.broker.is_connected)
        self.assertIsNone(self.broker._api)
    
    def test_connect_empty_credentials(self):
        """測試使用空憑證連線"""
        with self.assertRaises(ValueError):
            self.broker.connect("", "")
        
        with self.assertRaises(ValueError):
            self.broker.connect("key", "")
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_connect_success(self, mock_shioaji):
        """測試成功連線"""
        mock_api = MagicMock()
        mock_shioaji.return_value = mock_api
        
        self.broker.connect("test_key", "test_secret", simulation=True)
        
        self.assertTrue(self.broker.is_connected)
        mock_shioaji.assert_called_once_with(simulation=True)
        mock_api.login.assert_called_once_with(
            api_key="test_key",
            secret_key="test_secret"
        )
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_connect_failure(self, mock_shioaji):
        """測試連線失敗"""
        mock_shioaji.side_effect = ConnectionError("Connection failed")
        
        with self.assertRaises(ConnectionError):
            self.broker.connect("test_key", "test_secret")
    
    def test_disconnect_not_connected(self):
        """測試未連線時斷開連線"""
        with self.assertRaises(RuntimeError):
            self.broker.disconnect()
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_disconnect_success(self, mock_shioaji):
        """測試成功斷開連線"""
        mock_api = MagicMock()
        mock_shioaji.return_value = mock_api
        
        self.broker.connect("test_key", "test_secret")
        self.broker.disconnect()
        
        self.assertFalse(self.broker.is_connected)
        mock_api.logout.assert_called_once()
    
    def test_setup_order_callback_not_connected(self):
        """測試未連線時設定回調"""
        handler = OrderCallbackHandler()
        
        with self.assertRaises(RuntimeError):
            self.broker.setup_order_callback(handler)
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_setup_order_callback_invalid_handler(self, mock_shioaji):
        """測試使用無效的處理器"""
        mock_api = MagicMock()
        mock_shioaji.return_value = mock_api
        
        self.broker.connect("test_key", "test_secret")
        
        with self.assertRaises(TypeError):
            self.broker.setup_order_callback("invalid")
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_setup_order_callback_success(self, mock_shioaji):
        """測試成功設定回調"""
        mock_api = MagicMock()
        mock_shioaji.return_value = mock_api
        
        self.broker.connect("test_key", "test_secret")
        handler = OrderCallbackHandler()
        self.broker.setup_order_callback(handler)
        
        mock_api.set_order_callback.assert_called_once()
        mock_api.set_deal_callback.assert_called_once()
    
    def test_get_api_not_connected(self):
        """測試未連線時取得 API"""
        with self.assertRaises(RuntimeError):
            self.broker.get_api()
    
    @patch('src.broker.shioaji_broker.sj.Shioaji')
    def test_get_api_success(self, mock_shioaji):
        """測試成功取得 API"""
        mock_api = MagicMock()
        mock_shioaji.return_value = mock_api
        
        self.broker.connect("test_key", "test_secret")
        api = self.broker.get_api()
        
        self.assertEqual(api, mock_api)


if __name__ == '__main__':
    unittest.main()
