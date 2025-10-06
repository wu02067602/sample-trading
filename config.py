"""Config 类用于管理永丰 API 登录所需的参数。

此模块提供配置管理功能，从 YAML 文件读取并验证登录参数。
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """配置相关的错误。"""
    pass


class Config:
    """管理永丰 API 登录配置的类。
    
    此类从 YAML 文件读取配置，验证配置格式，并将配置存储为类属性。
    
    Attributes:
        person_id (str): 身份证字号
        api_key (str): API Key
        api_secret (str): API Secret
        ca_path (Optional[str]): 凭证路径（可选）
    
    Examples:
        >>> config = Config('config.yaml')
        >>> print(config.person_id)
        'A123456789'
        >>> print(config.api_key)
        'your_api_key'
    
    Raises:
        ConfigError: 当配置文件不存在、读取失败或验证失败时抛出
        FileNotFoundError: 当配置文件不存在时抛出
        yaml.YAMLError: 当 YAML 文件格式错误时抛出
    """
    
    # 必需的配置字段
    REQUIRED_FIELDS = ['person_id', 'api_key', 'api_secret']
    # 可选的配置字段
    OPTIONAL_FIELDS = ['ca_path']
    
    def __init__(self, config_path: str) -> None:
        """初始化 Config 类。
        
        Args:
            config_path (str): 配置文件的路径
            
        Raises:
            FileNotFoundError: 当配置文件不存在时
            ConfigError: 当配置验证失败或读取失败时
            yaml.YAMLError: 当 YAML 文件格式错误时
        
        Examples:
            >>> config = Config('config.yaml')
            >>> config = Config('/path/to/config.yaml')
        """
        self.config_path = Path(config_path)
        self._validate_file_exists()
        config_data = self._load_yaml()
        self._validate_schema(config_data)
        self._set_attributes(config_data)
    
    def _validate_file_exists(self) -> None:
        """验证配置文件是否存在。
        
        Raises:
            FileNotFoundError: 当配置文件不存在时
        
        Examples:
            >>> config = Config('nonexistent.yaml')  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            FileNotFoundError: 配置文件不存在: nonexistent.yaml
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
    
    def _load_yaml(self) -> Dict[str, Any]:
        """从文件加载 YAML 配置。
        
        Returns:
            Dict[str, Any]: 配置数据字典
            
        Raises:
            ConfigError: 当读取配置文件失败时
            yaml.YAMLError: 当 YAML 文件格式错误时
        
        Examples:
            >>> config = Config('config.yaml')  # doctest: +SKIP
            >>> data = config._load_yaml()
            >>> isinstance(data, dict)
            True
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    raise ConfigError(f"配置文件为空: {self.config_path}")
                return data
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 文件格式错误: {e}")
        except Exception as e:
            raise ConfigError(f"读取配置文件失败: {e}")
    
    def _validate_schema(self, config_data: Dict[str, Any]) -> None:
        """验证配置数据的格式是否符合 schema。
        
        Args:
            config_data (Dict[str, Any]): 配置数据字典
            
        Raises:
            ConfigError: 当配置验证失败时
        
        Examples:
            >>> config = Config('config.yaml')  # doctest: +SKIP
            >>> config._validate_schema({'person_id': 'A123456789'})
            Traceback (most recent call last):
                ...
            ConfigError: 缺少必需的配置字段: api_key, api_secret
        """
        if not isinstance(config_data, dict):
            raise ConfigError("配置数据必须是字典格式")
        
        # 检查必需字段
        missing_fields = [
            field for field in self.REQUIRED_FIELDS 
            if field not in config_data
        ]
        if missing_fields:
            raise ConfigError(
                f"缺少必需的配置字段: {', '.join(missing_fields)}"
            )
        
        # 检查必需字段不能为空
        empty_fields = [
            field for field in self.REQUIRED_FIELDS 
            if not config_data.get(field)
        ]
        if empty_fields:
            raise ConfigError(
                f"配置字段不能为空: {', '.join(empty_fields)}"
            )
        
        # 验证字段类型
        for field in self.REQUIRED_FIELDS:
            if not isinstance(config_data[field], str):
                raise ConfigError(
                    f"配置字段 {field} 必须是字符串类型"
                )
        
        # 验证可选字段类型
        for field in self.OPTIONAL_FIELDS:
            if field in config_data and config_data[field] is not None:
                if not isinstance(config_data[field], str):
                    raise ConfigError(
                        f"配置字段 {field} 必须是字符串类型"
                    )
    
    def _set_attributes(self, config_data: Dict[str, Any]) -> None:
        """将配置数据设置为类的属性。
        
        Args:
            config_data (Dict[str, Any]): 配置数据字典
        
        Examples:
            >>> config = Config('config.yaml')  # doctest: +SKIP
            >>> hasattr(config, 'person_id')
            True
            >>> hasattr(config, 'api_key')
            True
        """
        # 设置必需字段
        for field in self.REQUIRED_FIELDS:
            setattr(self, field, config_data[field])
        
        # 设置可选字段
        for field in self.OPTIONAL_FIELDS:
            setattr(self, field, config_data.get(field))
    
    def __repr__(self) -> str:
        """返回 Config 对象的字符串表示。
        
        Returns:
            str: Config 对象的字符串表示
        
        Examples:
            >>> config = Config('config.yaml')  # doctest: +SKIP
            >>> repr(config)
            "Config(person_id='A***6789', api_key='***', api_secret='***')"
        """
        # 隐藏敏感信息
        person_id_masked = (
            f"{self.person_id[0]}***{self.person_id[-4:]}" 
            if len(self.person_id) > 5 else "***"
        )
        return (
            f"Config(person_id='{person_id_masked}', "
            f"api_key='***', api_secret='***')"
        )
