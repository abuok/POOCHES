/**
 * Dashboard Utilities - Shared JavaScript functions
 * Eliminates code duplication between dashboard files
 */

// Global error boundary
window.addEventListener('error', function(e) {
    console.error('Global error caught:', e.error);
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'block';
        errorContainer.innerHTML = `<div class="error-message">⚠️ Error: ${e.error?.message || 'Unknown error'}</div>`;
    }
});

// Clock update function
function updateClock() {
    try {
        const now = new Date();
        const clockEl = document.getElementById('clk');
        const dateEl = document.getElementById('clkd');
        
        if (clockEl) {
            clockEl.textContent = now.toLocaleTimeString('en-GB', { hour12: false });
        }
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('en-GB', { 
                weekday: 'short', 
                day: 'numeric', 
                month: 'short' 
            });
        }
    } catch (error) {
        console.error('Clock update error:', error);
    }
}

// Price update function with error handling
function updatePrice(price, change, changePercent) {
    try {
        const priceEl = document.getElementById('live-price');
        const changeEl = document.getElementById('price-chg');
        
        if (priceEl) {
            priceEl.textContent = price.toFixed(2);
            priceEl.className = change >= 0 ? 'up' : 'dn';
        }
        
        if (changeEl) {
            const sign = change >= 0 ? '+' : '';
            changeEl.textContent = `${sign}${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
            changeEl.className = change >= 0 ? 'up' : 'dn';
        }
    } catch (error) {
        console.error('Price update error:', error);
    }
}

// Session management
function updateSession() {
    try {
        const hour = new Date().getUTCHours();
        let session = 'Asian';
        if (hour >= 7 && hour < 12) session = 'London';
        else if (hour >= 12 && hour < 17) session = 'NY';
        else if (hour >= 17 && hour < 22) session = 'NY_Evening';
        
        const sessionEl = document.getElementById('sess-badge');
        if (sessionEl) {
            sessionEl.textContent = session;
            sessionEl.className = session.toLowerCase().replace('_', '-');
        }
    } catch (error) {
        console.error('Session update error:', error);
    }
}

// Direction toggle
let currentDirection = 'LONG';
function setDir(direction) {
    try {
        currentDirection = direction;
        const longBtn = document.getElementById('dtb-long');
        const shortBtn = document.getElementById('dtb-short');
        
        if (longBtn && shortBtn) {
            longBtn.className = direction === 'LONG' ? 'dtb on long' : 'dtb long';
            shortBtn.className = direction === 'SHORT' ? 'dtb on short' : 'dtb short';
        }
    } catch (error) {
        console.error('Direction toggle error:', error);
    }
}

// Manual refresh with error boundary
function manualRefresh() {
    try {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.textContent = 'Loading...';
        }
        
        // Simulate data refresh
        setTimeout(() => {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '↺ Refresh';
            }
            updateLastUpdated();
        }, 1000);
    } catch (error) {
        console.error('Refresh error:', error);
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.textContent = '↺ Refresh';
        }
    }
}

// Update last updated timestamp
function updateLastUpdated() {
    try {
        const lastUpdatedEl = document.getElementById('last-updated');
        if (lastUpdatedEl) {
            lastUpdatedEl.textContent = 'Updated: ' + new Date().toLocaleTimeString();
        }
    } catch (error) {
        console.error('Update timestamp error:', error);
    }
}

// Initialize dashboard
function initDashboard() {
    try {
        // Start clock
        updateClock();
        setInterval(updateClock, 1000);
        
        // Update session
        updateSession();
        setInterval(updateSession, 60000);
        
        // Update last updated
        updateLastUpdated();
        
        console.log('✅ Dashboard initialized successfully');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

// Memory management - cleanup function
function cleanupEventListeners() {
    try {
        // Remove old event listeners to prevent memory leaks
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });
    } catch (error) {
        console.error('Cleanup error:', error);
    }
}

// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateClock,
        updatePrice,
        updateSession,
        setDir,
        manualRefresh,
        updateLastUpdated,
        initDashboard,
        cleanupEventListeners
    };
}
