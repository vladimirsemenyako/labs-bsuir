PRAGMA foreign_keys = ON;

-- Company providing services
CREATE TABLE IF NOT EXISTS company (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT NOT NULL,
  legal_address TEXT NOT NULL
);

-- Parks
CREATE TABLE IF NOT EXISTS park (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  address TEXT NOT NULL
);

-- Zones within a park
CREATE TABLE IF NOT EXISTS zone (
  id INTEGER PRIMARY KEY,
  park_id INTEGER NOT NULL REFERENCES park(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  UNIQUE(park_id, name)
);

-- Species (plant kinds)
CREATE TABLE IF NOT EXISTS species (
  id INTEGER PRIMARY KEY,
  latin_name TEXT NOT NULL UNIQUE,
  common_name TEXT
);

-- Plants planted in zones
CREATE TABLE IF NOT EXISTS plant (
  id INTEGER PRIMARY KEY,
  zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE CASCADE,
  species_id INTEGER NOT NULL REFERENCES species(id),
  plant_number INTEGER NOT NULL,
  planting_date DATE NOT NULL,
  age_years_at_planting INTEGER NOT NULL CHECK (age_years_at_planting >= 0),
  UNIQUE(zone_id, plant_number)
);

-- Watering regime depends on species and age ranges
CREATE TABLE IF NOT EXISTS watering_regime (
  id INTEGER PRIMARY KEY,
  species_id INTEGER NOT NULL REFERENCES species(id) ON DELETE CASCADE,
  min_age_years INTEGER NOT NULL CHECK (min_age_years >= 0),
  max_age_years INTEGER NOT NULL CHECK (max_age_years >= min_age_years),
  day_pattern TEXT NOT NULL, -- e.g., 'daily', 'weekly:2' (Mon), 'odd_days', 'even_days'
  time_of_day TEXT NOT NULL, -- 'HH:MM'
  water_liters REAL NOT NULL CHECK (water_liters > 0)
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_regime_species_age
ON watering_regime(species_id, min_age_years, max_age_years, day_pattern, time_of_day);

-- Concrete waterings (at most once per plant per day)
CREATE TABLE IF NOT EXISTS watering (
  id INTEGER PRIMARY KEY,
  plant_id INTEGER NOT NULL REFERENCES plant(id) ON DELETE CASCADE,
  watering_date DATE NOT NULL,
  time_of_day TEXT NOT NULL,
  liters REAL NOT NULL CHECK (liters > 0),
  UNIQUE(plant_id, watering_date)
);

-- Park attendants caring for plants
CREATE TABLE IF NOT EXISTS attendant (
  id INTEGER PRIMARY KEY,
  full_name TEXT NOT NULL,
  birth_date DATE,
  phone TEXT,
  address TEXT
);

-- Assignment of attendant to a plant for specific date (one per date)
CREATE TABLE IF NOT EXISTS attendant_assignment (
  id INTEGER PRIMARY KEY,
  plant_id INTEGER NOT NULL REFERENCES plant(id) ON DELETE CASCADE,
  assignment_date DATE NOT NULL,
  attendant_id INTEGER NOT NULL REFERENCES attendant(id) ON DELETE RESTRICT,
  UNIQUE(plant_id, assignment_date)
);

-- Park decorators
CREATE TABLE IF NOT EXISTS decorator (
  id INTEGER PRIMARY KEY,
  full_name TEXT NOT NULL,
  birth_date DATE,
  phone TEXT,
  address TEXT,
  education TEXT,
  institution TEXT,
  category TEXT
);

-- Seed data for convenience
INSERT INTO company(id, name, legal_address)
  VALUES (1, 'ООО "Зелёный Город"', 'г. Минск, ул. Примерная, 1')
  ON CONFLICT(id) DO NOTHING;


