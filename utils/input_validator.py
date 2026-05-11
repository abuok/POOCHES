"""
Input Validation and Sanitization Module
Provides comprehensive validation for all user inputs and API data
"""

import re
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')
    API_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{16,64}$')
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{3,6}/[A-Z]{3,6}$')
    
    # Limits
    MAX_STRING_LENGTH = 1000
    MAX_NUMBER_VALUE = 1e15
    MIN_NUMBER_VALUE = -1e15
    
    @classmethod
    def validate_string(cls, value: Any, field_name: str = "value", 
                       min_length: int = 1, max_length: int = 1000,
                       allow_empty: bool = False) -> Optional[str]:
        """Validate and sanitize string input"""
        try:
            if value is None:
                if allow_empty:
                    return None
                raise ValueError(f"{field_name} cannot be None")
            
            # Convert to string
            value = str(value).strip()
            
            # Check length
            if len(value) < min_length:
                raise ValueError(f"{field_name} must be at least {min_length} characters")
            
            if len(value) > max_length:
                value = value[:max_length]
                logger.warning(f"{field_name} truncated to {max_length} characters")
            
            # Sanitize - remove dangerous characters
            value = cls._sanitize_string(value)
            
            return value
            
        except Exception as e:
            logger.error(f"String validation error for {field_name}: {e}")
            raise
    
    @classmethod
    def _sanitize_string(cls, value: str) -> str:
        """Remove potentially dangerous characters"""
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except common whitespace
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Escape HTML special characters
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        
        return value
    
    @classmethod
    def validate_number(cls, value: Any, field_name: str = "value",
                       min_val: Optional[float] = None, 
                       max_val: Optional[float] = None) -> Optional[float]:
        """Validate and sanitize numeric input"""
        try:
            if value is None:
                return None
            
            # Convert to float
            num = float(value)
            
            # Check absolute limits
            if abs(num) > cls.MAX_NUMBER_VALUE:
                raise ValueError(f"{field_name} exceeds maximum allowed value")
            
            # Check range
            if min_val is not None and num < min_val:
                raise ValueError(f"{field_name} must be at least {min_val}")
            
            if max_val is not None and num > max_val:
                raise ValueError(f"{field_name} must be at most {max_val}")
            
            return num
            
        except ValueError as e:
            if "could not convert" in str(e).lower():
                raise ValueError(f"{field_name} must be a valid number")
            raise
        except Exception as e:
            logger.error(f"Number validation error for {field_name}: {e}")
            raise
    
    @classmethod
    def validate_email(cls, email: Any) -> Optional[str]:
        """Validate email address"""
        try:
            email = cls.validate_string(email, "email", min_length=5, max_length=254)
            
            if email and not cls.EMAIL_PATTERN.match(email):
                raise ValueError("Invalid email format")
            
            return email.lower() if email else None
            
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            raise
    
    @classmethod
    def validate_api_key(cls, api_key: Any) -> Optional[str]:
        """Validate API key format"""
        try:
            api_key = cls.validate_string(api_key, "api_key", min_length=16, max_length=64)
            
            if api_key and not cls.API_KEY_PATTERN.match(api_key):
                raise ValueError("Invalid API key format")
            
            return api_key
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            raise
    
    @classmethod
    def validate_symbol(cls, symbol: Any) -> Optional[str]:
        """Validate trading symbol format"""
        try:
            symbol = cls.validate_string(symbol, "symbol", min_length=6, max_length=12)
            
            if symbol:
                # Normalize to uppercase
                symbol = symbol.upper()
                
                # Add slash if missing
                if '/' not in symbol and len(symbol) == 6:
                    symbol = symbol[:3] + '/' + symbol[3:]
                
                if not cls.SYMBOL_PATTERN.match(symbol):
                    raise ValueError("Invalid symbol format. Expected: XXX/XXX or XXXXXX")
            
            return symbol
            
        except Exception as e:
            logger.error(f"Symbol validation error: {e}")
            raise
    
    @classmethod
    def validate_date(cls, date_str: Any, date_format: str = "%Y-%m-%d") -> Optional[datetime]:
        """Validate and parse date string"""
        try:
            if date_str is None:
                return None
            
            date_str = str(date_str).strip()
            
            # Try to parse date
            try:
                date_obj = datetime.strptime(date_str, date_format)
            except ValueError:
                # Try common alternative formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(f"Invalid date format. Expected: {date_format}")
            
            # Validate date is not in the future
            if date_obj > datetime.now():
                raise ValueError("Date cannot be in the future")
            
            # Validate date is not too old (before 2000)
            if date_obj.year < 2000:
                raise ValueError("Date cannot be before year 2000")
            
            return date_obj
            
        except Exception as e:
            logger.error(f"Date validation error: {e}")
            raise
    
    @classmethod
    def validate_dict(cls, data: Any, required_fields: List[str] = None,
                     allowed_fields: List[str] = None) -> Dict[str, Any]:
        """Validate dictionary structure"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Data must be a dictionary")
            
            # Check required fields
            if required_fields:
                missing = [f for f in required_fields if f not in data]
                if missing:
                    raise ValueError(f"Missing required fields: {', '.join(missing)}")
            
            # Check allowed fields
            if allowed_fields:
                extra = [f for f in data.keys() if f not in allowed_fields]
                if extra:
                    raise ValueError(f"Unexpected fields: {', '.join(extra)}")
            
            return data
            
        except Exception as e:
            logger.error(f"Dictionary validation error: {e}")
            raise
    
    @classmethod
    def validate_price(cls, price: Any) -> Optional[float]:
        """Validate price value"""
        try:
            price = cls.validate_number(price, "price", min_val=0.01, max_val=100000)
            return round(price, 4) if price else None
        except Exception as e:
            logger.error(f"Price validation error: {e}")
            raise
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        try:
            # Remove path components
            filename = filename.replace('..', '')
            filename = filename.replace('/', '')
            filename = filename.replace('\\', '')
            
            # Remove control characters
            filename = ''.join(char for char in filename if ord(char) >= 32)
            
            # Limit length
            if len(filename) > 255:
                name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
                filename = name[:250] + '.' + ext if ext else filename[:255]
            
            return filename
            
        except Exception as e:
            logger.error(f"Filename sanitization error: {e}")
            raise

# Convenience functions for common validations
def validate_trade_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate trade input data"""
    try:
        validator = InputValidator
        
        validated = {
            'symbol': validator.validate_symbol(data.get('symbol')),
            'direction': validator.validate_string(data.get('direction'), 'direction', 
                                                  min_length=4, max_length=5),
            'entry_price': validator.validate_price(data.get('entry_price')),
            'stop_loss': validator.validate_price(data.get('stop_loss')),
            'take_profit': validator.validate_price(data.get('take_profit')),
            'volume': validator.validate_number(data.get('volume'), 'volume', 
                                              min_val=0.01, max_val=1000)
        }
        
        # Validate direction
        if validated['direction'] and validated['direction'].upper() not in ['LONG', 'SHORT']:
            raise ValueError("Direction must be LONG or SHORT")
        
        return validated
        
    except Exception as e:
        logger.error(f"Trade input validation error: {e}")
        raise

def validate_api_response(data: Dict[str, Any]) -> bool:
    """Validate API response data"""
    try:
        if not isinstance(data, dict):
            return False
        
        # Check for required fields
        if 'status' not in data:
            return False
        
        # Validate status
        if data['status'] not in ['success', 'error']:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"API response validation error: {e}")
        return False

# Export main validator
__all__ = ['InputValidator', 'validate_trade_input', 'validate_api_response']
