/**
 * StateManager - Centralized State Management for Trading Dashboard
 * Implements singleton pattern for global state management
 * Provides type-safe state updates and persistence
 */
import { TradeEntry, TradeStatistics, Alert, FeedStatus, RiskStatus } from '../../types/trading';
import { DashboardState } from '../../types/dashboard';
export declare class StateManager {
    private static instance;
    private state;
    private listeners;
    private readonly STORAGE_KEY;
    private readonly MAX_ALERTS;
    private constructor();
    static getInstance(): StateManager;
    private loadInitialState;
    private getDefaultState;
    private getDefaultStats;
    getState(): DashboardState;
    setState(partialState: Partial<DashboardState>): void;
    addTrade(trade: TradeEntry): void;
    updateTrade(updatedTrade: TradeEntry): void;
    closeTrade(tradeId: string, exitPrice: number): void;
    addAlert(alert: Alert): void;
    dismissAlert(index: number): void;
    removeTrade(tradeId: string): void;
    updateFeedStatus(feedStatus: FeedStatus): void;
    updateRiskStatus(riskStatus: RiskStatus): void;
    private calculateTodayPnL;
    calculateStatistics(trades?: TradeEntry[]): TradeStatistics;
    private calculateAverageR;
    private calculateMaxDrawdown;
    subscribe(listener: (state: DashboardState) => void): () => void;
    private notifyListeners;
    saveState(): void;
    resetState(): void;
    /**
     * Sync legacy trades array from vanilla JS into TypeScript state
     * Called by loadAll() in HTML when loading from localStorage
     */
    syncLegacyTrades(legacyTrades: any[]): void;
    /**
     * Sync legacy settings (S object) from vanilla JS
     */
    syncLegacySettings(settings: any): void;
    /**
     * Export TypeScript state in legacy format for vanilla JS
     * Called when HTML needs to access TypeScript-managed trades
     */
    exportToLegacyFormat(): {
        trades: any[];
        settings: any;
    };
    /**
     * Force TypeScript state to persist to localStorage
     * Called by saveAll() in HTML
     */
    forcePersist(): void;
    /**
     * Load from TypeScript storage (different key than vanilla JS)
     * Returns true if data was loaded
     */
    loadFromTSStorage(): boolean;
}
export declare const stateManager: StateManager;
//# sourceMappingURL=StateManager.d.ts.map