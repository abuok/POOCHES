#!/usr/bin/env python3
"""
SECURE CONFIGURATION MANAGEMENT
Environment-based configuration for API keys and sensitive data
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Secure configuration manager for API keys and settings"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path.home() / '.trading_system' / 'config.env'
        self._ensure_config_dir()
        self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set appropriate permissions (user read/write only)
        try:
            os.chmod(self.config_path.parent, 0o700)
            if self.config_path.exists():
                os.chmod(self.config_path, 0o600)
        except OSError as e:
            logger.warning(f"Could not set file permissions: {e}")
    
    def _load_config(self) -> None:
        """Load configuration from environment variables and config file"""
        self.config = {}
        
        # Load from environment variables first (most secure)
        env_mapping = {
            'TWELVE_DATA_API_KEY': 'twelve_data_api_key',
            'OPENAI_API_KEY': 'openai_api_key',
            'ALPHA_VANTAGE_KEY': 'alpha_vantage_key',
            'NEWS_API_KEY': 'news_api_key',
            'FRED_API_KEY': 'fred_api_key'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                self.config[config_key] = value
                logger.info(f"Loaded {config_key} from environment variables")
        
        # Load from config file as fallback
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Only load if not already set from environment
                            if key not in self.config:
                                self.config[key] = value
                                logger.info(f"Loaded {key} from config file")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Set defaults for missing keys
        self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default values for missing configuration"""
        defaults = {
            'twelve_data_api_key': '',
            'openai_api_key': '',
            'alpha_vantage_key': '',
            'news_api_key': '',
            'fred_api_key': '',
            'log_level': 'INFO',
            'data_retention_days': '30',
            'max_requests_per_hour': '1000'
        }
        
        for key, default_value in defaults.items():
            if key not in self.config:
                self.config[key] = default_value
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value"""
        return self.config.get(key, default or '')
    
    def set(self, key: str, value: str) -> None:
        """Set configuration value"""
        self.config[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                for key, value in self.config.items():
                    # Don't save empty API keys to file for security
                    if 'api_key' not in key or value:
                        f.write(f"{key}={value}\n")
            
            # Set secure permissions
            os.chmod(self.config_path, 0o600)
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def validate_required_keys(self) -> Dict[str, bool]:
        """Validate required API keys are present"""
        required_keys = [
            'twelve_data_api_key',
            'openai_api_key',
            'alpha_vantage_key',
            'news_api_key',
            'fred_api_key'
        ]
        
        validation_results = {}
        for key in required_keys:
            validation_results[key] = bool(self.get(key))
        
        return validation_results
    
    def get_api_status(self) -> Dict[str, str]:
        """Get API key status for display"""
        status = {}
        key_names = {
            'twelve_data_api_key': 'Twelve Data',
            'openai_api_key': 'OpenAI',
            'alpha_vantage_key': 'Alpha Vantage',
            'news_api_key': 'News API',
            'fred_api_key': 'FRED'
        }
        
        for key, name in key_names.items():
            value = self.get(key)
            if value:
                status[key] = f"✅ {name} configured"
            else:
                status[key] = f"❌ {name} missing"
        
        return status
    
    def create_env_template(self) -> str:
        """Create environment variable template"""
        template = """# Trading System Environment Variables
# Copy this to .env file in your project root

# Twelve Data API Key (for live price data)
TWELVE_DATA_API_KEY=your_twelve_data_api_key_here

# OpenAI API Key (for AI coach functionality)
OPENAI_API_KEY=sk-your-openai-key-here

# Alpha Vantage API Key (for stock market data)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# News API Key (for financial news)
NEWS_API_KEY=your_news_api_key_here

# FRED API Key (for economic indicators)
FRED_API_KEY=your_fred_api_key_here

# Optional Settings
LOG_LEVEL=INFO
DATA_RETENTION_DAYS=30
MAX_REQUESTS_PER_HOUR=1000
"""
        return template

# Global configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_api_key(service_name: str) -> str:
    """Get API key by service name"""
    key_mapping = {
        'twelve_data': 'twelve_data_api_key',
        'openai': 'openai_api_key',
        'alpha_vantage': 'alpha_vantage_key',
        'news': 'news_api_key',
        'fred': 'fred_api_key'
    }
    
    config_key = key_mapping.get(service_name.lower())
    if config_key:
        return config_manager.get(config_key)
    
    raise ValueError(f"Unknown service: {service_name}")

def is_api_configured(service_name: str) -> bool:
    """Check if API key is configured for service"""
    try:
        return bool(get_api_key(service_name))
    except ValueError:
        return False

if __name__ == "__main__":
    # Example usage
    print("Configuration Manager Test")
    print("=" * 50)
    
    # Show API status
    status = config_manager.get_api_status()
    for key, value in status.items():
        print(f"{value}")
    
    print("\nEnvironment Template:")
    print(config_manager.create_env_template())
