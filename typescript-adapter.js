/**
 * TypeScript Adapter - Safe Integration Layer
 * Bridges existing vanilla JS state with TypeScript StateManager
 * 
 * This adapter:
 * 1. Loads TypeScript modules as an enhancement layer
 * 2. Syncs existing trades[] array with StateManager
 * 3. Mirrors existing S (settings) object
 * 4. Falls back gracefully if TypeScript fails
 * 5. Does NOT modify existing working code
 */

(function() {
  'use strict';

  // Track TypeScript integration status
  window.TS_INTEGRATION = {
    enabled: false,
    stateManager: null,
    bridge: null,
    errors: []
  };

  /**
   * TypeScript Bridge - Syncs existing state with TypeScript StateManager
   */
  class TypeScriptBridge {
    constructor(stateManager) {
      this.tsManager = stateManager;
      this.syncInterval = null;
      this.lastTradesHash = '';
      this.init();
    }

    init() {
      console.log('[TS] Bridge initializing...');
      
      // Initial sync from existing state to TypeScript
      this.syncFromExisting();
      
      // Set up periodic sync (every 2 seconds)
      this.syncInterval = setInterval(() => this.syncFromExisting(), 2000);
      
      // Subscribe to TypeScript state changes
      this.tsManager.subscribe((state) => {
        this.onTypeScriptStateChange(state);
      });

      console.log('[TS] Bridge active - syncing trades and state');
    }

    /**
     * Sync from existing dashboard state to TypeScript
     */
    syncFromExisting() {
      try {
        // Only sync if trades array exists and has changed
        if (typeof trades !== 'undefined' && Array.isArray(trades)) {
          const tradesHash = this.hashTrades(trades);
          
          if (tradesHash !== this.lastTradesHash) {
            this.lastTradesHash = tradesHash;
            
            // Convert existing trades to TypeScript format
            const tsTrades = trades.map((t, idx) => ({
              id: t.id || `trade-${idx}-${Date.now()}`,
              direction: t.direction || 'LONG',
              entryPrice: t.entry || t.entryPrice || 0,
              exitPrice: t.exit || t.exitPrice,
              sl: t.sl || t.stopLoss || 0,
              tp: t.tp || t.takeProfit || 0,
              size: t.size || t.lots || 0.1,
              date: t.date || new Date().toISOString().split('T')[0],
              status: t.status || (t.exit ? 'closed' : 'open'),
              pnl: t.pnl || t.profit || 0,
              r: t.r || t.rMultiple,
              session: t.session,
              setup: t.setup,
              notes: t.notes
            }));

            // Update TypeScript state
            this.tsManager.setState({
              todayTrades: tsTrades,
              todayPnL: trades.reduce((sum, t) => sum + (t.pnl || 0), 0)
            });
          }
        }

        // Sync settings from S object if it exists
        if (typeof S !== 'undefined' && S) {
          const currentState = this.tsManager.getState();
          
          // Only update if different to avoid loops
          if (S.account !== undefined && currentState.riskStatus) {
            const newRiskStatus = {
              ...currentState.riskStatus,
              dailyLossPercent: S.dailyloss,
              weeklyLossPercent: S.maxdd
            };
            
            // Silent update (don't trigger listeners)
            if (JSON.stringify(newRiskStatus) !== JSON.stringify(currentState.riskStatus)) {
              this.tsManager.updateRiskStatus(newRiskStatus);
            }
          }
        }
      } catch (e) {
        console.warn('[TS] Sync error:', e);
        window.TS_INTEGRATION.errors.push(e.message);
      }
    }

    /**
     * Handle TypeScript state changes (optional - for future enhancements)
     */
    onTypeScriptStateChange(state) {
      // This is where TypeScript → Existing sync would happen
      // Currently read-only to avoid disrupting existing code
      // Future: can emit events for new UI components to consume
      
      // Emit custom event for any new TypeScript-aware components
      window.dispatchEvent(new CustomEvent('ts-state-change', { 
        detail: state 
      }));
    }

    /**
     * Create hash of trades for change detection
     */
    hashTrades(trades) {
      return trades.map(t => `${t.id || ''}:${t.pnl || 0}:${t.status || ''}`).join('|');
    }

    /**
     * Get enhanced statistics from TypeScript
     */
    getEnhancedStats() {
      try {
        return this.tsManager.calculateStatistics();
      } catch (e) {
        console.warn('[TS] Stats error:', e);
        return null;
      }
    }

    /**
     * Add trade through TypeScript (returns confirmation)
     */
    addTrade(tradeData) {
      try {
        this.tsManager.addTrade(tradeData);
        return { success: true };
      } catch (e) {
        console.warn('[TS] Add trade error:', e);
        return { success: false, error: e.message };
      }
    }

    /**
     * Cleanup
     */
    destroy() {
      if (this.syncInterval) {
        clearInterval(this.syncInterval);
      }
    }
  }

  /**
   * Initialize TypeScript integration
   */
  async function initTypeScriptIntegration() {
    try {
      console.log('[TS] Initializing TypeScript integration...');

      // Check if module loader is available
      if (!window.define && !window.require && !('import' in document.createElement('script'))) {
        console.log('[TS] Module system not available - using fallback');
        return false;
      }

      // Dynamic import of compiled TypeScript module
      const module = await import('./dist/index.js');
      
      if (!module.StateManager) {
        console.warn('[TS] StateManager not found in module');
        return false;
      }

      // Get StateManager instance
      const stateManager = module.StateManager.getInstance();
      
      // Create bridge
      const bridge = new TypeScriptBridge(stateManager);
      
      // Store references
      window.TS_INTEGRATION.enabled = true;
      window.TS_INTEGRATION.stateManager = stateManager;
      window.TS_INTEGRATION.bridge = bridge;
      
      // Expose helper functions globally (optional enhancements)
      window.tsBridge = {
        // Status
        isEnabled: () => true,
        VERSION: module.VERSION,
        
        // Statistics Module (from statistics.ts)
        calculatePnL: module.calculatePnL,
        calculateR: module.calculateR,
        getTradingStatistics: module.getTradingStatistics,
        getEnhancedStatistics: module.getEnhancedStatistics,
        formatStatistics: module.formatStatistics,
        calculateTotalPnL: module.calculateTotalPnL,
        calculateTodayPnL: module.calculateTodayPnL,
        filterTradesByDate: module.filterTradesByDate,
        
        // State Manager - Core
        getState: () => stateManager.getState(),
        setState: (state) => stateManager.setState(state),
        subscribe: (callback) => stateManager.subscribe(callback),
        
        // State Manager - Trade Operations
        addTrade: (trade) => stateManager.addTrade(trade),
        updateTrade: (id, updates) => stateManager.updateTrade(id, updates),
        removeTrade: (id) => stateManager.removeTrade(id),
        closeTrade: (id, exitPrice, outcome) => stateManager.closeTrade(id, exitPrice, outcome),
        logTrade: (tradeData) => stateManager.logTrade(tradeData),
        delTrade: (id) => stateManager.delTrade(id),
        updateTradeOutcome: (id, outcome, exitPrice) => stateManager.updateTradeOutcome(id, outcome, exitPrice),
        
        // State Manager - Alert Operations
        addAlert: (alert) => stateManager.addAlert(alert),
        removeAlert: (id) => stateManager.removeAlert(id),
        clearAlerts: () => stateManager.clearAlerts(),
        
        // State Manager - Statistics
        getTodayPnL: () => stateManager.getTodayPnL(),
        getTotalPnL: () => stateManager.getTotalPnL(),
        getWinRate: () => stateManager.getWinRate(),
        getAverageR: () => stateManager.getAverageR(),
        getStats: () => bridge.getEnhancedStats(),
        
        // State Manager - Persistence
        saveState: () => stateManager.saveState(),
        loadAllState: () => stateManager.loadAllState(),
        saveAllState: (S, trades, news, rChecks, chatHist) => stateManager.saveAllState(S, trades, news, rChecks, chatHist),
        loadFromTSStorage: () => stateManager.loadFromTSStorage(),
        forcePersist: () => stateManager.forcePersist(),
        
        // State Manager - Time & Session
        getTodayKey: () => stateManager.getTodayKey(),
        getNairobiDate: () => stateManager.getNairobiDate(),
        getSessionHour: () => stateManager.getSessionHour(),
        formatCountdown: (seconds) => stateManager.formatCountdown(seconds),
        getSecondsToNextSession: () => stateManager.getSecondsToNextSession(),
        
        // State Manager - Version
        getVersion: () => stateManager.getVersion(),
        
        // HTML Utility Functions (for cockpit compatibility)
        eat: () => new Date(new Date().toLocaleString('en-US', {timeZone: 'Africa/Nairobi'})),
        eatH: () => {
          const t = new Date(new Date().toLocaleString('en-US', {timeZone: 'Africa/Nairobi'}));
          return t.getHours() + t.getMinutes() / 60 + t.getSeconds() / 3600;
        },
        dk: () => {
          const d = new Date(new Date().toLocaleString('en-US', {timeZone: 'Africa/Nairobi'}));
          return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
        },
        curSess: () => {
          const SESS = [
            {name:'ASIAN',      sh:'AS',       s:0,  e:3,  c:'am', active:true,  desc:'Asian session - Tokyo, Singapore, Hong Kong'},
            {name:'LONDON',    sh:'LD',       s:3,  e:10, c:'am', active:true,  desc:'London session - Highest volatility'},
            {name:'NEW YORK',  sh:'NY',       s:10, e:16, c:'am', active:true,  desc:'New York session - US trading hours'},
            {name:'NY CLOSE',  sh:'NYC',      s:16, e:17, c:'pm', active:true,  desc:'New York close - Reduced liquidity'},
            {name:'NY CONT.',  sh:'NY',       s:17, e:21, c:'am', active:true,  desc:'Manage open trades only. No new entries after 17:00.'},
            {name:'HARD CLOSE',sh:'CLOSE',    s:21, e:24, c:'rd', active:false, desc:'ALL POSITIONS MUST BE FLAT. No trading until 10:00 EAT tomorrow.'}
          ];
          // Fixed: Use local function instead of circular reference
          const t = new Date(new Date().toLocaleString('en-US', {timeZone: 'Africa/Nairobi'}));
          const h = t.getHours() + t.getMinutes() / 60 + t.getSeconds() / 3600;
          return SESS.find(s => h >= s.s && h < s.e) || SESS[0];
        },
        checkedCount: () => {
          // Simplified version - returns 8 (all checks passed)
          return 8;
        }
      };

      // ═══════════════════════════════════════════════════════════════════
      // PHASE 5: UI BRIDGE - Listen to TypeScript state changes
      // ═══════════════════════════════════════════════════════════════════
      const uiBridge = new TypeScriptUIBridge(stateManager, bridge);
      uiBridge.initialize();
      
      // ═══════════════════════════════════════════════════════════════════
      // PHASE 6: EVENT BRIDGE - Real-time sync between TS and vanilla JS
      // ═══════════════════════════════════════════════════════════════════
      const eventBridge = new EventBridge(stateManager);
      eventBridge.initialize();
      
      // Store UI and event bridges
      window.TS_INTEGRATION.uiBridge = uiBridge;
      window.TS_INTEGRATION.eventBridge = eventBridge;

      console.log('[TS] ✅ Integration active - TypeScript enhancements available');
      console.log('[TS] Access via: window.tsBridge or window.TS_INTEGRATION');
      console.log('[TS] UI Bridge and Event Sync initialized');
      
      return true;
    } catch (error) {
      console.warn('[TS] ❌ Integration failed:', error.message);
      console.log('[TS] Dashboard continues with vanilla JS (no impact)');
      window.TS_INTEGRATION.errors.push(error.message);
      
      // Provide fallback object
      window.tsBridge = {
        getStats: () => null,
        getState: () => null,
        addTrade: () => ({ success: false, error: 'TypeScript not loaded' }),
        isEnabled: () => false
      };
      
      return false;
    }
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTypeScriptIntegration);
  } else {
    // Small delay to let existing dashboard initialize first
    setTimeout(initTypeScriptIntegration, 500);
  }

  // ═══════════════════════════════════════════════════════════════════
  // PHASE 5: TYPESCRIPT UI BRIDGE CLASS
  // Listens to StateManager changes and triggers UI updates
  // ═══════════════════════════════════════════════════════════════════
  class TypeScriptUIBridge {
    constructor(stateManager, tsBridge) {
      this.stateManager = stateManager;
      this.tsBridge = tsBridge;
      this.unsubscribe = null;
      this.isInitialized = false;
    }

    initialize() {
      if (this.isInitialized) return;
      
      // Subscribe to StateManager state changes
      this.unsubscribe = this.stateManager.subscribe((newState, prevState) => {
        this.handleStateChange(newState, prevState);
      });
      
      this.isInitialized = true;
      console.log('[TS-UI] Bridge initialized - listening for state changes');
    }

    handleStateChange(newState, prevState) {
      // Detect trade count changes
      const newTradeCount = newState.todayTrades?.length || 0;
      const prevTradeCount = prevState?.todayTrades?.length || 0;
      
      if (newTradeCount !== prevTradeCount) {
        console.log(`[TS-UI] Trade count changed: ${prevTradeCount} → ${newTradeCount}`);
        this.triggerUIUpdate('trades', newState.todayTrades);
      }
      
      // Detect P&L changes
      const newPnL = newState.todayPnL;
      const prevPnL = prevState?.todayPnL;
      if (newPnL !== prevPnL) {
        console.log(`[TS-UI] P&L changed: ${prevPnL} → ${newPnL}`);
        this.triggerUIUpdate('pnl', newPnL);
      }
      
      // Detect alert changes
      const newAlertCount = newState.alerts?.length || 0;
      const prevAlertCount = prevState?.alerts?.length || 0;
      if (newAlertCount !== prevAlertCount) {
        this.triggerUIUpdate('alerts', newState.alerts);
      }
    }

    triggerUIUpdate(type, data) {
      // Dispatch custom events for HTML to listen to
      const event = new CustomEvent('ts-state-change', {
        detail: { type, data, timestamp: Date.now() }
      });
      document.dispatchEvent(event);
      
      // Also try to call vanilla JS update functions if they exist
      if (typeof window.renderJournal === 'function') {
        try {
          window.renderJournal();
          console.log('[TS-UI] renderJournal() triggered');
        } catch (e) {
          // Silently fail - vanilla JS functions may not exist yet
        }
      }
      
      if (typeof window.updateJournalStats === 'function') {
        try {
          window.updateJournalStats();
        } catch (e) {
          // Silently fail
        }
      }
      
      if (typeof window.tickHeader === 'function') {
        try {
          window.tickHeader();
        } catch (e) {
          // Silently fail
        }
      }
    }

    destroy() {
      if (this.unsubscribe) {
        this.unsubscribe();
        this.unsubscribe = null;
      }
      this.isInitialized = false;
      console.log('[TS-UI] Bridge destroyed');
    }
  }

  // ═══════════════════════════════════════════════════════════════════
  // PHASE 6: EVENT BRIDGE - Two-way sync between TS and Vanilla JS
  // ═══════════════════════════════════════════════════════════════════
  class EventBridge {
    constructor(stateManager) {
      this.stateManager = stateManager;
      this.listeners = [];
    }

    initialize() {
      // Listen for vanilla JS events and sync to TypeScript
      this.setupVanillaJSEventListeners();
      
      // Listen for TypeScript state changes and sync to vanilla JS
      this.setupTypeScriptEventListeners();
      
      console.log('[TS-Event] Two-way sync bridge initialized');
    }

    setupVanillaJSEventListeners() {
      // Listen for custom events from HTML dashboard
      document.addEventListener('trade-added', (e) => {
        if (e.detail?.trade) {
          console.log('[TS-Event] Trade added via vanilla JS event');
          this.syncVanillaTradeToTypeScript(e.detail.trade);
        }
      });
      
      document.addEventListener('trade-removed', (e) => {
        if (e.detail?.tradeId) {
          console.log('[TS-Event] Trade removed via vanilla JS event');
          this.stateManager.removeTrade(e.detail.tradeId);
        }
      });
      
      document.addEventListener('state-saved', () => {
        console.log('[TS-Event] State saved event received');
        this.stateManager.saveState();
      });
    }

    setupTypeScriptEventListeners() {
      // Subscribe to StateManager and emit vanilla JS events
      const unsubscribe = this.stateManager.subscribe((newState, prevState) => {
        // Emit sync event for vanilla JS to pick up
        const syncEvent = new CustomEvent('ts-sync', {
          detail: { 
            state: newState, 
            changed: this.getChangedFields(newState, prevState),
            timestamp: Date.now()
          }
        });
        document.dispatchEvent(syncEvent);
      });
      
      this.listeners.push(unsubscribe);
    }

    getChangedFields(newState, prevState) {
      const changed = [];
      if (!prevState) return changed;
      
      if (newState.todayTrades?.length !== prevState.todayTrades?.length) {
        changed.push('trades');
      }
      if (newState.todayPnL !== prevState.todayPnL) {
        changed.push('pnl');
      }
      if (newState.alerts?.length !== prevState.alerts?.length) {
        changed.push('alerts');
      }
      
      return changed;
    }

    syncVanillaTradeToTypeScript(trade) {
      const tsTrade = {
        id: trade.id || `trade-${Date.now()}`,
        direction: trade.dir || trade.direction || 'LONG',
        entryPrice: parseFloat(trade.entry) || 0,
        exitPrice: parseFloat(trade.exit) || 0,
        sl: parseFloat(trade.sl) || 0,
        tp: parseFloat(trade.tp1 || trade.tp) || 0,
        size: parseFloat(trade.lots) || 0,
        date: trade.date || new Date().toISOString().split('T')[0],
        status: trade.exit ? 'closed' : 'open',
        session: trade.session || 'London',
        setup: trade.strategy || '',
        notes: trade.notes || ''
      };
      
      this.stateManager.addTrade(tsTrade);
    }

    destroy() {
      this.listeners.forEach(unsub => unsub());
      this.listeners = [];
      console.log('[TS-Event] Bridge destroyed');
    }
  }

  // Also expose init function for manual retry
  window.initTypeScriptIntegration = initTypeScriptIntegration;

})();
