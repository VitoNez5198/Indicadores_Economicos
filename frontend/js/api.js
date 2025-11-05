// ==================== CONFIGURACIÓN ====================
const API_BASE_URL = 'http://localhost:5000/api';

// ==================== FUNCIONES API ====================

/**
 * Obtener todos los indicadores con su último valor
 */
async function fetchIndicators() {
    try {
        const response = await fetch(`${API_BASE_URL}/indicators`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Error fetching indicators:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Obtener histórico de un indicador específico
 * @param {string} code - Código del indicador (ej: 'dolar', 'uf')
 * @param {number} days - Número de días de histórico (default: 30)
 */
async function fetchIndicatorHistory(code, days = 30) {
    try {
        const response = await fetch(`${API_BASE_URL}/indicators/${code}/history?days=${days}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error(`Error fetching history for ${code}:`, error);
        return { success: false, error: error.message };
    }
}

/**
 * Obtener estadísticas de los últimos valores
 */
async function fetchLatestStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/latest`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Error fetching latest stats:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Health check del backend
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Backend health check failed:', error);
        return { success: false, error: error.message };
    }
}