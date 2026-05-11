#!/usr/bin/env python3
"""
COMPREHENSIVE GOLD MARKET ANALYSIS
Institutional-grade quantitative research for XAUUSD trading strategies

PHASE 1-8: Complete market microstructure analysis and strategy discovery
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up professional plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class GoldMarketAnalyzer:
    """
    Comprehensive gold market analysis framework
    """
    
    def __init__(self):
        self.data = {}
        self.analysis_results = {}
        self.strategies = {}
        
    def load_and_audit_data(self):
        """PHASE 1: Data Audit - Load and validate all datasets"""
        print("=" * 80)
        print("PHASE 1: DATA AUDIT AND QUALITY ASSESSMENT")
        print("=" * 80)
        
        # Load Gold datasets
        gold_files = {
            'H1': 'GOLD_H1_201901020000_202605082300.csv',
            'H4': 'GOLD_H4_201901020000_202605082000.csv',
            'M15_2022': 'GOLD_M15_202202102030_202211301415.csv',
            'M15_recent': 'GOLD_M15_202211300100_202605082345.csv',
            'M30': 'GOLD_M30_201901020000_202605082330.csv'
        }
        
        # Load DXY datasets
        dxy_files = [f'Download Data - INDEX_US_IFUS_DXY{i}.csv' 
                    for i in range(1, 8)] + ['Download Data - INDEX_US_IFUS_DXY.csv']
        
        # Load US10Y yields
        bond_file = 'DGS10.csv'
        
        print("Loading datasets...")
        
        # Load Gold data
        for timeframe, file in gold_files.items():
            try:
                df = pd.read_csv(file, sep='\t')
                df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
                df.set_index('datetime', inplace=True)
                df.rename(columns={
                    '<OPEN>': 'open', '<HIGH>': 'high', '<LOW>': 'low', 
                    '<CLOSE>': 'close', '<TICKVOL>': 'tick_volume', 
                    '<VOL>': 'volume', '<SPREAD>': 'spread'
                }, inplace=True)
                
                # Convert to numeric
                price_cols = ['open', 'high', 'low', 'close']
                df[price_cols] = df[price_cols].astype(float)
                
                self.data[f'gold_{timeframe}'] = df
                print(f"✓ Gold {timeframe}: {len(df)} candles from {df.index[0]} to {df.index[-1]}")
                
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        # Load and combine DXY data
        dxy_data = []
        for file in dxy_files:
            try:
                df = pd.read_csv(file)
                df['datetime'] = pd.to_datetime(df['Date'])
                df.set_index('datetime', inplace=True)
                df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
                dxy_data.append(df)
            except:
                continue
        
        if dxy_data:
            dxy_combined = pd.concat(dxy_data).sort_index()
            self.data['dxy'] = dxy_combined
            print(f"✓ DXY: {len(dxy_combined)} candles from {dxy_combined.index[0]} to {dxy_combined.index[-1]}")
        
        # Load US10Y yields
        try:
            df = pd.read_csv(bond_file)
            df['datetime'] = pd.to_datetime(df['observation_date'])
            df.set_index('datetime', inplace=True)
            df.rename(columns={'DGS10': 'yield_10y'}, inplace=True)
            df['yield_10y'] = pd.to_numeric(df['yield_10y'], errors='coerce')
            self.data['us10y'] = df
            print(f"✓ US10Y: {len(df)} observations from {df.index[0]} to {df.index[-1]}")
        except Exception as e:
            print(f"✗ Error loading US10Y: {e}")
        
        return self.data
    
    def data_quality_report(self):
        """Generate comprehensive data quality assessment"""
        print("\n" + "=" * 80)
        print("DATA QUALITY REPORT")
        print("=" * 80)
        
        quality_report = {}
        
        for name, df in self.data.items():
            if 'gold' in name:
                # Gold data quality checks
                missing_candles = df.isnull().sum().sum()
                duplicate_candles = df.index.duplicated().sum()
                
                # Check for weekend data
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
    
    def _calculate_quality_score(self, df):
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
    
    def market_structure_analysis(self):
        """PHASE 2: Market Structure Analysis - Candle-by-candle pattern detection"""
        print("\n" + "=" * 80)
        print("PHASE 2: MARKET STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Focus on H1 data for primary analysis
        if 'gold_H1' not in self.data:
            print("H1 data not available for analysis")
            return
        
        df = self.data['gold_H1'].copy()
        
        # Calculate technical indicators
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
        
        # Analyze pattern statistics
        structure_stats = self._analyze_structure_patterns(df)
        
        self.analysis_results['market_structure'] = {
            'data': df,
            'statistics': structure_stats
        }
        
        return structure_stats
    
    def _detect_swing_points(self, df, window=5):
        """Detect swing highs and lows"""
        df['swing_high'] = df['high'].rolling(window*2+1, center=True).apply(
            lambda x: x[window] == x.max(), raw=False)
        df['swing_low'] = df['low'].rolling(window*2+1, center=True).apply(
            lambda x: x[window] == x.min(), raw=False)
        
        df['swing_high'] = df['swing_high'].fillna(False).astype(bool)
        df['swing_low'] = df['swing_low'].fillna(False).astype(bool)
        
        return df
    
    def _detect_bos_choch(self, df):
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
    
    def _detect_displacement_candles(self, df):
        """Detect displacement candles (strong momentum moves)"""
        df['displacement'] = ((df['body_ratio'] > 0.8) & 
                            (df['range'] > df['range'].rolling(20).mean() * 2) &
                            (df['tick_volume'] > df['volume_ma'] * 2))
        
        return df
    
    def _analyze_structure_patterns(self, df):
        """Analyze statistical properties of detected patterns"""
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
    
    def _analyze_follow_through(self, df, pattern, periods=5):
        """Analyze follow-through behavior after patterns"""
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
                'avg_return': np.mean(follow_data),
                'win_rate': np.mean(np.array(follow_data) > 0),
                'max_return': np.max(follow_data),
                'min_return': np.min(follow_data),
                'volatility': np.std(follow_data)
            }
        
        return {}
    
    def session_analysis(self):
        """PHASE 3: Session Analysis - Trading behavior by session"""
        print("\n" + "=" * 80)
        print("PHASE 3: SESSION ANALYSIS")
        print("=" * 80)
        
        if 'gold_H1' not in self.data:
            print("H1 data not available for session analysis")
            return
        
        df = self.data['gold_H1'].copy()
        
        # Calculate required columns if not already calculated
        if 'range' not in df.columns:
            df['range'] = df['high'] - df['low']
            df['body'] = abs(df['close'] - df['open'])
            df['volume_ma'] = df['tick_volume'].rolling(20).mean()
            
            # Recalculate patterns if needed
            if 'displacement' not in df.columns:
                df = self._detect_displacement_candles(df)
            if 'liquidity_sweep_up' not in df.columns:
                df = self._detect_liquidity_sweeps(df)
        
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
                'displacement_freq': session_data['displacement'].mean() * 100 if 'displacement' in session_data.columns else 0,
                'liquidity_sweep_freq': ((session_data['liquidity_sweep_up'] | session_data['liquidity_sweep_down']).mean() * 100) if 'liquidity_sweep_up' in session_data.columns else 0
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
    
    def dxy_correlation_analysis(self):
        """PHASE 4: DXY Correlation Analysis"""
        print("\n" + "=" * 80)
        print("PHASE 4: DXY CORRELATION ANALYSIS")
        print("=" * 80)
        
        if 'gold_H1' not in self.data or 'dxy' not in self.data:
            print("Required data not available for correlation analysis")
            return
        
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
        correlation = combined['gold_returns'].corr(combined['dxy_returns'])
        
        # Rolling correlation
        rolling_corr = combined['gold_returns'].rolling(50).corr(combined['dxy_returns'])
        
        # Session-based correlation
        combined['hour'] = combined.index.hour
        session_correlations = {}
        
        for hour in range(24):
            hour_data = combined[combined['hour'] == hour]
            if len(hour_data) > 50:
                session_correlations[hour] = hour_data['gold_returns'].corr(hour_data['dxy_returns'])
        
        # Volatility regime analysis
        gold_vol = combined['gold_returns'].rolling(20).std()
        vol_regimes = pd.cut(gold_vol, bins=3, labels=['Low', 'Medium', 'High'])
        
        regime_correlations = {}
        for regime in vol_regimes.cat.categories:
            regime_data = combined[vol_regimes == regime]
            if len(regime_data) > 50:
                regime_correlations[regime] = regime_data['gold_returns'].corr(regime_data['dxy_returns'])
        
        # Lag analysis
        lag_correlations = {}
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
            print(f"  Lag {lag:+d}: {corr:.3f}")
        
        return correlation_results
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ANALYSIS REPORT GENERATION")
        print("=" * 80)
        
        report = {
            'data_quality': self.analysis_results.get('data_quality', {}),
            'market_structure': self.analysis_results.get('market_structure', {}),
            'session_analysis': self.analysis_results.get('session_analysis', {}),
            'dxy_correlation': self.analysis_results.get('dxy_correlation', {}),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report

# Main execution
if __name__ == "__main__":
    analyzer = GoldMarketAnalyzer()
    
    # Phase 1: Data Audit
    analyzer.load_and_audit_data()
    analyzer.data_quality_report()
    
    # Phase 2: Market Structure Analysis
    analyzer.market_structure_analysis()
    
    # Phase 3: Session Analysis
    analyzer.session_analysis()
    
    # Phase 4: DXY Correlation Analysis
    analyzer.dxy_correlation_analysis()
    
    # Generate final report
    final_report = analyzer.generate_comprehensive_report()
    
    print("\n" + "=" * 80)
    print("INITIAL ANALYSIS COMPLETE")
    print("=" * 80)
    print("Next phases (5-8) will be implemented based on findings...")
