# Trading System API Documentation

## Table of Contents

1. [Data Access Layer](#data-access-layer)
2. [Configuration Management](#configuration-management)
3. [Cache Management](#cache-management)
4. [Repository Pattern](#repository-pattern)
5. [Constants and Configuration](#constants-and-configuration)
6. [State Management](#state-management)
7. [Error Handling](#error-handling)
8. [Testing Framework](#testing-framework)

---

## Data Access Layer

### Overview

The data access layer provides a unified interface for loading and validating market data across different sources and formats.

### Classes

#### `DataAccessManager`

Central manager for coordinating data access across Gold and market data sources.

**Methods:**

- `load_gold_data(timeframe: str) -> Optional[pd.DataFrame]`
- `load_market_data(data_type: str) -> Optional[pd.DataFrame]`
- `get_data_summary() -> Dict[str, Any]`
- `clear_cache() -> None`

**Example:**

```python
from data.access_layer import create_data_manager

# Create data manager
data_manager = create_data_manager()

# Load Gold H1 data
gold_data = data_manager.load_gold_data('H1')
if gold_data is not None:
    print(f"Loaded {len(gold_data)} rows")
```

#### `GoldDataAccess`
Specialized access layer for Gold market data with comprehensive validation.

**Features:**
- Automatic column standardization
- Data quality validation
- OHLC relationship checks
- Price range validation

#### `MarketDataAccess`
Access layer for market data (DXY, yields, economic indicators).

**Supported Data Types:**
- DXY (Dollar Index)
- US10Y (10-Year Treasury Yield)
- Custom market indicators

---

## Configuration Management

### Overview
Secure configuration management using environment variables and encrypted local storage.

### Classes

#### `ConfigManager`
Manages API keys, file paths, and system settings with security best practices.

**Methods:**
- `get(key: str, default: Optional[str] = None) -> str`
- `set(key: str, value: str) -> None`
- `validate_required_keys() -> Dict[str, bool]`
- `get_api_status() -> Dict[str, str]`

**Security Features:**
- Environment variable priority
- Encrypted local storage
- File permission controls (600)
- No hardcoded credentials

**Example:**
```python
from config.settings import config_manager, get_api_key

# Get API key securely
api_key = get_api_key('twelve_data')
if api_key:
    print("API key configured")
else:
    print("API key missing")
```

---

## Cache Management

### Overview
High-performance caching system with memory and file-based storage, LRU eviction, and TTL support.

### Classes

#### `CacheManager`
Unified caching with automatic fallback and performance monitoring.

**Features:**
- Memory cache with LRU eviction
- File-based persistence
- Configurable TTL per entry
- Performance statistics
- Thread-safe operations

**Methods:**
- `get(key: str, use_file_cache: bool = True) -> Optional[Any]`
- `set(key: str, value: Any, ttl_seconds: int = 3600, persist_to_file: bool = True) -> None`
- `delete(key: str) -> bool`
- `clear() -> None`
- `get_hit_rate() -> float`
- `cleanup_expired() -> int`

**Decorator:**
```python
from utils.cache_manager import cache_result

@cache_result(ttl_seconds=1800, persist_to_file=True)
def expensive_calculation(data):
    # Expensive operation
    return result
```

---

## Repository Pattern

### Overview
Repository pattern implementation for clean data access abstraction and testability.

### Classes

#### `GoldDataRepository`
Repository for Gold market data with time-based queries and validation.

**Methods:**
- `get_data_by_timerange(start: datetime, end: datetime, timeframe: str = 'H1') -> Optional[pd.DataFrame]`
- `get_latest_data(count: int = None, timeframe: str = 'H1') -> Optional[pd.DataFrame]`
- `get_data_by_date(date: datetime, timeframe: str = 'H1') -> Optional[pd.DataFrame]`
- `get_data_summary(timeframe: str = 'H1') -> Dict[str, Any]`
- `validate_data_quality(timeframe: str = 'H1') -> Dict[str, Any]`

#### `MarketDataRepository`
Repository for market data with correlation analysis capabilities.

**Methods:**
- `get_data_by_timerange(start: datetime, end: datetime, data_type: str = 'DXY') -> Optional[pd.DataFrame]`
- `get_correlation_data(gold_timeframe: str = 'H1', market_data_type: str = 'DXY', period_days: int = 30) -> Optional[pd.DataFrame]`

#### `RepositoryFactory`
Factory for creating repository instances with dependency injection.

**Example:**
```python
from repositories.data_repository import get_gold_repository, get_market_repository

# Get repositories
gold_repo = get_gold_repository()
market_repo = get_market_repository()

# Use repositories
data = gold_repo.get_latest_data(count=100)
correlation = market_repo.get_correlation_data()
```

---

## Constants and Configuration

### Overview
Centralized constants for trading parameters, eliminating magic numbers throughout the codebase.

### Classes

#### `TradingParameters`
All trading system parameters with validation functions.

**Categories:**
- Timeframe configurations
- RSI parameters
- EMA parameters
- Volume parameters
- Session parameters
- Risk management parameters
- Backtesting parameters
- Performance parameters

**Example:**
```python
from constants.trading_constants import TRADING_PARAMS

# Use constants instead of magic numbers
rsi_period = TRADING_PARAMS.RSI_PERIOD  # 14
atr_multiplier = TRADING_PARAMS.ATR_STOP_LOSS_MULTIPLIER  # 2.0
```

#### `StrategyConfig`
Strategy definitions and configurations.

**Available Strategies:**
- `scanner_8_condition`: 8-Condition Technical Strategy
- `bos_reversal`: BOS Reversal Strategy
- `session_volatility`: Session Volatility Breakout
- `liquidity_sweep`: Liquidity Sweep Strategy

---

## State Management

### Overview
Centralized state management for JavaScript components with persistence and history tracking.

### Classes

#### `StateManager`
JavaScript state manager with subscription pattern and validation.

**Features:**
- Immutable state updates
- Subscription-based notifications
- State history tracking
- Persistence to localStorage
- Schema validation
- Performance monitoring

**Methods:**
- `getState(path: str = null) -> Any`
- `setState(updates: Object, options: Object = {}) -> Object`
- `subscribe(listener: Function, options: Object = {}) -> Function`
- `validateState(schema: Object) -> Array`
- `getHistory(count: Number = null) -> Array`

**Example:**
```javascript
import { TradingStateActions, TradingStateSelectors } from './utils/state_manager.js';

// Update state
TradingStateActions.setStrategy('bos_reversal');
TradingStateActions.updatePrice(1925.50, 5.2, 'up');

// Subscribe to changes
const unsubscribe = tradingStateManager.subscribe(
  (newState, prevState, currentState) => {
    console.log('State changed:', newState);
  },
  { path: 'scanner.currentStrategy' }
);

// Get state
const currentStrategy = TradingStateSelectors.getCurrentStrategy();
```

---

## Error Handling

### Overview
Comprehensive error handling strategy with specific exception types and logging.

### Custom Exceptions

#### `DataValidationError`
Raised when data validation fails.

**Attributes:**
- Message describing validation failure
- Context information
- Suggested fixes

#### `DataConnectionError`
Raised when data source connection fails.

**Features:**
- Automatic retry logic
- Fallback data sources
- Graceful degradation

### Error Handling Patterns

#### Python
```python
try:
    data = repository.get_data_by_timerange(start, end)
    if data is None:
        raise DataValidationError("No data available for specified range")
except DataValidationError as e:
    logger.error(f"Data validation failed: {e}")
    # Handle validation error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected error
```

#### JavaScript
```javascript
try {
  const data = await fetchData();
  if (!data || data.length === 0) {
    throw new Error('No data available');
  }
} catch (error) {
  console.error('Data fetch failed:', error);
  // Show user-friendly error message
  showErrorMessage('Unable to load market data. Please try again later.');
}
```

---

## Testing Framework

### Overview
Comprehensive testing suite with unit tests, integration tests, and performance tests.

### Test Categories

#### Unit Tests
- Repository pattern tests
- Cache manager tests
- Configuration tests
- Constants validation tests

#### Integration Tests
- End-to-end data flow tests
- Component interaction tests
- API integration tests

#### Performance Tests
- Large dataset handling
- Memory usage validation
- Response time benchmarks

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_data_repository.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── test_data_repository.py
├── test_cache_manager.py
├── test_configuration.py
├── test_constants.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_api_integration.py
└── performance/
    ├── test_large_datasets.py
    └── test_memory_usage.py
```

---

## Security Best Practices

### API Key Management
- Use environment variables in production
- Never commit API keys to version control
- Implement key rotation strategy
- Use HTTPS for all API calls

### Data Validation
- Validate all input parameters
- Sanitize user inputs
- Implement rate limiting
- Use parameterized queries

### Error Information
- Never expose sensitive data in error messages
- Log errors without user information
- Provide generic error messages to users
- Implement proper error codes

---

## Performance Optimization

### Caching Strategy
- Cache frequently accessed data
- Use appropriate TTL values
- Implement cache warming
- Monitor cache hit rates

### Memory Management
- Use generators for large datasets
- Implement data pagination
- Clean up resources properly
- Monitor memory usage

### Async Operations
- Use async/await for I/O operations
- Implement parallel processing
- Use web workers for heavy computations
- Implement loading states

---

## Deployment Guidelines

### Environment Setup
1. Set up environment variables
2. Configure data directories
3. Set up logging configuration
4. Validate API keys
5. Run health checks

### Monitoring
- Implement health check endpoints
- Monitor performance metrics
- Set up alerting for errors
- Log usage statistics

### Backup Strategy
- Regular data backups
- Configuration backups
- Disaster recovery plan
- Data retention policies

---

## Contributing Guidelines

### Code Standards
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Add type hints everywhere
- Write comprehensive docstrings

### Testing Requirements
- Write tests for all new features
- Maintain >80% code coverage
- Include performance tests
- Add integration tests

### Documentation
- Update API documentation
- Add code comments
- Create usage examples
- Document breaking changes

---

## Troubleshooting

### Common Issues

#### Data Loading Problems
- Check file permissions
- Validate data formats
- Verify file paths
- Check available disk space

#### Cache Issues
- Clear cache if stale
- Check TTL settings
- Monitor memory usage
- Verify cache permissions

#### Performance Issues
- Monitor memory usage
- Check for memory leaks
- Profile slow operations
- Optimize database queries

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks
Run system health check:
```python
from utils.health_checker import run_health_check

results = run_health_check()
print(f"System health: {results['overall_status']}")
```

---

## Version History

### v2.0.0 (Current)
- Complete architectural refactoring
- Added repository pattern
- Implemented caching layer
- Added comprehensive testing
- Enhanced security measures

### v1.0.0 (Legacy)
- Initial monolithic implementation
- Basic data access
- No error handling
- No testing framework

---

## Support

For issues, questions, or contributions:
- Create GitHub issue
- Check documentation first
- Provide error logs
- Include system information
