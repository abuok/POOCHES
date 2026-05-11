/**
 * Statistics Module - TypeScript Migration (Phase 1)
 *
 * Migrated from: XAU_USD Trading System — Nairobi.html (lines 2920-2939)
 * Pure functions with full type safety
 */
/**
 * Calculate P&L for a single trade
 * Migrated from: calcPnL(t) in HTML
 *
 * @param trade - Trade entry with direction, entry, exit, and size
 * @returns Profit/Loss in dollars
 */
export function calculatePnL(trade) {
    // Handle both old format (entry/exit/lots) and new format (entryPrice/exitPrice/size)
    const entry = trade.entryPrice || trade.entry || 0;
    const exit = trade.exitPrice || trade.exit || 0;
    const size = trade.size || trade.lots || 0;
    if (!exit || !entry || !size)
        return 0;
    const direction = trade.direction === 'LONG' ? 1 : -1;
    return (exit - entry) * direction * size * 100;
}
/**
 * Calculate R-multiple for a trade
 * Migrated from: calcR(t) in HTML
 *
 * @param trade - Trade entry
 * @param accountBalance - Current account balance
 * @param riskPercent - Risk percent per trade (default 1%)
 * @returns R-multiple (e.g., 2.5 means 2.5x risk reward)
 */
export function calculateR(trade, accountBalance, riskPercent = 1) {
    const pnl = calculatePnL(trade);
    const riskAmount = accountBalance * (riskPercent / 100);
    return riskAmount > 0 ? pnl / riskAmount : 0;
}
/**
 * Get today's date string (EAT timezone)
 * Migrated from: dk() function in HTML
 */
export function getTodayString() {
    const d = new Date();
    return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
}
/**
 * Filter trades to only today's trades
 * Migrated from: todayTrades() in HTML
 */
export function getTodayTrades(trades) {
    const today = getTodayString();
    return trades.filter(t => {
        // Handle both old format (t.date) and new format
        const tradeDate = t.date || t.date;
        return tradeDate === today;
    });
}
/**
 * Calculate total P&L for an array of trades
 * Migrated from: totalPnL() in HTML
 */
export function calculateTotalPnL(trades) {
    return trades.reduce((sum, trade) => sum + calculatePnL(trade), 0);
}
/**
 * Calculate today's P&L
 * Migrated from: todayPnL() in HTML
 */
export function calculateTodayPnL(trades) {
    return calculateTotalPnL(getTodayTrades(trades));
}
/**
 * Get comprehensive trading statistics
 * Migrated from: getStats() in HTML (line 2926-2935)
 *
 * @param trades - Array of all trades
 * @returns Complete statistics object with type safety
 */
export function getTradingStatistics(trades) {
    // Handle empty trades
    if (!trades.length) {
        return {
            totalTrades: 0,
            wins: 0,
            losses: 0,
            winRate: 0,
            avgR: 0,
            totalPnL: 0,
            bestTrade: 0,
            worstTrade: 0,
            consecutiveWins: 0,
            consecutiveLosses: 0
        };
    }
    let wins = 0;
    let losses = 0;
    let totalPnL = 0;
    let bestTrade = -99999;
    let worstTrade = 99999;
    let currentWinStreak = 0;
    let currentLossStreak = 0;
    let maxConsecutiveWins = 0;
    let maxConsecutiveLosses = 0;
    trades.forEach(trade => {
        const pnl = calculatePnL(trade);
        totalPnL += pnl;
        // Track best/worst trades
        if (pnl > bestTrade)
            bestTrade = pnl;
        if (pnl < worstTrade)
            worstTrade = pnl;
        // Determine outcome (handle both formats)
        const outcome = trade.outcome || (pnl > 0 ? 'WIN' : pnl < 0 ? 'LOSS' : 'BREAKEVEN');
        // Track streaks
        if (outcome === 'WIN' || outcome === 'WIN1') {
            wins++;
            currentWinStreak++;
            currentLossStreak = 0;
            if (currentWinStreak > maxConsecutiveWins) {
                maxConsecutiveWins = currentWinStreak;
            }
        }
        else if (outcome === 'LOSS') {
            losses++;
            currentLossStreak++;
            currentWinStreak = 0;
            if (currentLossStreak > maxConsecutiveLosses) {
                maxConsecutiveLosses = currentLossStreak;
            }
        }
        // Breakeven doesn't affect streaks
    });
    const winRate = trades.length > 0 ? (wins / trades.length) * 100 : 0;
    // Calculate average R (will need account balance - use 0 if not available)
    const avgR = 0; // Placeholder - requires account context
    return {
        totalTrades: trades.length,
        wins,
        losses,
        winRate: parseFloat(winRate.toFixed(2)),
        avgR: parseFloat(avgR.toFixed(2)),
        totalPnL: parseFloat(totalPnL.toFixed(2)),
        bestTrade: parseFloat(bestTrade.toFixed(2)),
        worstTrade: parseFloat(worstTrade.toFixed(2)),
        consecutiveWins: maxConsecutiveWins,
        consecutiveLosses: maxConsecutiveLosses
    };
}
/**
 * Calculate statistics with full R-multiple support
 * Enhanced version that includes R calculations
 */
export function getEnhancedStatistics(trades, accountBalance, riskPercent = 1) {
    const baseStats = getTradingStatistics(trades);
    if (!trades.length)
        return baseStats;
    // Calculate R-multiples
    const rMultiples = trades
        .map(t => calculateR(t, accountBalance, riskPercent))
        .filter(r => !isNaN(r) && isFinite(r));
    const avgR = rMultiples.length > 0
        ? rMultiples.reduce((a, b) => a + b, 0) / rMultiples.length
        : 0;
    // Calculate profit factor
    const wins = trades.filter(t => calculatePnL(t) > 0);
    const losses = trades.filter(t => calculatePnL(t) < 0);
    const totalWins = wins.reduce((sum, t) => sum + calculatePnL(t), 0);
    const totalLosses = Math.abs(losses.reduce((sum, t) => sum + calculatePnL(t), 0));
    const profitFactor = totalLosses > 0
        ? totalWins / totalLosses
        : totalWins > 0 ? Infinity : 0;
    // Calculate expectancy
    const winRateDecimal = baseStats.winRate / 100;
    const lossRateDecimal = 1 - winRateDecimal;
    const avgWin = wins.length > 0 ? totalWins / wins.length : 0;
    const avgLoss = losses.length > 0 ? totalLosses / losses.length : 0;
    const expectancy = (winRateDecimal * avgWin) - (lossRateDecimal * avgLoss);
    return {
        ...baseStats,
        avgR: parseFloat(avgR.toFixed(2)),
        profitFactor: parseFloat(profitFactor.toFixed(2)),
        expectancy: parseFloat(expectancy.toFixed(2))
    };
}
/**
 * Format statistics for display
 * Helper to format numbers with currency symbols
 */
export function formatStatistics(stats, currency = '$') {
    return {
        totalTrades: String(stats.totalTrades),
        winRate: stats.winRate.toFixed(1) + '%',
        avgR: stats.avgR.toFixed(2) + 'R',
        totalPnL: currency + stats.totalPnL.toFixed(2),
        bestTrade: currency + stats.bestTrade.toFixed(2),
        worstTrade: currency + stats.worstTrade.toFixed(2),
        profitFactor: stats.profitFactor?.toFixed(2) || 'N/A',
        expectancy: currency + (stats.expectancy?.toFixed(2) || '0.00')
    };
}
//# sourceMappingURL=statistics.js.map