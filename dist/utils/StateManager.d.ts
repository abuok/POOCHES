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
}
export declare const stateManager: StateManager;
//# sourceMappingURL=StateManager.d.ts.map