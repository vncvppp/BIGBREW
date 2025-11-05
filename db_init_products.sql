-- Drop and recreate categories
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE categories;
SET FOREIGN_KEY_CHECKS=1;
INSERT INTO categories (category_name, description) VALUES 
('milkTea', 'Milk tea beverages'),
('praf', 'PRAF beverages'),
('fruitTea', 'Fruit tea beverages'),
('coffee', 'Coffee beverages'),
('brosty', 'Brosty beverages'),
('add-ons', 'Additional toppings and add-ons');

-- Milk Tea Products
INSERT INTO products (product_code, product_name, description, category_id, cost_price, unit_price) VALUES
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT001', 'Cookies n Cream', 'Cookies and cream flavored milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT002', 'Okinawa', 'Okinawa-style roasted milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT003', 'Dark Choco', 'Dark chocolate milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT004', 'Matcha', 'Japanese green tea with milk', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT005', 'Red Velvet', 'Red velvet flavored milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT006', 'Winter Melon', 'Winter melon milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT007', 'Cheesecake', 'Cheesecake flavored milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT008', 'Chocolate', 'Classic chocolate milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT009', 'Taro', 'Taro flavored milk tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'milkTea'), 'MT010', 'Salted Caramel', 'Salted caramel milk tea', 25.00, 29.00);

-- Coffee Products
INSERT INTO products (category_id, product_code, product_name, description, cost_price, unit_price) VALUES
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF001', 'Brusko', 'Strong brewed coffee', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF002', 'Mocha', 'Coffee with chocolate', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF003', 'Macchiato', 'Espresso with steamed milk', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF004', 'Vanilla', 'Coffee with vanilla flavoring', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF005', 'Caramel', 'Coffee with caramel flavoring', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF006', 'Matcha', 'Coffee with matcha green tea', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF007', 'Fudge', 'Coffee with chocolate fudge', 25.00, 29.00),
((SELECT category_id FROM categories WHERE category_name = 'coffee'), 'CF008', 'Spanish Latte', 'Coffee with sweetened condensed milk', 25.00, 29.00);

-- Initialize inventory for all products
INSERT INTO inventory (product_id, current_stock, minimum_stock, reorder_point)
SELECT product_id, 100, 10, 20 FROM products;