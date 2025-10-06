"""Config class for managing trading system login parameters.

This module provides a Config class that reads and validates configuration
parameters from a YAML file.
"""

import os
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


class LoginConfig(BaseModel):
    """Login configuration schema.
    
    Attributes:
        api_key: API key for authentication
        secret_key: Secret key for authentication
        person_id: Person ID for the trading account
        ca_password: Certificate password for secure connection
    """
    
    api_key: str = Field(..., min_length=1, description="API key for authentication")
    secret_key: str = Field(..., min_length=1, description="Secret key for authentication")
    person_id: str = Field(..., min_length=1, description="Person ID for the trading account")
    ca_password: str = Field(..., min_length=1, description="Certificate password")


class Config:
    """Configuration manager for trading system login parameters.
    
    This class reads configuration from a YAML file, validates the content
    against a predefined schema, and provides access to configuration parameters
    as class attributes.
    
    Attributes:
        api_key: API key for authentication
        secret_key: Secret key for authentication
        person_id: Person ID for the trading account
        ca_password: Certificate password for secure connection
    
    Raises:
        FileNotFoundError: When the specified YAML file does not exist
        ValueError: When the YAML file format is invalid or validation fails
        yaml.YAMLError: When the YAML file cannot be parsed
    
    Examples:
        >>> config = Config("config.yaml")
        >>> print(config.api_key)
        'your_api_key'
        >>> print(config.person_id)
        'A123456789'
    """
    
    def __init__(self, config_path: str) -> None:
        """Initialize Config with path to YAML configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Raises:
            FileNotFoundError: When the specified YAML file does not exist
            ValueError: When the YAML file format is invalid or validation fails
            yaml.YAMLError: When the YAML file cannot be parsed
            
        Examples:
            >>> config = Config("config.yaml")
            >>> config = Config("/path/to/config.yaml")
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to read configuration file: {e}") from e
        
        if config_data is None:
            raise ValueError("Configuration file is empty")
        
        if not isinstance(config_data, dict):
            raise ValueError("Configuration file must contain a dictionary")
        
        try:
            validated_config = LoginConfig(**config_data)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}") from e
        
        # Store validated config as class attributes
        self.api_key = validated_config.api_key
        self.secret_key = validated_config.secret_key
        self.person_id = validated_config.person_id
        self.ca_password = validated_config.ca_password
    
    def __repr__(self) -> str:
        """Return string representation of Config object.
        
        Returns:
            String representation with masked sensitive information
            
        Examples:
            >>> config = Config("config.yaml")
            >>> print(repr(config))
            Config(api_key='***', person_id='A123456789')
        """
        return (
            f"Config("
            f"api_key='***', "
            f"secret_key='***', "
            f"person_id='{self.person_id}', "
            f"ca_password='***'"
            f")"
        )
