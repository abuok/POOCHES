/**
 * STATE MANAGER
 * Centralized state management for trading system
 */

class StateManager {
  constructor(initialState = {}, options = {}) {
    this.state = { ...initialState };
    this.listeners = new Map();
    this.history = [];
    this.maxHistorySize = options.maxHistorySize || 50;
    this.persistenceKey = options.persistenceKey || 'trading_system_state';
    this.enablePersistence = options.enablePersistence !== false;
    
    // Initialize persistence
    if (this.enablePersistence) {
      this.loadFromPersistence();
    }
    
    // Add cleanup on page unload
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.cleanup();
      });
    }
  }

  /**
   * Get current state or specific property
   */
  getState(path = null) {
    if (path === null) {
      return { ...this.state };
    }
    
    return this.getNestedValue(this.state, path);
  }

  /**
   * Update state with new values
   */
  setState(updates, options = {}) {
    const { merge = true, persist = true, notify = true } = options;
    
    // Store previous state for history
    const previousState = { ...this.state };
    
    // Apply updates
    if (merge) {
      this.state = this.deepMerge(this.state, updates);
    } else {
      this.state = { ...updates };
    }
    
    // Add to history
    this.addToHistory(previousState, updates, options.source || 'unknown');
    
    // Persist if enabled
    if (persist && this.enablePersistence) {
      this.saveToPersistence();
    }
    
    // Notify listeners
    if (notify) {
      this.notifyListeners(updates, previousState, this.state);
    }
    
    return this.state;
  }

  /**
   * Reset state to initial values
   */
  resetState(newState = {}) {
    const previousState = { ...this.state };
    this.state = { ...newState };
    this.history = [];
    
    if (this.enablePersistence) {
      this.saveToPersistence();
    }
    
    this.notifyListeners(newState, previousState, this.state, { type: 'reset' });
    return this.state;
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener, options = {}) {
    const { 
      path = null, 
      immediate = false, 
      filter = null 
    } = options;
    
    const listenerId = this.generateListenerId();
    
    const wrappedListener = {
      id: listenerId,
      callback: listener,
      path,
      filter,
      immediate
    };
    
    this.listeners.set(listenerId, wrappedListener);
    
    // Call immediately if requested
    if (immediate) {
      const currentState = path ? this.getNestedValue(this.state, path) : this.state;
      listener(currentState, null, this.state, { type: 'immediate' });
    }
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listenerId);
    };
  }

  /**
   * Unsubscribe from state changes
   */
  unsubscribe(listenerId) {
    return this.listeners.delete(listenerId);
  }

  /**
   * Get state history
   */
  getHistory(count = null) {
    if (count === null) {
      return [...this.history];
    }
    return this.history.slice(-count);
  }

  /**
   * Clear history
   */
  clearHistory() {
    this.history = [];
  }

  /**
   * Get state statistics
   */
  getStateStats() {
    return {
      listenerCount: this.listeners.size,
      historySize: this.history.length,
      stateSize: JSON.stringify(this.state).length,
      lastUpdated: this.history.length > 0 ? this.history[this.history.length - 1].timestamp : null
    };
  }

  /**
   * Validate state against schema
   */
  validateState(schema) {
    const errors = [];
    
    const validateObject = (obj, schemaObj, path = '') => {
      for (const [key, rules] of Object.entries(schemaObj)) {
        const currentPath = path ? `${path}.${key}` : key;
        
        if (rules.required && !(key in obj)) {
          errors.push(`Required property missing: ${currentPath}`);
          continue;
        }
        
        if (key in obj) {
          const value = obj[key];
          
          // Type validation
          if (rules.type && typeof value !== rules.type) {
            errors.push(`Type mismatch at ${currentPath}: expected ${rules.type}, got ${typeof value}`);
          }
          
          // Range validation
          if (rules.min !== undefined && value < rules.min) {
            errors.push(`Value below minimum at ${currentPath}: ${value} < ${rules.min}`);
          }
          
          if (rules.max !== undefined && value > rules.max) {
            errors.push(`Value above maximum at ${currentPath}: ${value} > ${rules.max}`);
          }
          
          // Pattern validation
          if (rules.pattern && !rules.pattern.test(value)) {
            errors.push(`Pattern mismatch at ${currentPath}: ${value}`);
          }
          
          // Nested object validation
          if (rules.properties && typeof value === 'object' && value !== null) {
            validateObject(value, rules.properties, currentPath);
          }
        }
      }
    };
    
    validateObject(this.state, schema);
    return errors;
  }

  /**
   * Create state selector
   */
  createSelector(path, defaultValue = null) {
    return () => {
      const value = this.getNestedValue(this.state, path);
      return value !== undefined ? value : defaultValue;
    };
  }

  /**
   * Create state action
   */
  createAction(path) {
    return (value) => {
      const updates = this.setNestedValue({}, path, value);
      return this.setState(updates);
    };
  }

  /**
   * Batch multiple state updates
   */
  batchUpdate(updatesArray) {
    let accumulatedUpdates = {};
    const previousState = { ...this.state };
    
    updatesArray.forEach((updates, index) => {
      accumulatedUpdates = this.deepMerge(accumulatedUpdates, updates);
      
      if (index === updatesArray.length - 1) {
        this.state = this.deepMerge(this.state, accumulatedUpdates);
        this.addToHistory(previousState, accumulatedUpdates, 'batch');
        
        if (this.enablePersistence) {
          this.saveToPersistence();
        }
        
        this.notifyListeners(accumulatedUpdates, previousState, this.state, { type: 'batch' });
      }
    });
    
    return this.state;
  }

  /**
   * Get nested value from object using dot notation
   */
  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  /**
   * Set nested value in object using dot notation
   */
  setNestedValue(obj, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    
    const nestedObj = keys.reduce((current, key) => {
      if (!current[key] || typeof current[key] !== 'object') {
        current[key] = {};
      }
      return current[key];
    }, obj);
    
    nestedObj[lastKey] = value;
    return obj;
  }

  /**
   * Deep merge two objects
   */
  deepMerge(target, source) {
    const result = { ...target };
    
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (
          typeof source[key] === 'object' && 
          source[key] !== null && 
          !Array.isArray(source[key])
        ) {
          result[key] = this.deepMerge(result[key] || {}, source[key]);
        } else {
          result[key] = source[key];
        }
      }
    }
    
    return result;
  }

  /**
   * Add state change to history
   */
  addToHistory(previousState, updates, source) {
    const historyEntry = {
      timestamp: Date.now(),
      previousState: { ...previousState },
      updates: { ...updates },
      state: { ...this.state },
      source
    };
    
    this.history.push(historyEntry);
    
    // Limit history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    }
  }

  /**
   * Notify all listeners of state changes
   */
  notifyListeners(updates, previousState, currentState, options = {}) {
    for (const [listenerId, listener] of this.listeners) {
      try {
        // Check if listener should be notified
        if (listener.filter && !listener.filter(updates, previousState, currentState)) {
          continue;
        }
        
        // Get relevant state for listener
        let relevantPreviousState = previousState;
        let relevantCurrentState = currentState;
        
        if (listener.path) {
          relevantPreviousState = this.getNestedValue(previousState, listener.path);
          relevantCurrentState = this.getNestedValue(currentState, listener.path);
        }
        
        // Call listener
        listener.callback(relevantCurrentState, relevantPreviousState, currentState, options);
      } catch (error) {
        console.error(`Error in state listener ${listenerId}:`, error);
      }
    }
  }

  /**
   * Generate unique listener ID
   */
  generateListenerId() {
    return `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Save state to persistence
   */
  saveToPersistence() {
    try {
      const stateToSave = {
        state: this.state,
        timestamp: Date.now(),
        version: '1.0'
      };
      
      localStorage.setItem(this.persistenceKey, JSON.stringify(stateToSave));
    } catch (error) {
      console.warn('Failed to save state to persistence:', error);
    }
  }

  /**
   * Load state from persistence
   */
  loadFromPersistence() {
    try {
      const savedData = localStorage.getItem(this.persistenceKey);
      
      if (savedData) {
        const parsed = JSON.parse(savedData);
        
        // Validate version compatibility
        if (parsed.version && parsed.version === '1.0') {
          this.state = { ...parsed.state };
          this.addToHistory({}, parsed.state, 'persistence');
        }
      }
    } catch (error) {
      console.warn('Failed to load state from persistence:', error);
    }
  }

  /**
   * Clear persisted state
   */
  clearPersistence() {
    try {
      localStorage.removeItem(this.persistenceKey);
    } catch (error) {
      console.warn('Failed to clear persisted state:', error);
    }
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.listeners.clear();
    this.history = [];
    
    if (this.enablePersistence) {
      this.saveToPersistence();
    }
  }

  /**
   * Export state for debugging
   */
  exportState() {
    return {
      currentState: this.state,
      history: this.history,
      stats: this.getStateStats(),
      listeners: Array.from(this.listeners.keys())
    };
  }

  /**
   * Import state for debugging/testing
   */
  importState(exportedState) {
    if (exportedState.currentState) {
      this.setState(exportedState.currentState, { 
        persist: true, 
        source: 'import' 
      });
    }
    
    if (exportedState.history) {
      this.history = [...exportedState.history];
    }
  }
}

// Trading system specific state schemas
const TradingStateSchema = {
  scanner: {
    type: 'object',
    required: true,
    properties: {
      currentStrategy: { type: 'string', required: true },
      currentDirection: { type: 'string', required: true, pattern: /^(LONG|SHORT)$/ },
      conditions: { type: 'object', required: true },
      manualOverrides: { type: 'object', required: true },
      autoChecks: { type: 'object', required: true }
    }
  },
  trading: {
    type: 'object',
    required: true,
    properties: {
      accountBalance: { type: 'number', required: true, min: 0 },
      dailyPnL: { type: 'number', required: true },
      dailyStop: { type: 'number', required: true, min: 0 },
      tradeCount: { type: 'object', required: true },
      riskPerTrade: { type: 'number', required: true, min: 0, max: 0.1 }
    }
  },
  market: {
    type: 'object',
    required: true,
    properties: {
      currentPrice: { type: 'number', required: true, min: 0 },
      priceChange: { type: 'number', required: true },
      priceDirection: { type: 'string', required: true, pattern: /^(up|down|neutral)$/ },
      feedStatus: { type: 'string', required: true, pattern: /^(live|connecting|off)$/ },
      session: { type: 'string', required: true }
    }
  }
};

// Create global state manager instance
const tradingStateManager = new StateManager({
  scanner: {
    currentStrategy: 'scanner_8_condition',
    currentDirection: 'LONG',
    conditions: {},
    manualOverrides: {},
    autoChecks: {}
  },
  trading: {
    accountBalance: 10000,
    dailyPnL: 0,
    dailyStop: 500,
    tradeCount: { total: 0, winning: 0, losing: 0 },
    riskPerTrade: 0.02
  },
  market: {
    currentPrice: 0,
    priceChange: 0,
    priceDirection: 'neutral',
    feedStatus: 'off',
    session: 'Asian'
  }
}, {
  persistenceKey: 'xau_trading_system_state',
  maxHistorySize: 100,
  enablePersistence: true
});

// Convenience functions for common state operations
const TradingStateActions = {
  // Scanner actions
  setStrategy: (strategy) => tradingStateManager.setState({
    scanner: { currentStrategy: strategy }
  }, { source: 'user_strategy_selection' }),
  
  setDirection: (direction) => tradingStateManager.setState({
    scanner: { currentDirection: direction }
  }, { source: 'user_direction_selection' }),
  
  updateCondition: (index, checked) => tradingStateManager.setState({
    scanner: { 
      manualOverrides: { 
        [`${tradingStateManager.getState('scanner.currentDirection')}_${index}`]: checked 
      }
    }
  }, { source: 'user_condition_toggle' }),
  
  // Trading actions
  updateAccountBalance: (balance) => tradingStateManager.setState({
    trading: { accountBalance: balance }
  }, { source: 'account_update' }),
  
  updateDailyPnL: (pnl) => tradingStateManager.setState({
    trading: { dailyPnL: pnl }
  }, { source: 'pnl_update' }),
  
  // Market actions
  updatePrice: (price, change, direction) => tradingStateManager.setState({
    market: { 
      currentPrice: price,
      priceChange: change,
      priceDirection: direction
    }
  }, { source: 'price_update' }),
  
  setFeedStatus: (status) => tradingStateManager.setState({
    market: { feedStatus: status }
  }, { source: 'feed_status_update' })
};

// State selectors for common state queries
const TradingStateSelectors = {
  getCurrentStrategy: () => tradingStateManager.getState('scanner.currentStrategy'),
  getCurrentDirection: () => tradingStateManager.getState('scanner.currentDirection'),
  getAccountBalance: () => tradingStateManager.getState('trading.accountBalance'),
  getCurrentPrice: () => tradingStateManager.getState('market.currentPrice'),
  getFeedStatus: () => tradingStateManager.getState('market.feedStatus'),
  getSession: () => tradingStateManager.getState('market.session'),
  
  // Complex selectors
  getScannerConditions: () => {
    const state = tradingStateManager.getState();
    const strategy = state.scanner.currentStrategy;
    const direction = state.scanner.currentDirection;
    return state.scanner.conditions[strategy]?.[direction] || {};
  },
  
  getTradingStats: () => {
    const state = tradingStateManager.getState();
    const { total, winning, losing } = state.trading.tradeCount;
    const winRate = total > 0 ? (winning / total * 100).toFixed(1) : '0.0';
    
    return {
      total,
      winning,
      losing,
      winRate: parseFloat(winRate),
      accountBalance: state.trading.accountBalance,
      dailyPnL: state.trading.dailyPnL
    };
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    StateManager,
    TradingStateSchema,
    tradingStateManager,
    TradingStateActions,
    TradingStateSelectors
  };
}

// Global assignment for browser
if (typeof window !== 'undefined') {
  window.StateManager = StateManager;
  window.tradingStateManager = tradingStateManager;
  window.TradingStateActions = TradingStateActions;
  window.TradingStateSelectors = TradingStateSelectors;
}
