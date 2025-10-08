"""環境配置模組

此模組負責讀取與管理環境變數配置。
"""

from typing import Optional
from pathlib import Path


class ConfigurationError(Exception):
    """配置錯誤的自訂例外"""
    pass


class Config:
    """環境配置管理
    
    此類別封裝了環境變數的讀取與驗證功能，
    從 .env 檔案載入 API 金鑰、密鑰、憑證路徑等配置。
    """
    
    def __init__(self, env_file: str = ".env") -> None:
        """初始化配置管理器
        
        Args:
            env_file (str): 環境變數檔案路徑，預設為 ".env"
        
        Raises:
            ConfigurationError: 當環境變數檔案不存在時
        """
        self._env_file = env_file
        self._config: dict[str, Optional[str]] = {}
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        """載入環境變數檔案（內部方法）
        
        Raises:
            ConfigurationError: 當環境變數檔案不存在或無法讀取時
        """
        env_path = Path(self._env_file)
        
        if not env_path.exists():
            raise ConfigurationError(f"環境變數檔案不存在: {self._env_file}")
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳過空行和註釋
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引號
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self._config[key] = value
        
        except IOError as e:
            raise ConfigurationError(f"無法讀取環境變數檔案: {e}")
        except UnicodeDecodeError as e:
            raise ConfigurationError(f"環境變數檔案編碼錯誤: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """取得指定的環境變數值
        
        Args:
            key (str): 環境變數鍵名
            default (Optional[str]): 預設值，如果找不到則返回此值
        
        Returns:
            Optional[str]: 環境變數值，如果不存在則返回預設值
        
        Examples:
            >>> config = Config()
            >>> api_key = config.get('API_KEY')
            >>> print(f"API Key: {api_key}")
        
        Raises:
            ValueError: 當 key 為空字串時
        """
        if not key:
            raise ValueError("環境變數鍵名不可為空")
        
        return self._config.get(key, default)
    
    def get_required(self, key: str) -> str:
        """取得必要的環境變數值
        
        Args:
            key (str): 環境變數鍵名
        
        Returns:
            str: 環境變數值
        
        Examples:
            >>> config = Config()
            >>> api_key = config.get_required('API_KEY')
        
        Raises:
            ValueError: 當 key 為空字串時
            ConfigurationError: 當必要的環境變數不存在或為空時
        """
        if not key:
            raise ValueError("環境變數鍵名不可為空")
        
        value = self._config.get(key)
        
        if value is None or value == '':
            raise ConfigurationError(f"必要的環境變數未設定: {key}")
        
        return value
    
    @property
    def person_id(self) -> str:
        """取得 Person ID
        
        Returns:
            str: Person ID
        
        Examples:
            >>> config = Config()
            >>> person_id = config.person_id
        
        Raises:
            ConfigurationError: 當 PERSON_ID 未設定時
        """
        return self.get_required('PERSON_ID')
    
    @property
    def api_key(self) -> str:
        """取得 API Key
        
        Returns:
            str: API Key
        
        Examples:
            >>> config = Config()
            >>> api_key = config.api_key
        
        Raises:
            ConfigurationError: 當 API_KEY 未設定時
        """
        return self.get_required('API_KEY')
    
    @property
    def api_secret(self) -> str:
        """取得 API Secret
        
        Returns:
            str: API Secret
        
        Examples:
            >>> config = Config()
            >>> api_secret = config.api_secret
        
        Raises:
            ConfigurationError: 當 API_SECRET 未設定時
        """
        return self.get_required('API_SECRET')
    
    @property
    def ca_path(self) -> str:
        """取得 CA 憑證路徑
        
        Returns:
            str: CA 憑證路徑
        
        Examples:
            >>> config = Config()
            >>> ca_path = config.ca_path
        
        Raises:
            ConfigurationError: 當 CA_PATH 未設定時
        """
        return self.get_required('CA_PATH')
    
    @property
    def simulation(self) -> bool:
        """取得模擬環境
        
        Returns:
            bool: 模擬環境
        """
        return self.get_required('SIMULATION')
    
    def validate(self) -> bool:
        """驗證所有必要的環境變數是否已設定
        
        Returns:
            bool: 如果所有必要環境變數都已設定則返回 True
        
        Examples:
            >>> config = Config()
            >>> if config.validate():
            ...     print("配置驗證通過")
        
        Raises:
            ConfigurationError: 當任何必要的環境變數未設定時
        """
        required_keys = ['PERSON_ID', 'API_KEY', 'API_SECRET', 'CA_PATH']
        
        for key in required_keys:
            self.get_required(key)
        
        return True
    
    def get_all(self) -> dict[str, Optional[str]]:
        """取得所有環境變數
        
        Returns:
            dict[str, Optional[str]]: 所有環境變數的字典
        
        Examples:
            >>> config = Config()
            >>> all_config = config.get_all()
            >>> print(f"總共載入 {len(all_config)} 個環境變數")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._config.copy()
    
    def __repr__(self) -> str:
        """字串表示
        
        Returns:
            str: Config 物件的字串表示（隱藏敏感資訊）
        """
        keys = list(self._config.keys())
        return f"Config(loaded_keys={keys})"
