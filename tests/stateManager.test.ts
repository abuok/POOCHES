/**
 * Unit Tests for State Manager
 * Tests the centralized state management functionality
 */

import { StateManager } from '../src/utils/StateManager';
import { DashboardState, TradeEntry, Alert } from '../types/trading';

describe('StateManager', () => {
  let stateManager: StateManager;

  beforeEach(() => {
    stateManager = new StateManager();
    // Clear any persisted state
    localStorage.clear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with default state', () => {
      const state = stateManager.getState();
      
      expect(state).toBeDefined();
      expect(state.todayPnL).toBe(0);
      expect(state.todayTrades).toEqual([]);
      expect(state.alerts).toEqual([]);
    });

    test('should load persisted state from localStorage', () => {
      const persistedState: Partial<DashboardState> = {
        todayPnL: 150.50,
        totalTrades: 5,
      };
      
      localStorage.setItem('dashboardState', JSON.stringify(persistedState));
      
      const stateManager2 = new StateManager();
      const state = stateManager2.getState();
      
      expect(state.todayPnL).toBe(150.50);
    });
  });

  describe('Trade Management', () => {
    const mockTrade: TradeEntry = {
      id: 'trade-001',
      direction: 'LONG',
      entryPrice: 1950.50,
      sl: 1940.00,
      tp: 1970.00,
      size: 0.1,
      date: '2024-01-15',
      status: 'open',
    };

    test('should add a new trade', () => {
      stateManager.addTrade(mockTrade);
      
      const state = stateManager.getState();
      expect(state.todayTrades).toHaveLength(1);
      expect(state.todayTrades[0].id).toBe('trade-001');
    });

    test('should update existing trade', () => {
      stateManager.addTrade(mockTrade);
      
      const updatedTrade = {
        ...mockTrade,
        status: 'closed' as const,
        exitPrice: 1965.00,
        pnl: 145.00,
      };
      
      stateManager.updateTrade(updatedTrade);
      
      const state = stateManager.getState();
      expect(state.todayTrades[0].status).toBe('closed');
      expect(state.todayTrades[0].pnl).toBe(145.00);
    });

    test('should calculate PnL correctly when closing trade', () => {
      stateManager.addTrade(mockTrade);
      stateManager.closeTrade('trade-001', 1965.00);
      
      const state = stateManager.getState();
      const closedTrade = state.todayTrades.find(t => t.id === 'trade-001');
      
      expect(closedTrade?.pnl).toBeCloseTo(145.00, 2);
      expect(closedTrade?.status).toBe('closed');
    });

    test('should throw error when closing non-existent trade', () => {
      expect(() => {
        stateManager.closeTrade('non-existent', 1965.00);
      }).toThrow('Trade not found');
    });
  });

  describe('Alert Management', () => {
    const mockAlert: Alert = {
      type: 'warning',
      message: 'Daily loss limit approaching',
      timestamp: new Date(),
      category: 'risk',
    };

    test('should add alert', () => {
      stateManager.addAlert(mockAlert);
      
      const state = stateManager.getState();
      expect(state.alerts).toHaveLength(1);
      expect(state.alerts[0].message).toBe('Daily loss limit approaching');
    });

    test('should dismiss alert', () => {
      stateManager.addAlert({ ...mockAlert, type: 'info' });
      stateManager.dismissAlert(0);
      
      const state = stateManager.getState();
      expect(state.alerts).toHaveLength(0);
    });

    test('should limit maximum alerts to prevent memory issues', () => {
      // Add more than 50 alerts
      for (let i = 0; i < 55; i++) {
        stateManager.addAlert({
          type: 'info',
          message: `Alert ${i}`,
          timestamp: new Date(),
        });
      }
      
      const state = stateManager.getState();
      expect(state.alerts.length).toBeLessThanOrEqual(50);
    });
  });

  describe('Statistics Calculation', () => {
    const mockTrades: TradeEntry[] = [
      { id: '1', direction: 'LONG', entryPrice: 1950, exitPrice: 1960, sl: 1940, tp: 1980, size: 0.1, date: '2024-01-01', status: 'closed', pnl: 100 },
      { id: '2', direction: 'SHORT', entryPrice: 1970, exitPrice: 1960, sl: 1980, tp: 1950, size: 0.1, date: '2024-01-02', status: 'closed', pnl: 100 },
      { id: '3', direction: 'LONG', entryPrice: 1955, exitPrice: 1945, sl: 1940, tp: 1970, size: 0.1, date: '2024-01-03', status: 'closed', pnl: -100 },
    ];

    test('should calculate win rate correctly', () => {
      mockTrades.forEach(trade => stateManager.addTrade(trade));
      
      const stats = stateManager.calculateStatistics();
      
      expect(stats.totalTrades).toBe(3);
      expect(stats.winRate).toBeCloseTo(66.67, 2);
    });

    test('should calculate profit factor correctly', () => {
      mockTrades.forEach(trade => stateManager.addTrade(trade));
      
      const stats = stateManager.calculateStatistics();
      
      expect(stats.profitFactor).toBe(2); // 200 / 100
    });

    test('should calculate expectancy correctly', () => {
      mockTrades.forEach(trade => stateManager.addTrade(trade));
      
      const stats = stateManager.calculateStatistics();
      
      // (WinRate * AvgWin) - (LossRate * AvgLoss)
      // (0.667 * 100) - (0.333 * 100) = 33.33
      expect(stats.expectancy).toBeCloseTo(33.33, 2);
    });
  });

  describe('Persistence', () => {
    test('should save state to localStorage', () => {
      const mockTrade: TradeEntry = {
        id: 'persist-test',
        direction: 'LONG',
        entryPrice: 1950,
        sl: 1940,
        tp: 1970,
        size: 0.1,
        date: '2024-01-15',
        status: 'open',
      };
      
      stateManager.addTrade(mockTrade);
      stateManager.saveState();
      
      expect(localStorage.setItem).toHaveBeenCalled();
      const savedData = (localStorage.setItem as jest.Mock).mock.calls[0][1];
      const parsed = JSON.parse(savedData);
      expect(parsed.todayTrades).toHaveLength(1);
    });
  });
});
