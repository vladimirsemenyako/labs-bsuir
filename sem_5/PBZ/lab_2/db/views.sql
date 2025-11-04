-- View 1: Полная информация по всем растениям
CREATE OR REPLACE VIEW v_all_plants_info AS 
SELECT
    p.plant_id,
    p.local_plant_number,
    p.date_planted,
    p.age_at_planting_months,
    fn_get_plant_current_age(p.plant_id) AS current_age_months,
    ps.species_id,
    ps.species_name,
    z.zone_id,
    z.name AS zone_name,
    pr.park_id,
    pr.name AS park_name,
    f.firm_id,
    f.name AS firm_name
FROM plants p
JOIN plant_species ps ON p.species_id = ps.species_id
JOIN zones z ON p.zone_id = z.zone_id
JOIN parks pr ON z.park_id = pr.park_id
JOIN firm f ON pr.firm_id = f.firm_id;

-- View 2: Текущие режимы полива для всех растений
CREATE OR REPLACE VIEW v_plant_current_regimes AS 
SELECT
    v.plant_id,
    v.local_plant_number,
    v.species_name,
    v.zone_name,
    v.park_name,
    v.current_age_months,
    wr.regime_id,
    wr.periodicity,
    wr.time_of_day,
    wr.water_liters
FROM v_all_plants_info v
LEFT JOIN watering_regimes wr ON v.species_id = wr.species_id
    AND v.current_age_months >= wr.min_age_months
    AND (wr.max_age_months IS NULL OR v.current_age_months <= wr.max_age_months);

-- View 3: Полный график работы сотрудников
CREATE OR REPLACE VIEW v_employee_schedule AS 
SELECT
    s.schedule_id,
    s.assignment_date,
    e.employee_id,
    e.full_name,
    e.phone,
    e.address,
    p.plant_id,
    p.local_plant_number,
    z.name AS zone_name,
    pr.name AS park_name
FROM schedule s
JOIN employees e ON s.employee_id = e.employee_id
JOIN plants p ON s.plant_id = p.plant_id
JOIN zones z ON p.zone_id = z.zone_id
JOIN parks pr ON z.park_id = pr.park_id
WHERE e.employee_type = 'служитель';

