-- Idempotent import script for products, ingredients, and recipes
-- Assumes tables `products`, `ingredients`, and `recipes` exist with unique constraints on `name` (products, ingredients)
-- Run this against your MySQL `breadshop` database. It uses INSERT ... ON DUPLICATE KEY UPDATE to be re-runnable.
USE breadshop;
START TRANSACTION;

-- Ingredients (costs)
INSERT INTO ingredients (`name`, `cost`) VALUES
('Harina fuerza(100g)', 0.125),
('Harina espelta(100g)', 0.3),
('Harina centeno(100g)', 0.2),
('Harina integral(100g)', 0.184),
('Semillas(100g)', 0.38),
('Nueces(100g)', 1.5),
('Pasas(100g)', 0.38),
('Pistachos(100g)', 2.2),
('Aceitunas(100g)', 0.7),
('Patata(100g)', 0.15),
('Cebolla(100g)', 0.1),
('Leche(100g)', 0.3),
('Bolsa papel', 0.06),
('Agua(100g)', 0),
('Electricidad', 0),
('Levadura(1g)', 0.05),
('Trabajo(1h)', 10),
('Desgaste(herramienta)', 1)
ON DUPLICATE KEY UPDATE cost=VALUES(cost);

-- Products (precios)
INSERT INTO products (`name`,`display_name`,`price`,`cost`,`benefits`,`category`) VALUES
('Olive_stick','Olive stick',2.5,0.985,1.515,'stick'),
('Olive_loaf','Olive loaf',4,1.335,2.665,'loaf'),
('White_stick','White stick',2,0.435,1.565,'stick'),
('White_loaf','White loaf',3,0.76,2.24,'loaf'),
('Onion_stick','Onion stick',2.5,0.70375,1.79625,'stick'),
('Onion_loaf','Onion loaf',4,1.31,2.69,'loaf'),
('Wholemeal_Rye_stick','Wholemeal Rye stick',2.5,0.50375,1.99625,'stick'),
('Wholemeal_Rye_loaf','Wholemeal Rye loaf',4,0.91,3.09,'loaf'),
('Wholemeal_Spelt_stick','Wholemeal Spelt stick',2.5,0.60375,1.89625,'stick'),
('Wholemeal_Spelt_loaf','Wholemeal Spelt loaf',4,1.11,2.89,'loaf'),
('Wholemeal_White_stick','Wholemeal White stick',2.5,0.48775,2.01225,'stick'),
('Wholemeal_White_loaf','Wholemeal White loaf',4,0.878,3.122,'loaf'),
('Wholemeal_Seeds_stick','Wholemeal Seeds stick',2.5,0.58575,1.91425,'stick'),
('Wholemeal_Seeds_loaf','Wholemeal Seeds loaf',4,1.258,2.742,'loaf'),
('Walnut_stick','Walnut stick',2.5,1.05375,1.44625,'stick'),
('Walnut_loaf','Walnut loaf',4,1.9975,2.0025,'loaf'),
('Wholemeal_Walnut_stick','Wholemeal Walnut stick',2.5,1.07075,1.42925,'stick'),
('Wholemeal_Walnut_loaf','Wholemeal Walnut loaf',4,2.044,1.956,'loaf'),
('Walnut_and_Sultanas_stick','Walnut and Sultanas stick',2.5,0.924,1.576,'stick'),
('Walnut_and_Sultanas_loaf','Walnut and Sultanas loaf',4,1.738,2.262,'loaf'),
('Wholemeal_Walnut_and_Sultanas_stick','Wholemeal Walnut and Sultanas stick',2.5,1.33575,1.16425,'stick'),
('Wholemeal_Walnut_and_Sultanas_loaf','Wholemeal Walnut and Sultanas loaf',4,1.634,2.366,'loaf'),
('Potato_stick','Potato stick',2,0.45375,1.54625,'stick'),
('Potato_loaf','Potato loaf',3,0.81,2.19,'loaf'),
('Pistacho_stick','Pistacho stick',3,1.6375,1.3625,'stick'),
('Pistacho_loaf','Pistacho loaf',4.5,2.6275,1.8725,'loaf'),
('Wholemeal_Pistacho_stick','Wholemeal Pistacho stick',3,1.39825,1.60175,'stick'),
('Wholemeal_Pistacho_loaf','Wholemeal Pistacho loaf',5,2.5615,2.4385,'loaf'),
('Seeds_stick','Seeds stick',2,0.7525,1.2475,'stick'),
('Seeds_loaf','Seeds loaf',3,1.015,1.985,'loaf')
ON DUPLICATE KEY UPDATE price=VALUES(price), cost=VALUES(cost), benefits=VALUES(benefits), display_name=VALUES(display_name), category=VALUES(category);

-- Recipes (map ingredient -> quantity/cost as JSON string). Uses a subselect to find product_id by name.
-- JSON strings are stored in the `ingredients_json` TEXT column.
-- Convert recipes to normalized product_ingredients associations.
-- Remove existing associations for these products then insert fresh rows (idempotent)
DELETE pi FROM product_ingredients pi JOIN products p ON pi.product_id = p.id WHERE p.name IN (
	'White_loaf','Seeds_loaf','Walnut_loaf','Wholemeal_White_loaf','Wholemeal_Spelt_loaf','Pistacho_loaf',
	'Nueces y pasas hogaza','Wholemeal_Seeds_loaf =','Wholemeal_Walnut_loaf','Wholemeal_Walnut_and_Sultanas_loaf',
	'Wholemeal_Pistacho_loaf','White_stick','Seeds_stick','Walnut_stick','Wholemeal_White_stick','Wholemeal_Spelt_stick',
	'Wholemeal_Rye_stick','Pistacho_stick','Walnut_and_Sultanas_stick','Wholemeal_Seeds_stick','Wholemeal_Walnut_stick',
	'Wholemeal_Walnut_and_Sultanas_stick','Wholemeal_Pistacho_stick'
);

-- Replace big VALUES block with INSERT ... SELECT so NULL ids are not inserted.
-- Each INSERT here only runs when matching product and ingredient exist.
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 5.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='White_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 4.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Semillas(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Seeds_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Seeds_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Seeds_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Seeds_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 4.3 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.9 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Walnut_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_White_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_White_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2 FROM products p JOIN ingredients i ON i.name='Harina espelta(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Spelt_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Spelt_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 4.3 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.9 FROM products p JOIN ingredients i ON i.name='Pistachos(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Pistacho_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 4 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.6 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.6 FROM products p JOIN ingredients i ON i.name='Pasas(100g)' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Nueces y pasas hogaza';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Nueces y pasas hogaza';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Semillas(100g)' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Seeds_loaf =';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Seeds_loaf =';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.9 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Pasas(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2.3 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.9 FROM products p JOIN ingredients i ON i.name='Pistachos(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 3.1 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Pistacho_loaf';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Pistacho_loaf';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2.6 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='White_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2.1 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Semillas(100g)' WHERE p.name='Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Seeds_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2.15 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.45 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Walnut_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_White_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_White_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina espelta(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Spelt_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Spelt_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Harina centeno(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Rye_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Rye_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 4.3 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.45 FROM products p JOIN ingredients i ON i.name='Pistachos(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Pistacho_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 2 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.3 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.3 FROM products p JOIN ingredients i ON i.name='Pasas(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Walnut_and_Sultanas_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Semillas(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Seeds_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Seeds_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.45 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Nueces(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Pasas(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Walnut_and_Sultanas_stick';

INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.65 FROM products p JOIN ingredients i ON i.name='Harina fuerza(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.45 FROM products p JOIN ingredients i ON i.name='Pistachos(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.5 FROM products p JOIN ingredients i ON i.name='Harina integral(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1.55 FROM products p JOIN ingredients i ON i.name='Agua(100g)' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 0.2 FROM products p JOIN ingredients i ON i.name='Electricidad' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Bolsa papel' WHERE p.name='Wholemeal_Pistacho_stick';
INSERT INTO product_ingredients (product_id, ingredient_id, quantity)
SELECT p.id, i.id, 1 FROM products p JOIN ingredients i ON i.name='Levadura(1g)' WHERE p.name='Wholemeal_Pistacho_stick';
;
drop table recipes;
COMMIT;
