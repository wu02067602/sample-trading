"""
Config 模組用於管理交易系統的登入設定參數。

此模組提供 Config 類別，用於從 YAML 檔案讀取並驗證登入所需的參數。
"""

import os
from typing import Dict, Any
import yaml


class ConfigError(Exception):
    """Config 相關的異常基礎類別。"""
    pass


class ConfigFileNotFoundError(ConfigError):
    """當配置檔案不存在時拋出的異常。"""
    pass


class ConfigReadError(ConfigError):
    """當配置檔案讀取失敗時拋出的異常。"""
    pass


class ConfigValidationError(ConfigError):
    """當配置參數驗證失敗時拋出的異常。"""
    pass


class Config:
    """
    Config 類別用於管理交易系統登入所需的參數。
    
    此類別負責從 YAML 檔案讀取配置，驗證參數格式，並將配置參數
    儲存為類別屬性以便後續使用。
    
    Attributes:
        person_id (str): 身份證字號
        account (str): 帳號
        password (str): 密碼
        ca_password (str): CA 密碼
    
    Examples:
        >>> config = Config('config.yaml')
        >>> print(config.person_id)
        'A123456789'
        >>> print(config.account)
        '1234567'
    
    Raises:
        ConfigFileNotFoundError: 當指定的 YAML 檔案不存在時
        ConfigReadError: 當讀取 YAML 檔案失敗時
        ConfigValidationError: 當配置參數驗證失敗時
    """
    
    # 定義必要的配置參數
    REQUIRED_FIELDS = ['person_id', 'account', 'password', 'ca_password']
    
    def __init__(self, config_path: str):
        """
        初始化 Config 物件。
        
        從指定的 YAML 檔案路徑讀取配置參數，驗證參數格式，
        並將參數儲存為類別屬性。
        
        Args:
            config_path (str): YAML 配置檔案的路徑
        
        Raises:
            ConfigFileNotFoundError: 當指定的 YAML 檔案不存在時
            ConfigReadError: 當讀取 YAML 檔案失敗時
            ConfigValidationError: 當配置參數驗證失敗時
        
        Examples:
            >>> config = Config('config.yaml')
            >>> config = Config('/path/to/config.yaml')
        """
        self._config_path = config_path
        self._config_data = self._load_config()
        self._validate_config()
        self._set_attributes()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        從 YAML 檔案載入配置資料。
        
        Returns:
            Dict[str, Any]: 從 YAML 檔案解析出的配置資料字典
        
        Raises:
            ConfigFileNotFoundError: 當指定的 YAML 檔案不存在時
            ConfigReadError: 當讀取或解析 YAML 檔案失敗時
        """
        # 檢查檔案是否存在
        if not os.path.exists(self._config_path):
            raise ConfigFileNotFoundError(
                f"配置檔案不存在: {self._config_path}"
            )
        
        # 讀取並解析 YAML 檔案
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                raise ConfigReadError(
                    f"配置檔案為空或格式不正確: {self._config_path}"
                )
            
            return config_data
        
        except yaml.YAMLError as e:
            raise ConfigReadError(
                f"讀取配置檔案失敗: {self._config_path}, 錯誤: {str(e)}"
            )
        except Exception as e:
            raise ConfigReadError(
                f"讀取配置檔案時發生未預期的錯誤: {self._config_path}, 錯誤: {str(e)}"
            )
    
    def _validate_config(self) -> None:
        """
        驗證配置資料是否符合要求的 schema。
        
        檢查所有必要欄位是否存在，以及欄位值是否為有效的字串。
        
        Raises:
            ConfigValidationError: 當配置參數驗證失敗時
        """
        # 檢查配置資料是否為字典
        if not isinstance(self._config_data, dict):
            raise ConfigValidationError(
                "配置資料格式錯誤: 必須是鍵值對格式"
            )
        
        # 檢查所有必要欄位是否存在
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in self._config_data:
                missing_fields.append(field)
        
        if missing_fields:
            raise ConfigValidationError(
                f"配置缺少必要欄位: {', '.join(missing_fields)}"
            )
        
        # 檢查所有必要欄位的值是否為非空字串
        invalid_fields = []
        for field in self.REQUIRED_FIELDS:
            value = self._config_data[field]
            if not isinstance(value, str) or not value.strip():
                invalid_fields.append(field)
        
        if invalid_fields:
            raise ConfigValidationError(
                f"配置欄位值無效（必須為非空字串）: {', '.join(invalid_fields)}"
            )
    
    def _set_attributes(self) -> None:
        """
        將驗證過的配置參數設定為類別屬性。
        
        此方法將配置資料中的所有必要欄位設定為類別的實例屬性，
        使其可以直接透過 self.field_name 的方式存取。
        """
        for field in self.REQUIRED_FIELDS:
            setattr(self, field, self._config_data[field])
    
    def __repr__(self) -> str:
        """
        返回 Config 物件的字串表示。
        
        Returns:
            str: Config 物件的字串表示，包含所有配置參數（密碼會被遮蔽）
        """
        return (
            f"Config(person_id='{self.person_id}', "
            f"account='{self.account}', "
            f"password='***', "
            f"ca_password='***')"
        )
