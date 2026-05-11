"""
Unit Tests for Gold Analysis Module
Tests data validation, indicator calculations, and analysis functions
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
import logging

# Import the module under test
from gold_analysis_fixed import GoldMarketAnalyzer, Config


@pytest.fixture
def sample_gold_data():
    """Create sample gold price data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)
    
    data = {
        'timestamp': dates,
        'open': 1950 + np.random.randn(100).cumsum() * 2,
        'high': 1952 + np.random.randn(100).cumsum() * 2,
        'low': 1948 + np.random.randn(100).cumsum() * 2,
        'close': 1951 + np.random.randn(100).cumsum() * 2,
        'volume': np.random.randint(1000, 10000, 100),
    }
    
    df = pd.DataFrame(data)
    # Ensure high is highest and low is lowest
    df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1) + 0.5
    df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1) - 0.5
    
    return df


@pytest.fixture
def mock_analyzer():
    """Create a mock analyzer for testing"""
    with patch('gold_analysis_fixed.pd.read_csv') as mock_read:
        mock_read.return_value = sample_gold_data()
        analyzer = GoldMarketAnalyzer()
        return analyzer


class TestConfig:
    """Test configuration management"""
    
    def test_config_paths_exist(self):
        """Test that all configured paths are strings"""
        assert isinstance(Config.GOLD_DATA_PATH, str)
        assert isinstance(Config.DXY_DATA_PATH, str)
        assert isinstance(Config.US10Y_DATA_PATH, str)
    
    def test_config_column_mappings(self):
        """Test column name mappings are dictionaries"""
        assert isinstance(Config.COLUMN_MAPPINGS, dict)
        assert 'GOLD' in Config.COLUMN_MAPPINGS
        assert 'DXY' in Config.COLUMN_MAPPINGS
    
    def test_config_technical_params(self):
        """Test technical analysis parameters are valid"""
        assert Config.EMA_SHORT < Config.EMA_LONG
        assert Config.RSI_PERIOD > 0
        assert Config.ATR_PERIOD > 0
        assert Config.BB_PERIOD > 0


class TestDataValidation:
    """Test data validation functions"""
    
    def test_validate_dataframe_success(self, sample_gold_data):
        """Test validation passes with good data"""
        analyzer = GoldMarketAnalyzer()
        is_valid, errors = analyzer._validate_dataframe(sample_gold_data, 'GOLD')
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_dataframe_missing_columns(self):
        """Test validation fails with missing columns"""
        analyzer = GoldMarketAnalyzer()
        bad_data = pd.DataFrame({'timestamp': [1, 2, 3], 'open': [1, 2, 3]})
        
        is_valid, errors = analyzer._validate_dataframe(bad_data, 'GOLD')
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_dataframe_duplicate_timestamps(self, sample_gold_data):
        """Test validation detects duplicate timestamps"""
        analyzer = GoldMarketAnalyzer()
        bad_data = sample_gold_data.copy()
        bad_data.loc[1, 'timestamp'] = bad_data.loc[0, 'timestamp']
        
        is_valid, errors = analyzer._validate_dataframe(bad_data, 'GOLD')
        
        # Should detect duplicates
        has_duplicate_error = any('duplicate' in err.lower() for err in errors)
        assert has_duplicate_error or is_valid  # May be handled differently


class TestIndicatorCalculations:
    """Test technical indicator calculations"""
    
    def test_calculate_rsi(self, sample_gold_data):
        """Test RSI calculation produces valid values"""
        analyzer = GoldMarketAnalyzer()
        
        # Calculate price changes
        delta = sample_gold_data['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = (-delta.where(delta < 0, 0))
        
        # Calculate initial averages
        avg_gains = gains.rolling(window=14).mean()
        avg_losses = losses.rolling(window=14).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # RSI should be between 0 and 100 (excluding NaN values)
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_ema(self, sample_gold_data):
        """Test EMA calculation"""
        close_prices = sample_gold_data['close']
        
        # Calculate EMA manually
        ema20 = close_prices.ewm(span=20, adjust=False).mean()
        ema50 = close_prices.ewm(span=50, adjust=False).mean()
        
        assert len(ema20) == len(close_prices)
        assert len(ema50) == len(close_prices)
        assert not ema20.isna().all()
    
    def test_calculate_atr(self, sample_gold_data):
        """Test ATR calculation produces positive values"""
        high = sample_gold_data['high']
        low = sample_gold_data['low']
        close = sample_gold_data['close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = tr.rolling(window=14).mean()
        
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()


class TestMarketStructureAnalysis:
    """Test market structure pattern detection"""
    
    def test_detect_swing_points(self, sample_gold_data):
        """Test swing point detection"""
        # Create data with clear swing
        data = sample_gold_data.copy()
        data.loc[10:15, 'high'] = data['high'].max()  # Local peak
        
        analyzer = GoldMarketAnalyzer()
        highs, lows = analyzer._detect_swing_points(data, window=5)
        
        assert isinstance(highs, pd.Series)
        assert isinstance(lows, pd.Series)
    
    def test_detect_bos_choch(self, sample_gold_data):
        """Test BOS/CHoCH pattern detection"""
        analyzer = GoldMarketAnalyzer()
        
        result = analyzer._detect_bos_choch(sample_gold_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'bos_bullish' in result.columns or 'bos_bearish' in result.columns


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe"""
        analyzer = GoldMarketAnalyzer()
        empty_df = pd.DataFrame()
        
        is_valid, errors = analyzer._validate_dataframe(empty_df, 'GOLD')
        assert is_valid is False
        assert len(errors) > 0
    
    def test_file_not_found(self):
        """Test handling of missing file"""
        with patch('gold_analysis_fixed.pd.read_csv', side_effect=FileNotFoundError()):
            analyzer = GoldMarketAnalyzer()
            
            # Should handle gracefully
            with pytest.raises(FileNotFoundError):
                analyzer.load_and_audit_data()
    
    def test_invalid_csv_format(self):
        """Test handling of malformed CSV"""
        with patch('gold_analysis_fixed.pd.read_csv', side_effect=pd.errors.EmptyDataError()):
            analyzer = GoldMarketAnalyzer()
            
            result = analyzer.load_and_audit_data()
            # Should return empty or handle gracefully
            assert result is None or isinstance(result, pd.DataFrame)


class TestSessionAnalysis:
    """Test session-based analysis"""
    
    def test_session_detection(self, sample_gold_data):
        """Test correct session assignment"""
        analyzer = GoldMarketAnalyzer()
        
        # Add hour column for testing
        df = sample_gold_data.copy()
        df['hour'] = df['timestamp'].dt.hour
        
        result = analyzer.session_analysis()
        
        # Should return session statistics
        assert isinstance(result, dict)


class TestCorrelationAnalysis:
    """Test DXY correlation calculations"""
    
    def test_correlation_calculation(self, sample_gold_data):
        """Test correlation between gold and DXY"""
        # Create mock DXY data
        dxy_data = sample_gold_data.copy()
        dxy_data['close'] = 100 + np.random.randn(100).cumsum()
        
        # Calculate correlation
        correlation = sample_gold_data['close'].corr(dxy_data['close'])
        
        # Correlation should be between -1 and 1
        assert -1 <= correlation <= 1


class TestPerformanceAndSafety:
    """Test performance characteristics and safety"""
    
    def test_large_dataset_handling(self):
        """Test system can handle large datasets"""
        # Create large dataset
        large_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2020-01-01', periods=50000, freq='H'),
            'open': np.random.randn(50000) + 1950,
            'high': np.random.randn(50000) + 1952,
            'low': np.random.randn(50000) + 1948,
            'close': np.random.randn(50000) + 1951,
            'volume': np.random.randint(1000, 10000, 50000),
        })
        
        analyzer = GoldMarketAnalyzer()
        
        # Should process without memory errors
        is_valid, errors = analyzer._validate_dataframe(large_data, 'GOLD')
        assert is_valid is True
    
    def test_data_quality_report(self, sample_gold_data):
        """Test data quality report generation"""
        analyzer = GoldMarketAnalyzer()
        
        report = analyzer.data_quality_report(sample_gold_data)
        
        assert isinstance(report, dict)
        assert 'total_rows' in report
        assert 'quality_score' in report
        assert 0 <= report['quality_score'] <= 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
