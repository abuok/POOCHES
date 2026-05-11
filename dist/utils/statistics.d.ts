/**
 * Statistics Module - TypeScript Migration (Phase 1)
 *
 * Migrated from: XAU_USD Trading System — Nairobi.html (lines 2920-2939)
 * Pure functions with full type safety
 */
import { TradeEntry } from '../../types/trading';
/**
 * Trading Statistics Interface
 * Type-safe version of the getStats() return object
 */
export interface TradingStatistics {
    totalTrades: number;
    wins: number;
    losses: number;
    winRate: number;
    avgR: number;
    totalPnL: number;
    bestTrade: number;
    worstTrade: number;
    consecutiveWins: number;
    consecutiveLosses: number;
    profitFactor?: number;
    expectancy?: number;
}
/**
 * Calculate P&L for a single trade
 * Migrated from: calcPnL(t) in HTML
 *
 * @param trade - Trade entry with direction, entry, exit, and size
 * @returns Profit/Loss in dollars
 */
export declare function calculatePnL(trade: TradeEntry): number;
/**
 * Calculate R-multiple for a trade
 * Migrated from: calcR(t) in HTML
 *
 * @param trade - Trade entry
 * @param accountBalance - Current account balance
 * @param riskPercent - Risk percent per trade (default 1%)
 * @returns R-multiple (e.g., 2.5 means 2.5x risk reward)
 */
export declare function calculateR(trade: TradeEntry, accountBalance: number, riskPercent?: number): number;
/**
 * Get today's date string (EAT timezone)
 * Migrated from: dk() function in HTML
 */
export declare function getTodayString(): string;
/**
 * Filter trades to only today's trades
 * Migrated from: todayTrades() in HTML
 */
export declare function getTodayTrades(trades: TradeEntry[]): TradeEntry[];
/**
 * Calculate total P&L for an array of trades
 * Migrated from: totalPnL() in HTML
 */
export declare function calculateTotalPnL(trades: TradeEntry[]): number;
/**
 * Calculate today's P&L
 * Migrated from: todayPnL() in HTML
 */
export declare function calculateTodayPnL(trades: TradeEntry[]): number;
/**
 * Get comprehensive trading statistics
 * Migrated from: getStats() in HTML (line 2926-2935)
 *
 * @param trades - Array of all trades
 * @returns Complete statistics object with type safety
 */
export declare function getTradingStatistics(trades: TradeEntry[]): TradingStatistics;
/**
 * Calculate statistics with full R-multiple support
 * Enhanced version that includes R calculations
 */
export declare function getEnhancedStatistics(trades: TradeEntry[], accountBalance: number, riskPercent?: number): TradingStatistics;
/**
 * Format statistics for display
 * Helper to format numbers with currency symbols
 */
export declare function formatStatistics(stats: TradingStatistics, currency?: string): Record<string, string>;
//# sourceMappingURL=statistics.d.ts.map