-- Drop existing tables to start fresh
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS "order";
DROP TABLE IF EXISTS transaction_log;
DROP TABLE IF EXISTS promotion;
DROP TABLE IF EXISTS feature_flag;

-- User table for authentication
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' -- e.g., 'admin', 'user'
);

-- Product table
CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  price REAL NOT NULL,
  stock INTEGER NOT NULL
);

-- Order table
CREATE TABLE "order" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_name TEXT NOT NULL,
  total_amount REAL NOT NULL,
  status TEXT NOT NULL, -- e.g., 'pending', 'shipped', 'delivered'
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Transaction log for historical data
CREATE TABLE transaction_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Promotion table
CREATE TABLE promotion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  discount_percent REAL NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL
);

-- Feature flag table
CREATE TABLE feature_flag (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  is_active BOOLEAN NOT NULL CHECK (is_active IN (0, 1))
);

-- Seed data
INSERT INTO user (username, password, role) VALUES ('admin', 'scrypt:32768:8:1$H48K1xCMWgqgvJgF$ad6ddce6959309ee63deb773dee9d83fba631c760ad17bff62492ff2998ede2f159583d44418d04cf2a008695d5012671e2707e712a7a34d1e02a7f1a19a8dc2', 'admin'); -- pw is 'admin'
INSERT INTO user (username, password, role) VALUES ('featureuser', 'scrypt:32768:8:1$sMnZXbtHRh2xMKEf$dc5d475db4874c3f3ab81d413ddeabfda5946f202bd30110e169bd28f790aadcdfa64995868f379b795949da8148c6bdf770d6c6dd7794c306bbb1587ddb7463', 'user'); -- pw is 'password'
INSERT INTO product (name, price, stock) VALUES
  ('Laptop Gamer XYZ', 1500.00, 10),
  ('Mouse Inalámbrico', 25.50, 100),
  ('Teclado Mecánico RGB', 80.75, 50);

INSERT INTO "order" (customer_name, total_amount, status) VALUES
  ('Juan Perez', 1525.50, 'Shipped'),
  ('Maria Garcia', 80.75, 'Pending');

INSERT INTO transaction_log (description, amount, created_at) VALUES
  ('Venta de Laptop Gamer XYZ a Juan Perez', 1500.00, '2023-10-27 10:00:00'),
  ('Venta de Mouse Inalámbrico a Juan Perez', 25.50, '2023-10-27 10:00:00'),
  ('Venta de Teclado Mecánico RGB a Maria Garcia', 80.75, '2023-10-27 11:30:00');

INSERT INTO promotion (name, discount_percent, start_date, end_date) VALUES
  ('Venta de Viernes Negro', 20.0, '2024-11-20', '2024-11-26');

INSERT INTO feature_flag (name, is_active) VALUES
  ('promo_editor', 1),
  ('new_dashboard', 1); 