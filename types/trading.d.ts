/**
 * Type definitions for Trading System
 * These interfaces define the core data structures used throughout the application
 */

// Trade Direction
export type TradeDirection = 'LONG' | 'SHORT';

// Trade Status
export type TradeStatus = 'open' | 'closed' | 'pending';

// Session Types
export type TradingSession = 'Asian' | 'London' | 'NY' | 'NY_Evening' | 'Asian_Late';

// Impact Levels
export type ImpactLevel = 'high' | 'medium' | 'low';

// Alert Types
export type AlertType = 'warning' | 'opportunity' | 'info';

// Trade Entry Interface
export interface TradeEntry {
  id: string;
  direction: TradeDirection;
  entryPrice: number;
  exitPrice?: number;
  sl: number; // Stop Loss
  tp: number; // Take Profit
  size: number;
  date: string;
  status: TradeStatus;
  pnl?: number;
  r?: number; // R-multiple
  session?: TradingSession;
  setup?: string;
  notes?: string;
}

// Trade Statistics
export interface TradeStatistics {
  totalTrades: number;
  wins: number;
  losses: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  expectancy: number;
  avgR: number;
  maxDD: number; // Maximum Drawdown
  totalPnL: number;
}

// Session Analysis
export interface SessionStats {
  name: TradingSession;
  trades: number;
  winRate: number;
  avgPnL: number;
  profitFactor: number;
}

// Market Data Interface
export interface MarketData {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  symbol: string;
}

// Indicator Data
export interface IndicatorData {
  ema20?: number;
  ema50?: number;
  rsi14?: number;
  atr14?: number;
  macd?: number;
  bbUpper?: number;
  bbLower?: number;
  bbMiddle?: number;
}

// Feed Connection Status
export interface FeedStatus {
  connected: boolean;
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  lastUpdate: Date;
  indicators?: IndicatorData;
}

// Economic Event
export interface EconomicEvent {
  id: string;
  name: string;
  date: string;
  time: string;
  impact: ImpactLevel;
  country: string;
  currency: string;
  actual?: string;
  forecast?: string;
  previous?: string;
  description?: string;
}

// Daily Briefing
export interface DailyBriefing {
  date: string;
  timestamp: number;
  content: string;
  session: TradingSession;
  pnl: number;
  trades: number;
}

// Risk Status
export interface RiskStatus {
  level: 'safe' | 'caution' | 'danger';
  message: string;
  dailyLossPercent?: number;
  weeklyLossPercent?: number;
}

// Prop Account Phase
export interface PropPhase {
  id: string;
  name: string;
  targetPercent: number;
  currentPercent: number;
  status: 'active' | 'completed' | 'pending';
}

// Alert
export interface Alert {
  type: AlertType;
  message: string;
  timestamp: Date;
  category?: string;
}
