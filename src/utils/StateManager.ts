/**
 * StateManager - Centralized State Management for Trading Dashboard
 * Implements singleton pattern for global state management
 * Provides type-safe state updates and persistence
 */

import { 
  TradeEntry, 
  TradeStatistics, 
  Alert, 
  FeedStatus,
  RiskStatus 
} from '../../types/trading';
import { DashboardState } from '../../types/dashboard';

export class StateManager {
  private static instance: StateManager;
  private state: DashboardState;
  private listeners: Set<(state: DashboardState) => void>;
  private readonly STORAGE_KEY = 'dashboardState';
  private readonly MAX_ALERTS = 50;

  private constructor() {
    this.listeners = new Set();
    this.state = this.loadInitialState();
  }

  public static getInstance(): StateManager {
    if (!StateManager.instance) {
      StateManager.instance = new StateManager();
    }
    return StateManager.instance;
  }

  private loadInitialState(): DashboardState {
    try {
      const persisted = localStorage.getItem(this.STORAGE_KEY);
      if (persisted) {
        const parsed = JSON.parse(persisted);
        return {
          ...this.getDefaultState(),
          ...parsed,
          todayTrades: parsed.todayTrades || [],
          alerts: parsed.alerts || [],
        };
      }
    } catch (error) {
      console.error('Failed to load persisted state:', error);
    }
    return this.getDefaultState();
  }

  private getDefaultState(): DashboardState {
    return {
      currentSession: 'Asian',
      isWeekend: false,
      feedStatus: {
        connected: false,
        symbol: 'XAUUSD',
        price: 0,
        change: 0,
        changePercent: 0,
        lastUpdate: new Date(),
      },
      riskStatus: {
        level: 'safe',
        message: 'Risk parameters within limits',
      },
      todayPnL: 0,
      todayTrades: [],
      weeklyStats: this.getDefaultStats(),
      monthlyStats: this.getDefaultStats(),
      allTimeStats: this.getDefaultStats(),
      alerts: [],
      scannerConditions: [],
      economicEvents: [],
      activeTrades: [],
      closedTrades: [],
    };
  }

  private getDefaultStats(): TradeStatistics {
    return {
      totalTrades: 0,
      wins: 0,
      losses: 0,
      winRate: 0,
      avgWin: 0,
      avgLoss: 0,
      profitFactor: 0,
      expectancy: 0,
      avgR: 0,
      maxDD: 0,
      totalPnL: 0,
    };
  }

  public getState(): DashboardState {
    return { ...this.state };
  }

  public setState(partialState: Partial<DashboardState>): void {
    this.state = { ...this.state, ...partialState };
    this.notifyListeners();
    this.saveState();
  }

  public addTrade(trade: TradeEntry): void {
    this.state.todayTrades.push(trade);
    this.calculateTodayPnL();
    this.notifyListeners();
    this.saveState();
  }

  public updateTrade(updatedTrade: TradeEntry): void {
    const index = this.state.todayTrades.findIndex((t: TradeEntry) => t.id === updatedTrade.id);
    if (index >= 0) {
      this.state.todayTrades[index] = updatedTrade;
      this.calculateTodayPnL();
      this.notifyListeners();
      this.saveState();
    }
  }

  public closeTrade(tradeId: string, exitPrice: number): void {
    const trade = this.state.todayTrades.find((t: TradeEntry) => t.id === tradeId);
    if (!trade) {
      throw new Error(`Trade not found: ${tradeId}`);
    }

    const pnl = trade.direction === 'LONG' 
      ? (exitPrice - trade.entryPrice) * trade.size * 100
      : (trade.entryPrice - exitPrice) * trade.size * 100;

    this.updateTrade({
      ...trade,
      exitPrice,
      pnl,
      status: 'closed',
    });
  }

  public addAlert(alert: Alert): void {
    this.state.alerts.unshift(alert);
    if (this.state.alerts.length > this.MAX_ALERTS) {
      this.state.alerts = this.state.alerts.slice(0, this.MAX_ALERTS);
    }
    this.notifyListeners();
    this.saveState();
  }

  public dismissAlert(index: number): void {
    this.state.alerts.splice(index, 1);
    this.notifyListeners();
    this.saveState();
  }

  public removeTrade(tradeId: string): void {
    const index = this.state.todayTrades.findIndex((t: TradeEntry) => t.id === tradeId);
    if (index >= 0) {
      this.state.todayTrades.splice(index, 1);
      this.calculateTodayPnL();
      this.notifyListeners();
      this.saveState();
    }
  }

  public updateFeedStatus(feedStatus: FeedStatus): void {
    this.state.feedStatus = feedStatus;
    this.notifyListeners();
  }

  public updateRiskStatus(riskStatus: RiskStatus): void {
    this.state.riskStatus = riskStatus;
    this.notifyListeners();
    this.saveState();
  }

  private calculateTodayPnL(): void {
    this.state.todayPnL = this.state.todayTrades.reduce((total: number, trade: TradeEntry) => {
      return total + (trade.pnl || 0);
    }, 0);
  }

  public calculateStatistics(trades?: TradeEntry[]): TradeStatistics {
    const targetTrades = trades || this.state.todayTrades.filter((t: TradeEntry) => t.status === 'closed');
    
    if (targetTrades.length === 0) {
      return this.getDefaultStats();
    }

    const wins = targetTrades.filter((t: TradeEntry) => (t.pnl || 0) > 0);
    const losses = targetTrades.filter((t: TradeEntry) => (t.pnl || 0) < 0);
    
    const totalPnL = targetTrades.reduce((sum: number, t: TradeEntry) => sum + (t.pnl || 0), 0);
    const totalWins = wins.reduce((sum: number, t: TradeEntry) => sum + (t.pnl || 0), 0);
    const totalLosses = Math.abs(losses.reduce((sum: number, t: TradeEntry) => sum + (t.pnl || 0), 0));
    
    const winRate = targetTrades.length > 0 ? (wins.length / targetTrades.length) * 100 : 0;
    const avgWin = wins.length > 0 ? totalWins / wins.length : 0;
    const avgLoss = losses.length > 0 ? totalLosses / losses.length : 0;
    
    return {
      totalTrades: targetTrades.length,
      wins: wins.length,
      losses: losses.length,
      winRate: parseFloat(winRate.toFixed(2)),
      avgWin: parseFloat(avgWin.toFixed(2)),
      avgLoss: parseFloat(avgLoss.toFixed(2)),
      profitFactor: totalLosses > 0 ? parseFloat((totalWins / totalLosses).toFixed(2)) : totalWins > 0 ? Infinity : 0,
      expectancy: parseFloat(((winRate / 100) * avgWin - ((100 - winRate) / 100) * avgLoss).toFixed(2)),
      avgR: this.calculateAverageR(targetTrades),
      maxDD: this.calculateMaxDrawdown(targetTrades),
      totalPnL: parseFloat(totalPnL.toFixed(2)),
    };
  }

  private calculateAverageR(trades: TradeEntry[]): number {
    const tradesWithR = trades.filter((t: TradeEntry) => t.r !== undefined);
    if (tradesWithR.length === 0) return 0;
    const totalR = tradesWithR.reduce((sum: number, t: TradeEntry) => sum + (t.r || 0), 0);
    return parseFloat((totalR / tradesWithR.length).toFixed(2));
  }

  private calculateMaxDrawdown(trades: TradeEntry[]): number {
    if (trades.length === 0) return 0;
    let peak = 0;
    let maxDD = 0;
    let runningPnL = 0;
    
    for (const trade of trades) {
      runningPnL += trade.pnl || 0;
      if (runningPnL > peak) peak = runningPnL;
      const drawdown = peak - runningPnL;
      if (drawdown > maxDD) maxDD = drawdown;
    }
    return parseFloat(maxDD.toFixed(2));
  }

  public subscribe(listener: (state: DashboardState) => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(): void {
    const stateSnapshot = this.getState();
    this.listeners.forEach(listener => {
      try {
        listener(stateSnapshot);
      } catch (error) {
        console.error('Error in state listener:', error);
      }
    });
  }

  public saveState(): void {
    try {
      const stateToSave = {
        ...this.state,
        feedStatus: {
          ...this.state.feedStatus,
          lastUpdate: this.state.feedStatus.lastUpdate.toISOString(),
        },
        alerts: this.state.alerts.map((alert: Alert) => ({
          ...alert,
          timestamp: alert.timestamp.toISOString(),
        })),
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(stateToSave));
    } catch (error) {
      console.error('Failed to save state:', error);
    }
  }

  public resetState(): void {
    this.state = this.getDefaultState();
    localStorage.removeItem(this.STORAGE_KEY);
    this.notifyListeners();
  }

  // ═══════════════════════════════════════════════════════════════════
  // PHASE 4: LEGACY SYNC METHODS
  // Bridge between vanilla JS and TypeScript state
  // ═══════════════════════════════════════════════════════════════════

  /**
   * Sync legacy trades array from vanilla JS into TypeScript state
   * Called by loadAll() in HTML when loading from localStorage
   */
  public syncLegacyTrades(legacyTrades: any[]): void {
    if (!Array.isArray(legacyTrades)) return;
    
    const convertedTrades: TradeEntry[] = legacyTrades.map((t, index) => ({
      id: t.id || `legacy-${Date.now()}-${index}`,
      direction: t.dir || t.direction || 'LONG',
      entryPrice: parseFloat(t.entry) || 0,
      exitPrice: parseFloat(t.exit) || 0,
      sl: parseFloat(t.sl) || 0,
      tp: parseFloat(t.tp1 || t.tp) || 0,
      size: parseFloat(t.lots) || 0,
      date: t.date || new Date().toISOString().split('T')[0],
      status: t.exit ? 'closed' : 'open',
      pnl: parseFloat(t.pnl) || 0,
      r: parseFloat(t.r) || 0,
      session: t.session || 'London',
      setup: t.strategy || '',
      notes: t.notes || '',
    }));
    
    this.state.todayTrades = convertedTrades;
    this.calculateTodayPnL();
    this.notifyListeners();
    console.log('[TS] Synced', convertedTrades.length, 'legacy trades');
  }

  /**
   * Sync legacy settings (S object) from vanilla JS
   */
  public syncLegacySettings(settings: any): void {
    if (!settings) return;
    
    // Update feed status with settings
    this.state.feedStatus = {
      ...this.state.feedStatus,
      price: parseFloat(settings.price) || this.state.feedStatus.price,
    };
    
    // Update risk status
    if (settings.risk !== undefined) {
      const riskLevel = settings.risk > 5 ? 'danger' : 'safe';
      this.state.riskStatus = {
        level: riskLevel,
        message: `Risk: ${settings.risk}%`,
      };
    }
    
    this.notifyListeners();
    console.log('[TS] Synced legacy settings');
  }

  /**
   * Export TypeScript state in legacy format for vanilla JS
   * Called when HTML needs to access TypeScript-managed trades
   */
  public exportToLegacyFormat(): { trades: any[], settings: any } {
    const legacyTrades = this.state.todayTrades.map(t => ({
      id: t.id,
      date: t.date,
      dir: t.direction,
      entry: t.entryPrice,
      exit: t.exitPrice,
      sl: t.sl,
      tp1: t.tp,
      lots: t.size,
      pnl: t.pnl,
      r: t.r,
      status: t.status,
      session: t.session,
      strategy: t.setup,
      notes: t.notes,
    }));
    
    return {
      trades: legacyTrades,
      settings: {
        price: this.state.feedStatus.price,
        risk: this.state.riskStatus.level === 'danger' ? 8 : 2,
      }
    };
  }

  /**
   * Force TypeScript state to persist to localStorage
   * Called by saveAll() in HTML
   */
  public forcePersist(): void {
    this.saveState();
    console.log('[TS] State persisted via forcePersist');
  }

  /**
   * Load from TypeScript storage (different key than vanilla JS)
   * Returns true if data was loaded
   */
  public loadFromTSStorage(): boolean {
    const loaded = this.loadInitialState();
    const hasData = loaded.todayTrades.length > 0;
    if (hasData) {
      this.state = loaded;
      this.notifyListeners();
      console.log('[TS] Loaded', loaded.todayTrades.length, 'trades from TS storage');
    }
    return hasData;
  }
}

export const stateManager = StateManager.getInstance();
