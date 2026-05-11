/**
 * Statistics Module Tests (Phase 1 TypeScript Migration)
 * 
 * Tests the migrated statistics functions from HTML
 */

import {
  calculatePnL,
  calculateR,
  getTradingStatistics,
  getEnhancedStatistics,
  formatStatistics,
  calculateTotalPnL,
  calculateTodayPnL,
  getTodayTrades,
  getTodayString,
  TradingStatistics
} from '../src/utils/statistics';
import { TradeEntry } from '../types/trading';

describe('Statistics Module - Phase 1 Migration', () => {
  
  // Mock trades matching the HTML format
  const mockTrades: TradeEntry[] = [
    {
      id: '1',
      direction: 'LONG',
      entryPrice: 1950.00,
      exitPrice: 1960.00,  // +$10
      sl: 1940.00,
      tp: 1970.00,
      size: 0.1,
      date: getTodayString(),
      status: 'closed',
      pnl: 100,  // (1960-1950) * 0.1 * 100 = $100
    },
    {
      id: '2',
      direction: 'LONG',
      entryPrice: 1970.00,
      exitPrice: 1960.00,  // -$10
      sl: 1980.00,
      tp: 1980.00,
      size: 0.1,
      date: getTodayString(),
      status: 'closed',
      pnl: -100,  // (1960-1970) * 0.1 * 100 = -$100
    },
    {
      id: '3',
      direction: 'SHORT',
      entryPrice: 1980.00,
      exitPrice: 1960.00,  // SHORT: +$20
      sl: 1990.00,
      tp: 1960.00,
      size: 0.1,
      date: getTodayString(),
      status: 'closed',
      pnl: 200,  // (1980-1960) * 0.1 * 100 = $200
    },
    {
      id: '4',
      direction: 'LONG',
      entryPrice: 1950.00,
      exitPrice: 1940.00,  // -$10
      sl: 1940.00,
      tp: 1970.00,
      size: 0.1,
      date: '2020-01-01',  // OLD DATE - not today
      status: 'closed',
      pnl: -100,
    },
    {
      id: '5',
      direction: 'LONG',
      entryPrice: 1955.00,
      exitPrice: 1965.00,  // +$10
      sl: 1945.00,
      tp: 1975.00,
      size: 0.1,
      date: getTodayString(),
      status: 'closed',
      pnl: 100,
    },
  ];

  describe('calculatePnL()', () => {
    it('should calculate LONG trade PnL correctly', () => {
      const trade: TradeEntry = {
        id: 'test-1',
        direction: 'LONG',
        entryPrice: 1950,
        exitPrice: 1960,
        sl: 1940,
        tp: 1970,
        size: 0.1,
        date: getTodayString(),
        status: 'closed',
      };
      
      const pnl = calculatePnL(trade);
      expect(pnl).toBeCloseTo(100, 2); // (1960-1950) * 0.1 * 100 = $100
    });

    it('should calculate SHORT trade PnL correctly', () => {
      const trade: TradeEntry = {
        id: 'test-2',
        direction: 'SHORT',
        entryPrice: 1980,
        exitPrice: 1960,
        sl: 1990,
        tp: 1940,
        size: 0.1,
        date: getTodayString(),
        status: 'closed',
      };
      
      const pnl = calculatePnL(trade);
      expect(pnl).toBeCloseTo(200, 2); // (1980-1960) * 0.1 * 100 = $200
    });

    it('should return 0 for missing data', () => {
      const trade: TradeEntry = {
        id: 'test-3',
        direction: 'LONG',
        entryPrice: 0,
        exitPrice: 0,
        sl: 0,
        tp: 0,
        size: 0,
        date: getTodayString(),
        status: 'open',
      };
      
      expect(calculatePnL(trade)).toBe(0);
    });

    it('should handle old format (entry/exit/lots)', () => {
      const oldFormatTrade = {
        id: 'old-1',
        direction: 'LONG' as const,
        entry: 1950,
        exit: 1960,
        lots: 0.1,
        sl: 1940,
        tp: 1970,
        date: getTodayString(),
        status: 'closed' as const,
      };
      
      // @ts-ignore - testing old format compatibility
      const pnl = calculatePnL(oldFormatTrade);
      expect(pnl).toBeCloseTo(100, 2);
    });
  });

  describe('calculateR()', () => {
    it('should calculate R-multiple correctly', () => {
      const trade: TradeEntry = {
        id: 'test-r',
        direction: 'LONG',
        entryPrice: 1950,
        exitPrice: 1970,  // +$20
        sl: 1940,         // risk = $10
        tp: 1980,
        size: 0.1,
        date: getTodayString(),
        status: 'closed',
      };
      
      // Account $10,000, risk 1% = $100 risk
      // PnL = $200, R = 200/100 = 2R
      const r = calculateR(trade, 10000, 1);
      expect(r).toBeCloseTo(2, 2);
    });

    it('should return 0 when risk amount is 0', () => {
      const trade = mockTrades[0];
      const r = calculateR(trade, 0, 1);
      expect(r).toBe(0);
    });
  });

  describe('getTodayTrades()', () => {
    it('should filter only today\'s trades', () => {
      const todayTrades = getTodayTrades(mockTrades);
      
      // Should return trades with today's date (4 trades)
      expect(todayTrades).toHaveLength(4);
      expect(todayTrades.every(t => t.date === getTodayString())).toBe(true);
    });

    it('should return empty array for no trades today', () => {
      const oldTrades = mockTrades.filter(t => t.date !== getTodayString()); // Only trade #4
      expect(getTodayTrades(oldTrades)).toHaveLength(0); // None are from today
    });
  });

  describe('calculateTotalPnL()', () => {
    it('should sum all trade PnLs', () => {
      const total = calculateTotalPnL(mockTrades);
      // 100 + (-100) + 200 + (-100) + 100 = 200
      expect(total).toBeCloseTo(200, 2);
    });

    it('should return 0 for empty array', () => {
      expect(calculateTotalPnL([])).toBe(0);
    });
  });

  describe('calculateTodayPnL()', () => {
    it('should calculate only today\'s PnL', () => {
      const todayPnl = calculateTodayPnL(mockTrades);
      // Today's trades: 100 + (-100) + 200 + 100 = 300
      // (excluding trade #4 which is old)
      expect(todayPnl).toBeCloseTo(300, 2);
    });
  });

  describe('getTradingStatistics()', () => {
    it('should return zeroed stats for empty trades', () => {
      const stats = getTradingStatistics([]);
      
      expect(stats).toEqual({
        totalTrades: 0,
        wins: 0,
        losses: 0,
        winRate: 0,
        avgR: 0,
        totalPnL: 0,
        bestTrade: 0,
        worstTrade: 0,
        consecutiveWins: 0,
        consecutiveLosses: 0,
      });
    });

    it('should calculate correct statistics', () => {
      const stats = getTradingStatistics(mockTrades);
      
      expect(stats.totalTrades).toBe(5);
      expect(stats.wins).toBe(3);  // trades 1, 3, 5
      expect(stats.losses).toBe(2); // trades 2, 4
      expect(stats.winRate).toBeCloseTo(60, 2); // 3/5 = 60%
      expect(stats.totalPnL).toBeCloseTo(200, 2);
      expect(stats.bestTrade).toBeCloseTo(200, 2); // trade 3
      expect(stats.worstTrade).toBeCloseTo(-100, 2); // trades 2, 4
    });

    it('should track consecutive wins/losses', () => {
      const streakTrades: TradeEntry[] = [
        { id: 's1', direction: 'LONG', entryPrice: 1950, exitPrice: 1960, sl: 1940, tp: 1970, size: 0.1, date: getTodayString(), status: 'closed', pnl: 100 }, // WIN
        { id: 's2', direction: 'LONG', entryPrice: 1960, exitPrice: 1970, sl: 1950, tp: 1980, size: 0.1, date: getTodayString(), status: 'closed', pnl: 100 }, // WIN (2 streak)
        { id: 's3', direction: 'LONG', entryPrice: 1970, exitPrice: 1960, sl: 1980, tp: 1990, size: 0.1, date: getTodayString(), status: 'closed', pnl: -100 }, // LOSS
        { id: 's4', direction: 'SHORT', entryPrice: 1980, exitPrice: 1990, sl: 1990, tp: 1970, size: 0.1, date: getTodayString(), status: 'closed', pnl: -100 }, // LOSS (2 streak)
        { id: 's5', direction: 'LONG', entryPrice: 1990, exitPrice: 2000, sl: 1980, tp: 2010, size: 0.1, date: getTodayString(), status: 'closed', pnl: 100 }, // WIN
      ];
      
      const stats = getTradingStatistics(streakTrades);
      expect(stats.consecutiveWins).toBe(2); // s1, s2
      expect(stats.consecutiveLosses).toBe(2); // s3, s4
    });
  });

  describe('getEnhancedStatistics()', () => {
    it('should calculate R-multiples when account balance provided', () => {
      const stats = getEnhancedStatistics(mockTrades, 10000, 1);
      
      expect(stats.avgR).toBeDefined();
      expect(stats.profitFactor).toBeDefined();
      expect(stats.expectancy).toBeDefined();
      
      // Profit factor: wins / |losses| = 400 / 200 = 2
      expect(stats.profitFactor).toBeCloseTo(2, 1);
    });

    it('should handle infinity profit factor (no losses)', () => {
      const winOnlyTrades = mockTrades.filter(t => (t.pnl || 0) > 0);
      const stats = getEnhancedStatistics(winOnlyTrades, 10000, 1);
      
      expect(stats.profitFactor).toBe(Infinity);
    });
  });

  describe('formatStatistics()', () => {
    it('should format all values for display', () => {
      const stats: TradingStatistics = {
        totalTrades: 50,
        wins: 30,
        losses: 20,
        winRate: 60.0,
        avgR: 1.85,
        totalPnL: 2500.50,
        bestTrade: 500.00,
        worstTrade: -200.00,
        consecutiveWins: 5,
        consecutiveLosses: 3,
        profitFactor: 2.5,
        expectancy: 100.00,
      };
      
      const formatted = formatStatistics(stats, '$');
      
      expect(formatted.totalTrades).toBe('50');
      expect(formatted.winRate).toBe('60.0%');
      expect(formatted.avgR).toBe('1.85R');
      expect(formatted.totalPnL).toBe('$2500.50');
      expect(formatted.profitFactor).toBe('2.50');
    });
  });

  describe('Backward Compatibility with HTML', () => {
    it('should match vanilla JS getStats() output format', () => {
      // Simulate the old HTML getStats() return structure
      const oldFormatStats = {
        tot: 5,
        wins: 3,
        losses: 2,
        wr: 60,
        avgR: expect.any(Number),
        totPnl: 200,
        best: 200,
        worst: -100,
        cw: expect.any(Number),
        cl: expect.any(Number),
      };
      
      const newStats = getTradingStatistics(mockTrades);
      
      // Map new format to old format
      const mapped = {
        tot: newStats.totalTrades,
        wins: newStats.wins,
        losses: newStats.losses,
        wr: newStats.winRate,
        avgR: newStats.avgR,
        totPnl: newStats.totalPnL,
        best: newStats.bestTrade,
        worst: newStats.worstTrade,
        cw: newStats.consecutiveWins,
        cl: newStats.consecutiveLosses,
      };
      
      expect(mapped).toMatchObject(oldFormatStats);
    });
  });
});
