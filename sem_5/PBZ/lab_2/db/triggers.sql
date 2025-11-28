-- Триггерная функция для проверки типа сотрудника при назначении графика
CREATE OR REPLACE FUNCTION trg_check_employee_type_for_schedule() 
RETURNS TRIGGER AS $$
DECLARE
    v_emp_type T_EMPLOYEE_TYPE;
BEGIN
    -- Получаем тип сотрудника, которого пытаемся назначить
    SELECT employee_type INTO v_emp_type
    FROM employees
    WHERE employee_id = NEW.employee_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Сотрудник с ID=% не найден', NEW.employee_id;
    END IF;
    
    -- Если он НЕ 'служитель', генерируем ошибку
    IF v_emp_type != 'служитель' THEN
        RAISE EXCEPTION 'Назначение невозможно: Сотрудник (ID=%) является "%", а не "служитель"', 
            NEW.employee_id, v_emp_type;
    END IF;
    
    -- Если все в порядке, разрешаем операцию
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к таблице 'schedule'
CREATE TRIGGER before_schedule_insert_or_update 
BEFORE INSERT OR UPDATE ON schedule
FOR EACH ROW
EXECUTE FUNCTION trg_check_employee_type_for_schedule();


-- Триггерная функция для проверки уникальности режимов полива по возрасту
-- Обеспечивает, что для одного вида растения с одинаковым возрастом - только один режим полива
CREATE OR REPLACE FUNCTION trg_check_watering_regime_uniqueness()
RETURNS TRIGGER AS $$
DECLARE
    v_overlapping_count INT;
    v_overlapping_regime RECORD;
    v_new_max INT;
    v_existing_max INT;
BEGIN
    -- Используем большое, но безопасное значение для NULL (999999 вместо 2147483647)
    v_new_max := COALESCE(NEW.max_age_months, 999999);
    
    -- Проверяем, есть ли режимы с пересекающимися возрастными диапазонами для того же вида
    SELECT COUNT(*) INTO v_overlapping_count
    FROM watering_regimes wr
    WHERE wr.species_id = NEW.species_id
      AND wr.regime_id != COALESCE(NEW.regime_id, -1)
      AND int4range(wr.min_age_months, COALESCE(wr.max_age_months, 999999), '[]') 
          && 
          int4range(NEW.min_age_months, v_new_max, '[]');
    
    IF v_overlapping_count > 0 THEN
        -- Получаем информацию о первом пересекающемся режиме для более информативного сообщения
        SELECT wr.regime_id, wr.min_age_months, wr.max_age_months, ps.species_name
        INTO v_overlapping_regime
        FROM watering_regimes wr
        JOIN plant_species ps ON wr.species_id = ps.species_id
        WHERE wr.species_id = NEW.species_id
          AND wr.regime_id != COALESCE(NEW.regime_id, -1)
          AND int4range(wr.min_age_months, COALESCE(wr.max_age_months, 999999), '[]') 
              && 
              int4range(NEW.min_age_months, v_new_max, '[]')
        LIMIT 1;
        
        RAISE EXCEPTION 'Ошибка: Для вида "%" уже существует режим полива (ID=%) с пересекающимся возрастным диапазоном (%-% месяцев). Для одного растения с одинаковым возрастом может быть только один режим полива.',
            v_overlapping_regime.species_name,
            v_overlapping_regime.regime_id,
            v_overlapping_regime.min_age_months,
            COALESCE(v_overlapping_regime.max_age_months::TEXT, '∞');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Привязываем триггер к таблице 'watering_regimes'
CREATE TRIGGER before_watering_regime_insert_or_update
BEFORE INSERT OR UPDATE ON watering_regimes
FOR EACH ROW
EXECUTE FUNCTION trg_check_watering_regime_uniqueness();

