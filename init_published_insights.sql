-- ============================================================================
-- INIT_PUBLISHED_INSIGHTS.sql
-- Inicializa tabla published_insights con esquema y datos de ejemplo
-- ============================================================================

-- Crear tabla (si no existe)
CREATE TABLE IF NOT EXISTS published_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_category TEXT NOT NULL,
    date_published DATE NOT NULL,
    next_available_date DATE NOT NULL,
    UNIQUE(insight_category, date_published)
);

-- Crear índices para velocidad de búsqueda
CREATE INDEX IF NOT EXISTS idx_published_insights_category 
    ON published_insights(insight_category);
CREATE INDEX IF NOT EXISTS idx_published_insights_next_available 
    ON published_insights(next_available_date);

-- (Opcional) Insertar categorías iniciales si están vacías
-- Esto es solo para referencia; el código Python maneja inserciones
INSERT OR IGNORE INTO published_insights 
    (insight_category, date_published, next_available_date)
VALUES
    ('explosion_anotadora_nba', '2026-04-10', '2026-05-01'),
    ('triple_doble_nba', '2026-04-10', '2026-05-01');

-- Verificar tabla
SELECT COUNT(*) as total_registros FROM published_insights;
SELECT * FROM published_insights ORDER BY date_published DESC LIMIT 5;
