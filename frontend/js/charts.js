// ==================== CONFIGURACIÓN DE CHART.JS ====================

let mainChart = null; // Variable global para el gráfico principal

/**
 * Configuración base para los gráficos
 */
const chartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',
        intersect: false,
    },
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                color: '#e4e7eb',
                font: {
                    size: 12,
                    family: 'Inter'
                },
                padding: 15
            }
        },
        tooltip: {
            backgroundColor: 'rgba(10, 14, 39, 0.9)',
            titleColor: '#e4e7eb',
            bodyColor: '#e4e7eb',
            borderColor: 'rgba(59, 130, 246, 0.5)',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += new Intl.NumberFormat('es-CL').format(context.parsed.y);
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(255, 255, 255, 0.05)',
                drawBorder: false
            },
            ticks: {
                color: '#9ca3af',
                font: {
                    size: 11
                }
            }
        },
        y: {
            grid: {
                color: 'rgba(255, 255, 255, 0.05)',
                drawBorder: false
            },
            ticks: {
                color: '#9ca3af',
                font: {
                    size: 11
                },
                callback: function(value) {
                    return new Intl.NumberFormat('es-CL', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2
                    }).format(value);
                }
            }
        }
    }
};

/**
 * Crear o actualizar el gráfico principal
 * @param {Array} labels - Etiquetas del eje X (fechas)
 * @param {Array} data - Datos del eje Y (valores)
 * @param {string} label - Nombre del indicador
 */
function createOrUpdateChart(labels, data, label) {
    const ctx = document.getElementById('main-chart');
    
    if (!ctx) {
        console.error('Canvas element not found');
        return;
    }

    // Si ya existe un gráfico, destruirlo
    if (mainChart) {
        mainChart.destroy();
    }

    // Crear nuevo gráfico
    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.reverse(), // Invertir para mostrar de más antiguo a más reciente
            datasets: [{
                label: label,
                data: data.reverse(),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: chartConfig
    });
}

/**
 * Mostrar mensaje cuando no hay datos para graficar
 */
function showNoDataMessage() {
    const container = document.querySelector('.chart-container');
    if (container) {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #9ca3af;">
                <p style="font-size: 1.2rem; margin-bottom: 8px;">📊 Sin datos</p>
                <p>Selecciona un indicador para ver su histórico</p>
            </div>
        `;
    }
}