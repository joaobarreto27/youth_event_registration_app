DELETE FROM events
WHERE id_event = :id_event
RETURNING id_event;
