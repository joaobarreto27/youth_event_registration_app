UPDATE event_participants
SET participant_name = COALESCE(:participant_name, participant_name),
WHERE id_registration = :id_registration
RETURNING id_registration, id_event, participant_name, registration_date;
