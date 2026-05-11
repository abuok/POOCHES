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
        getStats: () => bridge.getEnhancedStats(),
        getState: () => stateManager.getState(),
        addTrade: (trade) => bridge.addTrade(trade),
        isEnabled: () => true
      };

      console.log('[TS] ✅ Integration active - TypeScript enhancements available');
      console.log('[TS] Access via: window.tsBridge or window.TS_INTEGRATION');
      
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

  // Also expose init function for manual retry
  window.initTypeScript = initTypeScriptIntegration;

})();
