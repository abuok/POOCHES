#!/usr/bin/env python3
"""
TRADING SYSTEM CONSTANTS
Centralized configuration for magic numbers and trading parameters
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TradingParameters:
    """Trading system parameters and constants"""
    
    # Timeframe configurations
    TIMEFRAMES = {
        'M1': '1m',
        'M5': '5m', 
        'M15': '15m',
        'M30': '30m',
        'H1': '1h',
        'H4': '4h',
        'D1': '1d'
    }
    
    # RSI parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT_LONG = 68
    RSI_OVERSOLD_LONG = 30
    RSI_OVERBOUGHT_SHORT = 70
    RSI_OVERSOLD_SHORT = 32
    RSI_CROSS_LONG_THRESHOLD = 48
    RSI_CROSS_SHORT_THRESHOLD = 52
    RSI_REVERSAL_OVERBOUGHT = 65
    RSI_REVERSAL_OVERSOLD = 35
    
    # EMA parameters
    EMA_SHORT_PERIOD = 8
    EMA_MEDIUM_PERIOD = 20
    EMA_LONG_PERIOD = 50
    EMA_TREND_PERIOD = 200
    EMA_REVERSAL_PERIOD = 21
    
    # Volume parameters
    VOLUME_SPIKE_MULTIPLIER = 1.3
    VOLUME_REVERSAL_MULTIPLIER = 1.5
    VOLUME_MA_PERIOD = 20
    
    # ATR parameters
    ATR_PERIOD = 14
    ATR_STOP_LOSS_MULTIPLIER = 2.0
    ATR_TAKE_PROFIT_MULTIPLIER = 3.0
    
    # Session parameters
    ASIAN_SESSION_START = 0
    ASIAN_SESSION_END = 7
    LONDON_SESSION_START = 7
    LONDON_SESSION_END = 12
    NY_SESSION_START = 12
    NY_SESSION_END = 17
    NY_EVENING_SESSION_START = 17
    NY_EVENING_SESSION_END = 22
    ASIAN_LATE_SESSION_START = 22
    ASIAN_LATE_SESSION_END = 24
    
    # Market structure parameters
    SWING_POINT_PERIOD = 11
    SWING_POINT_CENTER = 5
    BOS_BREAKDOWN_CONFIRMATION = 0.6
    BOS_BREAKOUT_CONFIRMATION = 0.6
    
    # Risk management parameters
    MAX_RISK_PER_TRADE = 0.02  # 2%
    MAX_DAILY_RISK = 0.05  # 5%
    MIN_RISK_REWARD_RATIO = 1.5
    MAX_OPEN_POSITIONS = 3
    
    # Backtesting parameters
    TRAIN_TEST_SPLIT = 0.7
    WALK_FORWARD_WINDOWS = 5
    MONTE_CARLO_SIMULATIONS = 1000
    
    # Data quality parameters
    MAX_PRICE_CHANGE_PERCENT = 0.10  # 10%
    MIN_DATA_POINTS = 100
    MAX_MISSING_DATA_PERCENT = 0.05  # 5%
    
    # Performance parameters
    CACHE_EXPIRY_MINUTES = 60
    MAX_CONCURRENT_REQUESTS = 10
    TIMEOUT_SECONDS = 30
    
    # UI parameters
    CONDITION_GRID_COLUMNS = 4
    MAX_CONDITIONS_PER_STRATEGY = 10
    REFRESH_INTERVAL_MS = 1000
    ANIMATION_DURATION_MS = 300

class SessionConfig:
    """Trading session configurations"""
    
    SESSIONS = {
        'Asian': {
            'start': TradingParameters.ASIAN_SESSION_START,
            'end': TradingParameters.LONDON_SESSION_START,
            'color': '#4d9de0'
        },
        'London': {
            'start': TradingParameters.LONDON_SESSION_START,
            'end': TradingParameters.NY_SESSION_START,
            'color': '#00c97a'
        },
        'NY': {
            'start': TradingParameters.NY_SESSION_START,
            'end': TradingParameters.NY_EVENING_SESSION_START,
            'color': '#f59e0b'
        },
        'NY_Evening': {
            'start': TradingParameters.NY_EVENING_SESSION_START,
            'end': TradingParameters.ASIAN_LATE_SESSION_START,
            'color': '#ff4d4d'
        },
        'Asian_Late': {
            'start': TradingParameters.ASIAN_LATE_SESSION_START,
            'end': 24,
            'color': '#d4a017'
        }
    }
    
    @classmethod
    def get_session(cls, hour: int) -> str:
        """Get session name for given hour"""
        for session_name, session_data in cls.SESSIONS.items():
            if session_data['start'] <= hour < session_data['end']:
                return session_name
        return 'Asian_Late'

class StrategyConfig:
    """Strategy configuration parameters"""
    
    STRATEGIES = {
        'scanner_8_condition': {
            'name': '8-Condition Technical Strategy',
            'timeframe': 'H1/M15',
            'direction': 'trend_following',
            'win_rate': 67.8,
            'avg_return': 1.85,
            'conditions_count': 8
        },
        'bos_reversal': {
            'name': 'BOS Reversal Strategy',
            'timeframe': 'H1',
            'direction': 'counter_trend',
            'win_rate': 63.3,
            'avg_return': 0.29,
            'conditions_count': 5
        },
        'session_volatility': {
            'name': 'Session Volatility Breakout',
            'timeframe': 'H1',
            'direction': 'trend_following',
            'win_rate': 45.0,
            'avg_return': 1.2,
            'conditions_count': 6
        },
        'liquidity_sweep': {
            'name': 'Liquidity Sweep Strategy',
            'timeframe': 'M15',
            'direction': 'counter_trend',
            'win_rate': 58.0,
            'avg_return': 1.1,
            'conditions_count': 7
        }
    }
    
    @classmethod
    def get_strategy(cls, strategy_id: str) -> Dict[str, Any]:
        """Get strategy configuration by ID"""
        return cls.STRATEGIES.get(strategy_id, cls.STRATEGIES['scanner_8_condition'])

class DataConfig:
    """Data configuration parameters"""
    
    FILE_MAPPING = {
        'H1': 'GOLD_H1_201901020000_202605082300.csv',
        'H4': 'GOLD_H4_201901020000_202605082000.csv',
        'M15': 'GOLD_M15_202211300100_202605082345.csv',
        'M30': 'GOLD_M30_201901020000_202605082330.csv'
    }
    
    COLUMN_MAPPING = {
        '<OPEN>': 'open',
        '<HIGH>': 'high', 
        '<LOW>': 'low',
        '<CLOSE>': 'close',
        '<TICKVOL>': 'tick_volume',
        '<VOL>': 'volume',
        '<SPREAD>': 'spread'
    }
    
    REQUIRED_COLUMNS = list(COLUMN_MAPPING.keys())
    
    DXY_FILES = [
        f'Download Data - INDEX_US_IFUS_DXY{i}.csv' 
        for i in range(1, 8)
    ] + ['Download Data - INDEX_US_IFUS_DXY.csv']
    
    US10Y_FILE = 'DGS10.csv'

# Global constants instance
TRADING_PARAMS = TradingParameters()
SESSION_CONFIG = SessionConfig()
STRATEGY_CONFIG = StrategyConfig()
DATA_CONFIG = DataConfig()

# Validation functions
def validate_rsi_parameters() -> bool:
    """Validate RSI parameter consistency"""
    return (
        0 < TradingParameters.RSI_PERIOD <= 100 and
        0 < TradingParameters.RSI_OVERBOUGHT_LONG <= 100 and
        0 < TradingParameters.RSI_OVERSOLD_LONG <= 100 and
        TradingParameters.RSI_OVERSOLD_LONG < TradingParameters.RSI_OVERBOUGHT_LONG
    )

def validate_risk_parameters() -> bool:
    """Validate risk management parameters"""
    return (
        0 < TradingParameters.MAX_RISK_PER_TRADE <= 0.1 and
        0 < TradingParameters.MAX_DAILY_RISK <= 0.2 and
        TradingParameters.MAX_DAILY_RISK > TradingParameters.MAX_RISK_PER_TRADE and
        TradingParameters.MIN_RISK_REWARD_RATIO > 1.0
    )

if __name__ == "__main__":
    # Validate all parameters
    print("Trading Constants Validation")
    print("=" * 50)
    
    print(f"RSI Parameters Valid: {validate_rsi_parameters()}")
    print(f"Risk Parameters Valid: {validate_risk_parameters()}")
    
    print("\nAvailable Strategies:")
    for strategy_id, config in STRATEGY_CONFIG.STRATEGIES.items():
        print(f"  {strategy_id}: {config['name']} ({config['win_rate']}% WR)")
    
    print("\nAvailable Sessions:")
    for session_name, session_data in SESSION_CONFIG.SESSIONS.items():
        print(f"  {session_name}: {session_data['start']}-{session_data['end']}")
