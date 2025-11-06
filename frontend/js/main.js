// ==================== ESTADO GLOBAL ====================
let allIndicators = [];
let currentIndicator = null;
let currentDays = 30; // Default 30 días

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando aplicación...');
    
    const healthCheck = await checkBackendHealth();
    if (!healthCheck.success) {
        showError('No se puede conectar con el backend. Verifica que esté corriendo en http://localhost:5000');
        return;
    }
    
    await loadInitialData();
    setupEventListeners();
    
    console.log('✅ Aplicación iniciada correctamente');
});

async function loadInitialData() {
    showLoading();
    
    try {
        const response = await fetchIndicators();
        
        if (!response.success) {
            throw new Error(response.error);
        }
        
        allIndicators = response.data;
        
        renderStatsCards(allIndicators);
        updateLastUpdateTime();
        
        hideLoading();
        showContent();
        
        // Auto-cargar el primer indicador con datos
        const firstIndicator = allIndicators.find(ind => ind.latest_value !== null);
        if (firstIndicator) {
            loadIndicatorChart(firstIndicator.code);
        }
        
    } catch (error) {
        console.error('Error loading initial data:', error);
        showError('Error al cargar los datos: ' + error.message);
    }
}

// ==================== UI STATES ====================

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('stats-section').classList.add('hidden');
    document.getElementById('chart-section').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    hideLoading();
    const errorDiv = document.getElementById('error');
    errorDiv.querySelector('p').textContent = '❌ ' + message;
    errorDiv.classList.remove('hidden');
}

function showContent() {
    document.getElementById('stats-section').classList.remove('hidden');
    document.getElementById('chart-section').classList.remove('hidden');
}

// ==================== RENDER FUNCTIONS ====================

function renderStatsCards(indicators) {
    const container = document.getElementById('stats-cards');
    container.innerHTML = '';
    
    const validIndicators = indicators.filter(ind => ind.latest_value !== null);
    
    validIndicators.forEach(indicator => {
        const card = createStatCard(indicator);
        container.appendChild(card);
    });
}

function createStatCard(indicator) {
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.dataset.code = indicator.code;
    card.onclick = () => loadIndicatorChart(indicator.code);
    
    const formattedValue = formatCurrency(indicator.latest_value, indicator.unit);
    const formattedDate = indicator.latest_date 
        ? new Date(indicator.latest_date).toLocaleDateString('es-CL')
        : 'Sin fecha';
    
    card.innerHTML = `
        <div class="stat-card-header">
            <span class="stat-card-code">${indicator.code}</span>
        </div>
        <div class="stat-card-name">${indicator.name}</div>
        <div class="stat-card-value">${formattedValue}</div>
        <div class="stat-card-date">Actualizado: ${formattedDate}</div>
    `;
    
    return card;
}

// ==================== CHART FUNCTIONS ====================

async function loadIndicatorChart(code) {
    console.log(`📈 Cargando gráfico para: ${code}`);
    
    // Actualizar UI: marcar card activo
    document.querySelectorAll('.stat-card').forEach(card => {
        card.classList.remove('active');
    });
    const activeCard = document.querySelector(`[data-code="${code}"]`);
    if (activeCard) {
        activeCard.classList.add('active');
    }
    
    // Actualizar título
    const indicator = allIndicators.find(ind => ind.code === code);
    if (indicator) {
        document.getElementById('chart-title').textContent = `🪙​ ​​${indicator.name} 🪙​`;
    }
    
    // Mostrar loading en el gráfico
    const chartContainer = document.querySelector('.chart-container');
    chartContainer.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
            <div class="spinner"></div>
        </div>
    `;
    
    try {
        const response = await fetchIndicatorHistory(code, currentDays);
        
        if (!response.success) {
            throw new Error(response.error);
        }
        
        const historyData = response.data;
        
        if (!historyData.values || historyData.values.length === 0) {
            chartContainer.innerHTML = `
                <div class="chart-placeholder">
                    <p class="chart-placeholder-icon">📊</p>
                    <p class="chart-placeholder-text">Sin datos históricos disponibles</p>
                </div>
            `;
            return;
        }
        
        const labels = historyData.values.map(v => {
            const date = new Date(v.date);
            return date.toLocaleDateString('es-CL', { 
                day: '2-digit', 
                month: 'short' 
            });
        });
        
        const data = historyData.values.map(v => v.value);
        
        chartContainer.innerHTML = '<canvas id="main-chart"></canvas>';
        createOrUpdateChart(labels, data, historyData.indicator.name);
        
        currentIndicator = code;
        
    } catch (error) {
        console.error('Error loading chart:', error);
        chartContainer.innerHTML = `
            <div class="chart-placeholder">
                <p class="chart-placeholder-icon">❌</p>
                <p class="chart-placeholder-text">Error: ${error.message}</p>
            </div>
        `;
    }
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Botones de período
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Actualizar botones activos
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Actualizar días y recargar gráfico
            currentDays = parseInt(e.target.dataset.days);
            if (currentIndicator) {
                loadIndicatorChart(currentIndicator);
            }
        });
    });
}

// ==================== UTILITY FUNCTIONS ====================

function formatCurrency(value, unit) {
    if (value === null || value === undefined) {
        return '-';
    }
    
    const formatted = new Intl.NumberFormat('es-CL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
    
    if (unit === 'CLP') {
        return `$${formatted}`;
    }
    
    if (unit === '%') {
        return `${formatted}%`;
    }
    
    return `${formatted} ${unit || ''}`;
}

function updateLastUpdateTime() {
    const lastUpdateSpan = document.getElementById('last-update');
    const now = new Date();
    lastUpdateSpan.textContent = now.toLocaleString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

window.appFunctions = {
    loadIndicatorChart,
    loadInitialData,
    formatCurrency
};

console.log('✅ main.js cargado correctamente');