#!/usr/bin/env python3
"""
COMPREHENSIVE GOLD MARKET ANALYSIS - FIXED VERSION
Institutional-grade quantitative research for XAUUSD trading strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gold_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration management
class Config:
    """Configuration class for trading system paths and settings"""
    
    DATA_DIR: Path = Path('data')
    GOLD_FILES: Dict[str, str] = {
        'H1': 'GOLD_H1_201901020000_202605082300.csv',
        'H4': 'GOLD_H4_201901020000_202605082000.csv',
        'M15_2022': 'GOLD_M15_202202102030_202211301415.csv',
        'M15_recent': 'GOLD_M15_202211300100_202605082345.csv',
        'M30': 'GOLD_M30_201901020000_202605082330.csv'
    }
    DXY_FILES: List[str] = [f'Download Data - INDEX_US_IFUS_DXY{i}.csv' 
                for i in range(1, 8)] + ['Download Data - INDEX_US_IFUS_DXY.csv']
    US10Y_FILE: str = 'DGS10.csv'
    
    @classmethod
    def validate_files(cls) -> bool:
        """Check if all required data files exist
        
        Returns:
            bool: True if all files exist, False otherwise
        """
        missing_files: List[str] = []
        
        for timeframe, file in cls.GOLD_FILES.items():
            if not Path(file).exists():
                missing_files.append(file)
                
        for file in cls.DXY_FILES:
            if not Path(file).exists():
                missing_files.append(file)
                
        if not Path(cls.US10Y_FILE).exists():
            missing_files.append(cls.US10Y_FILE)
            
        if missing_files:
            logger.error(f"Missing data files: {missing_files}")
            return False
            
        logger.info("All required data files found")
        return True

class GoldMarketAnalyzer:
    """Gold market analyzer with comprehensive data validation and analysis capabilities"""
    
    def __init__(self) -> None:
        """Initialize the Gold market analyzer"""
        self.data: Dict[str, pd.DataFrame] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.config = Config()
        
    def load_and_audit_data(self) -> Dict[str, pd.DataFrame]:
        """PHASE 1: Data Audit and Quality Assessment
        
        Returns:
            Dict[str, pd.DataFrame]: Loaded and validated Gold data by timeframe
        """
        logger.info("=" * 80)
        logger.info("PHASE 1: DATA AUDIT AND QUALITY ASSESSMENT")
        logger.info("=" * 80)
        
        # Validate data files exist
        if not self.config.validate_files():
            raise FileNotFoundError("Required data files missing. Check configuration.")
        
        logger.info("Loading datasets...")
        
        # Load Gold data with proper error handling
        for timeframe, file in self.config.GOLD_FILES.items():
            try:
                if not Path(file).exists():
                    raise FileNotFoundError(f"Data file not found: {file}")
                    
                df = pd.read_csv(file, sep='\t')
                
                # Validate required columns
                required_cols = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Missing required columns in {file}: {missing_cols}")
                
                df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
                df.set_index('datetime', inplace=True)
                df.rename(columns={
                    '<OPEN>': 'open', '<HIGH>': 'high', '<LOW>': 'low', 
                    '<CLOSE>': 'close', '<TICKVOL>': 'tick_volume', 
                    '<VOL>': 'volume', '<SPREAD>': 'spread'
                }, inplace=True)
                
                # Convert to numeric with validation
                price_cols = ['open', 'high', 'low', 'close']
                for col in price_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Data quality checks
                self._validate_dataframe(df, f"gold_{timeframe}")
                
                self.data[timeframe] = df
                logger.info(f"✓ Loaded {len(df)} {timeframe} data points from {df.index[0]} to {df.index[-1]}")
                
            except FileNotFoundError as e:
                logger.error(f"✗ File not found {file}: {e}")
                raise
            except pd.errors.EmptyDataError:
                logger.error(f"✗ Empty data file: {file}")
                raise
            except ValueError as e:
                logger.error(f"✗ Data validation error in {file}: {e}")
                raise
            except Exception as e:
                logger.error(f"✗ Unexpected error loading {file}: {e}")
                raise
        
    def _validate_dataframe(self, df: pd.DataFrame, dataset_name: str) -> None:
        """Validate dataframe for data quality issues
        
        Args:
            df: DataFrame to validate
            dataset_name: Name of the dataset for logging
            
        Raises:
            ValueError: If data quality issues are found
        """
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            logger.warning(f"Missing values in {dataset_name}: {missing_values[missing_values > 0].to_dict()}")
        
        # Check for duplicate indices
        duplicate_indices = df.index.duplicated().sum()
        if duplicate_indices > 0:
            logger.warning(f"Found {duplicate_indices} duplicate indices in {dataset_name}")
        
        # Check for negative prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                negative_prices = (df[col] < 0).sum()
                if negative_prices > 0:
                    logger.warning(f"Found {negative_prices} negative values in {dataset_name} {col}")
        
        # Check for invalid OHLC relationships
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            invalid_ohlc = (
                (df['high'] < df['low']).any() |
                (df['high'] < df['open']).any() |
                (df['high'] < df['close']).any() |
                (df['low'] > df['open']).any() |
                (df['low'] > df['close']).any()
            )
            if invalid_ohlc.any():
                logger.warning(f"Invalid OHLC relationships found in {dataset_name}")
        
        # Check data range
        if 'close' in df.columns:
            price_stats = df['close'].describe()
            logger.info(f"{dataset_name} price range: {price_stats['min']:.2f} - {price_stats['max']:.2f}")
        
        # Load DXY data with error handling
        dxy_data = []
        for file in self.config.DXY_FILES:
            try:
                if not Path(file).exists():
                    logger.warning(f"DXY file not found: {file}")
                    continue
                    
                df = pd.read_csv(file)
                
                # Validate DXY columns
                required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Missing DXY columns in {file}: {missing_cols}")
                
                df['datetime'] = pd.to_datetime(df['Date'])
                df.set_index('datetime', inplace=True)
                df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
                
                # Convert to numeric
                price_cols = ['open', 'high', 'low', 'close']
                for col in price_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                self._validate_dataframe(df, f"dxy_{Path(file).stem}")
                dxy_data.append(df)
                logger.info(f"✓ DXY {Path(file).stem}: {len(df)} candles")
                
            except Exception as e:
                logger.error(f"✗ Error loading DXY {file}: {e}")
                continue
        
        if dxy_data:
            dxy_combined = pd.concat(dxy_data).sort_index()
            self.data['dxy'] = dxy_combined
            logger.info(f"✓ DXY combined: {len(dxy_combined)} candles from {dxy_combined.index[0]} to {dxy_combined.index[-1]}")
        
        # Load US10Y yields with error handling
        try:
            if not Path(self.config.US10Y_FILE).exists():
                logger.warning(f"US10Y file not found: {self.config.US10Y_FILE}")
            else:
                df = pd.read_csv(self.config.US10Y_FILE)
                
                # Validate US10Y columns
                required_cols = ['observation_date', 'DGS10']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Missing US10Y columns: {missing_cols}")
                
                df['datetime'] = pd.to_datetime(df['observation_date'])
                df.set_index('datetime', inplace=True)
                df.rename(columns={'DGS10': 'yield_10y'}, inplace=True)
                df['yield_10y'] = pd.to_numeric(df['yield_10y'], errors='coerce')
                
                self._validate_dataframe(df, "us10y")
                self.data['us10y'] = df
                logger.info(f"✓ US10Y: {len(df)} observations from {df.index[0]} to {df.index[-1]}")
                
        except Exception as e:
            logger.error(f"✗ Error loading US10Y: {e}")
            # Continue without US10Y data
        
        logger.info("Data loading completed successfully")
        return self.data
    
    def _validate_dataframe(self, df: pd.DataFrame, data_name: str) -> None:
        """Validate dataframe quality and log issues
        
        Args:
            df: DataFrame to validate
            data_name: Name of the dataset for logging
        """
        if df.empty:
            logger.warning(f"Empty dataframe: {data_name}")
            return
            
        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values in {data_name}: {null_counts[null_counts > 0].to_dict()}")
        
        # Check for duplicates
        if df.index.duplicated().any():
            duplicate_count = df.index.duplicated().sum()
            logger.warning(f"Found {duplicate_count} duplicate timestamps in {data_name}")
        
        # Check data range
        if 'close' in df.columns:
            close_stats = df['close'].describe()
            logger.info(f"{data_name} price stats: min={close_stats['min']:.2f}, max={close_stats['max']:.2f}, mean={close_stats['mean']:.2f}")
        
        # Check for outliers (basic)
        if 'close' in df.columns:
            q1 = df['close'].quantile(0.25)
            q3 = df['close'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = df[(df['close'] < lower_bound) | (df['close'] > upper_bound)]
            if len(outliers) > 0:
                logger.warning(f"Found {len(outliers)} price outliers in {data_name}")
        
        logger.info(f"✓ {data_name} validation completed")
    
    def data_quality_report(self) -> Dict[str, Dict]:
        """Generate comprehensive data quality assessment
        
        Returns:
            Dict[str, Dict]: Quality metrics for each dataset
        """
        logger.info("\n" + "=" * 80)
        logger.info("DATA QUALITY REPORT")
        logger.info("=" * 80)
        
        quality_report = {}
        
        for name, df in self.data.items():
            if 'gold' in name:
                # Gold data quality checks
                missing_candles = df.isnull().sum().sum()
                duplicate_candles = df.index.duplicated().sum()
                weekend_candles = df.index[df.index.weekday >= 5].size
                
                # Price consistency checks
                price_inconsistencies = ((df['high'] < df['low']) | 
                                       (df['high'] < df['open']) | 
                                       (df['high'] < df['close']) |
                                       (df['low'] > df['open']) | 
                                       (df['low'] > df['close'])).sum()
                
                # Spread analysis
                avg_spread = df['spread'].mean()
                spread_anomalies = (df['spread'] > df['spread'].quantile(0.99)).sum()
                
                quality_report[name] = {
                    'total_candles': len(df),
                    'missing_values': missing_candles,
                    'duplicate_candles': duplicate_candles,
                    'weekend_candles': weekend_candles,
                    'price_inconsistencies': price_inconsistencies,
                    'avg_spread': avg_spread,
                    'spread_anomalies': spread_anomalies,
                    'date_range': f"{df.index[0]} to {df.index[-1]}",
                    'data_quality_score': self._calculate_quality_score(df)
                }
                
                print(f"\n{name.upper()}:")
                print(f"  Total candles: {len(df):,}")
                print(f"  Date range: {df.index[0]} to {df.index[-1]}")
                print(f"  Missing values: {missing_candles}")
                print(f"  Duplicate timestamps: {duplicate_candles}")
                print(f"  Weekend candles: {weekend_candles}")
                print(f"  Price inconsistencies: {price_inconsistencies}")
                print(f"  Average spread: {avg_spread:.1f} pips")
                print(f"  Spread anomalies: {spread_anomalies}")
                print(f"  Data quality score: {quality_report[name]['data_quality_score']:.1%}")
        
        self.analysis_results['data_quality'] = quality_report
        return quality_report
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score (0-100%)"""
        base_score = 100
        
        # Deduct points for issues
        if df.isnull().sum().sum() > 0:
            base_score -= 10
        if df.index.duplicated().sum() > 0:
            base_score -= 10
        if ((df['high'] < df['low']) | 
            (df['high'] < df['open']) | 
            (df['high'] < df['close']) |
            (df['low'] > df['open']) | 
            (df['low'] > df['close'])).sum() > 0:
            base_score -= 20
        
        return max(0, base_score / 100)
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all necessary indicators and patterns
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with all calculated indicators
        """
        # Basic price action indicators
        df['range'] = df['high'] - df['low']
        df['body'] = abs(df['close'] - df['open'])
        df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body_ratio'] = df['body'] / df['range']
        df['volume_ma'] = df['tick_volume'].rolling(20).mean()
        df['volatility'] = df['range'].rolling(20).std()
        
        # Detect market structure patterns
        df = self._detect_swing_points(df)
        df = self._detect_bos_choch(df)
        df = self._detect_fair_value_gaps(df)
        df = self._detect_liquidity_sweeps(df)
        df = self._detect_displacement_candles(df)
        
        return df
    
    def _detect_swing_points(self, df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """Detect swing highs and lows
        
        Args:
            df: DataFrame with OHLC data
            window: Window size for swing detection
            
        Returns:
            pd.DataFrame: DataFrame with swing points marked
        """
        df['swing_high'] = df['high'].rolling(window*2+1, center=True).apply(
            lambda x: x[window] == x.max(), raw=False)
        df['swing_low'] = df['low'].rolling(window*2+1, center=True).apply(
            lambda x: x[window] == x.min(), raw=False)
        
        df['swing_high'] = df['swing_high'].fillna(False).astype(bool)
        df['swing_low'] = df['swing_low'].fillna(False).astype(bool)
        
        return df
    
    def _detect_bos_choch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect Break of Structure and Change of Character"""
        df['higher_high'] = df['high'].rolling(10).apply(
            lambda x: x.iloc[-1] == x.max(), raw=False).fillna(False).astype(bool)
        df['lower_low'] = df['low'].rolling(10).apply(
            lambda x: x.iloc[-1] == x.min(), raw=False).fillna(False).astype(bool)
        
        # BOS: Break previous swing high/low with momentum
        df['bos_up'] = (df['higher_high'] & 
                       (df['tick_volume'] > df['volume_ma'] * 1.5) &
                       (df['body_ratio'] > 0.6))
        
        df['bos_down'] = (df['lower_low'] & 
                         (df['tick_volume'] > df['volume_ma'] * 1.5) &
                         (df['body_ratio'] > 0.6))
        
        # CHOCH: Change of Character - reversal at structure points
        df['choch_up'] = (df['swing_low'] & 
                         (df['close'] > df['open']) &
                         (df['tick_volume'] > df['volume_ma']))
        
        df['choch_down'] = (df['swing_high'] & 
                           (df['close'] < df['open']) &
                           (df['tick_volume'] > df['volume_ma']))
        
        return df
    
    def _detect_fair_value_gaps(self, df):
        """Detect Fair Value Gaps (Imbalances)"""
        df['fvg_up'] = ((df['low'] > df['high'].shift(1)) & 
                       (df['tick_volume'] > df['volume_ma']))
        
        df['fvg_down'] = ((df['high'] < df['low'].shift(1)) & 
                         (df['tick_volume'] > df['volume_ma']))
        
        return df
    
    def _detect_liquidity_sweeps(self, df):
        """Detect liquidity sweeps (stop hunts)"""
        # Wick ratio indicates potential liquidity grab
        df['wick_ratio'] = (df['upper_wick'] + df['lower_wick']) / df['range']
        
        df['liquidity_sweep_up'] = ((df['lower_wick'] > df['body'] * 2) & 
                                   (df['close'] > df['open']) &
                                   (df['wick_ratio'] > 0.7))
        
        df['liquidity_sweep_down'] = ((df['upper_wick'] > df['body'] * 2) & 
                                     (df['close'] < df['open']) &
                                     (df['wick_ratio'] > 0.7))
        
        return df
    
    def _detect_displacement_candles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect displacement candles (strong momentum moves)
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with displacement patterns detected
        """
        df['displacement'] = ((df['body_ratio'] > 0.8) & 
                            (df['range'] > df['range'].rolling(20).mean() * 2) &
                            (df['tick_volume'] > df['volume_ma'] * 2))
        
        return df
    
    def market_structure_analysis(self) -> Dict[str, Any]:
        """PHASE 2: Market Structure Analysis
        
        Returns:
            Dict[str, Any]: Market structure analysis results
        """
        print("\n" + "=" * 80)
        print("PHASE 2: MARKET STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Focus on H1 data for primary analysis
        if 'gold_H1' not in self.data:
            print("H1 data not available for analysis")
            return {}
        
        df = self.data['gold_H1'].copy()
        df = self.calculate_all_indicators(df)
        
        # Analyze pattern statistics
        structure_stats = self._analyze_structure_patterns(df)
        
        self.analysis_results['market_structure'] = {
            'data': df,
            'statistics': structure_stats
        }
        
        # Print key findings
        print("MARKET STRUCTURE PATTERN ANALYSIS:")
        for pattern, stats in structure_stats.items():
            if stats['count'] > 0:
                print(f"\n{pattern.upper()}:")
                print(f"  Count: {stats['count']:,} ({stats['frequency']:.2f}% of candles)")
                if stats['follow_through']:
                    ft = stats['follow_through']
                    print(f"  Follow-through - Avg Return: {ft['avg_return']*100:.2f}%")
                    print(f"  Follow-through - Win Rate: {ft['win_rate']*100:.1f}%")
        
        return structure_stats
    
    def _analyze_structure_patterns(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Analyze statistical properties of detected patterns
        
        Args:
            df: DataFrame with pattern detection results
            
        Returns:
            Dict[str, Dict]: Statistical analysis of each pattern type
        """
        stats = {}
        
        # Pattern frequencies
        patterns = ['bos_up', 'bos_down', 'choch_up', 'choch_down', 
                   'fvg_up', 'fvg_down', 'liquidity_sweep_up', 'liquidity_sweep_down', 
                   'displacement']
        
        for pattern in patterns:
            if pattern in df.columns:
                count = df[pattern].sum()
                freq = count / len(df) * 100
                
                # Follow-through analysis (next 5 candles)
                follow_through = self._analyze_follow_through(df, pattern)
                
                stats[pattern] = {
                    'count': int(count),
                    'frequency': freq,
                    'follow_through': follow_through
                }
        
        return stats
    
    def _analyze_follow_through(self, df: pd.DataFrame, pattern: str, periods: int = 5) -> Dict[str, float]:
        """Analyze follow-through behavior after patterns
        
        Args:
            df: DataFrame with pattern detection results
            pattern: Pattern name to analyze
            periods: Number of periods to analyze after pattern
            
        Returns:
            Dict[str, float]: Follow-through statistics
        """
        if pattern not in df.columns:
            return {}
        
        pattern_indices = df[df[pattern]].index
        
        if len(pattern_indices) == 0:
            return {}
        
        follow_data = []
        
        for idx in pattern_indices:
            pos = df.index.get_loc(idx)
            if pos + periods < len(df):
                future_returns = (df['close'].iloc[pos+1:pos+periods+1] - 
                               df['close'].iloc[pos]) / df['close'].iloc[pos]
                follow_data.extend(future_returns.values)
        
        if follow_data:
            return {
                'avg_return': float(np.mean(follow_data)),
                'win_rate': float(np.mean(np.array(follow_data) > 0)),
                'max_return': float(np.max(follow_data)),
                'min_return': float(np.min(follow_data)),
                'volatility': float(np.std(follow_data))
            }
        
        return {}
    
    def session_analysis(self) -> Dict[str, Any]:
        """PHASE 3: Session Analysis
        
        Returns:
            Dict[str, Any]: Session analysis results
        """
        print("\n" + "=" * 80)
        print("PHASE 3: SESSION ANALYSIS")
        print("=" * 80)
        
        if 'gold_H1' not in self.data:
            print("H1 data not available for session analysis")
            return
        
        df = self.data['gold_H1'].copy()
        df = self.calculate_all_indicators(df)
        
        # Define session times (UTC)
        def get_session(hour):
            if 0 <= hour < 7:
                return 'Asian'
            elif 7 <= hour < 12:
                return 'London'
            elif 12 <= hour < 17:
                return 'NY'
            elif 17 <= hour < 22:
                return 'NY_Evening'
            else:
                return 'Asian_Late'
        
        df['hour'] = df.index.hour
        df['session'] = df['hour'].apply(get_session)
        df['day_of_week'] = df.index.dayofweek
        
        # Session statistics
        session_stats = {}
        
        for session in df['session'].unique():
            session_data = df[df['session'] == session]
            
            session_stats[session] = {
                'candle_count': len(session_data),
                'avg_range': session_data['range'].mean(),
                'avg_volume': session_data['tick_volume'].mean(),
                'avg_volatility': session_data['range'].std(),
                'up_candles': (session_data['close'] > session_data['open']).mean() * 100,
                'displacement_freq': session_data['displacement'].mean() * 100,
                'liquidity_sweep_freq': ((session_data['liquidity_sweep_up'] | session_data['liquidity_sweep_down']).mean() * 100)
            }
        
        # Day of week analysis
        dow_stats = {}
        for dow in range(7):
            dow_data = df[df['day_of_week'] == dow]
            if len(dow_data) > 0:
                dow_stats[dow] = {
                    'avg_range': dow_data['range'].mean(),
                    'avg_volume': dow_data['tick_volume'].mean(),
                    'up_candles': (dow_data['close'] > dow_data['open']).mean() * 100,
                    'volatility': dow_data['range'].std()
                }
        
        self.analysis_results['session_analysis'] = {
            'session_stats': session_stats,
            'dow_stats': dow_stats,
            'data': df
        }
        
        # Print session analysis
        print("SESSION PERFORMANCE:")
        for session, stats in session_stats.items():
            print(f"\n{session}:")
            print(f"  Candles: {stats['candle_count']:,}")
            print(f"  Avg Range: {stats['avg_range']:.2f}")
            print(f"  Avg Volume: {stats['avg_volume']:,.0f}")
            print(f"  Up Candles: {stats['up_candles']:.1f}%")
            print(f"  Displacement Freq: {stats['displacement_freq']:.2f}%")
            print(f"  Liquidity Sweep Freq: {stats['liquidity_sweep_freq']:.2f}%")
        
        return session_stats, dow_stats
    
    def dxy_correlation_analysis(self) -> Dict[str, Any]:
        """PHASE 4: DXY Correlation Analysis
        
        Returns:
            Dict[str, Any]: DXY correlation analysis results
        """
        print("\n" + "=" * 80)
        print("PHASE 4: DXY CORRELATION ANALYSIS")
        print("=" * 80)
        
        if 'gold_H1' not in self.data or 'dxy' not in self.data:
            print("Required data not available for correlation analysis")
            return {}
        
        # Align data by timestamp
        gold_df = self.data['gold_H1'].copy()
        dxy_df = self.data['dxy'].copy()
        
        # Resample DXY to hourly to match gold data
        dxy_hourly = dxy_df.resample('H').last().dropna()
        
        # Align datasets
        start_date = max(gold_df.index[0], dxy_hourly.index[0])
        end_date = min(gold_df.index[-1], dxy_hourly.index[-1])
        
        gold_aligned = gold_df.loc[start_date:end_date]
        dxy_aligned = dxy_hourly.loc[start_date:end_date]
        
        # Calculate returns
        gold_aligned['returns'] = gold_aligned['close'].pct_change()
        dxy_aligned['returns'] = dxy_aligned['close'].pct_change()
        
        # Combine data
        combined = pd.DataFrame({
            'gold_close': gold_aligned['close'],
            'gold_returns': gold_aligned['returns'],
            'dxy_close': dxy_aligned['close'],
            'dxy_returns': dxy_aligned['returns']
        }).dropna()
        
        # Correlation analysis
        correlation: float = combined['gold_returns'].corr(combined['dxy_returns'])
        
        # Rolling correlation
        rolling_corr: pd.Series = combined['gold_returns'].rolling(50).corr(combined['dxy_returns'])
        
        # Session-based correlation
        combined['hour'] = combined.index.hour
        session_correlations: Dict[int, float] = {}
        
        for hour in range(24):
            hour_data = combined[combined['hour'] == hour]
            if len(hour_data) > 50:
                session_correlations[hour] = hour_data['gold_returns'].corr(hour_data['dxy_returns'])
        
        # Volatility regime analysis
        gold_vol = combined['gold_returns'].rolling(20).std()
        vol_regimes = pd.cut(gold_vol, bins=3, labels=['Low', 'Medium', 'High'])
        
        regime_correlations: Dict[str, float] = {}
        for regime in vol_regimes.cat.categories:
            regime_data = combined[vol_regimes == regime]
            if len(regime_data) > 50:
                regime_correlations[regime] = regime_data['gold_returns'].corr(regime_data['dxy_returns'])
        
        # Lag analysis
        lag_correlations: Dict[int, float] = {}
        for lag in range(-5, 6):
            if lag != 0:
                lagged_corr = combined['gold_returns'].corr(combined['dxy_returns'].shift(lag))
                lag_correlations[lag] = lagged_corr
        
        correlation_results = {
            'overall_correlation': correlation,
            'rolling_correlation_mean': rolling_corr.mean(),
            'rolling_correlation_std': rolling_corr.std(),
            'session_correlations': session_correlations,
            'regime_correlations': regime_correlations,
            'lag_correlations': lag_correlations,
            'combined_data': combined
        }
        
        self.analysis_results['dxy_correlation'] = correlation_results
        
        # Print results
        print(f"Overall Gold-DXY Correlation: {correlation:.3f}")
        print(f"Rolling Correlation - Mean: {rolling_corr.mean():.3f}, Std: {rolling_corr.std():.3f}")
        
        print("\nCorrelation by Volatility Regime:")
        for regime, corr in regime_correlations.items():
            print(f"  {regime} Volatility: {corr:.3f}")
        
        print("\nBest Lag Correlations:")
        sorted_lags = sorted(lag_correlations.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        for lag, corr in sorted_lags:
            print(f"  Lag {lag:+.1f}h: {corr:.3f}")

# Main execution
def main() -> None:
    """Main execution with proper error handling
    
    Raises:
        Exception: If fatal error occurs during execution
    """
    try:
        logger.info("Starting Gold Market Analysis System")
        analyzer = GoldMarketAnalyzer()
        
        # Phase 1: Data Audit
        logger.info("Starting Phase 1: Data Audit")
        analyzer.load_and_audit_data()
        analyzer.data_quality_report()
        
        # Phase 2: Market Structure Analysis
        logger.info("Starting Phase 2: Market Structure Analysis")
        analyzer.market_structure_analysis()
        
        # Phase 3: Session Analysis
        logger.info("Starting Phase 3: Session Analysis")
        analyzer.session_analysis()
        
        # Phase 4: DXY Correlation Analysis
        logger.info("Starting Phase 4: DXY Correlation Analysis")
        analyzer.dxy_correlation_analysis()
        
        logger.info("Analysis completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
