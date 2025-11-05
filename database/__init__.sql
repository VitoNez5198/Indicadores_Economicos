-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS indicator_values CASCADE;
DROP TABLE IF EXISTS indicators CASCADE;
DROP VIEW IF EXISTS latest_indicators;

-- Tabla de indicadores (catálogo)
CREATE TABLE indicators (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de valores históricos
CREATE TABLE indicator_values (
    id SERIAL PRIMARY KEY,
    indicator_id INT REFERENCES indicators(id) ON DELETE CASCADE,
    value NUMERIC(15, 4) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(indicator_id, date)
);

-- Índices para optimizar queries
CREATE INDEX idx_indicator_values_date ON indicator_values(date);
CREATE INDEX idx_indicator_values_indicator_id ON indicator_values(indicator_id);
CREATE INDEX idx_indicator_values_indicator_date ON indicator_values(indicator_id, date);

-- Vista útil: últimos valores de cada indicador
CREATE VIEW latest_indicators AS
SELECT DISTINCT ON (i.code)
    i.id,
    i.code,
    i.name,
    i.unit,
    iv.value,
    iv.date
FROM indicators i
LEFT JOIN indicator_values iv ON i.id = iv.indicator_id
ORDER BY i.code, iv.date DESC NULLS LAST;

-- Insertar indicadores iniciales
INSERT INTO indicators (code, name, unit) VALUES
('dolar', 'Dólar observado', 'CLP'),
('uf', 'Unidad de Fomento (UF)', 'CLP'),
('euro', 'Euro', 'CLP'),
('utm', 'Unidad Tributaria Mensual (UTM)', 'CLP'),
('ipc', 'Índice de Precios al Consumidor (IPC)', '%'),
('bitcoin', 'Bitcoin', 'USD');

-- Confirmar creación
SELECT * FROM indicators;