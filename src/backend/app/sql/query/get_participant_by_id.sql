SELECT id_registration, id_event, participant_name, registration_date
FROM event_participants
WHERE id_registration = :id_registration;
