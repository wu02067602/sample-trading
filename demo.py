#!/usr/bin/env python3
"""
BrokerageAuth 示範程式

此程式展示如何使用 BrokerageAuth 類別進行永豐金證券 API 的認證流程，
包括登入、獲取 Session、刷新 Token 以及錯誤處理的完整示例。

運行前請確保設置以下環境變數：
- BROKER_API_KEY: 永豐金證券 API Key
- BROKER_CERT_PATH: 憑證檔案路徑

Author: Senior Backend Engineer
Date: 2025-09-25
"""

import os
import sys
import logging
import time
from brokerage_auth import (
    BrokerageAuth, 
    BrokerageAuthError,
    EnvironmentError,
    CertificateError,
    AuthenticationError,
    SessionError
)


def setup_logging():
    """設置日誌配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/workspace/demo.log')
        ]
    )
    return logging.getLogger(__name__)


def test_environment_validation():
    """測試環境變數驗證功能"""
    logger = logging.getLogger(__name__)
    logger.info("=== 測試環境變數驗證 ===")
    
    # 備份原始環境變數
    original_api_key = os.getenv('BROKER_API_KEY')
    original_cert_path = os.getenv('BROKER_CERT_PATH')
    
    try:
        # 測試缺少 API Key
        if 'BROKER_API_KEY' in os.environ:
            del os.environ['BROKER_API_KEY']
        
        try:
            BrokerageAuth()
            logger.error("❌ 應該拋出 EnvironmentError (API Key)")
        except EnvironmentError as e:
            logger.info(f"✅ 正確捕獲 API Key 錯誤: {e}")
        
        # 恢復 API Key，測試缺少憑證路徑
        if original_api_key:
            os.environ['BROKER_API_KEY'] = original_api_key
        
        if 'BROKER_CERT_PATH' in os.environ:
            del os.environ['BROKER_CERT_PATH']
        
        try:
            BrokerageAuth()
            logger.error("❌ 應該拋出 EnvironmentError (Cert Path)")
        except EnvironmentError as e:
            logger.info(f"✅ 正確捕獲憑證路徑錯誤: {e}")
        
        # 測試憑證檔案不存在
        os.environ['BROKER_CERT_PATH'] = '/nonexistent/path/cert.pem'
        
        try:
            BrokerageAuth()
            logger.error("❌ 應該拋出 CertificateError")
        except CertificateError as e:
            logger.info(f"✅ 正確捕獲憑證檔案錯誤: {e}")
            
    finally:
        # 恢復原始環境變數
        if original_api_key:
            os.environ['BROKER_API_KEY'] = original_api_key
        if original_cert_path:
            os.environ['BROKER_CERT_PATH'] = original_cert_path


def test_basic_authentication():
    """測試基本認證功能"""
    logger = logging.getLogger(__name__)
    logger.info("=== 測試基本認證功能 ===")
    
    try:
        # 初始化認證物件
        auth = BrokerageAuth()
        logger.info("✅ BrokerageAuth 初始化成功")
        
        # 檢查初始狀態
        status = auth.get_status()
        logger.info(f"初始狀態: {status}")
        
        # 測試登入
        logger.info("嘗試登入...")
        try:
            login_result = auth.login()
            logger.info(f"✅ 登入成功: {login_result}")
            
            # 檢查登入後狀態
            status = auth.get_status()
            logger.info(f"登入後狀態: {status}")
            
            # 測試獲取 Session
            session = auth.get_session()
            logger.info(f"✅ 成功獲取 Session: {type(session)}")
            
            # 測試是否已登入
            if auth.is_logged_in():
                logger.info("✅ 確認已成功登入")
            else:
                logger.warning("⚠️ 登入狀態檢查失敗")
            
            # 測試刷新功能
            logger.info("測試 Token 刷新...")
            refresh_result = auth.refresh()
            logger.info(f"✅ Token 刷新成功: {refresh_result}")
            
            # 測試登出
            logout_result = auth.logout()
            logger.info(f"✅ 登出成功: {logout_result}")
            
        except AuthenticationError as e:
            logger.warning(f"⚠️ 認證失敗（可能是測試環境或憑證問題）: {e}")
            return False
            
    except (EnvironmentError, CertificateError) as e:
        logger.error(f"❌ 環境配置錯誤: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 未預期錯誤: {e}")
        return False
    
    return True


def test_session_management():
    """測試 Session 管理功能"""
    logger = logging.getLogger(__name__)
    logger.info("=== 測試 Session 管理功能 ===")
    
    try:
        auth = BrokerageAuth()
        
        # 測試在沒有登入時獲取 Session（應自動登入）
        logger.info("測試自動登入功能...")
        session = auth.get_session()
        logger.info("✅ 自動登入成功")
        
        # 測試重複獲取 Session（應返回快取的 Session）
        session2 = auth.get_session()
        if session is session2:
            logger.info("✅ Session 快取機制正常")
        else:
            logger.warning("⚠️ Session 快取機制可能有問題")
        
        # 測試 Session 狀態檢查
        status = auth.get_status()
        logger.info(f"Session 狀態: {status}")
        
        # 清理
        auth.logout()
        
    except AuthenticationError as e:
        logger.warning(f"⚠️ 認證相關錯誤: {e}")
    except Exception as e:
        logger.error(f"❌ Session 管理測試失敗: {e}")


def test_error_scenarios():
    """測試各種錯誤情境"""
    logger = logging.getLogger(__name__)
    logger.info("=== 測試錯誤情境 ===")
    
    try:
        auth = BrokerageAuth()
        
        # 測試在沒有 Session 時進行刷新
        try:
            auth.refresh()
            logger.error("❌ 應該拋出 SessionError")
        except SessionError as e:
            logger.info(f"✅ 正確捕獲 Session 錯誤: {e}")
        
        logger.info("錯誤情境測試完成")
        
    except Exception as e:
        logger.error(f"❌ 錯誤情境測試失敗: {e}")


def interactive_demo():
    """互動式示範"""
    logger = logging.getLogger(__name__)
    logger.info("=== 互動式示範 ===")
    
    try:
        print("\n🚀 BrokerageAuth 互動式示範")
        print("=" * 50)
        
        # 初始化
        print("📝 正在初始化 BrokerageAuth...")
        auth = BrokerageAuth()
        print("✅ 初始化成功！")
        
        # 顯示初始狀態
        status = auth.get_status()
        print(f"\n📊 初始狀態:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # 執行登入
        print("\n🔐 正在執行登入...")
        try:
            login_result = auth.login()
            print("✅ 登入成功！")
            print(f"   登入時間: {login_result['login_time']}")
            print(f"   Session ID: {login_result['session_id']}")
        except AuthenticationError as e:
            print(f"❌ 登入失敗: {e}")
            print("💡 請檢查環境變數和憑證設定")
            return
        
        # 顯示登入後狀態
        status = auth.get_status()
        print(f"\n📊 登入後狀態:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # 測試 Session 獲取
        print("\n🔄 測試 Session 獲取...")
        session = auth.get_session()
        print(f"✅ 成功獲取 Session: {type(session).__name__}")
        
        # 測試刷新
        print("\n🔄 測試 Token 刷新...")
        refresh_result = auth.refresh()
        print("✅ Token 刷新成功！")
        print(f"   刷新時間: {refresh_result['refresh_time']}")
        
        # 最終狀態
        status = auth.get_status()
        print(f"\n📊 最終狀態:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # 登出
        print("\n👋 正在登出...")
        logout_result = auth.logout()
        print(f"✅ {logout_result['message']}")
        
        print("\n🎉 示範完成！")
        
    except Exception as e:
        print(f"\n❌ 示範過程發生錯誤: {e}")
        logger.error(f"互動式示範失敗: {e}")


def main():
    """主程式"""
    logger = setup_logging()
    logger.info("開始執行 BrokerageAuth 示範程式")
    
    print("🔍 BrokerageAuth 功能驗證程式")
    print("=" * 50)
    
    # 檢查環境變數
    api_key = os.getenv('BROKER_API_KEY')
    cert_path = os.getenv('BROKER_CERT_PATH')
    
    print(f"環境變數檢查:")
    print(f"  BROKER_API_KEY: {'✅ 已設定' if api_key else '❌ 未設定'}")
    print(f"  BROKER_CERT_PATH: {'✅ 已設定' if cert_path else '❌ 未設定'}")
    
    if cert_path and os.path.exists(cert_path):
        print(f"  憑證檔案: ✅ 存在")
    elif cert_path:
        print(f"  憑證檔案: ❌ 不存在於 {cert_path}")
    else:
        print(f"  憑證檔案: ❌ 路徑未設定")
    
    print()
    
    # 執行測試
    tests = [
        ("環境變數驗證", test_environment_validation),
        ("錯誤情境", test_error_scenarios),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"🧪 執行 {test_name} 測試...")
            test_func()
            print(f"✅ {test_name} 測試完成\n")
        except Exception as e:
            print(f"❌ {test_name} 測試失敗: {e}\n")
            logger.error(f"{test_name} 測試失敗", exc_info=True)
    
    # 如果環境變數完整，執行完整功能測試
    if api_key and cert_path and os.path.exists(cert_path):
        print("🚀 環境配置完整，執行完整功能測試...")
        
        # 基本認證測試
        if test_basic_authentication():
            print("✅ 基本認證測試通過")
        else:
            print("⚠️ 基本認證測試有問題（可能是網路或憑證問題）")
        
        # Session 管理測試
        test_session_management()
        
        # 互動式示範
        try:
            interactive_demo()
        except KeyboardInterrupt:
            print("\n\n👋 使用者中斷示範")
        except Exception as e:
            print(f"\n❌ 互動式示範發生錯誤: {e}")
    else:
        print("⚠️ 環境變數不完整，跳過實際 API 測試")
        print("\n💡 要執行完整測試，請設定:")
        print("   export BROKER_API_KEY='your_api_key'")
        print("   export BROKER_CERT_PATH='/path/to/cert.pem'")
    
    logger.info("BrokerageAuth 示範程式執行完成")


if __name__ == "__main__":
    main()