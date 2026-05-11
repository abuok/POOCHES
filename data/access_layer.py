#!/usr/bin/env python3
"""
DATA ACCESS LAYER
Abstract data operations and provide unified interface for data access
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class DataConnectionError(Exception):
    """Custom exception for data connection errors"""
    pass

class BaseDataAccess(ABC):
    """Abstract base class for data access operations"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._validate_path()
    
    def _validate_path(self) -> None:
        """Validate data path exists and is accessible"""
        if not self.data_path.exists():
            raise DataValidationError(f"Data path does not exist: {self.data_path}")
        
        if not self.data_path.is_dir():
            raise DataValidationError(f"Data path is not a directory: {self.data_path}")
    
    @abstractmethod
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load data from file with validation"""
        pass
    
    @abstractmethod
    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """Validate dataframe structure and content"""
        pass
    
    @abstractmethod
    def get_available_files(self) -> List[str]:
        """Get list of available data files"""
        pass

class GoldDataAccess(BaseDataAccess):
    """Data access layer for Gold market data"""
    
    def __init__(self, data_path: Path = Path('.')):
        super().__init__(data_path)
        self.required_columns = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<TICKVOL>', '<VOL>', '<SPREAD>']
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load Gold data with comprehensive validation"""
        try:
            file_path = self.data_path / filename
            if not file_path.exists():
                raise DataValidationError(f"Gold data file not found: {filename}")
            
            logger.info(f"Loading Gold data from: {filename}")
            df = pd.read_csv(file_path, sep='\t')
            
            # Validate required columns
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            if missing_cols:
                raise DataValidationError(f"Missing required columns in {filename}: {missing_cols}")
            
            # Convert datetime index
            if '<DATE>' in df.columns and '<TIME>' in df.columns:
                df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
                df.set_index('datetime', inplace=True)
                df.drop(columns=['<DATE>', '<TIME>'], inplace=True)
            
            # Rename columns to standard format
            column_mapping = {
                '<OPEN>': 'open', '<HIGH>': 'high', '<LOW>': 'low', 
                '<CLOSE>': 'close', '<TICKVOL>': 'tick_volume', 
                '<VOL>': 'volume', '<SPREAD>': 'spread'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert price columns to numeric
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Validate data quality
            self._validate_gold_data(df, filename)
            
            logger.info(f"✓ Gold data loaded successfully: {len(df)} rows from {df.index[0]} to {df.index[-1]}")
            return df
            
        except pd.errors.EmptyDataError:
            raise DataValidationError(f"Empty data file: {filename}")
        except Exception as e:
            raise DataConnectionError(f"Error loading Gold data {filename}: {e}")
    
    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """Validate Gold dataframe structure and content"""
        if df.empty:
            raise DataValidationError("Dataframe is empty")
        
        # Check for required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise DataValidationError(f"Missing required columns: {missing_cols}")
        
        # Validate price data
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            # Check for negative prices
            for col in ['open', 'high', 'low', 'close']:
                if (df[col] < 0).any():
                    logger.warning(f"Found negative values in {col}")
            
            # Check for invalid OHLC relationships
            invalid_ohlc = (
                (df['high'] < df['low']).any() or
                (df['high'] < df['open']).any() or
                (df['high'] < df['close']).any() or
                (df['low'] > df['open']).any() or
                (df['low'] > df['close']).any()
            )
            
            if invalid_ohlc:
                raise DataValidationError("Invalid OHLC relationships detected")
        
        # Check for duplicate timestamps
        if df.index.duplicated().any():
            duplicate_count = df.index.duplicated().sum()
            logger.warning(f"Found {duplicate_count} duplicate timestamps")
        
        # Check data range
        if 'close' in df.columns:
            price_stats = df['close'].describe()
            logger.info(f"Price range: {price_stats['min']:.2f} - {price_stats['max']:.2f}")
        
        return df
    
    def _validate_gold_data(self, df: pd.DataFrame, filename: str) -> None:
        """Additional Gold-specific validation"""
        # Check for reasonable price ranges
        if 'close' in df.columns:
            close_prices = df['close'].dropna()
            if len(close_prices) > 0:
                # Check for extreme price movements
                price_changes = close_prices.pct_change().dropna()
                extreme_moves = price_changes[abs(price_changes) > 0.1]  # >10% move
                if len(extreme_moves) > 0:
                    logger.warning(f"Found {len(extreme_moves)} extreme price movements >10% in {filename}")
        
        # Check volume data if available
        if 'tick_volume' in df.columns:
            volume_stats = df['tick_volume'].describe()
            logger.info(f"Volume range: {volume_stats['min']:.0f} - {volume_stats['max']:.0f}")
    
    def get_available_files(self) -> List[str]:
        """Get list of available Gold data files"""
        gold_files = []
        for file_path in self.data_path.glob("GOLD_*.csv"):
            gold_files.append(file_path.name)
        return sorted(gold_files)

class MarketDataAccess(BaseDataAccess):
    """Data access layer for market data (DXY, yields, etc.)"""
    
    def __init__(self, data_path: Path = Path('.')):
        super().__init__(data_path)
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load market data with validation"""
        try:
            file_path = self.data_path / filename
            if not file_path.exists():
                raise DataValidationError(f"Market data file not found: {filename}")
            
            logger.info(f"Loading market data from: {filename}")
            df = pd.read_csv(file_path)
            
            # Basic validation
            if df.empty:
                raise DataValidationError(f"Empty market data file: {filename}")
            
            # Try to detect and standardize date column
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'DATE' in col.upper()]
            if date_columns:
                date_col = date_columns[0]
                df['datetime'] = pd.to_datetime(df[date_col])
                df.set_index('datetime', inplace=True)
                df.drop(columns=[date_col], inplace=True)
                logger.info(f"Standardized date column: {date_col}")
            
            logger.info(f"✓ Market data loaded successfully: {len(df)} rows")
            return df
            
        except Exception as e:
            raise DataConnectionError(f"Error loading market data {filename}: {e}")
    
    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """Validate market dataframe structure"""
        if df.empty:
            raise DataValidationError("Market dataframe is empty")
        
        # Basic validation
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing optional columns in market data: {missing_cols}")
        
        return df
    
    def get_available_files(self) -> List[str]:
        """Get list of available market data files"""
        market_files = []
        for file_path in self.data_path.glob("*.csv"):
            if 'DXY' in file_path.name or 'DGS' in file_path.name:
                market_files.append(file_path.name)
        return sorted(market_files)

class DataAccessManager:
    """Unified data access manager"""
    
    def __init__(self, data_path: Path = Path('.')):
        self.data_path = data_path
        self.gold_access = GoldDataAccess(data_path)
        self.market_access = MarketDataAccess(data_path)
        self._cached_data = {}
    
    def load_gold_data(self, timeframe: str) -> Optional[pd.DataFrame]:
        """Load Gold data by timeframe with caching"""
        cache_key = f"gold_{timeframe}"
        
        if cache_key not in self._cached_data:
            try:
                # Map timeframe to filename
                filename_map = {
                    'H1': 'GOLD_H1_201901020000_202605082300.csv',
                    'H4': 'GOLD_H4_201901020000_202605082000.csv',
                    'M15': 'GOLD_M15_202211300100_202605082345.csv',
                    'M30': 'GOLD_M30_201901020000_202605082330.csv'
                }
                
                filename = filename_map.get(timeframe)
                if not filename:
                    raise DataValidationError(f"Unsupported timeframe: {timeframe}")
                
                df = self.gold_access.load_data(filename)
                self._cached_data[cache_key] = df
                logger.info(f"✓ Cached {timeframe} data: {len(df)} rows")
                return df
                
            except Exception as e:
                logger.error(f"Error loading {timeframe} data: {e}")
                raise
        
        return self._cached_data.get(cache_key)
    
    def load_market_data(self, data_type: str) -> Optional[pd.DataFrame]:
        """Load market data by type with caching"""
        cache_key = f"market_{data_type}"
        
        if cache_key not in self._cached_data:
            try:
                # Map data type to filename
                if data_type.lower() == 'dxy':
                    # Load multiple DXY files
                    dxy_files = []
                    for i in range(1, 8):
                        filename = f'Download Data - INDEX_US_IFUS_DXY{i}.csv'
                        file_path = self.data_path / filename
                        if file_path.exists():
                            df = self.market_access.load_data(filename)
                            dxy_files.append(df)
                    
                    # Add main file
                    main_file = self.data_path / 'Download Data - INDEX_US_IFUS_DXY.csv'
                    if main_file.exists():
                        df = self.market_access.load_data(main_file)
                        dxy_files.append(df)
                    
                    if dxy_files:
                        combined_df = pd.concat(dxy_files, ignore_index=True).sort_index()
                        self._cached_data[cache_key] = combined_df
                        logger.info(f"✓ Cached DXY data: {len(combined_df)} rows")
                        return combined_df
                
                elif data_type.lower() == 'us10y':
                    filename = 'DGS10.csv'
                    df = self.market_access.load_data(filename)
                    self._cached_data[cache_key] = df
                    logger.info(f"✓ Cached US10Y data: {len(df)} rows")
                    return df
                
                else:
                    raise DataValidationError(f"Unsupported market data type: {data_type}")
                    
            except Exception as e:
                logger.error(f"Error loading {data_type} data: {e}")
                raise
        
        return self._cached_data.get(cache_key)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data"""
        summary = {
            'gold_files': self.gold_access.get_available_files(),
            'market_files': self.market_access.get_available_files(),
            'cached_data': list(self._cached_data.keys()),
            'data_path': str(self.data_path)
        }
        
        # Add data quality info
        for cache_key, df in self._cached_data.items():
            if 'close' in df.columns:
                summary[f'{cache_key}_rows'] = len(df)
                summary[f'{cache_key}_date_range'] = f"{df.index[0]} to {df.index[-1]}"
                summary[f'{cache_key}_price_range'] = f"{df['close'].min():.2f} - {df['close'].max():.2f}"
        
        return summary
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cached_data.clear()
        logger.info("Data cache cleared")

# Factory function for easy access
def create_data_manager(data_path: str = '.') -> DataAccessManager:
    """Factory function to create data access manager"""
    path = Path(data_path)
    return DataAccessManager(path)

# Example usage
if __name__ == "__main__":
    # Create data manager
    data_manager = create_data_manager()
    
    try:
        # Load Gold H1 data
        gold_h1 = data_manager.load_gold_data('H1')
        print(f"Gold H1 data shape: {gold_h1.shape}")
        
        # Load DXY data
        dxy_data = data_manager.load_market_data('DXY')
        print(f"DXY data shape: {dxy_data.shape}")
        
        # Get data summary
        summary = data_manager.get_data_summary()
        print("Data Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")
