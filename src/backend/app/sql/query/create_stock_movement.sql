INSERT INTO stock_movements (id_product, movement_type, quantity, total_value, movement_date) VALUES (:id_product, :movement_type, :quantity,:total_value, :movement_date)
RETURNING *;
