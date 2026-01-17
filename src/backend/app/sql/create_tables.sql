-- Tabela de Eventos para Registro de Eventos Juvenis
CREATE TABLE IF NOT EXISTS events (
    id_event SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL UNIQUE,
    create_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_create_date (create_date),
    INDEX idx_event_name (event_name)
);

-- Tabela de Participantes nos Eventos
CREATE TABLE IF NOT EXISTS event_participants (
    id_registration SERIAL PRIMARY KEY,
    id_event INT NOT NULL,
    participant_name VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Chave estrangeira para eventos
    FOREIGN KEY (id_event) REFERENCES events(id_event) ON DELETE CASCADE,

    -- Garantir que cada participante se registra apenas uma vez por evento
    UNIQUE KEY uq_event_participant (id_event, participant_name),

    -- Índices para melhor performance
    INDEX idx_event_id (id_event),
    INDEX idx_registration_date (registration_date)
);

-- Trigger para atualizar update_date da tabela events (PostgreSQL)
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
