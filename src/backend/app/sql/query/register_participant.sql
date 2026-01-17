INSERT INTO event_participants (id_event, participant_name)
VALUES (:id_event, :participant_name)
RETURNING id_registration, id_event, participant_name, registration_date;
