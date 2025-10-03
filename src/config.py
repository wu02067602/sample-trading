"""永豐 Shioaji API 配置管理模組

此模組提供配置檔案的讀取、驗證和管理功能。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


class ConfigError(Exception):
    """配置錯誤異常"""
    pass


class Config:
    """永豐 Shioaji API 配置管理類別
    
    此類別負責讀取和驗證 YAML 格式的配置檔案，支援兩種登入方式：
    1. API Key 方式 (version >= 1.0，推薦)
    2. 帳號密碼方式 (version < 1.0，舊版)
    
    Attributes:
        config_data (Dict[str, Any]): 配置資料字典
        login_method (str): 登入方式 ('api' 或 'account')
    
    Example:
        >>> config = Config("config.yaml")
        >>> api_key = config.get("api.api_key")
        >>> config.validate()
    """
    
    # 定義必填欄位
    REQUIRED_FIELDS_API = ["api.api_key", "api.secret_key"]
    REQUIRED_FIELDS_ACCOUNT = ["account.person_id", "account.passwd"]
    
    # 定義預設值
    DEFAULTS = {
        "api": {
            "fetch_contract": True,
            "contracts_timeout": 0,
            "subscribe_trade": True,
            "receive_window": 30000,
        },
        "account": {
            "fetch_contract": True,
            "contracts_timeout": 0,
            "hashed": False,
        }
    }
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """初始化 Config 物件
        
        Args:
            config_path: 配置檔案路徑，若為 None 則使用預設路徑 'config.yaml'
        
        Raises:
            ConfigError: 當配置檔案不存在或格式錯誤時
        """
        self.config_data: Dict[str, Any] = {}
        self.login_method: Optional[str] = None
        
        if config_path is None:
            config_path = Path("config.yaml")
        else:
            config_path = Path(config_path)
        
        self.config_path = config_path
        self._load_config()
        self._apply_defaults()
        self._determine_login_method()
    
    def _load_config(self) -> None:
        """從 YAML 檔案載入配置
        
        Raises:
            ConfigError: 當檔案不存在或 YAML 格式錯誤時
        """
        if not self.config_path.exists():
            raise ConfigError(f"配置檔案不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"YAML 格式錯誤: {e}")
        except Exception as e:
            raise ConfigError(f"讀取配置檔案失敗: {e}")
    
    def _apply_defaults(self) -> None:
        """套用預設值到配置資料"""
        for section, defaults in self.DEFAULTS.items():
            if section in self.config_data:
                for key, value in defaults.items():
                    if key not in self.config_data[section]:
                        self.config_data[section][key] = value
    
    def _determine_login_method(self) -> None:
        """判斷使用的登入方式"""
        has_api = "api" in self.config_data and self.config_data["api"]
        has_account = "account" in self.config_data and self.config_data["account"]
        
        if has_api and has_account:
            raise ConfigError("不可同時設定 'api' 和 'account' 登入方式，請擇一使用")
        elif has_api:
            self.login_method = "api"
        elif has_account:
            self.login_method = "account"
        else:
            raise ConfigError("必須設定登入方式 ('api' 或 'account')")
    
    def get(self, key: str, default: Any = None) -> Any:
        """取得配置值，支援點號分隔的巢狀鍵值
        
        Args:
            key: 配置鍵，可使用點號分隔巢狀結構，例如 'api.api_key'
            default: 當鍵不存在時的預設值
        
        Returns:
            配置值或預設值
        
        Example:
            >>> config.get("api.api_key")
            "YOUR_API_KEY"
            >>> config.get("api.unknown", "default_value")
            "default_value"
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate(self) -> None:
        """驗證配置的必填欄位
        
        Raises:
            ConfigError: 當必填欄位缺失或值為空時
        """
        if self.login_method == "api":
            required_fields = self.REQUIRED_FIELDS_API
        elif self.login_method == "account":
            required_fields = self.REQUIRED_FIELDS_ACCOUNT
        else:
            raise ConfigError("未設定登入方式")
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            value = self.get(field)
            if value is None:
                missing_fields.append(field)
            elif isinstance(value, str) and not value.strip():
                empty_fields.append(field)
        
        errors = []
        if missing_fields:
            errors.append(f"缺少必填欄位: {', '.join(missing_fields)}")
        if empty_fields:
            errors.append(f"必填欄位不可為空: {', '.join(empty_fields)}")
        
        if errors:
            raise ConfigError("; ".join(errors))
    
    def get_login_params(self) -> Dict[str, Any]:
        """取得登入參數字典
        
        Returns:
            適用於 Shioaji API login() 方法的參數字典
        
        Example:
            >>> params = config.get_login_params()
            >>> api.login(**params)
        """
        self.validate()
        
        if self.login_method == "api":
            return {
                "api_key": self.get("api.api_key"),
                "secret_key": self.get("api.secret_key"),
                "fetch_contract": self.get("api.fetch_contract"),
                "contracts_timeout": self.get("api.contracts_timeout"),
                "subscribe_trade": self.get("api.subscribe_trade"),
                "receive_window": self.get("api.receive_window"),
            }
        else:  # account
            return {
                "person_id": self.get("account.person_id"),
                "passwd": self.get("account.passwd"),
                "hashed": self.get("account.hashed"),
                "fetch_contract": self.get("account.fetch_contract"),
                "contracts_timeout": self.get("account.contracts_timeout"),
            }
    
    def __repr__(self) -> str:
        """字串表示"""
        return f"Config(path='{self.config_path}', method='{self.login_method}')"
