/**
 * Main TypeScript Entry Point
 * 
 * This file demonstrates how to use TypeScript in the project.
 * Import types and utilities from this file in your application code.
 */

// Export types (explicit to avoid conflicts)
export type {
  TradeEntry,
  TradeStatistics,
  TradeDirection,
  TradeStatus,
  TradingSession,
  ImpactLevel,
  AlertType,
  SessionStats,
  MarketData,
  IndicatorData,
  FeedStatus,
  Alert,
  EconomicEvent,
  DailyBriefing,
  RiskStatus,
  PropPhase,
} from '../types/trading';

export type {
  ChartConfig,
  ChartData,
  Dataset,
  ChartOptions,
  DashboardState,
  ScannerCondition,
  TradeTableProps,
  StatisticsCardProps,
  ChartComponentProps,
  AlertComponentProps,
  SessionTimerProps,
  Theme,
  ViewMode,
  TimeRange,
  TradeUpdateHandler,
  PriceUpdateHandler,
  AlertHandler,
  ApiResponse,
  DataUpdateEvent,
} from '../types/dashboard';

// Export utilities
export { StateManager, stateManager } from './utils/StateManager';

// Export statistics module (Phase 1 TypeScript migration)
export {
  calculatePnL,
  calculateR,
  getTodayTrades,
  calculateTotalPnL,
  calculateTodayPnL,
  getTradingStatistics,
  getEnhancedStatistics,
  formatStatistics,
  getTodayString,
  type TradingStatistics,
} from './utils/statistics';

// Version info
export const VERSION = '1.0.0';
export const TYPEScript_ENABLED = true;

/**
 * Example usage in your HTML/JavaScript:
 * 
 * ```html
 * <script type="module">
 *   import { StateManager, TradeEntry, Alert } from './dist/index.js';
 *   
 *   // Now you have full type safety!
 *   const manager = StateManager.getInstance();
 *   
 *   const newTrade: TradeEntry = {
 *     id: 'trade-001',
 *     direction: 'LONG',
 *     entryPrice: 1950.50,
 *     sl: 1940.00,
 *     tp: 1970.00,
 *     size: 0.1,
 *     date: new Date().toISOString().split('T')[0],
 *     status: 'open'
 *   };
 *   
 *   manager.addTrade(newTrade);
 * </script>
 * ```
 */

// Type guard helpers
export function isTradeEntry(obj: unknown): obj is import('../types/trading').TradeEntry {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'direction' in obj &&
    'entryPrice' in obj &&
    'status' in obj
  );
}

export function isValidPnL(pnl: number): boolean {
  return !isNaN(pnl) && isFinite(pnl);
}

// Utility functions with type safety
export function calculatePositionSize(
  accountBalance: number,
  riskPercent: number,
  stopLossPips: number,
  pipValue: number = 10
): number {
  const riskAmount = accountBalance * (riskPercent / 100);
  const positionSize = riskAmount / (stopLossPips * pipValue);
  return Math.round(positionSize * 100) / 100;
}

export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(value);
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}
