-- ====================================================================
-- Idempotent Import & Mock Data Script for Bread Shop
-- Database: `breadshop`
-- ====================================================================
-- Sets up schema (if not exists), bakeries, site settings, staff,
-- delivery drivers, users, user preferences, ingredients with initial stock,
-- products, recipes (product_ingredients associations), and sample orders.
-- ====================================================================

USE breadshop;

SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
START TRANSACTION;

-- --------------------------------------------------------------------
-- 1. Table Schemas (CREATE TABLE IF NOT EXISTS)
-- --------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `group` VARCHAR(255) NOT NULL,
    `date` VARCHAR(255) NOT NULL,
    `verified` TINYINT(1) NOT NULL DEFAULT 0,
    `legacy` TINYINT(1) NOT NULL DEFAULT 0,
    `address` VARCHAR(500) NULL,
    `delivery_notes` VARCHAR(500) NULL,
    `is_admin` TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `user_preferences` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `preferred_language` VARCHAR(10) DEFAULT 'en',
    `dark_mode` TINYINT(1) DEFAULT 0,
    `default_delivery_notes` VARCHAR(500) NULL,
    CONSTRAINT `fk_user_preferences_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `site_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    `value` TEXT NOT NULL,
    `description` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `delivery_persons` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(50) NOT NULL,
    `vehicle_type` VARCHAR(100) DEFAULT 'Van',
    `active` TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `bakeries` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `address` VARCHAR(500) NOT NULL,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `base_delivery_cost` DOUBLE NOT NULL DEFAULT 2.0,
    `cost_per_km` DOUBLE NOT NULL DEFAULT 0.5
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ingredients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `display_name` VARCHAR(255) NULL,
    `display_name_es` VARCHAR(255) NULL,
    `cost` DOUBLE NULL,
    `stock` DOUBLE NOT NULL DEFAULT 0.0,
    `unit` VARCHAR(50) NOT NULL DEFAULT 'kg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `inventory_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `ingredient_id` INT NOT NULL,
    `change_amount` DOUBLE NOT NULL,
    `current_stock` DOUBLE NOT NULL,
    `reason` VARCHAR(255) NULL,
    `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_inventory_logs_ingredient` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `display_name` VARCHAR(255) NULL,
    `display_name_es` VARCHAR(255) NULL,
    `price` DOUBLE NULL,
    `cost` DOUBLE NULL,
    `benefits` DOUBLE NULL,
    `category` VARCHAR(50) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `product_ingredients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `ingredient_id` INT NOT NULL,
    `quantity` DOUBLE NULL,
    CONSTRAINT `fk_product_ingredients_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_product_ingredients_ingredient` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `staff` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `role` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NULL,
    `phone` VARCHAR(50) NULL,
    `active` TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `staff_timetables` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `staff_id` INT NOT NULL,
    `day_of_week` INT NOT NULL DEFAULT 0,
    `shift_date` DATE NULL,
    `start_time` VARCHAR(20) NOT NULL DEFAULT '06:00',
    `end_time` VARCHAR(20) NOT NULL DEFAULT '14:00',
    `notes` VARCHAR(255) NULL,
    CONSTRAINT `fk_staff_timetables_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `orders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `order` VARCHAR(5000) NOT NULL,
    `date` DATE NULL,
    `payed` TINYINT(1) NOT NULL DEFAULT 0,
    `delivered` TINYINT(1) NOT NULL DEFAULT 0,
    `time_day` VARCHAR(255) NOT NULL,
    `client` VARCHAR(255) NOT NULL,
    `num_breads` INT NULL,
    `delivery_option` VARCHAR(50) DEFAULT 'profile',
    `delivery_address` VARCHAR(500) NULL,
    `delivery_notes` VARCHAR(500) NULL,
    `delivery_latitude` DOUBLE NULL,
    `delivery_longitude` DOUBLE NULL,
    `assigned_delivery_id` INT NULL,
    CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_orders_delivery_person` FOREIGN KEY (`assigned_delivery_id`) REFERENCES `delivery_persons` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- 2. Bakeries Data
-- --------------------------------------------------------------------

INSERT INTO `bakeries` (`name`, `address`, `latitude`, `longitude`, `base_delivery_cost`, `cost_per_km`) VALUES
('Sunrise Bread Lab', '12 Fictional Avenue, Madrid', 40.4168, -3.7038, 2.00, 0.50),
('The Golden Crust', '7 Imaginary Street, Madrid', 40.4230, -3.6900, 2.50, 0.45),
('Artisan Central Bakery', '24 Gran Via, Madrid', 40.4200, -3.7050, 2.00, 0.40)
ON DUPLICATE KEY UPDATE 
    `address`=VALUES(`address`), 
    `latitude`=VALUES(`latitude`), 
    `longitude`=VALUES(`longitude`), 
    `base_delivery_cost`=VALUES(`base_delivery_cost`), 
    `cost_per_km`=VALUES(`cost_per_km`);

-- --------------------------------------------------------------------
-- 3. Site Settings
-- --------------------------------------------------------------------

INSERT INTO `site_settings` (`key`, `value`, `description`) VALUES
('require_email_verification', 'false', 'Require users to verify email before placing orders'),
('admin_notification_email', 'admin@breadshop.com', 'Recipient email for daily summaries and system alerts'),
('site_announcement', 'Welcome to our artisanal bakery! Order fresh sourdough and specialty breads online.', 'Banner announcement displayed to customers'),
('delivery_enabled', 'true', 'Master toggle for home delivery calculation and options'),
('currency_symbol', '€', 'Currency symbol used throughout storefront')
ON DUPLICATE KEY UPDATE 
    `value`=VALUES(`value`), 
    `description`=VALUES(`description`);

-- --------------------------------------------------------------------
-- 4. Delivery Persons
-- --------------------------------------------------------------------

INSERT INTO `delivery_persons` (`id`, `name`, `phone`, `vehicle_type`, `active`) VALUES
(1, 'Carlos Gomez', '+34 600 123 456', 'Van', 1),
(2, 'Maria Rodriguez', '+34 600 654 321', 'Scooter', 1),
(3, 'Juan Martinez', '+34 600 987 654', 'E-Bike', 1)
ON DUPLICATE KEY UPDATE 
    `name`=VALUES(`name`), 
    `phone`=VALUES(`phone`), 
    `vehicle_type`=VALUES(`vehicle_type`), 
    `active`=VALUES(`active`);

-- --------------------------------------------------------------------
-- 5. Staff & Weekly Schedules
-- --------------------------------------------------------------------

INSERT INTO `staff` (`id`, `name`, `role`, `email`, `phone`, `active`) VALUES
(1, 'Marco Silva', 'Head Baker', 'marco@breadshop.com', '+34 611 111 222', 1),
(2, 'Elena Alvarez', 'Assistant Baker', 'elena@breadshop.com', '+34 622 222 333', 1),
(3, 'David Perez', 'Logistics & Packaging', 'david@breadshop.com', '+34 633 333 444', 1),
(4, 'Sofia Navarro', 'Delivery Coordinator', 'sofia@breadshop.com', '+34 644 444 555', 1)
ON DUPLICATE KEY UPDATE 
    `name`=VALUES(`name`), 
    `role`=VALUES(`role`), 
    `email`=VALUES(`email`), 
    `phone`=VALUES(`phone`), 
    `active`=VALUES(`active`);

DELETE FROM `staff_timetables` WHERE `staff_id` IN (1, 2, 3, 4);

INSERT INTO `staff_timetables` (`staff_id`, `day_of_week`, `start_time`, `end_time`, `notes`) VALUES
(1, 0, '04:00', '12:00', 'Sourdough preparation & oven master'),
(1, 1, '04:00', '12:00', 'Oven shifts & shaping'),
(1, 2, '04:00', '12:00', 'Oven shifts & shaping'),
(1, 3, '04:00', '12:00', 'Oven shifts & shaping'),
(1, 4, '04:00', '12:00', 'Weekend prep & fermentation checks'),
(2, 0, '05:00', '13:00', 'Kneading & proofing'),
(2, 1, '05:00', '13:00', 'Kneading & proofing'),
(2, 2, '05:00', '13:00', 'Kneading & proofing'),
(2, 3, '05:00', '13:00', 'Kneading & proofing'),
(2, 4, '05:00', '13:00', 'Kneading & proofing'),
(3, 0, '07:00', '15:00', 'Bagging, slicing, and order packing'),
(3, 1, '07:00', '15:00', 'Bagging, slicing, and order packing'),
(3, 2, '07:00', '15:00', 'Bagging, slicing, and order packing'),
(3, 3, '07:00', '15:00', 'Bagging, slicing, and order packing'),
(3, 4, '07:00', '15:00', 'Bagging, slicing, and order packing'),
(4, 0, '08:00', '16:00', 'Route dispatching and courier support'),
(4, 1, '08:00', '16:00', 'Route dispatching and courier support'),
(4, 2, '08:00', '16:00', 'Route dispatching and courier support'),
(4, 3, '08:00', '16:00', 'Route dispatching and courier support'),
(4, 4, '08:00', '16:00', 'Route dispatching and courier support');

-- --------------------------------------------------------------------
-- 6. Users & Preferences
-- Note: Passwords below are pbkdf2:sha256 hashed for 'password123'
-- --------------------------------------------------------------------

INSERT INTO `users` (`id`, `username`, `password`, `email`, `group`, `date`, `verified`, `legacy`, `address`, `delivery_notes`, `is_admin`) VALUES
(1, 'superadmin', 'pbkdf2:sha256:1000000$dY3frS0DOYVvp7$80a80cc6d9213402e3b33b5f7832f943fd11326ae11d11db22d5a08ab2fec059', 'admin@breadshop.com', 'admins', '2025-01-01', 1, 0, '12 Fictional Avenue, Madrid', 'Leave with bakery front desk', 1),
(2, 'baker_tom', 'pbkdf2:sha256:1000000$dY3frS0DOYVvp7$80a80cc6d9213402e3b33b5f7832f943fd11326ae11d11db22d5a08ab2fec059', 'tom@breadshop.com', 'bakers', '2025-01-01', 1, 0, 'Plaza Mayor 1, Madrid', 'Baker manager desk', 1),
(3, 'johndoe', 'pbkdf2:sha256:1000000$dY3frS0DOYVvp7$80a80cc6d9213402e3b33b5f7832f943fd11326ae11d11db22d5a08ab2fec059', 'john@example.com', 'customers', '2025-01-10', 1, 0, 'Calle Mayor 14, 28013 Madrid', 'Ring intercom #3B', 0),
(4, 'mercedes', 'pbkdf2:sha256:1000000$dY3frS0DOYVvp7$80a80cc6d9213402e3b33b5f7832f943fd11326ae11d11db22d5a08ab2fec059', 'mercedes@example.com', 'customers', '2025-01-15', 1, 0, 'Calle de Alcala 45, 28014 Madrid', 'Leave with concierge', 0),
(5, 'legacy_user', 'pbkdf2:sha256:1000000$dY3frS0DOYVvp7$80a80cc6d9213402e3b33b5f7832f943fd11326ae11d11db22d5a08ab2fec059', 'legacy@example.com', 'legacygroup', '2025-01-20', 1, 1, 'Paseo del Prado 10, 28014 Madrid', 'Deliver to side door', 0)
ON DUPLICATE KEY UPDATE 
    `password`=VALUES(`password`), 
    `email`=VALUES(`email`), 
    `group`=VALUES(`group`), 
    `verified`=VALUES(`verified`), 
    `legacy`=VALUES(`legacy`), 
    `address`=VALUES(`address`), 
    `delivery_notes`=VALUES(`delivery_notes`), 
    `is_admin`=VALUES(`is_admin`);

INSERT INTO `user_preferences` (`user_id`, `preferred_language`, `dark_mode`, `default_delivery_notes`) VALUES
(1, 'en', 1, 'Admin account default note'),
(2, 'es', 0, 'Bakery manager note'),
(3, 'en', 0, 'Ring intercom #3B'),
(4, 'es', 0, 'Leave with concierge'),
(5, 'es', 0, 'Deliver to side door')
ON DUPLICATE KEY UPDATE 
    `preferred_language`=VALUES(`preferred_language`), 
    `dark_mode`=VALUES(`dark_mode`), 
    `default_delivery_notes`=VALUES(`default_delivery_notes`);

-- --------------------------------------------------------------------
-- 7. Ingredients (Cost, Stock & Units)
-- --------------------------------------------------------------------

INSERT INTO `ingredients` (`name`, `display_name`, `display_name_es`, `cost`, `stock`, `unit`) VALUES
('Harina fuerza(100g)', 'Strong flour (100g)', 'Harina de fuerza (100g)', 0.125, 250.0, 'kg'),
('Harina espelta(100g)', 'Spelt flour (100g)', 'Harina de espelta (100g)', 0.300, 80.0, 'kg'),
('Harina centeno(100g)', 'Rye flour (100g)', 'Harina de centeno (100g)', 0.200, 75.0, 'kg'),
('Harina integral(100g)', 'Wholemeal flour (100g)', 'Harina integral (100g)', 0.184, 120.0, 'kg'),
('Semillas(100g)', 'Seeds (100g)', 'Semillas (100g)', 0.380, 45.0, 'kg'),
('Nueces(100g)', 'Walnuts (100g)', 'Nueces (100g)', 1.500, 30.0, 'kg'),
('Pasas(100g)', 'Sultanas (100g)', 'Pasas (100g)', 0.380, 25.0, 'kg'),
('Pistachos(100g)', 'Pistachios (100g)', 'Pistachos (100g)', 2.200, 20.0, 'kg'),
('Aceitunas(100g)', 'Olives (100g)', 'Aceitunas (100g)', 0.700, 35.0, 'kg'),
('Patata(100g)', 'Potato (100g)', 'Patata (100g)', 0.150, 40.0, 'kg'),
('Cebolla(100g)', 'Onion (100g)', 'Cebolla (100g)', 0.100, 35.0, 'kg'),
('Leche(100g)', 'Milk (100g)', 'Leche (100g)', 0.300, 50.0, 'l'),
('Bolsa papel', 'Paper bag', 'Bolsa de papel', 0.060, 1000.0, 'units'),
('Agua(100g)', 'Water (100g)', 'Agua (100g)', 0.000, 500.0, 'l'),
('Electricidad', 'Electricity', 'Electricidad', 0.000, 1000.0, 'kWh'),
('Levadura(1g)', 'Yeast (1g)', 'Levadura (1g)', 0.050, 15.0, 'kg'),
('Trabajo(1h)', 'Work (1h)', 'Trabajo (1h)', 10.000, 100.0, 'hours'),
('Desgaste(herramienta)', 'Wear and tear (tools)', 'Desgaste (herramienta)', 1.000, 100.0, 'units')
ON DUPLICATE KEY UPDATE 
    `display_name`=VALUES(`display_name`), 
    `display_name_es`=VALUES(`display_name_es`), 
    `cost`=VALUES(`cost`),
    `stock`=VALUES(`stock`),
    `unit`=VALUES(`unit`);

-- --------------------------------------------------------------------
-- 8. Products
-- --------------------------------------------------------------------

INSERT INTO `products` (`name`, `display_name`, `display_name_es`, `price`, `cost`, `benefits`, `category`) VALUES
('Olive_stick', 'Olive stick', 'Palito de aceituna', 2.50, 0.985, 1.515, 'bread'),
('Olive_loaf', 'Olive loaf', 'Hogaza de aceituna', 4.00, 1.335, 2.665, 'bread'),
('White_stick', 'White stick', 'Pan blanco', 2.00, 0.435, 1.565, 'bread'),
('White_loaf', 'White loaf', 'Hogaza blanca', 3.00, 0.760, 2.240, 'bread'),
('Onion_stick', 'Onion stick', 'Pan de cebolla', 2.50, 0.70375, 1.79625, 'bread'),
('Onion_loaf', 'Onion loaf', 'Hogaza de cebolla', 4.00, 1.310, 2.690, 'bread'),
('Wholemeal_Rye_stick', 'Wholemeal Rye stick', 'Centeno integral', 2.50, 0.50375, 1.99625, 'bread'),
('Wholemeal_Rye_loaf', 'Wholemeal Rye loaf', 'Hogaza de centeno integral', 4.00, 0.910, 3.090, 'bread'),
('Wholemeal_Spelt_stick', 'Wholemeal Spelt stick', 'Espelta integral', 2.50, 0.60375, 1.89625, 'bread'),
('Wholemeal_Spelt_loaf', 'Wholemeal Spelt loaf', 'Hogaza de espelta integral', 4.00, 1.110, 2.890, 'bread'),
('Wholemeal_White_stick', 'Wholemeal White stick', 'Blanco integral', 2.50, 0.48775, 2.01225, 'bread'),
('Wholemeal_White_loaf', 'Wholemeal White loaf', 'Hogaza de trigo integral', 4.00, 0.878, 3.122, 'bread'),
('Wholemeal_Seeds_stick', 'Wholemeal Seeds stick', 'Semillas integrales', 2.50, 0.58575, 1.91425, 'bread'),
('Wholemeal_Seeds_loaf', 'Wholemeal Seeds loaf', 'Hogaza integral con semillas', 4.00, 1.258, 2.742, 'bread'),
('Walnut_stick', 'Walnut stick', 'Nuez', 2.50, 1.05375, 1.44625, 'bread'),
('Walnut_loaf', 'Walnut loaf', 'Hogaza de nuez', 4.00, 1.9975, 2.0025, 'bread'),
('Wholemeal_Walnut_stick', 'Wholemeal Walnut stick', 'Nuez integral', 2.50, 1.07075, 1.42925, 'bread'),
('Wholemeal_Walnut_loaf', 'Wholemeal Walnut loaf', 'Hogaza de nuez integral', 4.00, 2.044, 1.956, 'bread'),
('Walnut_and_Sultanas_stick', 'Walnut and Sultanas stick', 'Nuez y pasas', 2.50, 0.924, 1.576, 'bread'),
('Walnut_and_Sultanas_loaf', 'Walnut and Sultanas loaf', 'Hogaza de nuez y pasas', 4.00, 1.738, 2.262, 'bread'),
('Wholemeal_Walnut_and_Sultanas_stick', 'Wholemeal Walnut and Sultanas stick', 'Nuez y pasas integral', 2.50, 1.33575, 1.16425, 'bread'),
('Wholemeal_Walnut_and_Sultanas_loaf', 'Wholemeal Walnut and Sultanas loaf', 'Hogaza integral de nuez y pasas', 4.00, 1.634, 2.366, 'bread'),
('Potato_stick', 'Potato stick', 'Pan de patata', 2.00, 0.45375, 1.54625, 'bread'),
('Potato_loaf', 'Potato loaf', 'Hogaza de patata', 3.00, 0.810, 2.190, 'bread'),
('Pistacho_stick', 'Pistacho stick', 'Pistacho', 3.00, 1.6375, 1.3625, 'bread'),
('Pistacho_loaf', 'Pistacho loaf', 'Hogaza de pistacho', 4.50, 2.6275, 1.8725, 'bread'),
('Wholemeal_Pistacho_stick', 'Wholemeal Pistacho stick', 'Pistacho integral', 3.00, 1.39825, 1.60175, 'bread'),
('Wholemeal_Pistacho_loaf', 'Wholemeal Pistacho loaf', 'Hogaza de pistacho integral', 5.00, 2.5615, 2.4385, 'bread'),
('Seeds_stick', 'Seeds stick', 'Semillas', 2.00, 0.7525, 1.2475, 'bread'),
('Seeds_loaf', 'Seeds loaf', 'Hogaza con semillas', 3.00, 1.015, 1.985, 'bread')
ON DUPLICATE KEY UPDATE 
    `price`=VALUES(`price`), 
    `cost`=VALUES(`cost`), 
    `benefits`=VALUES(`benefits`), 
    `display_name`=VALUES(`display_name`), 
    `display_name_es`=VALUES(`display_name_es`), 
    `category`=VALUES(`category`);

-- --------------------------------------------------------------------
-- 9. Product Ingredients / Recipes (Associations)
-- Clean and re-insert recipe mappings for all 30 products
-- --------------------------------------------------------------------

DELETE pi FROM `product_ingredients` pi 
JOIN `products` p ON pi.product_id = p.id 
WHERE p.name IN (
    'White_loaf', 'Seeds_loaf', 'Walnut_loaf', 'Wholemeal_White_loaf', 'Wholemeal_Spelt_loaf', 'Pistacho_loaf',
    'Walnut_and_Sultanas_loaf', 'Wholemeal_Seeds_loaf', 'Wholemeal_Walnut_loaf', 'Wholemeal_Walnut_and_Sultanas_loaf',
    'Wholemeal_Pistacho_loaf', 'White_stick', 'Seeds_stick', 'Walnut_stick', 'Wholemeal_White_stick', 'Wholemeal_Spelt_stick',
    'Wholemeal_Rye_stick', 'Pistacho_stick', 'Walnut_and_Sultanas_stick', 'Wholemeal_Seeds_stick', 'Wholemeal_Walnut_stick',
    'Wholemeal_Walnut_and_Sultanas_stick', 'Wholemeal_Pistacho_stick', 'Olive_stick', 'Olive_loaf', 'Onion_stick', 
    'Onion_loaf', 'Wholemeal_Rye_loaf', 'Potato_stick', 'Potato_loaf'
);

-- White_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 5.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='White_loaf';

-- Seeds_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Semillas(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Seeds_loaf';

-- Walnut_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.3 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.9 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Walnut_loaf';

-- Wholemeal_White_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_White_loaf';

-- Wholemeal_Spelt_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina espelta(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Spelt_loaf';

-- Pistacho_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.3 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.9 FROM `products` p JOIN `ingredients` i ON i.name='Pistachos(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Pistacho_loaf';

-- Walnut_and_Sultanas_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.6 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.6 FROM `products` p JOIN `ingredients` i ON i.name='Pasas(100g)' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Walnut_and_Sultanas_loaf';

-- Wholemeal_Seeds_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Semillas(100g)' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Seeds_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Seeds_loaf';

-- Wholemeal_Walnut_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.9 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_loaf';

-- Wholemeal_Walnut_and_Sultanas_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Pasas(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';

-- Wholemeal_Pistacho_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.3 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.9 FROM `products` p JOIN `ingredients` i ON i.name='Pistachos(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Pistacho_loaf';

-- Wholemeal_Rye_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Rye_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina centeno(100g)' WHERE p.name='Wholemeal_Rye_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Rye_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Rye_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Rye_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Rye_loaf';

-- Olive_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.2 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Olive_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Aceitunas(100g)' WHERE p.name='Olive_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Olive_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Olive_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Olive_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Olive_loaf';

-- Onion_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Onion_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 7.0 FROM `products` p JOIN `ingredients` i ON i.name='Cebolla(100g)' WHERE p.name='Onion_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Onion_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Onion_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Onion_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Onion_loaf';

-- Potato_loaf
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.4 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Potato_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Patata(100g)' WHERE p.name='Potato_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 3.1 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Potato_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Potato_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Potato_loaf';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Potato_loaf';

-- White_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.6 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='White_stick';

-- Seeds_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.1 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Semillas(100g)' WHERE p.name='Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Seeds_stick';

-- Walnut_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.15 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.45 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Walnut_stick';

-- Wholemeal_White_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_White_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_White_stick';

-- Wholemeal_Spelt_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina espelta(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Spelt_stick';

-- Wholemeal_Rye_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina centeno(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Rye_stick';

-- Pistacho_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.3 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.45 FROM `products` p JOIN `ingredients` i ON i.name='Pistachos(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Pistacho_stick';

-- Walnut_and_Sultanas_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 2.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.3 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.3 FROM `products` p JOIN `ingredients` i ON i.name='Pasas(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Walnut_and_Sultanas_stick';

-- Wholemeal_Seeds_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Semillas(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Seeds_stick';

-- Wholemeal_Walnut_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.45 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_stick';

-- Wholemeal_Walnut_and_Sultanas_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Pasas(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';

-- Wholemeal_Pistacho_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.65 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.45 FROM `products` p JOIN `ingredients` i ON i.name='Pistachos(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.5 FROM `products` p JOIN `ingredients` i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Pistacho_stick';

-- Wholemeal_Rye_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Harina centeno(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Rye_stick';

-- Olive_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.4 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Olive_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Aceitunas(100g)' WHERE p.name='Olive_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Olive_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Olive_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Olive_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Olive_stick';

-- Onion_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Onion_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 4.0 FROM `products` p JOIN `ingredients` i ON i.name='Cebolla(100g)' WHERE p.name='Onion_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Onion_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Onion_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Onion_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Onion_stick';

-- Potato_stick
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Harina fuerza(100g)' WHERE p.name='Potato_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Patata(100g)' WHERE p.name='Potato_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.55 FROM `products` p JOIN `ingredients` i ON i.name='Agua(100g)' WHERE p.name='Potato_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 0.2 FROM `products` p JOIN `ingredients` i ON i.name='Electricidad' WHERE p.name='Potato_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Bolsa papel' WHERE p.name='Potato_stick';
INSERT INTO `product_ingredients` (`product_id`, `ingredient_id`, `quantity`) SELECT p.id, i.id, 1.0 FROM `products` p JOIN `ingredients` i ON i.name='Levadura(1g)' WHERE p.name='Potato_stick';

-- --------------------------------------------------------------------
-- 10. Initial Inventory Logs (Audit Trail)
-- --------------------------------------------------------------------

INSERT INTO `inventory_logs` (`ingredient_id`, `change_amount`, `current_stock`, `reason`, `timestamp`)
SELECT id, stock, stock, 'Initial stock import', NOW()
FROM `ingredients`
WHERE NOT EXISTS (SELECT 1 FROM `inventory_logs` WHERE `inventory_logs`.ingredient_id = `ingredients`.id);

-- --------------------------------------------------------------------
-- 11. Sample Orders (Realistic Mock Orders)
-- --------------------------------------------------------------------

INSERT INTO `orders` (`id`, `user_id`, `order`, `date`, `payed`, `delivered`, `time_day`, `client`, `num_breads`, `delivery_option`, `delivery_address`, `delivery_notes`, `delivery_latitude`, `delivery_longitude`, `assigned_delivery_id`) VALUES
(1, 3, '{"White_loaf": 1, "Wholemeal_Seeds_loaf": 1}', '2025-05-12', 1, 1, 'Morning', 'John Doe', 2, 'profile', 'Calle Mayor 14, 28013 Madrid', 'Ring intercom #3B', 40.4155, -3.7074, 1),
(2, 4, '{"Olive_loaf": 1, "Seeds_stick": 2}', '2025-05-12', 1, 1, 'Evening', 'Mercedes MM', 3, 'profile', 'Calle de Alcala 45, 28014 Madrid', 'Leave with concierge', 40.4190, -3.6950, 2),
(3, 5, '{"Wholemeal_Rye_loaf": 2, "Walnut_and_Sultanas_stick": 1}', '2025-05-13', 1, 0, 'Morning', 'Legacy Customer', 3, 'profile', 'Paseo del Prado 10, 28014 Madrid', 'Deliver to side door', 40.4140, -3.6930, 1),
(4, 3, '{"Pistacho_loaf": 1, "Potato_loaf": 1}', '2025-05-15', 0, 0, 'Evening', 'John Doe', 2, 'custom', 'Calle Gran Via 30, 28013 Madrid', 'Call upon arrival', 40.4205, -3.7040, 3),
(5, 4, '{"Wholemeal_Spelt_loaf": 2, "White_stick": 2}', '2025-05-16', 1, 0, 'Morning', 'Mercedes MM', 4, 'bakery_pickup', NULL, 'Pickup at Sunrise Bread Lab', NULL, NULL, NULL)
ON DUPLICATE KEY UPDATE 
    `order`=VALUES(`order`), 
    `date`=VALUES(`date`), 
    `payed`=VALUES(`payed`), 
    `delivered`=VALUES(`delivered`), 
    `time_day`=VALUES(`time_day`), 
    `client`=VALUES(`client`), 
    `num_breads`=VALUES(`num_breads`), 
    `delivery_option`=VALUES(`delivery_option`), 
    `delivery_address`=VALUES(`delivery_address`), 
    `delivery_notes`=VALUES(`delivery_notes`), 
    `delivery_latitude`=VALUES(`delivery_latitude`), 
    `delivery_longitude`=VALUES(`delivery_longitude`), 
    `assigned_delivery_id`=VALUES(`assigned_delivery_id`);

-- --------------------------------------------------------------------
-- 12. Finalize Transaction
-- --------------------------------------------------------------------

SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
COMMIT;
