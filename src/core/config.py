"""Configuration management"""
import os
import configparser
from typing import Any, Optional
from pathlib import Path


class Config:
    """Configuration manager with validation"""
    
    DEFAULT_CONFIG = {
        'ADVANCED': {
            'port': '0',
            'adbrestart': 'True',
            'emulatorpath': '',
            'loadingMuliplier': '1.0',
            'debug': 'False'
        },
        'DISCORD': {
            'enable': 'False',
            'channel_id': '',
            'token': ''
        },
        'TELEGRAM': {
            'enable': 'False',
            'bot_token': '',
            'chat_id': ''
        }
    }
    
    def __init__(self, config_path: str = 'settings.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._load_or_create()
        
    def _load_or_create(self):
        """Load config or create with defaults"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            self._create_default_config()
            
    def _create_default_config(self):
        """Create default configuration file"""
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save()
        
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """Get configuration value"""
        return self.config.get(section, option, fallback=fallback)
        
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        return self.config.getint(section, option, fallback=fallback)
        
    def getfloat(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        return self.config.getfloat(section, option, fallback=fallback)
        
    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        return self.config.getboolean(section, option, fallback=fallback)
        
    def set(self, section: str, option: str, value: Any):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        
    def has_section(self, section: str) -> bool:
        """Check if section exists"""
        return self.config.has_section(section)
        
    def has_option(self, section: str, option: str) -> bool:
        """Check if option exists"""
        return self.config.has_option(section, option)
        
    def save(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            self.config.write(f)
            
    def reload(self):
        """Reload configuration from file"""
        self.config.read(self.config_path)
