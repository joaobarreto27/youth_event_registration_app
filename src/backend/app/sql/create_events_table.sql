-- Tabela de Eventos para Registro de Eventos Juvenis
CREATE TABLE IF NOT EXISTS events (
    id_event SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL UNIQUE,
    create_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_create_date (create_date),
    INDEX idx_event_name (event_name)
);

-- Trigger para atualizar update_date automaticamente (se usar MySQL)
-- Para PostgreSQL, usar:
-- CREATE OR REPLACE FUNCTION update_events_timestamp()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.update_date = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER events_update_timestamp
-- BEFORE UPDATE ON events
-- FOR EACH ROW
-- EXECUTE FUNCTION update_events_timestamp();
