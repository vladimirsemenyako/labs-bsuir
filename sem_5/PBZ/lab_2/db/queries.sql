-- Запросы для реализации требуемых функций

-- 1. Просмотр полной информации по насаждениям заданного вида
-- Использование: SELECT * FROM v_all_plants_info WHERE species_name = 'Берёза';

-- 2. Просмотр списка сотрудников, работающих на заданную дату
-- Использование: SELECT full_name, phone, address FROM v_employee_schedule WHERE assignment_date = '2025-11-05';

-- 3. Просмотр перечня всех растений заданного вида на текущую дату и режимы их полива
-- Использование: SELECT * FROM v_plant_current_regimes WHERE species_name = 'Туя';

-- CRUD операции для фирмы
-- INSERT INTO firm (name, legal_address) VALUES ($1, $2);
-- UPDATE firm SET name = $1, legal_address = $2 WHERE firm_id = $3;
-- DELETE FROM firm WHERE firm_id = $1;

-- CRUD операции для парков
-- INSERT INTO parks (firm_id, name) VALUES ($1, $2);
-- UPDATE parks SET name = $1 WHERE park_id = $2;
-- DELETE FROM parks WHERE park_id = $1;

-- CRUD операции для зон
-- INSERT INTO zones (park_id, name) VALUES ($1, $2);
-- UPDATE zones SET name = $1 WHERE zone_id = $2;
-- DELETE FROM zones WHERE zone_id = $1;

-- CRUD операции для видов растений
-- INSERT INTO plant_species (species_name) VALUES ($1);
-- UPDATE plant_species SET species_name = $1 WHERE species_id = $2;
-- DELETE FROM plant_species WHERE species_id = $1;

-- CRUD операции для режимов полива
-- INSERT INTO watering_regimes (species_id, min_age_months, max_age_months, periodicity, time_of_day, water_liters) 
-- VALUES ($1, $2, $3, $4, $5, $6);
-- UPDATE watering_regimes SET min_age_months = $1, max_age_months = $2, periodicity = $3, time_of_day = $4, water_liters = $5 
-- WHERE regime_id = $6;
-- DELETE FROM watering_regimes WHERE regime_id = $1;

-- CRUD операции для растений
-- INSERT INTO plants (local_plant_number, zone_id, species_id, date_planted, age_at_planting_months) 
-- VALUES ($1, $2, $3, $4, $5);
-- UPDATE plants SET local_plant_number = $1, zone_id = $2, species_id = $3, date_planted = $4, age_at_planting_months = $5 
-- WHERE plant_id = $6;
-- DELETE FROM plants WHERE plant_id = $1;

-- CRUD операции для сотрудников (служителей)
-- INSERT INTO employees (full_name, phone, address, employee_type) 
-- VALUES ($1, $2, $3, 'служитель');
-- UPDATE employees SET full_name = $1, phone = $2, address = $3 WHERE employee_id = $4;
-- DELETE FROM employees WHERE employee_id = $1;

-- CRUD операции для сотрудников (декораторов)
-- INSERT INTO employees (full_name, phone, address, employee_type, education, university, category) 
-- VALUES ($1, $2, $3, 'декоратор', $4, $5, $6);
-- UPDATE employees SET full_name = $1, phone = $2, address = $3, education = $4, university = $5, category = $6 
-- WHERE employee_id = $7;
-- DELETE FROM employees WHERE employee_id = $1;

-- CRUD операции для графика работ
-- INSERT INTO schedule (plant_id, employee_id, assignment_date) VALUES ($1, $2, $3);
-- UPDATE schedule SET plant_id = $1, employee_id = $2, assignment_date = $3 WHERE schedule_id = $4;
-- DELETE FROM schedule WHERE schedule_id = $1;

