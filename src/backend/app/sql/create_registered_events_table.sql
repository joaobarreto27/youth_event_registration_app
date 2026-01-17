CREATE TABLE registered_events (
    id_registered_event SERIAL PRIMARY KEY,
    id_event INT NOT NULL UNIQUE,
    event_name VARCHAR(255) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_event) REFERENCES events(id_event) ON DELETE CASCADE
);
