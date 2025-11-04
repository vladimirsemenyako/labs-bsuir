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

