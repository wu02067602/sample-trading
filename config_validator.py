"""
配置驗證器實作模組

此模組提供登入配置的驗證實作，遵循單一職責原則 (SRP)。
"""

from trading_client_interface import IConfigValidator, LoginConfig


class LoginConfigValidator(IConfigValidator):
    """
    登入配置驗證器
    
    負責驗證登入配置的有效性，遵循單一職責原則 (SRP)。
    將驗證邏輯從主要的客戶端類別中分離出來，提高代碼的可維護性。
    
    Examples:
        >>> config = LoginConfig(
        ...     api_key="YOUR_API_KEY",
        ...     secret_key="YOUR_SECRET_KEY",
        ...     person_id="A123456789"
        ... )
        >>> validator = LoginConfigValidator()
        >>> validator.validate(config)  # 如果有效則不拋出異常
    
    Raises:
        ValueError: 當配置參數不完整或格式錯誤時
    """
    
    def validate(self, config: LoginConfig) -> None:
        """
        驗證登入配置的有效性
        
        檢查配置物件中的必要欄位是否完整且格式正確。
        
        Args:
            config (LoginConfig): 要驗證的登入配置物件
        
        Raises:
            ValueError: 當配置參數不完整或格式錯誤時
        
        Examples:
            >>> config = LoginConfig(
            ...     api_key="YOUR_API_KEY",
            ...     secret_key="YOUR_SECRET_KEY",
            ...     person_id="A123456789"
            ... )
            >>> validator = LoginConfigValidator()
            >>> validator.validate(config)
        """
        self._validate_api_key(config.api_key)
        self._validate_secret_key(config.secret_key)
        self._validate_person_id(config.person_id)
    
    def _validate_api_key(self, api_key: str) -> None:
        """
        驗證 API 金鑰
        
        Args:
            api_key (str): API 金鑰
        
        Raises:
            ValueError: 當 API 金鑰為空或格式錯誤時
        """
        if not api_key or not api_key.strip():
            raise ValueError("API 金鑰不可為空")
    
    def _validate_secret_key(self, secret_key: str) -> None:
        """
        驗證密鑰
        
        Args:
            secret_key (str): 密鑰
        
        Raises:
            ValueError: 當密鑰為空或格式錯誤時
        """
        if not secret_key or not secret_key.strip():
            raise ValueError("密鑰不可為空")
    
    def _validate_person_id(self, person_id: str) -> None:
        """
        驗證身分證字號
        
        Args:
            person_id (str): 身分證字號或統一編號
        
        Raises:
            ValueError: 當身分證字號為空或格式錯誤時
        """
        if not person_id or not person_id.strip():
            raise ValueError("身分證字號不可為空")
