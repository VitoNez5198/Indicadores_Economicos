// ==================== ESTADO GLOBAL ====================
let allIndicators = [];
let currentIndicator = null;

// ==================== INICIALIZACIÓN ====================

/**
 * Función principal que se ejecuta al cargar la página
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando aplicación...');
    
    // Verificar salud del backend
    const healthCheck = await checkBackendHealth();
    if (!healthCheck.success) {
        showError('No se puede conectar con el backend. Verifica que esté corriendo en http://localhost:5000');
        return;
    }
    
    // Cargar datos iniciales
    await loadInitialData();
    
    // Configurar event listeners
    setupEventListeners();
    
    console.log('✅ Aplicación iniciada correctamente');
});

/**
 * Cargar datos iniciales del backend
 */
async function loadInitialData() {
    showLoading();
    
    try {
        // Obtener todos los indicadores
        const response = await fetchIndicators();
        
        if (!response.success) {
            throw new Error(response.error);
        }
        
        allIndicators = response.data;
        
        // Renderizar componentes
        renderStatsCards(allIndicators);
        renderTable(allIndicators);
        populateIndicatorSelect(allIndicators);
        updateLastUpdateTime();
        
        // Mostrar secciones
        hideLoading();
        showContent();
        
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
    document.getElementById('table-section').classList.add('hidden');
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
    document.getElementById('table-section').classList.remove('hidden');
}

// ==================== RENDER FUNCTIONS ====================

/**
 * Renderizar tarjetas de estadísticas
 */
function renderStatsCards(indicators) {
    const container = document.getElementById('stats-cards');
    container.innerHTML = '';
    
    // Filtrar solo indicadores con valores
    const validIndicators = indicators.filter(ind => ind.latest_value !== null);
    
    validIndicators.forEach(indicator => {
        const card = createStatCard(indicator);
        container.appendChild(card);
    });
}

/**
 * Crear una tarjeta de estadística individual
 */
function createStatCard(indicator) {
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.onclick = () => loadIndicatorChart(indicator.code);
    
    // Formatear valor
    const formattedValue = formatCurrency(indicator.latest_value, indicator.unit);
    
    // Formatear fecha
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

/**
 * Renderizar tabla de indicadores
 */
function renderTable(indicators) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';
    
    indicators.forEach(indicator => {
        const row = createTableRow(indicator);
        tbody.appendChild(row);
    });
}

/**
 * Crear fila de tabla individual
 */
function createTableRow(indicator) {
    const row = document.createElement('tr');
    
    const formattedValue = indicator.latest_value !== null
        ? formatCurrency(indicator.latest_value, indicator.unit)
        : '-';
    
    const formattedDate = indicator.latest_date
        ? new Date(indicator.latest_date).toLocaleDateString('es-CL')
        : '-';
    
    row.innerHTML = `
        <td><span class="table-code">${indicator.code}</span></td>
        <td>${indicator.name}</td>
        <td><span class="table-value">${formattedValue}</span></td>
        <td>${indicator.unit || '-'}</td>
        <td>${formattedDate}</td>
        <td>
            <button class="btn-chart" onclick="loadIndicatorChart('${indicator.code}')">
                Ver Gráfico
            </button>
        </td>
    `;
    
    return row;
}

/**
 * Poblar el select de indicadores
 */
function populateIndicatorSelect(indicators) {
    const select = document.getElementById('indicator-select');
    
    // Limpiar opciones anteriores (excepto la primera)
    select.innerHTML = '<option value="">Selecciona un indicador</option>';
    
    // Agregar indicadores
    indicators.forEach(indicator => {
        const option = document.createElement('option');
        option.value = indicator.code;
        option.textContent = `${indicator.name} (${indicator.code})`;
        select.appendChild(option);
    });
}

// ==================== CHART FUNCTIONS ====================

/**
 * Cargar y mostrar gráfico de un indicador
 */
async function loadIndicatorChart(code) {
    console.log(`📈 Cargando gráfico para: ${code}`);
    
    // Obtener días seleccionados
    const daysSelect = document.getElementById('days-select');
    const days = parseInt(daysSelect.value) || 30;
    
    // Actualizar select
    const indicatorSelect = document.getElementById('indicator-select');
    indicatorSelect.value = code;
    
    // Mostrar loading en el gráfico
    const chartContainer = document.querySelector('.chart-container');
    chartContainer.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
            <div class="spinner"></div>
        </div>
    `;
    
    try {
        // Fetch histórico
        const response = await fetchIndicatorHistory(code, days);
        
        if (!response.success) {
            throw new Error(response.error);
        }
        
        const historyData = response.data;
        
        // Verificar que haya datos
        if (!historyData.values || historyData.values.length === 0) {
            chartContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #9ca3af;">
                    <p style="font-size: 1.2rem; margin-bottom: 8px;">📊 Sin datos históricos</p>
                    <p>No hay datos disponibles para este indicador en el período seleccionado</p>
                </div>
            `;
            return;
        }
        
        // Preparar datos para Chart.js
        const labels = historyData.values.map(v => {
            const date = new Date(v.date);
            return date.toLocaleDateString('es-CL', { 
                day: '2-digit', 
                month: 'short' 
            });
        });
        
        const data = historyData.values.map(v => v.value);
        
        // Restaurar canvas
        chartContainer.innerHTML = '<canvas id="main-chart"></canvas>';
        
        // Crear gráfico
        createOrUpdateChart(labels, data, historyData.indicator.name);
        
        // Scroll suave al gráfico
        chartContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        currentIndicator = code;
        
    } catch (error) {
        console.error('Error loading chart:', error);
        chartContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #ef4444;">
                <p style="font-size: 1.2rem; margin-bottom: 8px;">❌ Error</p>
                <p>No se pudo cargar el gráfico: ${error.message}</p>
            </div>
        `;
    }
}

// ==================== EVENT LISTENERS ====================

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Select de indicadores
    const indicatorSelect = document.getElementById('indicator-select');
    indicatorSelect.addEventListener('change', (e) => {
        const code = e.target.value;
        if (code) {
            loadIndicatorChart(code);
        } else {
            showNoDataMessage();
        }
    });
    
    // Select de días
    const daysSelect = document.getElementById('days-select');
    daysSelect.addEventListener('change', () => {
        if (currentIndicator) {
            loadIndicatorChart(currentIndicator);
        }
    });
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Formatear valor monetario
 */
function formatCurrency(value, unit) {
    if (value === null || value === undefined) {
        return '-';
    }
    
    const formatted = new Intl.NumberFormat('es-CL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
    
    // Si la unidad es CLP, agregar símbolo $
    if (unit === 'CLP') {
        return `$${formatted}`;
    }
    
    // Si es porcentaje
    if (unit === '%') {
        return `${formatted}%`;
    }
    
    // Si es USD u otra moneda
    return `${formatted} ${unit || ''}`;
}

/**
 * Actualizar timestamp de última actualización
 */
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

/**
 * Calcular variación porcentual (para futuras mejoras)
 */
function calculateChange(current, previous) {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous) * 100;
}

// ==================== EXPORT PARA TESTING ====================
// Si necesitas usar estas funciones en la consola del navegador
window.appFunctions = {
    loadIndicatorChart,
    loadInitialData,
    formatCurrency
};

console.log('✅ main.js cargado correctamente');