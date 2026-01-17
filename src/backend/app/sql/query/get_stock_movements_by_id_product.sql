SELECT p.id_product, id_stock_movement, p.product_name, m.movement_type, m.quantity, p.create_date
        FROM stock_movements m
        JOIN products p ON m.id_product = p.id_product
        WHERE p.create_date IS NOT NULL AND m.id_product = :id_product
        ORDER BY p.create_date DESC
