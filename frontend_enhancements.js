
// Frontend Geliştirmeleri - index.html'e eklenecek JavaScript

// Gelişmiş analitik butonları ekle
function addAdvancedButtons() {
    const inputArea = document.querySelector('.input-area');
    
    const advancedPanel = document.createElement('div');
    advancedPanel.className = 'advanced-panel';
    advancedPanel.innerHTML = `
        <div class="advanced-buttons">
            <button onclick="requestAdvancedAnalysis()" class="advanced-btn analytics">
                📊 Gelişmiş Analiz
            </button>
            <button onclick="requestInsights()" class="advanced-btn insights">
                💡 Akıllı İçgörüler
            </button>
            <button onclick="requestForecast()" class="advanced-btn forecast">
                🔮 Tahmin
            </button>
            <button onclick="requestRecommendations()" class="advanced-btn recommendations">
                🎯 Öneriler
            </button>
        </div>
    `;
    
    inputArea.parentNode.insertBefore(advancedPanel, inputArea);
}

// Gelişmiş analiz istekleri
async function requestAdvancedAnalysis() {
    const query = "Kapsamlı veri analizi yap";
    await sendAdvancedQuery(query, 'comprehensive');
}

async function requestInsights() {
    const query = "Anomali tespiti ve kritik içgörüler";
    await sendAdvancedQuery(query, 'insights');
}

async function requestForecast() {
    const query = "Trend analizi ve gelecek tahminleri";
    await sendAdvancedQuery(query, 'forecast');
}

async function requestRecommendations() {
    const query = "Aksiyon önerileri ve iyileştirme planı";
    await sendAdvancedQuery(query, 'recommendations');
}

async function sendAdvancedQuery(query, type) {
    try {
        addMessage(query, 'user');
        
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai', 'thinking');
        thinkingDiv.textContent = 'Gelişmiş analiz yapılıyor...';
        document.getElementById('chat-container').appendChild(thinkingDiv);
        
        const response = await fetch('/api/advanced-analytics', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query, analysis_type: type})
        });
        
        thinkingDiv.remove();
        
        if (response.ok) {
            const result = await response.json();
            addMessage(result.text, 'ai', result.chart);
        } else {
            addMessage('Gelişmiş analiz sırasında bir hata oluştu.', 'ai');
        }
        
    } catch (error) {
        console.error('Advanced analytics error:', error);
        addMessage('Bağlantı hatası oluştu.', 'ai');
    }
}

// Sistem durumu kontrolü
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        if (response.ok) {
            const status = await response.json();
            updateSystemStatusIndicator(status);
        }
    } catch (error) {
        console.error('System status error:', error);
    }
}

function updateSystemStatusIndicator(status) {
    const header = document.querySelector('.header');
    const statusIndicator = document.createElement('div');
    statusIndicator.className = 'system-status';
    
    const activeFeatures = Object.keys(status).filter(key => 
        status[key] === true && key !== 'last_updated'
    ).length;
    
    statusIndicator.innerHTML = `
        <span class="status-badge ${activeFeatures >= 3 ? 'advanced' : 'basic'}">
            ${activeFeatures >= 3 ? '🚀 Gelişmiş' : '📊 Temel'} Mod
        </span>
    `;
    
    header.appendChild(statusIndicator);
}

// CSS Stilleri
const advancedStyles = `
.advanced-panel {
    padding: 1rem 2rem;
    background: rgba(26, 27, 35, 0.6);
    border-bottom: 1px solid var(--border);
}

.advanced-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.advanced-btn {
    padding: 0.5rem 1rem;
    border: 1px solid var(--primary);
    background: rgba(0, 212, 255, 0.1);
    color: var(--primary);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.advanced-btn:hover {
    background: rgba(0, 212, 255, 0.2);
    transform: translateY(-1px);
}

.system-status {
    display: flex;
    align-items: center;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.status-badge.advanced {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-badge.basic {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
`;

// Stilleri sayfaya ekle
const styleSheet = document.createElement('style');
styleSheet.textContent = advancedStyles;
document.head.appendChild(styleSheet);

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', function() {
    addAdvancedButtons();
    checkSystemStatus();
});
