-- Функция для расчета текущего возраста растения в месяцах
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
    
    -- Разница в месяцах между датой посадки и СЕГОДНЯ
    v_current_age_months := (
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM v_plant_record.date_planted)
    ) * 12 + (
        EXTRACT(MONTH FROM CURRENT_DATE) - EXTRACT(MONTH FROM v_plant_record.date_planted)
    );
    
    -- Возвращаем (возраст при посадке) + (прошедшие месяцы)
    RETURN v_plant_record.age_at_planting_months + v_current_age_months;
END;
$$ LANGUAGE plpgsql;

