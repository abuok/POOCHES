// SCANNER TYPESCRIPT COMPONENT
// Dynamic strategy condition management with type safety

interface StrategyCondition {
  tf: string;
  t: string;
  d: string;
  autoKey: string;
}

interface StrategyData {
  name: string;
  timeframe: string;
  direction: string;
  performance: string;
}

interface StrategyConfig {
  [strategyId: string]: {
    LONG: StrategyCondition[];
    SHORT: StrategyCondition[];
  };
}

interface ManualOverrides {
  [key: string]: boolean;
}

interface AutoChecks {
  [key: string]: boolean | null;
}

interface SignalStatus {
  status: 'ready' | 'part' | 'idle';
  label: string;
  description: string;
}

class ScannerComponent {
  private currentStrategy: string = 'scanner_8_condition';
  private currentDirection: 'LONG' | 'SHORT' = 'LONG';
  private manualOverrides: ManualOverrides = {};
  private autoChecks: AutoChecks = {};

  // Strategy configuration with proper typing
  private readonly strategyConfig: StrategyConfig = {
    'scanner_8_condition': {
      LONG: [
        {tf:'h1', t:'EMA50 > EMA200 on H1', d:'Macro bull trend confirmed. Check before session opens.', autoKey:'h1_ema_stack'},
        {tf:'h1', t:'Price > EMA20 on H1', d:'H1 close above EMA20. Price in upper half of trend structure.', autoKey:'h1_price_ema20'},
        {tf:'h1', t:'H1 RSI between 30 and 68', d:'Not overbought on H1. RSI above 68 = skip all long setups today.', autoKey:'h1_rsi'},
        {tf:'m15', t:'EMA8 > EMA21 on M15', d:'Short-term M15 momentum bullish. If below — pullback still running.', autoKey:'m15_ema_stack'},
        {tf:'m15', t:'M15 RSI crossed above 48', d:'RSI was below 50 last bar, now ≥ 48. This IS the trigger.', autoKey:'m15_rsi_cross'},
        {tf:'m15', t:'M15 RSI is below 65', d:'Not entering extended momentum. RSI 65+ = wait for dip first.', autoKey:'m15_rsi_level'},
        {tf:'m15', t:'Bull candle + Close > EMA8', d:'Current M15 candle green and close above EMA8. Strong body preferred.', autoKey:'m15_candle'},
        {tf:'vol', t:'Volume > 1.3× 20-bar average', d:'Tick volume exceeds 1.3× 20-bar avg. Institutional confirmation.', autoKey:'vol_spike'},
      ],
      SHORT: [
        {tf:'h1', t:'EMA50 < EMA200 on H1', d:'Macro bear trend confirmed. Check before session.', autoKey:'h1_ema_stack'},
        {tf:'h1', t:'Price < EMA20 on H1', d:'H1 close below EMA20. Price in lower half of bear structure.', autoKey:'h1_price_ema20'},
        {tf:'h1', t:'H1 RSI between 32 and 70', d:'Not oversold on H1. RSI below 32 = skip all shorts.', autoKey:'h1_rsi'},
        {tf:'m15', t:'EMA8 < EMA21 on M15', d:'Short-term M15 momentum bearish. If above — bounce still running.', autoKey:'m15_ema_stack'},
        {tf:'m15', t:'M15 RSI crossed below 52', d:'RSI was above 50 last bar, now ≤ 52. Failed bounce — SHORT trigger.', autoKey:'m15_rsi_cross'},
        {tf:'m15', t:'M15 RSI is above 35', d:'Not entering extreme oversold. RSI below 35 = skip short.', autoKey:'m15_rsi_level'},
        {tf:'m15', t:'Bear candle + Close < EMA8', d:'Current M15 candle red and close below EMA8.', autoKey:'m15_candle'},
        {tf:'vol', t:'Volume > 1.3× 20-bar average', d:'Tick volume exceeds 1.3× 20-bar avg. Institutional confirmation.', autoKey:'vol_spike'},
      ]
    },
    'bos_reversal': {
      LONG: [
        {tf:'h1', t:'BOS_DOWN pattern detected', d:'Break of Structure Down pattern identified on H1 timeframe.', autoKey:'bos_pattern'},
        {tf:'m15', t:'Price below BOS breakdown', d:'Current price below the breakdown level of BOS pattern.', autoKey:'bos_position'},
        {tf:'m15', t:'Volume > 1.5× 20-bar average', d:'Strong volume confirmation for reversal setup.', autoKey:'bos_volume'},
        {tf:'m15', t:'Bull candle body > 0.6', d:'Strong bullish candle body ratio indicating reversal momentum.', autoKey:'bos_body'},
        {tf:'m15', t:'RSI < 35 before reversal', d:'Oversold condition before reversal setup.', autoKey:'bos_rsi'},
      ],
      SHORT: [
        {tf:'h1', t:'BOS_UP pattern detected', d:'Break of Structure Up pattern identified on H1 timeframe.', autoKey:'bos_pattern'},
        {tf:'m15', t:'Price above BOS breakout', d:'Current price above the breakout level of BOS pattern.', autoKey:'bos_position'},
        {tf:'m15', t:'Volume > 1.5× 20-bar average', d:'Strong volume confirmation for reversal setup.', autoKey:'bos_volume'},
        {tf:'m15', t:'Bear candle body > 0.6', d:'Strong bearish candle body ratio indicating reversal momentum.', autoKey:'bos_body'},
        {tf:'m15', t:'RSI > 65 before reversal', d:'Overbought condition before reversal setup.', autoKey:'bos_rsi'},
      ]
    }
  };

  private readonly strategyInfo: { [key: string]: StrategyData } = {
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
    }
  };

  constructor() {
    this.loadState();
  }

  // Get strategy conditions with type safety
  private getStrategyConditions(strategyId: string): StrategyCondition[] {
    return this.strategyConfig[strategyId]?.[this.currentDirection] || this.strategyConfig['scanner_8_condition'][this.currentDirection] || [];
  }

  // Get strategy info with type safety
  private getStrategyInfo(strategyId: string): StrategyData | null {
    return this.strategyInfo[strategyId] || null;
  }

  // Render condition cards with type safety
  renderConditionCards(): void {
    const grid = document.getElementById('cgrid');
    if (!grid) return;

    grid.innerHTML = '';
    
    const conditions = this.getStrategyConditions(this.currentStrategy);

    conditions.forEach((condition, index) => {
      const isChecked = this.isChecked(index);
      const isAuto = this.manualOverrides[`${this.currentDirection}_${index}`] === undefined;
      const autoCheck = this.autoChecks[`${this.currentDirection}_${index}`];
      const card = document.createElement('div');
      card.className = `cc${isChecked ? ' ck' : ''}`;
      card.onclick = () => this.toggleCondition(index);

      const liveText = this.getLiveText(condition, index, autoCheck);
      const modeBadge = this.getModeBadge(isAuto);

      card.innerHTML = `
        <div class="cn">CONDITION ${index + 1} OF ${conditions.length} ${modeBadge}</div>
        <div class="ctf ${condition.tf}">${condition.tf.toUpperCase()}</div>
        <div class="ctitle">${condition.t}</div>
        <div class="cdetail">${condition.d}</div>
        ${liveText}
      `;

      grid.appendChild(card);
    });

    this.updateSignalBox();
  }

  // Get live text with type safety
  private getLiveText(condition: StrategyCondition, index: number, autoCheck: boolean | null): string {
    if (autoCheck !== null && autoCheck !== undefined) {
      const status = autoCheck ? 'ok' : 'fail';
      const text = autoCheck ? '✓ Condition true on live data' : '✗ Not met on live data';
      return `<div class="clive ${status}">${text}</div>`;
    }
    return '<div class="clive">Connect feed for auto-detection</div>';
  }

  // Get mode badge with type safety
  private getModeBadge(isAuto: boolean): string {
    const mode = isAuto ? 'AUTO' : 'MANUAL';
    const className = isAuto ? 'auto' : 'manual';
    return `<span class="auto-badge ${className}">${mode}</span>`;
  }

  // Check if condition is checked with type safety
  private isChecked(index: number): boolean {
    return this.manualOverrides[`${this.currentDirection}_${index}`] === true;
  }

  // Toggle condition with type safety
  private toggleCondition(index: number): void {
    const key = `${this.currentDirection}_${index}`;
    this.manualOverrides[key] = !this.isChecked(index);
    this.renderConditionCards();
    this.saveState();
  }

  // Update signal box with type safety
  private updateSignalBox(): void {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    const totalConditions = conditions.length;
    const checkedCount = this.getCheckedCount();

    const countElement = document.getElementById('sig-n') as HTMLElement;
    const labelElement = document.getElementById('sig-l') as HTMLElement;
    const descElement = document.getElementById('sig-a') as HTMLElement;
    const executeButton = document.getElementById('bd-scanner') as HTMLElement;

    if (!countElement || !labelElement || !descElement || !executeButton) return;

    countElement.textContent = `${checkedCount} / ${totalConditions}`;

    const signalStatus = this.getSignalStatus(checkedCount, totalConditions);
    this.setSignalStatus(signalStatus.status, signalStatus.label, signalStatus.description);

    if (signalStatus.status === 'ready') {
      executeButton.classList.add('on');
    } else {
      executeButton.classList.remove('on');
    }
  }

  // Get signal status with type safety
  private getSignalStatus(checkedCount: number, totalConditions: number): SignalStatus {
    if (checkedCount === totalConditions) {
      return {
        status: 'ready',
        label: `ALL ${totalConditions} MET — SIGNAL CONFIRMED`,
        description: '<strong style="color:var(--green)">✅ GO TO SIZER → CALCULATE LOTS → EXECUTE ON MT5</strong>'
      };
    } else if (checkedCount >= Math.floor(totalConditions * 0.6)) {
      return {
        status: 'part',
        label: `PARTIAL — WAIT FOR ALL ${totalConditions}`,
        description: `${totalConditions - checkedCount} more needed. Do NOT trade until all ${totalConditions} confirmed.`
      };
    } else {
      return {
        status: 'idle',
        label: 'CONDITIONS MET',
        description: 'Click each condition as it becomes true on your MT5 chart.'
      };
    }
  }

  // Set signal status with type safety
  private setSignalStatus(status: string, label: string, description: string): void {
    const box = document.getElementById('sig-box') as HTMLElement;
    const labelElement = document.getElementById('sig-l') as HTMLElement;
    const descElement = document.getElementById('sig-a') as HTMLElement;

    if (!box || !labelElement || !descElement) return;

    box.className = status;
    labelElement.textContent = label;
    descElement.innerHTML = description;
  }

  // Get checked count with type safety
  private getCheckedCount(): number {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    
    return conditions.reduce((count, _, index) => {
      return count + (this.isChecked(index) ? 1 : 0);
    }, 0);
  }

  // Save state with type safety
  private saveState(): void {
    try {
      localStorage.setItem('scanner_manual_overrides', JSON.stringify(this.manualOverrides));
      localStorage.setItem('scanner_auto_checks', JSON.stringify(this.autoChecks));
      localStorage.setItem('scanner_current_strategy', this.currentStrategy);
      localStorage.setItem('scanner_current_direction', this.currentDirection);
    } catch (error) {
      console.error('Error saving scanner state:', error);
    }
  }

  // Load state with type safety
  private loadState(): void {
    try {
      const manualOverrides = localStorage.getItem('scanner_manual_overrides');
      const autoChecks = localStorage.getItem('scanner_auto_checks');
      const currentStrategy = localStorage.getItem('scanner_current_strategy');
      const currentDirection = localStorage.getItem('scanner_current_direction');

      if (manualOverrides) this.manualOverrides = JSON.parse(manualOverrides);
      if (autoChecks) this.autoChecks = JSON.parse(autoChecks);
      if (currentStrategy) this.currentStrategy = currentStrategy;
      if (currentDirection) this.currentDirection = currentDirection as 'LONG' | 'SHORT';
    } catch (error) {
      console.error('Error loading scanner state:', error);
    }
  }

  // Update strategy with type safety
  updateStrategy(strategyId: string): void {
    this.currentStrategy = strategyId;
    this.renderConditionCards();
    this.saveState();
    this.updateStrategyInfo();
  }

  // Update strategy info with type safety
  private updateStrategyInfo(): void {
    const info = document.getElementById('scanner-strategy-info') as HTMLElement;
    if (!info) return;

    const strategyData = this.getStrategyInfo(this.currentStrategy);
    if (strategyData) {
      info.innerHTML = `
        <strong>${strategyData.name}</strong><br>
        ${strategyData.timeframe} • ${strategyData.direction}<br>
        ${strategyData.performance}
      `;
    }
  }

  // Set direction with type safety
  setDirection(direction: 'LONG' | 'SHORT'): void {
    this.currentDirection = direction;
    this.renderConditionCards();
    this.saveState();
    this.updateDirectionButtons();
  }

  // Update direction buttons with type safety
  private updateDirectionButtons(): void {
    const longBtn = document.getElementById('btn-long') as HTMLElement;
    const shortBtn = document.getElementById('btn-short') as HTMLElement;

    if (!longBtn || !shortBtn) return;

    if (this.currentDirection === 'LONG') {
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

  // Reset scan with type safety
  resetScan(): void {
    const conditions = this.getStrategyConditions(this.currentStrategy);
    
    conditions.forEach((_, index) => {
      delete this.manualOverrides[`${this.currentDirection}_${index}`];
    });

    this.saveState();
    this.renderConditionCards();
  }

  // Initialize with type safety
  init(): void {
    this.loadState();
    this.renderConditionCards();
  }
}

// Global functions with type safety
function showPanel(panelName: string): void {
  // Hide all panels
  document.querySelectorAll('.pnl').forEach(panel => {
    panel.classList.remove('on');
  });
  
  // Show selected panel
  const selectedPanel = document.getElementById(`pnl-${panelName}`) as HTMLElement;
  if (selectedPanel) {
    selectedPanel.classList.add('on');
  }
  
  // Update sidebar buttons
  document.querySelectorAll('.nb').forEach(btn => {
    btn.classList.remove('on');
  });
  
  const activeBtn = document.querySelector(`[data-panel="${panelName}"]`) as HTMLElement;
  if (activeBtn) {
    activeBtn.classList.add('on');
  }
}

function updateScannerStrategy(): void {
  const select = document.getElementById('scanner-strategy') as HTMLSelectElement;
  if (select) {
    scannerComponent.updateStrategy(select.value);
  }
}

function setDir(direction: 'LONG' | 'SHORT'): void {
  scannerComponent.setDirection(direction);
}

function resetScan(): void {
  scannerComponent.resetScan();
}

function executeScan(): void {
  console.log('Trade execution requested');
}

// Initialize scanner component with type safety
const scannerComponent = new ScannerComponent();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', (): void => {
  scannerComponent.init();
});
