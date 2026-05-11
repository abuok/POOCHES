/**
 * Main TypeScript Entry Point
 *
 * This file demonstrates how to use TypeScript in the project.
 * Import types and utilities from this file in your application code.
 */
export type { TradeEntry, TradeStatistics, TradeDirection, TradeStatus, TradingSession, ImpactLevel, AlertType, SessionStats, MarketData, IndicatorData, FeedStatus, Alert, EconomicEvent, DailyBriefing, RiskStatus, PropPhase, } from '../types/trading';
export type { ChartConfig, ChartData, Dataset, ChartOptions, DashboardState, ScannerCondition, TradeTableProps, StatisticsCardProps, ChartComponentProps, AlertComponentProps, SessionTimerProps, Theme, ViewMode, TimeRange, TradeUpdateHandler, PriceUpdateHandler, AlertHandler, ApiResponse, DataUpdateEvent, } from '../types/dashboard';
export { StateManager, stateManager } from './utils/StateManager';
export { calculatePnL, calculateR, getTodayTrades, calculateTotalPnL, calculateTodayPnL, getTradingStatistics, getEnhancedStatistics, formatStatistics, getTodayString, type TradingStatistics, } from './utils/statistics';
export declare const VERSION = "1.0.0";
export declare const TYPEScript_ENABLED = true;
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
export declare function isTradeEntry(obj: unknown): obj is import('../types/trading').TradeEntry;
export declare function isValidPnL(pnl: number): boolean;
export declare function calculatePositionSize(accountBalance: number, riskPercent: number, stopLossPips: number, pipValue?: number): number;
export declare function formatCurrency(value: number, currency?: string): string;
export declare function formatPercentage(value: number, decimals?: number): string;
//# sourceMappingURL=index.d.ts.map