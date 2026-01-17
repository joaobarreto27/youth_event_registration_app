SELECT p.id_product, m.id_stock_movement, p.product_name, m.movement_type, m.quantity, m.movement_date
        FROM stock_movements m
        JOIN products p ON m.id_product = p.id_product
        ORDER BY m.movement_date
