/**
 * Type definitions for Dashboard Components
 */

import { TradeEntry, TradeStatistics, SessionStats, FeedStatus, EconomicEvent, Alert, RiskStatus } from './trading';

// Chart Configuration
export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut';
  data: ChartData;
  options?: ChartOptions;
}

export interface ChartData {
  labels: string[];
  datasets: Dataset[];
}

export interface Dataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string;
  borderWidth?: number;
  fill?: boolean;
}

export interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  plugins?: {
    legend?: {
      display?: boolean;
      position?: 'top' | 'bottom' | 'left' | 'right';
    };
    title?: {
      display?: boolean;
      text?: string;
    };
  };
  scales?: {
    y?: {
      beginAtZero?: boolean;
    };
    x?: {
      display?: boolean;
    };
  };
}

// Dashboard State
export interface DashboardState {
  currentSession: string;
  isWeekend: boolean;
  feedStatus: FeedStatus;
  riskStatus: RiskStatus;
  todayPnL: number;
  todayTrades: TradeEntry[];
  weeklyStats: TradeStatistics;
  monthlyStats: TradeStatistics;
  allTimeStats: TradeStatistics;
  alerts: Alert[];
  scannerConditions: ScannerCondition[];
  economicEvents: EconomicEvent[];
  activeTrades: TradeEntry[];
  closedTrades: TradeEntry[];
}

export interface ScannerCondition {
  id: string;
  name: string;
  description: string;
  checked: boolean;
  value?: string | number;
  color?: 'green' | 'red' | 'amber' | 'neutral';
}

// Component Props
export interface TradeTableProps {
  trades: TradeEntry[];
  showActions?: boolean;
  onEdit?: (trade: TradeEntry) => void;
  onDelete?: (tradeId: string) => void;
  onClose?: (tradeId: string, exitPrice: number) => void;
}

export interface StatisticsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: string;
}

export interface ChartComponentProps {
  data: ChartData;
  config: ChartConfig;
  height?: number;
  width?: number;
}

export interface AlertComponentProps {
  alert: Alert;
  onDismiss?: (alertId: string) => void;
}

export interface SessionTimerProps {
  session: string;
  timeRemaining: number;
  isActive: boolean;
}

// Utility Types
export type Theme = 'dark' | 'light';

export type ViewMode = 'dashboard' | 'journal' | 'analysis' | 'settings';

export type TimeRange = 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';

// Event Handlers
export type TradeUpdateHandler = (trade: TradeEntry) => void;
export type PriceUpdateHandler = (price: number, change: number) => void;
export type AlertHandler = (alert: Alert) => void;

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface DataUpdateEvent {
  type: 'price' | 'indicator' | 'trade' | 'alert';
  payload: unknown;
  timestamp: Date;
}
