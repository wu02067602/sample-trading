"""
委託回報處理器測試模組
"""

import unittest
from unittest.mock import Mock, patch
import logging
import sys
import os

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.broker.order_callback_handler import OrderCallbackHandler


class TestOrderCallbackHandler(unittest.TestCase):
    """委託回報處理器測試類別"""
    
    def setUp(self):
        """測試前置作業"""
        self.handler = OrderCallbackHandler()
        self.mock_listener = Mock()
    
    def test_register_listener_success(self):
        """
        測試成功註冊監聽器
        
        預期結果：監聽器應該被成功註冊到列表中
        """
        self.handler.register_listener(self.mock_listener)
        self.assertIn(self.mock_listener, self.handler._listeners)
    
    def test_register_listener_invalid_type(self):
        """
        測試註冊無效的監聽器
        
        預期結果：應該拋出 TypeError
        """
        invalid_listener = "not_a_listener"
        with self.assertRaises(TypeError):
            self.handler.register_listener(invalid_listener)
    
    def test_remove_listener_success(self):
        """
        測試成功移除監聽器
        
        預期結果：監聽器應該被從列表中移除
        """
        self.handler.register_listener(self.mock_listener)
        self.handler.remove_listener(self.mock_listener)
        self.assertNotIn(self.mock_listener, self.handler._listeners)
    
    def test_remove_listener_not_found(self):
        """
        測試移除不存在的監聽器
        
        預期結果：應該拋出 ValueError
        """
        with self.assertRaises(ValueError):
            self.handler.remove_listener(self.mock_listener)
    
    def test_handle_order_callback_success(self):
        """
        測試成功處理委託回報
        
        預期結果：監聽器的 on_order_status_changed 方法應該被調用
        """
        self.handler.register_listener(self.mock_listener)
        
        stat = 0
        msg = {
            'order_id': 'ORDER123',
            'status': 'Filled',
            'order_quantity': 100,
            'deal_quantity': 100,
            'order_price': 50.0,
            'stock_id': '2330',
            'operation': 'Buy',
            'order_time': '2025-10-07 10:00:00'
        }
        
        self.handler.handle_order_callback(stat, msg)
        
        self.mock_listener.on_order_status_changed.assert_called_once()
        call_args = self.mock_listener.on_order_status_changed.call_args[0][0]
        self.assertEqual(call_args['order_id'], 'ORDER123')
        self.assertEqual(call_args['status'], 'Filled')
    
    def test_handle_order_callback_invalid_msg(self):
        """
        測試處理無效的委託訊息
        
        預期結果：應該拋出 ValueError
        """
        with self.assertRaises(ValueError):
            self.handler.handle_order_callback(0, "not_a_dict")
    
    def test_handle_deal_callback_success(self):
        """
        測試成功處理成交回報
        
        預期結果：監聽器的 on_deal_received 方法應該被調用
        """
        self.handler.register_listener(self.mock_listener)
        
        stat = 0
        msg = {
            'order_id': 'ORDER123',
            'deal_quantity': 100,
            'deal_price': 50.0,
            'stock_id': '2330',
            'deal_time': '2025-10-07 10:00:01'
        }
        
        self.handler.handle_deal_callback(stat, msg)
        
        self.mock_listener.on_deal_received.assert_called_once()
        call_args = self.mock_listener.on_deal_received.call_args[0][0]
        self.assertEqual(call_args['order_id'], 'ORDER123')
        self.assertEqual(call_args['deal_quantity'], 100)
    
    def test_handle_deal_callback_invalid_msg(self):
        """
        測試處理無效的成交訊息
        
        預期結果：應該拋出 ValueError
        """
        with self.assertRaises(ValueError):
            self.handler.handle_deal_callback(0, "not_a_dict")
    
    def test_listener_error_handling(self):
        """
        測試監聽器拋出錯誤時的處理
        
        預期結果：錯誤應該被記錄但不影響其他監聽器
        """
        # 建立兩個監聽器，第一個會拋出錯誤
        error_listener = Mock()
        error_listener.on_order_status_changed.side_effect = ValueError("Test error")
        
        normal_listener = Mock()
        
        self.handler.register_listener(error_listener)
        self.handler.register_listener(normal_listener)
        
        msg = {
            'order_id': 'ORDER123',
            'status': 'Filled',
            'order_quantity': 100,
            'deal_quantity': 100,
            'order_price': 50.0,
            'stock_id': '2330',
            'operation': 'Buy',
            'order_time': '2025-10-07 10:00:00'
        }
        
        # 應該不會拋出異常，且正常監聽器應該被通知
        self.handler.handle_order_callback(0, msg)
        
        error_listener.on_order_status_changed.assert_called_once()
        normal_listener.on_order_status_changed.assert_called_once()


if __name__ == '__main__':
    unittest.main()
