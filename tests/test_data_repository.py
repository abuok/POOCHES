#!/usr/bin/env python3
"""
UNIT TESTS FOR DATA REPOSITORY
Comprehensive testing of repository pattern implementation
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from repositories.data_repository import (
    GoldDataRepository, 
    MarketDataRepository, 
    RepositoryFactory,
    get_gold_repository,
    get_market_repository
)
from data.access_layer import DataAccessManager
from constants.trading_constants import TRADING_PARAMS, DATA_CONFIG

class TestGoldDataRepository(unittest.TestCase):
    """Test cases for Gold data repository"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_data_manager = Mock(spec=DataAccessManager)
        self.repository = GoldDataRepository(self.mock_data_manager)
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'open': [1900.0, 1905.0, 1910.0, 1915.0, 1920.0],
            'high': [1910.0, 1915.0, 1920.0, 1925.0, 1930.0],
            'low': [1895.0, 1900.0, 1905.0, 1910.0, 1915.0],
            'close': [1905.0, 1910.0, 1915.0, 1920.0, 1925.0],
            'tick_volume': [1000, 1200, 800, 1500, 900]
        }, index=pd.date_range('2024-01-01', periods=5, freq='H'))
    
    def test_get_data_by_timerange_success(self):
        """Test successful data retrieval by time range"""
        # Mock the data manager
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)  # First 3 data points
        self.mock_data_manager.load_gold_data.assert_called_once_with('H1')
    
    def test_get_data_by_timerange_empty_result(self):
        """Test empty result when no data in range"""
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        start_date = datetime(2024, 2, 1)  # Outside data range
        end_date = datetime(2024, 2, 3)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        self.assertIsNone(result)
    
    def test_get_data_by_timerange_no_data(self):
        """Test handling when no data available"""
        self.mock_data_manager.load_gold_data.return_value = None
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        self.assertIsNone(result)
    
    def test_get_latest_data_success(self):
        """Test successful latest data retrieval"""
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        result = self.repository.get_latest_data(count=3, timeframe='H1')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.mock_data_manager.load_gold_data.assert_called_once_with('H1')
    
    def test_get_latest_data_no_data(self):
        """Test handling when no data available"""
        self.mock_data_manager.load_gold_data.return_value = None
        
        result = self.repository.get_latest_data(timeframe='H1')
        
        self.assertIsNone(result)
    
    def test_get_data_by_date_success(self):
        """Test successful data retrieval by date"""
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        target_date = datetime(2024, 1, 2)
        result = self.repository.get_data_by_date(target_date, 'H1')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)  # One data point for the date
    
    def test_get_available_timeframes(self):
        """Test getting available timeframes"""
        timeframes = self.repository.get_available_timeframes()
        
        self.assertIsInstance(timeframes, list)
        self.assertIn('H1', timeframes)
        self.assertIn('H4', timeframes)
        self.assertIn('M15', timeframes)
    
    def test_get_data_summary_success(self):
        """Test successful data summary generation"""
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        summary = self.repository.get_data_summary('H1')
        
        self.assertIsInstance(summary, dict)
        self.assertIn('timeframe', summary)
        self.assertIn('total_records', summary)
        self.assertIn('price_range', summary)
        self.assertIn('volume_stats', summary)
        self.assertEqual(summary['timeframe'], 'H1')
        self.assertEqual(summary['total_records'], 5)
    
    def test_validate_data_quality_success(self):
        """Test successful data quality validation"""
        self.mock_data_manager.load_gold_data.return_value = self.sample_data
        
        validation = self.repository.validate_data_quality('H1')
        
        self.assertIsInstance(validation, dict)
        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)
        self.assertIn('stats', validation)
        self.assertTrue(validation['valid'])
    
    def test_validate_data_quality_with_errors(self):
        """Test data quality validation with errors"""
        # Create data with issues
        bad_data = self.sample_data.copy()
        bad_data.loc[bad_data.index[0], 'close'] = -100  # Negative price
        bad_data.loc[bad_data.index[1], 'high'] = 1800  # Invalid OHLC
        
        self.mock_data_manager.load_gold_data.return_value = bad_data
        
        validation = self.repository.validate_data_quality('H1')
        
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)

class TestMarketDataRepository(unittest.TestCase):
    """Test cases for Market data repository"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_data_manager = Mock(spec=DataAccessManager)
        self.repository = MarketDataRepository(self.mock_data_manager)
        
        # Create sample market data
        self.sample_market_data = pd.DataFrame({
            'close': [105.0, 105.5, 106.0, 105.8, 106.2],
            'volume': [50000, 52000, 48000, 55000, 51000]
        }, index=pd.date_range('2024-01-01', periods=5, freq='D'))
    
    def test_get_market_data_by_timerange_success(self):
        """Test successful market data retrieval"""
        self.mock_data_manager.load_market_data.return_value = self.sample_market_data
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'DXY')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.mock_data_manager.load_market_data.assert_called_once_with('DXY')
    
    def test_get_correlation_data_success(self):
        """Test successful correlation data calculation"""
        # Mock both gold and market data
        gold_data = pd.DataFrame({
            'close': [1900.0, 1910.0, 1920.0, 1915.0, 1925.0]
        }, index=pd.date_range('2024-01-01', periods=5, freq='D'))
        
        self.mock_data_manager.load_gold_data.return_value = gold_data
        self.mock_data_manager.load_market_data.return_value = self.sample_market_data
        
        correlation_data = self.repository.get_correlation_data('H1', 'DXY', 30)
        
        self.assertIsNotNone(correlation_data)
        self.assertIn('gold', correlation_data.columns)
        self.assertIn('market', correlation_data.columns)
        self.assertIn('correlation', correlation_data.columns)

class TestRepositoryFactory(unittest.TestCase):
    """Test cases for Repository Factory"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = RepositoryFactory()
    
    def test_create_gold_repository(self):
        """Test Gold repository creation"""
        repository = self.factory.create_gold_repository()
        
        self.assertIsInstance(repository, GoldDataRepository)
    
    def test_create_market_repository(self):
        """Test Market repository creation"""
        repository = self.factory.create_market_repository()
        
        self.assertIsInstance(repository, MarketDataRepository)
    
    def test_create_repository_by_type(self):
        """Test repository creation by type"""
        gold_repo = self.factory.create_repository('gold')
        market_repo = self.factory.create_repository('market')
        
        self.assertIsInstance(gold_repo, GoldDataRepository)
        self.assertIsInstance(market_repo, MarketDataRepository)
    
    def test_create_repository_invalid_type(self):
        """Test repository creation with invalid type"""
        with self.assertRaises(ValueError):
            self.factory.create_repository('invalid_type')

class TestRepositoryIntegration(unittest.TestCase):
    """Integration tests for repository functionality"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample CSV files
        sample_gold_data = pd.DataFrame({
            '<DATE>': ['2024-01-01', '2024-01-01', '2024-01-01'],
            '<TIME>': ['00:00', '01:00', '02:00'],
            '<OPEN>': [1900.0, 1905.0, 1910.0],
            '<HIGH>': [1910.0, 1915.0, 1920.0],
            '<LOW>': [1895.0, 1900.0, 1905.0],
            '<CLOSE>': [1905.0, 1910.0, 1915.0],
            '<TICKVOL>': [1000, 1200, 800],
            '<VOL>': [1000000, 1200000, 800000],
            '<SPREAD>': [0.5, 0.6, 0.4]
        })
        
        sample_gold_data.to_csv(self.temp_dir / 'test_gold.csv', sep='\t', index=False)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_repository_with_real_data(self):
        """Test repository with actual data files"""
        # This would test with real data files if available
        # For now, we'll test the structure
        data_manager = DataAccessManager(self.temp_dir)
        repository = GoldDataRepository(data_manager)
        
        # Test available timeframes
        timeframes = repository.get_available_timeframes()
        self.assertIsInstance(timeframes, list)

class TestRepositoryPerformance(unittest.TestCase):
    """Performance tests for repository operations"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.mock_data_manager = Mock(spec=DataAccessManager)
        self.repository = GoldDataRepository(self.mock_data_manager)
        
        # Create large dataset for performance testing
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='H')
        self.large_dataset = pd.DataFrame({
            'open': [1900.0] * len(dates),
            'high': [1910.0] * len(dates),
            'low': [1895.0] * len(dates),
            'close': [1905.0] * len(dates),
            'tick_volume': [1000] * len(dates)
        }, index=dates)
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        import time
        
        self.mock_data_manager.load_gold_data.return_value = self.large_dataset
        
        start_time = time.time()
        
        # Test multiple operations
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds)
        self.assertLess(execution_time, 5.0)
        self.assertIsNotNone(result)
    
    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        self.mock_data_manager.load_gold_data.return_value = self.large_dataset
        
        # Perform multiple operations
        for i in range(10):
            start_date = datetime(2023, i, 1)
            end_date = datetime(2023, i, 28)
            self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100)

class TestRepositoryErrorHandling(unittest.TestCase):
    """Test error handling in repository operations"""
    
    def setUp(self):
        """Set up error handling test fixtures"""
        self.mock_data_manager = Mock(spec=DataAccessManager)
        self.repository = GoldDataRepository(self.mock_data_manager)
    
    def test_data_manager_exception_handling(self):
        """Test handling of data manager exceptions"""
        self.mock_data_manager.load_gold_data.side_effect = Exception("Data loading failed")
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        result = self.repository.get_data_by_timerange(start_date, end_date, 'H1')
        
        self.assertIsNone(result)
    
    def test_invalid_dataframe_handling(self):
        """Test handling of invalid dataframes"""
        # Empty dataframe
        self.mock_data_manager.load_gold_data.return_value = pd.DataFrame()
        
        result = self.repository.get_data_summary('H1')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted data"""
        # Data with NaN values
        corrupted_data = pd.DataFrame({
            'open': [1900.0, None, 1910.0],
            'high': [1910.0, 1915.0, None],
            'low': [1895.0, 1900.0, 1905.0],
            'close': [1905.0, 1910.0, 1915.0],
            'tick_volume': [1000, 1200, 800]
        })
        
        self.mock_data_manager.load_gold_data.return_value = corrupted_data
        
        validation = self.repository.validate_data_quality('H1')
        
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)

# Test runner
if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestGoldDataRepository))
    test_suite.addTest(unittest.makeSuite(TestMarketDataRepository))
    test_suite.addTest(unittest.makeSuite(TestRepositoryFactory))
    test_suite.addTest(unittest.makeSuite(TestRepositoryIntegration))
    test_suite.addTest(unittest.makeSuite(TestRepositoryPerformance))
    test_suite.addTest(unittest.makeSuite(TestRepositoryErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
