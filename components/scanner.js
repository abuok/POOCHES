// SCANNER JAVASCRIPT COMPONENT
// Dynamic strategy condition management

class ScannerComponent {
  constructor() {
    this.currentStrategy = 'scanner_8_condition';
    this.currentDirection = 'LONG';
    this.conditions = [];
    this.manualOverrides = {};
    this.autoChecks = {};
  }

  // Strategy configuration
  getStrategyConditions(strategyId) {
    const strategies = {
      'scanner_8_condition': {
        LONG: [
          {tf:'h1',  t:'EMA50 > EMA200 on H1',        d:'Macro bull trend confirmed. Check before session opens.',                    autoKey:'h1_ema_stack'},
          {tf:'h1',  t:'Price > EMA20 on H1',          d:'H1 close above EMA20. Price in upper half of trend structure.',             autoKey:'h1_price_ema20'},
          {tf:'h1',  t:'H1 RSI between 30 and 68',     d:'Not overbought on H1. RSI above 68 = skip all long setups today.',         autoKey:'h1_rsi'},
          {tf:'m15', t:'EMA8 > EMA21 on M15',          d:'Short-term M15 momentum bullish. If below — pullback still running.',      autoKey:'m15_ema_stack'},
          {tf:'m15', t:'M15 RSI crossed above 48',     d:'RSI was below 50 last bar, now ≥ 48. This IS the trigger.',               autoKey:'m15_rsi_cross'},
          {tf:'m15', t:'M15 RSI is below 65',          d:'Not entering extended momentum. RSI 65+ = wait for dip first.',            autoKey:'m15_rsi_level'},
          {tf:'m15', t:'Bull candle + Close > EMA8',   d:'Current M15 candle green and close above EMA8. Strong body preferred.',    autoKey:'m15_candle'},
          {tf:'vol',  t:'Volume > 1.3× 20-bar average', d:'Tick volume exceeds 1.3× 20-bar avg. Institutional confirmation.',        autoKey:'vol_spike'},
        ],
        SHORT: [
          {tf:'h1',  t:'EMA50 < EMA200 on H1',        d:'Macro bear trend confirmed. Check before session.',                         autoKey:'h1_ema_stack'},
          {tf:'h1',  t:'Price < EMA20 on H1',          d:'H1 close below EMA20. Price in lower half of bear structure.',             autoKey:'h1_price_ema20'},
          {tf:'h1',  t:'H1 RSI between 32 and 70',     d:'Not oversold on H1. RSI below 32 = skip all shorts.',                     autoKey:'h1_rsi'},
          {tf:'m15', t:'EMA8 < EMA21 on M15',          d:'Short-term M15 momentum bearish. If above — bounce still running.',       autoKey:'m15_ema_stack'},
          {tf:'m15', t:'M15 RSI crossed below 52',     d:'RSI was above 50 last bar, now ≤ 52. Failed bounce — SHORT trigger.',     autoKey:'m15_rsi_cross'},
          {tf:'m15', t:'M15 RSI is above 35',          d:'Not entering extreme oversold. RSI below 35 = skip short.',               autoKey:'m15_rsi_level'},
          {tf:'m15', t:'Bear candle + Close < EMA8',   d:'Current M15 candle red and close below EMA8.',                              autoKey:'m15_candle'},
          {tf:'vol',  t:'Volume > 1.3× 20-bar average', d:'Tick volume exceeds 1.3× 20-bar avg. Institutional confirmation.',        autoKey:'vol_spike'},
        ]
      },
      'bos_reversal': {
        LONG: [
          {tf:'h1',  t:'BOS_DOWN pattern detected',    d:'Break of Structure Down pattern identified on H1 timeframe.',              autoKey:'bos_pattern'},
          {tf:'m15', t:'Price below BOS breakdown',    d:'Current price below the breakdown level of BOS pattern.',                   autoKey:'bos_position'},
          {tf:'m15', t:'Volume > 1.5× 20-bar average', d:'Strong volume confirmation for reversal setup.',                            autoKey:'bos_volume'},
          {tf:'m15', t:'Bull candle body > 0.6',       d:'Strong bullish candle body ratio indicating reversal momentum.',            autoKey:'bos_body'},
          {tf:'m15', t:'RSI < 35 before reversal',    d:'Oversold condition before reversal setup.',                               autoKey:'bos_rsi'},
        ],
        SHORT: [
          {tf:'h1',  t:'BOS_UP pattern detected',      d:'Break of Structure Up pattern identified on H1 timeframe.',                autoKey:'bos_pattern'},
          {tf:'m15', t:'Price above BOS breakout',     d:'Current price above the breakout level of BOS pattern.',                    autoKey:'bos_position'},
          {tf:'m15', t:'Volume > 1.5× 20-bar average', d:'Strong volume confirmation for reversal setup.',                            autoKey:'bos_volume'},
          {tf:'m15', t:'Bear candle body > 0.6',       d:'Strong bearish candle body ratio indicating reversal momentum.',           autoKey:'bos_body'},
          {tf:'m15', t:'RSI > 65 before reversal',    d:'Overbought condition before reversal setup.',                               autoKey:'bos_rsi'},
        ]
      }
    };

    return strategies[strategyId] || strategies['scanner_8_condition'];
  }

  // Render condition cards
  renderConditionCards() {
    const grid = document.getElementById('cgrid');
    if (!grid) return;

    grid.innerHTML = '';
    
    const conditions = this.getStrategyConditions(this.currentStrategy);
    const strategyConditions = conditions[this.currentDirection] || [];

    strategyConditions.forEach((condition, index) => {
      const isChecked = this.isChecked(index);
      const isAuto = this.manualOverrides[`${this.currentDirection}_${index}`] === undefined;
      const card = document.createElement('div');
      card.className = `cc${isChecked ? ' ck' : ''}`;
      card.onclick = () => this.toggleCondition(index);

      const liveText = this.getLiveText(condition, index);
      const modeBadge = this.getModeBadge(isAuto);

      card.innerHTML = `
        <div class="cn">CONDITION ${index + 1} OF ${strategyConditions.length} ${modeBadge}</div>
        <div class="ctf ${condition.tf}">${condition.tf.toUpperCase()}</div>
        <div class="ctitle">${condition.t}</div>
        <div class="cdetail">${condition.d}</div>
        ${liveText}
      `;

      grid.appendChild(card);
    });

    this.updateSignalBox();
  }

  // Get live text for condition
  getLiveText(condition, index) {
    const autoCheck = this.autoChecks[`${this.currentDirection}_${index}`];
    if (autoCheck !== null && autoCheck !== undefined) {
      const status = autoCheck ? 'ok' : 'fail';
      const text = autoCheck ? '✓ Condition true on live data' : '✗ Not met on live data';
      return `<div class="clive ${status}">${text}</div>`;
    }
    return '<div class="clive">Connect feed for auto-detection</div>';
  }

  // Get mode badge
  getModeBadge(isAuto) {
    const mode = isAuto ? 'AUTO' : 'MANUAL';
    const className = isAuto ? 'auto' : 'manual';
    return `<span class="auto-badge ${className}">${mode}</span>`;
  }

  // Check if condition is checked
  isChecked(index) {
    return this.manualOverrides[`${this.currentDirection}_${index}`] === true;
  }

  // Toggle condition
  toggleCondition(index) {
    const key = `${this.currentDirection}_${index}`;
    this.manualOverrides[key] = !this.isChecked(index);
    this.renderConditionCards();
    this.saveState();
  }

  // Update signal box
  updateSignalBox() {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    const strategyConditions = conditions[this.currentDirection] || [];
    const totalConditions = strategyConditions.length;
    const checkedCount = this.getCheckedCount();

    const countElement = document.getElementById('sig-n');
    const labelElement = document.getElementById('sig-l');
    const descElement = document.getElementById('sig-a');
    const executeButton = document.getElementById('bd-scanner');

    countElement.textContent = `${checkedCount} / ${totalConditions}`;

    if (checkedCount === totalConditions) {
      this.setSignalStatus('ready', `ALL ${totalConditions} MET — SIGNAL CONFIRMED`, 
        '<strong style="color:var(--green)">✅ GO TO SIZER → CALCULATE LOTS → EXECUTE ON MT5</strong>');
      executeButton.classList.add('on');
    } else if (checkedCount >= Math.floor(totalConditions * 0.6)) {
      this.setSignalStatus('part', `PARTIAL — WAIT FOR ALL ${totalConditions}`, 
        `${totalConditions - checkedCount} more needed. Do NOT trade until all ${totalConditions} confirmed.`);
      executeButton.classList.remove('on');
    } else {
      this.setSignalStatus('idle', 'CONDITIONS MET', 
        'Click each condition as it becomes true on your MT5 chart.');
      executeButton.classList.remove('on');
    }
  }

  // Set signal status
  setSignalStatus(status, label, description) {
    const box = document.getElementById('sig-box');
    const labelElement = document.getElementById('sig-l');
    const descElement = document.getElementById('sig-a');

    box.className = status;
    labelElement.textContent = label;
    descElement.innerHTML = description;
  }

  // Get checked count
  getCheckedCount() {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    const strategyConditions = conditions[this.currentDirection] || [];
    
    return strategyConditions.reduce((count, _, index) => {
      return count + (this.isChecked(index) ? 1 : 0);
    }, 0);
  }

  // Save state
  saveState() {
    localStorage.setItem('scanner_manual_overrides', JSON.stringify(this.manualOverrides));
    localStorage.setItem('scanner_auto_checks', JSON.stringify(this.autoChecks));
    localStorage.setItem('scanner_current_strategy', this.currentStrategy);
    localStorage.setItem('scanner_current_direction', this.currentDirection);
  }

  // Load state
  loadState() {
    try {
      this.manualOverrides = JSON.parse(localStorage.getItem('scanner_manual_overrides') || '{}');
      this.autoChecks = JSON.parse(localStorage.getItem('scanner_auto_checks') || '{}');
      this.currentStrategy = localStorage.getItem('scanner_current_strategy') || 'scanner_8_condition';
      this.currentDirection = localStorage.getItem('scanner_current_direction') || 'LONG';
    } catch (e) {
      console.error('Error loading scanner state:', e);
    }
  }

  // Update strategy
  updateStrategy(strategyId) {
    this.currentStrategy = strategyId;
    this.renderConditionCards();
    this.saveState();
    this.updateStrategyInfo();
  }

  // Update strategy info
  updateStrategyInfo() {
    const info = document.getElementById('scanner-strategy-info');
    if (!info) return;

    const strategyData = this.getStrategyInfo(strategyId);
    if (strategyData) {
      info.innerHTML = `
        <strong>${strategyData.name}</strong><br>
        ${strategyData.timeframe} • ${strategyData.direction}<br>
        ${strategyData.performance}
      `;
    }
  }

  // Get strategy info
  getStrategyInfo(strategyId) {
    const strategies = {
      'scanner_8_condition': {
        name: '8-Condition Technical Strategy',
        timeframe: 'H1/M15',
        direction: 'trend_following',
        performance: '67.8% WR • 1.85R avg'
      },
      'bos_reversal': {
        name: 'BOS Reversal Strategy',
        timeframe: 'H1',
        direction: 'counter_trend',
        performance: '63.3% WR • 0.29R avg'
      },
      'session_volatility': {
        name: 'Session Volatility Breakout',
        timeframe: 'H1',
        direction: 'trend_following',
        performance: '32% higher volatility edge'
      }
    };

    return strategies[strategyId];
  }

  // Set direction
  setDirection(direction) {
    this.currentDirection = direction;
    this.renderConditionCards();
    this.saveState();
    
    // Update button states
    const longBtn = document.getElementById('btn-long');
    const shortBtn = document.getElementById('btn-short');
    
    if (direction === 'LONG') {
      longBtn.classList.add('gl');
      longBtn.classList.remove('gy');
      shortBtn.classList.add('gy');
      shortBtn.classList.remove('gl');
    } else {
      shortBtn.classList.add('gl');
      shortBtn.classList.remove('gy');
      longBtn.classList.add('gy');
      longBtn.classList.remove('gl');
    }
  }

  // Reset scan
  resetScan() {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    const strategyConditions = conditions[this.currentDirection] || [];
    
    strategyConditions.forEach((_, index) => {
      delete this.manualOverrides[`${this.currentDirection}_${index}`];
    });

    this.saveState();
    this.renderConditionCards();
  }

  // Initialize
  init() {
    this.loadState();
    this.renderConditionCards();
  }
}

// Global functions for button onclick handlers
function showPanel(panelName) {
  // Hide all panels
  document.querySelectorAll('.pnl').forEach(panel => {
    panel.classList.remove('on');
  });
  
  // Show selected panel
  const selectedPanel = document.getElementById(`pnl-${panelName}`);
  if (selectedPanel) {
    selectedPanel.classList.add('on');
  }
  
  // Update sidebar buttons
  document.querySelectorAll('.nb').forEach(btn => {
    btn.classList.remove('on');
  });
  
  const activeBtn = document.querySelector(`[data-panel="${panelName}"]`);
  if (activeBtn) {
    activeBtn.classList.add('on');
  }
}

function updateScannerStrategy() {
  const select = document.getElementById('scanner-strategy');
  if (select) {
    scannerComponent.updateStrategy(select.value);
  }
}

function setDir(direction) {
  scannerComponent.setDirection(direction);
}

function resetScan() {
  scannerComponent.resetScan();
}

function executeScan() {
  // Placeholder for trade execution
  console.log('Trade execution requested');
}

// Initialize scanner component
const scannerComponent = new ScannerComponent();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  scannerComponent.init();
});
