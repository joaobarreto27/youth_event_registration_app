DELETE FROM event_participants
WHERE id_registration = :id_registration
RETURNING id_registration;
