SELECT id_registration, id_event, participant_name, registration_date
FROM event_participants
WHERE id_event = :id_event
ORDER BY registration_date DESC;
