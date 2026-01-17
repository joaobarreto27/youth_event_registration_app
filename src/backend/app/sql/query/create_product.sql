INSERT INTO products (product_name, quantity, price, create_date, update_date)
VALUES (:product_name, :quantity, :price, now(), now())
RETURNING *;
