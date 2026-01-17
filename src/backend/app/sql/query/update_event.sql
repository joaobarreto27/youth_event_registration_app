UPDATE events
SET event_name = COALESCE(:event_name, event_name),
WHERE id_event = :id_event
RETURNING id_event, event_name, create_date, update_date;
