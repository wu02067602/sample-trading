"""
配置管理模組

此模組提供永豐 Shioaji API 的配置管理功能。
"""

from pathlib import Path
from typing import Optional, Union
import yaml


class ConfigError(Exception):
    """配置錯誤異常"""
    pass


class Config:
    """
    永豐 Shioaji API 配置類別
    
    負責讀取和驗證 YAML 配置檔案，確保所有必要參數都已正確設定。
    
    必填欄位：
        api_key (str): API 金鑰
        secret_key (str): API 密鑰
        person_id (str): 身分證字號
    
    選填欄位：
        ca_path (str): 憑證檔案路徑
        ca_passwd (str): 憑證密碼
        simulation (bool): 是否為模擬環境，預設 False
        contracts_timeout (int): 合約下載逾時時間（秒），預設 0
    
    範例：
        >>> config = Config("config.yaml")
        >>> print(config.api_key)
        >>> print(config.simulation)
    """
    
    # 必填欄位
    REQUIRED_FIELDS = ["api_key", "secret_key", "person_id"]
    
    # 選填欄位及其預設值
    OPTIONAL_FIELDS = {
        "ca_path": None,
        "ca_passwd": None,
        "simulation": False,
        "contracts_timeout": 0,
    }
    
    def __init__(self, config_path: Union[str, Path]):
        """
        初始化配置物件
        
        Args:
            config_path: 配置檔案路徑
            
        Raises:
            ConfigError: 當配置檔案不存在或格式錯誤時
            ConfigError: 當必填欄位缺失時
        """
        self.config_path = Path(config_path)
        self._config_data = {}
        
        # 讀取並驗證配置
        self._load_config()
        self._validate_config()
        self._set_attributes()
    
    def _load_config(self) -> None:
        """
        從 YAML 檔案讀取配置
        
        Raises:
            ConfigError: 當檔案不存在或無法解析時
        """
        if not self.config_path.exists():
            raise ConfigError(f"配置檔案不存在: {self.config_path}")
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"無法解析 YAML 檔案: {e}")
        except Exception as e:
            raise ConfigError(f"讀取配置檔案失敗: {e}")
    
    def _validate_config(self) -> None:
        """
        驗證配置檔案中的必填欄位
        
        Raises:
            ConfigError: 當必填欄位缺失或為空時
        """
        missing_fields = []
        empty_fields = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in self._config_data:
                missing_fields.append(field)
            elif not self._config_data[field] or str(self._config_data[field]).strip() == "":
                empty_fields.append(field)
        
        if missing_fields:
            raise ConfigError(f"缺少必填欄位: {', '.join(missing_fields)}")
        
        if empty_fields:
            raise ConfigError(f"必填欄位不可為空: {', '.join(empty_fields)}")
    
    def _set_attributes(self) -> None:
        """設定配置屬性"""
        # 設定必填欄位
        for field in self.REQUIRED_FIELDS:
            setattr(self, field, self._config_data[field])
        
        # 設定選填欄位（使用預設值）
        for field, default_value in self.OPTIONAL_FIELDS.items():
            value = self._config_data.get(field, default_value)
            setattr(self, field, value)
    
    def __repr__(self) -> str:
        """返回配置物件的字串表示"""
        return (
            f"Config(api_key='{self.api_key[:8]}...', "
            f"person_id='{self.person_id}', "
            f"simulation={self.simulation})"
        )
    
    def to_dict(self) -> dict:
        """
        將配置轉換為字典格式
        
        Returns:
            包含所有配置參數的字典
        """
        return {
            "api_key": self.api_key,
            "secret_key": self.secret_key,
            "person_id": self.person_id,
            "ca_path": self.ca_path,
            "ca_passwd": self.ca_passwd,
            "simulation": self.simulation,
            "contracts_timeout": self.contracts_timeout,
        }
