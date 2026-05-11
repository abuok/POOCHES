#!/usr/bin/env python3
"""
DATA REPOSITORY PATTERN
Abstract data access with repository pattern implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import logging

from ..data.access_layer import DataAccessManager, GoldDataAccess, MarketDataAccess
from ..utils.cache_manager import cache_result, cache_manager
from ..constants.trading_constants import DATA_CONFIG, TRADING_PARAMS

logger = logging.getLogger(__name__)

class IRepository(ABC):
    """Abstract repository interface"""
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[Any]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def find_all(self, **filters) -> List[Any]:
        """Find all entities with optional filters"""
        pass
    
    @abstractmethod
    def save(self, entity: Any) -> bool:
        """Save entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass

class ITimeSeriesRepository(ABC):
    """Abstract time series repository interface"""
    
    @abstractmethod
    def get_data_by_timerange(self, start: datetime, end: datetime, 
                           timeframe: str = None) -> Optional[pd.DataFrame]:
        """Get data by time range"""
        pass
    
    @abstractmethod
    def get_latest_data(self, count: int = None, 
                       timeframe: str = None) -> Optional[pd.DataFrame]:
        """Get latest data points"""
        pass
    
    @abstractmethod
    def get_data_by_date(self, date: datetime, 
                        timeframe: str = None) -> Optional[pd.DataFrame]:
        """Get data by specific date"""
        pass

class GoldDataRepository(ITimeSeriesRepository):
    """Repository for Gold market data"""
    
    def __init__(self, data_manager: DataAccessManager = None):
        self.data_manager = data_manager or DataAccessManager()
        self._cache_prefix = "gold_data"
    
    @cache_result(ttl_seconds=TRADING_PARAMS.CACHE_EXPIRY_MINUTES * 60)
    def get_data_by_timerange(self, start: datetime, end: datetime, 
                           timeframe: str = 'H1') -> Optional[pd.DataFrame]:
        """Get Gold data by time range with caching"""
        try:
            df = self.data_manager.load_gold_data(timeframe)
            if df is None or df.empty:
                logger.warning(f"No data available for timeframe: {timeframe}")
                return None
            
            # Filter by date range
            filtered_df = df[(df.index >= start) & (df.index <= end)]
            
            if filtered_df.empty:
                logger.warning(f"No data in range {start} to {end} for {timeframe}")
                return None
            
            logger.info(f"Retrieved {len(filtered_df)} Gold data points for {timeframe}")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error getting Gold data by timerange: {e}")
            return None
    
    @cache_result(ttl_seconds=300)  # 5 minutes cache for latest data
    def get_latest_data(self, count: int = None, 
                       timeframe: str = 'H1') -> Optional[pd.DataFrame]:
        """Get latest Gold data points"""
        try:
            df = self.data_manager.load_gold_data(timeframe)
            if df is None or df.empty:
                return None
            
            if count:
                return df.tail(count)
            return df
            
        except Exception as e:
            logger.error(f"Error getting latest Gold data: {e}")
            return None
    
    @cache_result(ttl_seconds=TRADING_PARAMS.CACHE_EXPIRY_MINUTES * 60)
    def get_data_by_date(self, date: datetime, 
                        timeframe: str = 'H1') -> Optional[pd.DataFrame]:
        """Get Gold data by specific date"""
        try:
            df = self.data_manager.load_gold_data(timeframe)
            if df is None or df.empty:
                return None
            
            # Filter by date
            date_only = date.date()
            filtered_df = df[df.index.date == date_only]
            
            if filtered_df.empty:
                logger.warning(f"No data for date {date_only}")
                return None
            
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error getting Gold data by date: {e}")
            return None
    
    def get_available_timeframes(self) -> List[str]:
        """Get available timeframes"""
        return list(DATA_CONFIG.FILE_MAPPING.keys())
    
    def get_data_summary(self, timeframe: str = 'H1') -> Dict[str, Any]:
        """Get data summary for timeframe"""
        try:
            df = self.data_manager.load_gold_data(timeframe)
            if df is None or df.empty:
                return {}
            
            summary = {
                'timeframe': timeframe,
                'total_records': len(df),
                'date_range': {
                    'start': df.index[0],
                    'end': df.index[-1]
                },
                'price_range': {
                    'min': df['close'].min(),
                    'max': df['close'].max(),
                    'mean': df['close'].mean()
                },
                'volume_stats': {
                    'mean': df['tick_volume'].mean() if 'tick_volume' in df else 0,
                    'max': df['tick_volume'].max() if 'tick_volume' in df else 0
                },
                'data_quality': {
                    'missing_values': df.isnull().sum().sum(),
                    'duplicate_timestamps': df.index.duplicated().sum()
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
    
    def validate_data_quality(self, timeframe: str = 'H1') -> Dict[str, Any]:
        """Validate data quality for timeframe"""
        try:
            df = self.data_manager.load_gold_data(timeframe)
            if df is None or df.empty:
                return {'valid': False, 'error': 'No data available'}
            
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'stats': {}
            }
            
            # Check for missing data
            missing_data = df.isnull().sum()
            if missing_data.any():
                validation_results['errors'].append(f"Missing data: {missing_data[missing_data > 0].to_dict()}")
                validation_results['valid'] = False
            
            # Check for duplicate timestamps
            duplicates = df.index.duplicated().sum()
            if duplicates > 0:
                validation_results['errors'].append(f"Duplicate timestamps: {duplicates}")
                validation_results['valid'] = False
            
            # Check for negative prices
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df.columns:
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        validation_results['warnings'].append(f"Negative {col} values: {negative_count}")
            
            # Check for invalid OHLC relationships
            if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                invalid_ohlc = (
                    (df['high'] < df['low']).any() |
                    (df['high'] < df['open']).any() |
                    (df['high'] < df['close']).any() |
                    (df['low'] > df['open']).any() |
                    (df['low'] > df['close']).any()
                )
                if invalid_ohlc:
                    validation_results['errors'].append("Invalid OHLC relationships detected")
                    validation_results['valid'] = False
            
            # Add statistics
            validation_results['stats'] = {
                'total_records': len(df),
                'date_range': f"{df.index[0]} to {df.index[-1]}",
                'data_completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return {'valid': False, 'error': str(e)}

class MarketDataRepository(ITimeSeriesRepository):
    """Repository for market data (DXY, yields, etc.)"""
    
    def __init__(self, data_manager: DataAccessManager = None):
        self.data_manager = data_manager or DataAccessManager()
        self._cache_prefix = "market_data"
    
    @cache_result(ttl_seconds=TRADING_PARAMS.CACHE_EXPIRY_MINUTES * 60)
    def get_data_by_timerange(self, start: datetime, end: datetime, 
                           data_type: str = 'DXY') -> Optional[pd.DataFrame]:
        """Get market data by time range"""
        try:
            df = self.data_manager.load_market_data(data_type)
            if df is None or df.empty:
                logger.warning(f"No market data available for: {data_type}")
                return None
            
            # Filter by date range
            filtered_df = df[(df.index >= start) & (df.index <= end)]
            
            if filtered_df.empty:
                logger.warning(f"No market data in range {start} to {end} for {data_type}")
                return None
            
            logger.info(f"Retrieved {len(filtered_df)} market data points for {data_type}")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error getting market data by timerange: {e}")
            return None
    
    @cache_result(ttl_seconds=600)  # 10 minutes cache for latest market data
    def get_latest_data(self, count: int = None, 
                       data_type: str = 'DXY') -> Optional[pd.DataFrame]:
        """Get latest market data points"""
        try:
            df = self.data_manager.load_market_data(data_type)
            if df is None or df.empty:
                return None
            
            if count:
                return df.tail(count)
            return df
            
        except Exception as e:
            logger.error(f"Error getting latest market data: {e}")
            return None
    
    @cache_result(ttl_seconds=TRADING_PARAMS.CACHE_EXPIRY_MINUTES * 60)
    def get_data_by_date(self, date: datetime, 
                        data_type: str = 'DXY') -> Optional[pd.DataFrame]:
        """Get market data by specific date"""
        try:
            df = self.data_manager.load_market_data(data_type)
            if df is None or df.empty:
                return None
            
            # Filter by date
            date_only = date.date()
            filtered_df = df[df.index.date == date_only]
            
            if filtered_df.empty:
                logger.warning(f"No market data for date {date_only}")
                return None
            
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error getting market data by date: {e}")
            return None
    
    def get_correlation_data(self, gold_timeframe: str = 'H1', 
                          market_data_type: str = 'DXY',
                          period_days: int = 30) -> Optional[pd.DataFrame]:
        """Get correlation data between Gold and market data"""
        try:
            # Get Gold data
            gold_repo = GoldDataRepository(self.data_manager)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            gold_df = gold_repo.get_data_by_timerange(start_date, end_date, gold_timeframe)
            market_df = self.get_data_by_timerange(start_date, end_date, market_data_type)
            
            if gold_df is None or market_df is None:
                return None
            
            # Resample to common frequency
            gold_daily = gold_df['close'].resample('D').last()
            market_daily = market_df['close'].resample('D').last()
            
            # Combine and calculate correlation
            combined_df = pd.DataFrame({
                'gold': gold_daily,
                'market': market_daily
            }).dropna()
            
            # Calculate rolling correlation
            correlation_window = 10
            combined_df['correlation'] = combined_df['gold'].rolling(
                correlation_window).corr(combined_df['market'])
            
            return combined_df
            
        except Exception as e:
            logger.error(f"Error calculating correlation data: {e}")
            return None

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, data_manager: DataAccessManager = None):
        self.data_manager = data_manager or DataAccessManager()
    
    def create_gold_repository(self) -> GoldDataRepository:
        """Create Gold data repository"""
        return GoldDataRepository(self.data_manager)
    
    def create_market_repository(self) -> MarketDataRepository:
        """Create market data repository"""
        return MarketDataRepository(self.data_manager)
    
    def create_repository(self, repository_type: str):
        """Create repository by type"""
        repositories = {
            'gold': self.create_gold_repository,
            'market': self.create_market_repository,
            'dxy': self.create_market_repository,
            'us10y': self.create_market_repository
        }
        
        factory_method = repositories.get(repository_type.lower())
        if factory_method:
            return factory_method()
        
        raise ValueError(f"Unknown repository type: {repository_type}")

# Global repository factory instance
repository_factory = RepositoryFactory()

# Convenience functions
def get_gold_repository() -> GoldDataRepository:
    """Get Gold data repository instance"""
    return repository_factory.create_gold_repository()

def get_market_repository() -> MarketDataRepository:
    """Get market data repository instance"""
    return repository_factory.create_market_repository()

def get_repository(repository_type: str):
    """Get repository by type"""
    return repository_factory.create_repository(repository_type)

if __name__ == "__main__":
    # Test repository functionality
    print("Repository Pattern Test")
    print("=" * 50)
    
    # Test Gold repository
    gold_repo = get_gold_repository()
    
    # Get latest data
    latest_gold = gold_repo.get_latest_data(count=10)
    if latest_gold is not None:
        print(f"Latest Gold data shape: {latest_gold.shape}")
        print(f"Date range: {latest_gold.index[0]} to {latest_gold.index[-1]}")
    
    # Get data summary
    summary = gold_repo.get_data_summary()
    print(f"Gold data summary: {summary}")
    
    # Validate data quality
    validation = gold_repo.validate_data_quality()
    print(f"Data validation: {validation}")
    
    # Test market repository
    market_repo = get_market_repository()
    latest_market = market_repo.get_latest_data(count=5)
    if latest_market is not None:
        print(f"Latest market data shape: {latest_market.shape}")
    
    # Test correlation
    correlation_data = market_repo.get_correlation_data()
    if correlation_data is not None:
        print(f"Correlation data shape: {correlation_data.shape}")
        print(f"Latest correlation: {correlation_data['correlation'].iloc[-1]:.3f}")
