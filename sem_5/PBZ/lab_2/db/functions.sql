-- Функция: fn_get_plant_current_age - Расчет текущего возраста растения в месяцах
CREATE OR REPLACE FUNCTION fn_get_plant_current_age(p_plant_id INT) 
RETURNS INT AS $$
DECLARE
    v_current_age_months INT;
    v_plant_record RECORD;
BEGIN
    SELECT date_planted, age_at_planting_months INTO v_plant_record
    FROM plants
    WHERE plant_id = p_plant_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Растение с ID=% не найдено', p_plant_id;
    END IF;
    
    
    v_current_age_months := (
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM v_plant_record.date_planted)
    ) * 12 + (
        EXTRACT(MONTH FROM CURRENT_DATE) - EXTRACT(MONTH FROM v_plant_record.date_planted)
    );
    
    
    RETURN v_plant_record.age_at_planting_months + v_current_age_months;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_firms - Получить все фирмы
CREATE OR REPLACE FUNCTION fn_get_all_firms()
RETURNS TABLE (
    firm_id INT,
    name VARCHAR(255),
    legal_address TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT f.firm_id, f.name, f.legal_address
    FROM firm f
    ORDER BY f.firm_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_firm_by_id - Получить фирму по ID
CREATE OR REPLACE FUNCTION fn_get_firm_by_id(p_firm_id INT)
RETURNS TABLE (
    firm_id INT,
    name VARCHAR(255),
    legal_address TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT f.firm_id, f.name, f.legal_address
    FROM firm f
    WHERE f.firm_id = p_firm_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_firm - Добавить фирму (возвращает ID новой фирмы)
CREATE OR REPLACE FUNCTION sp_add_firm(
    p_name VARCHAR(255),
    p_legal_address TEXT
) RETURNS INT AS $$
DECLARE
    v_firm_id INT;
BEGIN
    INSERT INTO firm (name, legal_address)
    VALUES (p_name, p_legal_address)
    RETURNING firm_id INTO v_firm_id;
    RETURN v_firm_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_firm - Обновить данные фирмы
CREATE OR REPLACE PROCEDURE sp_update_firm(
    p_firm_id INT,
    p_name VARCHAR(255),
    p_legal_address TEXT
) AS $$
BEGIN
    UPDATE firm
    SET name = p_name, legal_address = p_legal_address
    WHERE firm_id = p_firm_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Фирма с ID=% не найдена', p_firm_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_firm - Удалить фирму
CREATE OR REPLACE PROCEDURE sp_delete_firm(p_firm_id INT) AS $$
BEGIN
    DELETE FROM firm WHERE firm_id = p_firm_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Фирма с ID=% не найдена', p_firm_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_parks - Получить все парки с названиями фирм
CREATE OR REPLACE FUNCTION fn_get_all_parks()
RETURNS TABLE (
    park_id INT,
    name VARCHAR(255),
    firm_id INT,
    firm_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.park_id, p.name, p.firm_id, f.name AS firm_name
    FROM parks p
    JOIN firm f ON p.firm_id = f.firm_id
    ORDER BY p.park_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_park_by_id - Получить парк по ID
CREATE OR REPLACE FUNCTION fn_get_park_by_id(p_park_id INT)
RETURNS TABLE (
    park_id INT,
    name VARCHAR(255),
    firm_id INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.park_id, p.name, p.firm_id
    FROM parks p
    WHERE p.park_id = p_park_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_park - Добавить парк (возвращает ID нового парка)
CREATE OR REPLACE FUNCTION sp_add_park(
    p_firm_id INT,
    p_name VARCHAR(255)
) RETURNS INT AS $$
DECLARE
    v_park_id INT;
BEGIN
    INSERT INTO parks (firm_id, name)
    VALUES (p_firm_id, p_name)
    RETURNING park_id INTO v_park_id;
    RETURN v_park_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_park - Обновить данные парка
CREATE OR REPLACE PROCEDURE sp_update_park(
    p_park_id INT,
    p_name VARCHAR(255)
) AS $$
BEGIN
    UPDATE parks
    SET name = p_name
    WHERE park_id = p_park_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Парк с ID=% не найден', p_park_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_park - Удалить парк
CREATE OR REPLACE PROCEDURE sp_delete_park(p_park_id INT) AS $$
BEGIN
    DELETE FROM parks WHERE park_id = p_park_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Парк с ID=% не найден', p_park_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_zones - Получить все зоны с названиями парков
CREATE OR REPLACE FUNCTION fn_get_all_zones()
RETURNS TABLE (
    zone_id INT,
    name VARCHAR(100),
    park_id INT,
    park_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT z.zone_id, z.name, z.park_id, p.name AS park_name
    FROM zones z
    JOIN parks p ON z.park_id = p.park_id
    ORDER BY z.zone_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_zone_by_id - Получить зону по ID
CREATE OR REPLACE FUNCTION fn_get_zone_by_id(p_zone_id INT)
RETURNS TABLE (
    zone_id INT,
    name VARCHAR(100),
    park_id INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT z.zone_id, z.name, z.park_id
    FROM zones z
    WHERE z.zone_id = p_zone_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_zone - Добавить зону (возвращает ID новой зоны)
CREATE OR REPLACE FUNCTION sp_add_zone(
    p_park_id INT,
    p_name VARCHAR(100)
) RETURNS INT AS $$
DECLARE
    v_zone_id INT;
BEGIN
    INSERT INTO zones (park_id, name)
    VALUES (p_park_id, p_name)
    RETURNING zone_id INTO v_zone_id;
    RETURN v_zone_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_zone - Обновить данные зоны
CREATE OR REPLACE PROCEDURE sp_update_zone(
    p_zone_id INT,
    p_name VARCHAR(100)
) AS $$
BEGIN
    UPDATE zones
    SET name = p_name
    WHERE zone_id = p_zone_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Зона с ID=% не найдена', p_zone_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_zone - Удалить зону
CREATE OR REPLACE PROCEDURE sp_delete_zone(p_zone_id INT) AS $$
BEGIN
    DELETE FROM zones WHERE zone_id = p_zone_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Зона с ID=% не найдена', p_zone_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_species - Получить все виды растений
CREATE OR REPLACE FUNCTION fn_get_all_species()
RETURNS TABLE (
    species_id INT,
    species_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT ps.species_id, ps.species_name
    FROM plant_species ps
    ORDER BY ps.species_name;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_species_by_id - Получить вид растения по ID
CREATE OR REPLACE FUNCTION fn_get_species_by_id(p_species_id INT)
RETURNS TABLE (
    species_id INT,
    species_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT ps.species_id, ps.species_name
    FROM plant_species ps
    WHERE ps.species_id = p_species_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_species - Добавить вид растения (возвращает ID нового вида)
CREATE OR REPLACE FUNCTION sp_add_species(
    p_species_name VARCHAR(100)
) RETURNS INT AS $$
DECLARE
    v_species_id INT;
BEGIN
    INSERT INTO plant_species (species_name)
    VALUES (p_species_name)
    RETURNING species_id INTO v_species_id;
    RETURN v_species_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_species - Обновить данные вида растения
CREATE OR REPLACE PROCEDURE sp_update_species(
    p_species_id INT,
    p_species_name VARCHAR(100)
) AS $$
BEGIN
    UPDATE plant_species
    SET species_name = p_species_name
    WHERE species_id = p_species_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Вид растения с ID=% не найден', p_species_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_species - Удалить вид растения
CREATE OR REPLACE PROCEDURE sp_delete_species(p_species_id INT) AS $$
BEGIN
    DELETE FROM plant_species WHERE species_id = p_species_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Вид растения с ID=% не найден', p_species_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_plants - Получить все растения с полной информацией
CREATE OR REPLACE FUNCTION fn_get_all_plants()
RETURNS TABLE (
    plant_id INT,
    local_plant_number VARCHAR(50),
    date_planted DATE,
    age_at_planting_months INT,
    current_age_months INT,
    species_id INT,
    species_name VARCHAR(100),
    zone_id INT,
    zone_name VARCHAR(100),
    park_id INT,
    park_name VARCHAR(255),
    firm_id INT,
    firm_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM v_all_plants_info
    ORDER BY plant_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_plant_by_id - Получить растение по ID
CREATE OR REPLACE FUNCTION fn_get_plant_by_id(p_plant_id INT)
RETURNS TABLE (
    plant_id INT,
    local_plant_number VARCHAR(50),
    zone_id INT,
    species_id INT,
    date_planted DATE,
    age_at_planting_months INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.plant_id, p.local_plant_number, p.zone_id, p.species_id, 
           p.date_planted, p.age_at_planting_months
    FROM plants p
    WHERE p.plant_id = p_plant_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_plants_by_species - Получить все растения заданного вида
CREATE OR REPLACE FUNCTION fn_get_plants_by_species(p_species_name VARCHAR(100))
RETURNS TABLE (
    plant_id INT,
    local_plant_number VARCHAR(50),
    date_planted DATE,
    age_at_planting_months INT,
    current_age_months INT,
    species_id INT,
    species_name VARCHAR(100),
    zone_id INT,
    zone_name VARCHAR(100),
    park_id INT,
    park_name VARCHAR(255),
    firm_id INT,
    firm_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM v_all_plants_info
    WHERE species_name = p_species_name
    ORDER BY plant_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_plant - Добавить растение (возвращает ID нового растения)
CREATE OR REPLACE FUNCTION sp_add_plant(
    p_local_plant_number VARCHAR(50),
    p_zone_id INT,
    p_species_id INT,
    p_date_planted DATE,
    p_age_at_planting_months INT
) RETURNS INT AS $$
DECLARE
    v_plant_id INT;
BEGIN
    INSERT INTO plants (local_plant_number, zone_id, species_id, date_planted, age_at_planting_months)
    VALUES (p_local_plant_number, p_zone_id, p_species_id, p_date_planted, p_age_at_planting_months)
    RETURNING plant_id INTO v_plant_id;
    RETURN v_plant_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_plant - Обновить данные растения
CREATE OR REPLACE PROCEDURE sp_update_plant(
    p_plant_id INT,
    p_local_plant_number VARCHAR(50),
    p_zone_id INT,
    p_species_id INT,
    p_date_planted DATE,
    p_age_at_planting_months INT
) AS $$
BEGIN
    UPDATE plants
    SET local_plant_number = p_local_plant_number,
        zone_id = p_zone_id,
        species_id = p_species_id,
        date_planted = p_date_planted,
        age_at_planting_months = p_age_at_planting_months
    WHERE plant_id = p_plant_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Растение с ID=% не найдено', p_plant_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_plant - Удалить растение
CREATE OR REPLACE PROCEDURE sp_delete_plant(p_plant_id INT) AS $$
BEGIN
    DELETE FROM plants WHERE plant_id = p_plant_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Растение с ID=% не найдено', p_plant_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_caretakers - Получить всех служителей
CREATE OR REPLACE FUNCTION fn_get_all_caretakers()
RETURNS TABLE (
    employee_id INT,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.employee_id, e.full_name, e.phone, e.address
    FROM employees e
    WHERE e.employee_type = 'служитель'
    ORDER BY e.employee_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_all_decorators - Получить всех декораторов
CREATE OR REPLACE FUNCTION fn_get_all_decorators()
RETURNS TABLE (
    employee_id INT,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    education TEXT,
    university VARCHAR(255),
    category T_DECORATOR_CATEGORY
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.employee_id, e.full_name, e.phone, e.address, 
           e.education, e.university, e.category
    FROM employees e
    WHERE e.employee_type = 'декоратор'
    ORDER BY e.employee_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_employee_by_id - Получить сотрудника по ID
CREATE OR REPLACE FUNCTION fn_get_employee_by_id(p_employee_id INT)
RETURNS TABLE (
    employee_id INT,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    employee_type T_EMPLOYEE_TYPE,
    education TEXT,
    university VARCHAR(255),
    category T_DECORATOR_CATEGORY
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.employee_id, e.full_name, e.phone, e.address, 
           e.employee_type, e.education, e.university, e.category
    FROM employees e
    WHERE e.employee_id = p_employee_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_caretaker - Добавить служителя (возвращает ID нового сотрудника)
CREATE OR REPLACE FUNCTION sp_add_caretaker(
    p_full_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address TEXT
) RETURNS INT AS $$
DECLARE
    v_employee_id INT;
BEGIN
    INSERT INTO employees (full_name, phone, address, employee_type)
    VALUES (p_full_name, p_phone, p_address, 'служитель')
    RETURNING employee_id INTO v_employee_id;
    RETURN v_employee_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_decorator - Добавить декоратора (возвращает ID нового сотрудника)
CREATE OR REPLACE FUNCTION sp_add_decorator(
    p_full_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address TEXT,
    p_education TEXT,
    p_university VARCHAR(255),
    p_category T_DECORATOR_CATEGORY
) RETURNS INT AS $$
DECLARE
    v_employee_id INT;
BEGIN
    INSERT INTO employees (full_name, phone, address, employee_type, education, university, category)
    VALUES (p_full_name, p_phone, p_address, 'декоратор', p_education, p_university, p_category)
    RETURNING employee_id INTO v_employee_id;
    RETURN v_employee_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_caretaker - Обновить данные служителя
CREATE OR REPLACE PROCEDURE sp_update_caretaker(
    p_employee_id INT,
    p_full_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address TEXT
) AS $$
BEGIN
    UPDATE employees
    SET full_name = p_full_name, phone = p_phone, address = p_address
    WHERE employee_id = p_employee_id AND employee_type = 'служитель';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Служитель с ID=% не найден', p_employee_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_update_decorator - Обновить данные декоратора
CREATE OR REPLACE PROCEDURE sp_update_decorator(
    p_employee_id INT,
    p_full_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address TEXT,
    p_education TEXT,
    p_university VARCHAR(255),
    p_category T_DECORATOR_CATEGORY
) AS $$
BEGIN
    UPDATE employees
    SET full_name = p_full_name, phone = p_phone, address = p_address,
        education = p_education, university = p_university, category = p_category
    WHERE employee_id = p_employee_id AND employee_type = 'декоратор';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Декоратор с ID=% не найден', p_employee_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Процедура: sp_delete_employee - Удалить сотрудника
CREATE OR REPLACE PROCEDURE sp_delete_employee(p_employee_id INT) AS $$
BEGIN
    DELETE FROM employees WHERE employee_id = p_employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Сотрудник с ID=% не найден', p_employee_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_schedule_by_date - Получить график работ на заданную дату
CREATE OR REPLACE FUNCTION fn_get_schedule_by_date(p_date DATE)
RETURNS TABLE (
    schedule_id INT,
    assignment_date DATE,
    employee_id INT,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    plant_id INT,
    local_plant_number VARCHAR(50),
    zone_name VARCHAR(100),
    park_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM v_employee_schedule v
    WHERE v.assignment_date = p_date
    ORDER BY v.assignment_date, v.full_name;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_employees_by_date - Получить список сотрудников, работающих на дату
CREATE OR REPLACE FUNCTION fn_get_employees_by_date(p_date DATE)
RETURNS TABLE (
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT e.full_name, e.phone, e.address
    FROM v_employee_schedule e
    WHERE e.assignment_date = p_date
    ORDER BY e.full_name;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_schedule - Добавить назначение в график (возвращает ID назначения)
CREATE OR REPLACE FUNCTION sp_add_schedule(
    p_plant_id INT,
    p_employee_id INT,
    p_assignment_date DATE
) RETURNS INT AS $$
DECLARE
    v_schedule_id INT;
BEGIN
    INSERT INTO schedule (plant_id, employee_id, assignment_date)
    VALUES (p_plant_id, p_employee_id, p_assignment_date)
    RETURNING schedule_id INTO v_schedule_id;
    RETURN v_schedule_id;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_all_watering_regimes - Получить все режимы полива
CREATE OR REPLACE FUNCTION fn_get_all_watering_regimes()
RETURNS TABLE (
    regime_id INT,
    species_id INT,
    species_name VARCHAR(100),
    min_age_months INT,
    max_age_months INT,
    periodicity T_WATERING_PERIODICITY,
    time_of_day TIME,
    water_liters DECIMAL(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT wr.regime_id, wr.species_id, ps.species_name, wr.min_age_months, 
           wr.max_age_months, wr.periodicity, wr.time_of_day, wr.water_liters
    FROM watering_regimes wr
    JOIN plant_species ps ON wr.species_id = ps.species_id
    ORDER BY ps.species_name, wr.min_age_months;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_plant_regimes_by_species - Получить режимы полива для растений заданного вида
CREATE OR REPLACE FUNCTION fn_get_plant_regimes_by_species(p_species_name VARCHAR(100))
RETURNS TABLE (
    plant_id INT,
    local_plant_number VARCHAR(50),
    species_name VARCHAR(100),
    zone_name VARCHAR(100),
    park_name VARCHAR(255),
    current_age_months INT,
    regime_id INT,
    periodicity T_WATERING_PERIODICITY,
    time_of_day TIME,
    water_liters DECIMAL(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM v_plant_current_regimes
    WHERE species_name = p_species_name
    ORDER BY plant_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: sp_add_watering_regime - Добавить режим полива (возвращает ID режима)
CREATE OR REPLACE FUNCTION sp_add_watering_regime(
    p_species_id INT,
    p_min_age_months INT,
    p_max_age_months INT,
    p_periodicity T_WATERING_PERIODICITY,
    p_time_of_day TIME,
    p_water_liters DECIMAL(5, 2)
) RETURNS INT AS $$
DECLARE
    v_regime_id INT;
BEGIN
    INSERT INTO watering_regimes (species_id, min_age_months, max_age_months, 
                                  periodicity, time_of_day, water_liters)
    VALUES (p_species_id, p_min_age_months, p_max_age_months, 
            p_periodicity, p_time_of_day, p_water_liters)
    RETURNING regime_id INTO v_regime_id;
    RETURN v_regime_id;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_firms_count - Получить количество фирм
CREATE OR REPLACE FUNCTION fn_get_firms_count()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM firm;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_parks_count - Получить количество парков
CREATE OR REPLACE FUNCTION fn_get_parks_count()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM parks;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_plants_count - Получить количество растений
CREATE OR REPLACE FUNCTION fn_get_plants_count()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM plants;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_employees_count - Получить количество сотрудников
CREATE OR REPLACE FUNCTION fn_get_employees_count()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM employees;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- Функция: fn_get_firms_list - Получить список фирм для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_firms_list()
RETURNS TABLE (
    firm_id INT,
    name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT f.firm_id, f.name
    FROM firm f
    ORDER BY f.firm_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_parks_list - Получить список парков для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_parks_list()
RETURNS TABLE (
    park_id INT,
    name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.park_id, p.name
    FROM parks p
    ORDER BY p.park_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_zones_list - Получить список зон для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_zones_list()
RETURNS TABLE (
    zone_id INT,
    name VARCHAR(100),
    park_id INT,
    park_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT z.zone_id, z.name, z.park_id, p.name AS park_name
    FROM zones z
    JOIN parks p ON z.park_id = p.park_id
    ORDER BY z.zone_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_species_list - Получить список видов растений для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_species_list()
RETURNS TABLE (
    species_id INT,
    species_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT ps.species_id, ps.species_name
    FROM plant_species ps
    ORDER BY ps.species_name;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_plants_list - Получить список растений для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_plants_list()
RETURNS TABLE (
    plant_id INT,
    local_plant_number VARCHAR(50),
    species_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.plant_id, p.local_plant_number, ps.species_name
    FROM plants p
    JOIN plant_species ps ON p.species_id = ps.species_id
    ORDER BY p.plant_id;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_caretakers_list - Получить список служителей для выпадающих списков
CREATE OR REPLACE FUNCTION fn_get_caretakers_list()
RETURNS TABLE (
    employee_id INT,
    full_name VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT e.employee_id, e.full_name
    FROM employees e
    WHERE e.employee_type = 'служитель'
    ORDER BY e.full_name;
END;
$$ LANGUAGE plpgsql;

-- Функция: fn_get_species_names - Получить список названий видов растений (для отчетов)
CREATE OR REPLACE FUNCTION fn_get_species_names()
RETURNS TABLE (
    species_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT ps.species_name
    FROM plant_species ps
    ORDER BY ps.species_name;
END;
$$ LANGUAGE plpgsql;

