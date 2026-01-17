INSERT INTO events (event_name)
VALUES (:event_name)
RETURNING id_event, event_name, create_date, update_date;
