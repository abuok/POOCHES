/**
 * Main TypeScript Entry Point
 *
 * This file demonstrates how to use TypeScript in the project.
 * Import types and utilities from this file in your application code.
 */
// Export utilities
export { StateManager, stateManager } from './utils/StateManager';
// Export statistics module (Phase 1 TypeScript migration)
export { calculatePnL, calculateR, getTodayTrades, calculateTotalPnL, calculateTodayPnL, getTradingStatistics, getEnhancedStatistics, formatStatistics, getTodayString, } from './utils/statistics';
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
export function isTradeEntry(obj) {
    return (typeof obj === 'object' &&
        obj !== null &&
        'id' in obj &&
        'direction' in obj &&
        'entryPrice' in obj &&
        'status' in obj);
}
export function isValidPnL(pnl) {
    return !isNaN(pnl) && isFinite(pnl);
}
// Utility functions with type safety
export function calculatePositionSize(accountBalance, riskPercent, stopLossPips, pipValue = 10) {
    const riskAmount = accountBalance * (riskPercent / 100);
    const positionSize = riskAmount / (stopLossPips * pipValue);
    return Math.round(positionSize * 100) / 100;
}
export function formatCurrency(value, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
    }).format(value);
}
export function formatPercentage(value, decimals = 2) {
    return `${(value * 100).toFixed(decimals)}%`;
}
//# sourceMappingURL=index.js.map