-- Включаем расширение для работы с диапазонами (нужно для сложного триггера)
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Создаем пользовательские типы ENUM для категориальных данных
CREATE TYPE T_WATERING_PERIODICITY AS ENUM (
    'ежедневно', 'раз в неделю',
    'раз в 2 недели', 'раз в месяц'
);

CREATE TYPE T_DECORATOR_CATEGORY AS ENUM (
    'высшая',
    'первая', 'средняя',
    'без категории'
);

CREATE TYPE T_EMPLOYEE_TYPE AS ENUM (
    'служитель',
    'декоратор'
);

-- Таблица 1: Фирма
CREATE TABLE firm (
    firm_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    legal_address TEXT
);

-- Таблица 2: Парки
CREATE TABLE parks (
    park_id SERIAL PRIMARY KEY,
    firm_id INT NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT fk_firm
    FOREIGN KEY(firm_id) REFERENCES firm(firm_id) ON DELETE CASCADE
);

-- Таблица 3: Зоны
CREATE TABLE zones (
    zone_id SERIAL PRIMARY KEY,
    park_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_park
    FOREIGN KEY(park_id) REFERENCES parks(park_id) ON DELETE CASCADE,
    UNIQUE(park_id, name)
);

-- Таблица 4: Виды растений
CREATE TABLE plant_species (
    species_id SERIAL PRIMARY KEY,
    species_name VARCHAR(100) NOT NULL UNIQUE
);

-- Таблица 5: Режимы полива
CREATE TABLE watering_regimes (
    regime_id SERIAL PRIMARY KEY,
    species_id INT NOT NULL,
    min_age_months INT NOT NULL,
    max_age_months INT,
    periodicity T_WATERING_PERIODICITY NOT NULL,
    time_of_day TIME,
    water_liters DECIMAL(5, 2) NOT NULL,
    CONSTRAINT fk_species FOREIGN KEY(species_id)
    REFERENCES plant_species(species_id) ON DELETE RESTRICT,
    CHECK (min_age_months >= 0),
    CHECK (max_age_months IS NULL OR max_age_months > min_age_months),
    CHECK (water_liters > 0),
    CONSTRAINT prevent_overlapping_regimes EXCLUDE USING GIST (
        species_id WITH =,
        int4range(min_age_months, COALESCE(max_age_months, 999999), '[]') WITH &&
    )
);

-- Таблица 6: Растения
CREATE TABLE plants (
    plant_id SERIAL PRIMARY KEY,
    local_plant_number VARCHAR(50) NOT NULL,
    zone_id INT NOT NULL,
    species_id INT NOT NULL,
    date_planted DATE NOT NULL DEFAULT CURRENT_DATE,
    age_at_planting_months INT NOT NULL,
    CONSTRAINT fk_zone FOREIGN KEY(zone_id)
    REFERENCES zones(zone_id) ON DELETE RESTRICT,
    CONSTRAINT fk_species FOREIGN KEY(species_id)
    REFERENCES plant_species(species_id) ON DELETE RESTRICT,
    UNIQUE(zone_id, local_plant_number),
    CHECK (age_at_planting_months >= 0)
);

-- Таблица 7: Сотрудники (единая таблица)
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE,
    address TEXT,
    employee_type T_EMPLOYEE_TYPE NOT NULL,
    education TEXT,
    university VARCHAR(255),
    category T_DECORATOR_CATEGORY
);

-- Таблица 8: График работ
CREATE TABLE schedule (
    schedule_id SERIAL PRIMARY KEY,
    plant_id INT NOT NULL,
    employee_id INT NOT NULL,
    assignment_date DATE NOT NULL,
    CONSTRAINT fk_plant FOREIGN KEY(plant_id)
    REFERENCES plants(plant_id) ON DELETE CASCADE,
    CONSTRAINT fk_employee FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id) ON DELETE RESTRICT,
    UNIQUE(plant_id, assignment_date)
);

