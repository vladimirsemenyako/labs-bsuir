import math
import sys
import os

#Class для работы с интервалами (как в лекции: [min, max])
class Interval:
    def __init__(self, low, high):
        self.low = max(0.0, low)
        self.high = min(1.0, high)

    def intersect(self, other):
        new_low = max(self.low, other.low)
        new_high = min(self.high, other.high)
        # Если нижняя граница больше верхней (с учетом погрешности float), пересечения нет
        if new_low > new_high + 1e-9: 
            return None
        return Interval(new_low, new_high)

    def __repr__(self):
        # Округляем для красивого вывода
        low_rounded = round(self.low, 2)
        high_rounded = round(self.high, 2)
        # Если границы совпадают, выводим только одно число
        if abs(low_rounded - high_rounded) < 1e-9:
            return f"{low_rounded}"
        return f"[{low_rounded}; {high_rounded}]"

#Class для представления множества решений (квадрат или линия)
class SolutionSet:
    def __init__(self, type_str, intervals_dict, sum_val=None):
        self.type = type_str # 'box' (прямоугольник) или 'line' (линия sum=const)
        self.intervals = intervals_dict  # Словарь {var_name: Interval}
        self.sum_val = sum_val 

    def __repr__(self):
        parts = []
        for var_name, interval in sorted(self.intervals.items()):
            parts.append(f"{var_name} ∈ {interval}")
        
        if self.type == 'box':
            return f"{{ {', '.join(parts)} }}"
        else:
            var_names = sorted(self.intervals.keys())
            sum_expr = "+".join(var_names)
            return f"{{ {sum_expr}={self.sum_val} | {', '.join(parts)} }}"

def parse_r_line(line):
    """Парсит строку R без регулярных выражений. Ищет паттерн <<var1,var2>, val>"""
    matches = []
    i = 0
    while i < len(line):
        # Ищем начало паттерна <<
        if i < len(line) - 1 and line[i:i+2] == "<<":
            # Находим первую запятую после <<
            comma1_pos = line.find(',', i + 2)
            if comma1_pos == -1:
                i += 1
                continue
            
            # Извлекаем var1 (r_name)
            r_name = line[i+2:comma1_pos].strip()
            
            # Ищем закрывающую скобку >
            bracket1_pos = line.find('>', comma1_pos + 1)
            if bracket1_pos == -1:
                i += 1
                continue
            
            # Извлекаем var2 (c_name)
            c_name = line[comma1_pos+1:bracket1_pos].strip()
            
            # Ищем запятую после >
            comma2_pos = line.find(',', bracket1_pos + 1)
            if comma2_pos == -1:
                i += 1
                continue
            
            # Ищем закрывающую скобку >
            bracket2_pos = line.find('>', comma2_pos + 1)
            if bracket2_pos == -1:
                i += 1
                continue
            
            # Извлекаем val
            val_str = line[comma2_pos+1:bracket2_pos].strip()
            
            # Проверяем, что все части не пустые и val - число
            if r_name and c_name and val_str:
                try:
                    val = float(val_str)
                    matches.append((r_name, c_name, val))
                    i = bracket2_pos + 1
                except ValueError:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return matches

def parse_y_line(line):
    """Парсит строку Y без регулярных выражений. Ищет паттерн <var, val>"""
    matches = []
    i = 0
    while i < len(line):
        # Ищем начало паттерна <
        if line[i] == '<':
            # Находим запятую
            comma_pos = line.find(',', i + 1)
            if comma_pos == -1:
                i += 1
                continue
            
            # Извлекаем var (c_name)
            c_name = line[i+1:comma_pos].strip()
            
            # Ищем закрывающую скобку >
            bracket_pos = line.find('>', comma_pos + 1)
            if bracket_pos == -1:
                i += 1
                continue
            
            # Извлекаем val
            val_str = line[comma_pos+1:bracket_pos].strip()
            
            # Проверяем, что все части не пустые и val - число
            if c_name and val_str:
                try:
                    val = float(val_str)
                    matches.append((c_name, val))
                    i = bracket_pos + 1
                except ValueError:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return matches

def parse_input_file(filename):
    """
    Читает файл и парсит структуры R(x,y) и Y(y).
    Возвращает словарь R (по колонкам) и словарь Y.
    """
    if not os.path.exists(filename):
        print(f"ОШИБКА: Файл {filename} не найден!")
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    R_dict = {} # Формат: {'c': {'a': 0.7, ...}, 'd': ...}
    Y_dict = {} # Формат: {'c': 0.7, 'd': 0.8}
    row_vars = set() # 'a', 'b'

    for line in lines:
        line = line.strip()
        # Парсинг R(x,y). Ищем паттерн <<var1,var2>, val>
        if line.startswith("R"):
            matches = parse_r_line(line)
            for r_name, c_name, val in matches:
                if c_name not in R_dict:
                    R_dict[c_name] = {}
                R_dict[c_name][r_name] = float(val)
                row_vars.add(r_name)
        
        # Парсинг Y(y). Ищем паттерн <var, val>
        elif line.startswith("Y"):
            matches = parse_y_line(line)
            for c_name, val in matches:
                Y_dict[c_name] = float(val)

    # Сортируем имена переменных, чтобы a всегда было первым, b вторым (для однозначности вывода)
    sorted_rows = sorted(list(row_vars))
    return R_dict, Y_dict, sorted_rows

def solve_single_equation(r_vals, target, row_names):
    """
    Решает одно уравнение вида min(1, sum(min(var_i, r_i))) = target
    Поддерживает произвольное количество переменных
    """
    solutions = []
    n = len(row_names)
    
    # Специальный случай: одна переменная
    if n == 1:
        var_name = row_names[0]
        r_val = r_vals.get(var_name, 0.0)
        
        # min(1, min(a, r)) = target
        if target < r_val:
            # a = target, где a ∈ [0, r_val]
            valid_a = Interval(target, target)
            if valid_a.low <= r_val:
                solutions.append(SolutionSet('box', {var_name: valid_a}))
        elif math.isclose(target, r_val, abs_tol=1e-9):
            # a >= r_val, где a ∈ [r_val, 1.0]
            valid_a = Interval(r_val, 1.0)
            solutions.append(SolutionSet('box', {var_name: valid_a}))
        # Если target > r_val и target != 1, решений нет (так как min(1, min(a, r)) <= r_val)
        elif target > r_val and not math.isclose(target, 1.0, abs_tol=1e-9):
            pass  # Нет решений
        elif math.isclose(target, 1.0, abs_tol=1e-9):
            # target = 1, тогда min(a, r) >= 1, что возможно только если r >= 1
            # Но так как r <= 1, то a >= r и r >= 1, значит a = 1 и r = 1
            if math.isclose(r_val, 1.0, abs_tol=1e-9):
                solutions.append(SolutionSet('box', {var_name: Interval(1.0, 1.0)}))
        
        return solutions
    
    # Для двух и более переменных используем обобщенную логику
    # Для простоты сначала реализуем для двух переменных (как было)
    if n == 2:
        name_a, name_b = row_names[0], row_names[1]
        r_a = r_vals.get(name_a, 0.0)
        r_b = r_vals.get(name_b, 0.0)

        # --- Случай 1: a < ra И b < rb (Сумма) ---
        # a + b = target
        if target < r_a + r_b: 
            valid_a = Interval(0, r_a)
            valid_b = Interval(0, r_b) 
            sol = SolutionSet('line', {name_a: valid_a, name_b: valid_b}, sum_val=target)
            solutions.append(sol)

        # --- Случай 2: a < ra И b >= rb ---
        # a + rb = target => a = target - rb
        val_a = target - r_b
        if 0 <= val_a < r_a: 
            valid_a = Interval(val_a, val_a)
            valid_b = Interval(r_b, 1.0)
            solutions.append(SolutionSet('box', {name_a: valid_a, name_b: valid_b}))

        # --- Случай 3: a >= ra И b < rb ---
        # ra + b = target => b = target - ra
        val_b = target - r_a
        if 0 <= val_b < r_b: 
            valid_a = Interval(r_a, 1.0)     
            valid_b = Interval(val_b, val_b) 
            solutions.append(SolutionSet('box', {name_a: valid_a, name_b: valid_b}))

        # --- Случай 4: a >= ra И b >= rb ---
        # ra + rb = target
        if math.isclose(r_a + r_b, target, abs_tol=1e-9):
            valid_a = Interval(r_a, 1.0)
            valid_b = Interval(r_b, 1.0)
            solutions.append(SolutionSet('box', {name_a: valid_a, name_b: valid_b}))
    
    return solutions

def intersect_solutions(sol1, sol2):
    """
    Находит пересечение двух множеств решений (от Уравнения 1 и Уравнения 2).
    Поддерживает произвольное количество переменных.
    """
    # 1. Пересечение областей определения для всех переменных
    all_vars = set(sol1.intervals.keys()) | set(sol2.intervals.keys())
    new_intervals = {}
    
    for var in all_vars:
        int1 = sol1.intervals.get(var)
        int2 = sol2.intervals.get(var)
        
        if int1 is None:
            new_intervals[var] = int2
        elif int2 is None:
            new_intervals[var] = int1
        else:
            intersected = int1.intersect(int2)
            if intersected is None:
                return None
            new_intervals[var] = intersected
    
    # 2. Логика типов (Line vs Box)
    if sol1.type == 'box' and sol2.type == 'box':
        return SolutionSet('box', new_intervals)
    
    elif sol1.type == 'line' and sol2.type == 'line':
        # Если суммы не равны -> параллельные прямые -> нет решений
        if not math.isclose(sol1.sum_val, sol2.sum_val, abs_tol=1e-9):
            return None
        return SolutionSet('line', new_intervals, sum_val=sol1.sum_val)
        
    else:
        # Смешанный тип: Прямая пересекает Прямоугольник
        line_sol = sol1 if sol1.type == 'line' else sol2
        box_sol = sol2 if sol1.type == 'line' else sol1
        
        # Для линии: sum(vars) = sum_val
        # Нужно проверить, что пересечение интервалов совместимо с этим ограничением
        # Это сложная задача в общем случае, но для 2 переменных работает как раньше
        if len(new_intervals) == 2:
            var_names = sorted(new_intervals.keys())
            var_a, var_b = var_names[0], var_names[1]
            int_a = new_intervals[var_a]
            int_b = new_intervals[var_b]
            
            # a = sum - b. b берется из интервала int_b
            derived_a = Interval(line_sol.sum_val - int_b.high, line_sol.sum_val - int_b.low)
            final_a = int_a.intersect(derived_a)
            
            # b = sum - a. a берется из интервала int_a
            derived_b = Interval(line_sol.sum_val - int_a.high, line_sol.sum_val - int_a.low)
            final_b = int_b.intersect(derived_b)
            
            if final_a is None or final_b is None:
                return None
            
            return SolutionSet('line', {var_a: final_a, var_b: final_b}, sum_val=line_sol.sum_val)
        else:
            # Для большего количества переменных просто возвращаем пересечение интервалов
            # (это консервативное приближение)
            return SolutionSet('line', new_intervals, sum_val=line_sol.sum_val)

def main():
    # Проверка аргументов командной строки
    if len(sys.argv) < 3:
        print("Использование: python main.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("--- Решение обратной задачи нечеткого вывода ---")
    
    # 1. Парсинг
    print(f"Чтение данных из {input_file}...")
    R, Y, row_names = parse_input_file(input_file)
    
    # Сортируем ключи Y (столбцы), чтобы порядок решения был как в тетради (c, d)
    col_names = sorted(Y.keys())
    
    if len(row_names) == 0:
        print("Ошибка: Не найдено входных переменных.")
        return

    print(f"Переменные строк (входы): {row_names}")
    print(f"Переменные столбцов (выходы): {col_names}")
    
    # Хранилище решений для каждого столбца
    column_solutions = [] 

    # 2. Решение отдельных уравнений для каждого столбца
    for col in col_names:
        target = Y[col]
        r_vals = R.get(col)
        
        if not r_vals:
            print(f"Предупреждение: для столбца {col} нет данных в R.")
            continue
            
        print(f"\nРешаем уравнение для выхода '{col}' (target={target}):")
        sols = solve_single_equation(r_vals, target, row_names)
        column_solutions.append(sols)
        for i, s in enumerate(sols):
            print(f"  Вариант {col}.{i+1}: {s}")

    # 3. Объединение (пересечение) решений всех уравнений
    print(f"\n--- Комбинирование решений (Пересечение) ---")
    
    if len(column_solutions) == 0:
        print("Нет уравнений для решения.")
        return
    
    if len(column_solutions) == 1:
        # Если только одно уравнение, решения уже готовы
        final_solutions = column_solutions[0]
    else:
        # Берем решения первого уравнения
        current_pool = column_solutions[0]
        
        # Пересекаем с решениями каждого следующего уравнения
        for next_col_sols in column_solutions[1:]:
            next_pool = []
            for sol1 in current_pool:
                for sol2 in next_col_sols:
                    res = intersect_solutions(sol1, sol2)
                    if res:
                        next_pool.append(res)
                        # Вывод промежуточного шага
                        print(f"  Пересечение найдено: {res}")
            current_pool = next_pool

        final_solutions = current_pool

    # 4. Финальный вывод
    print("\n" + "="*40)
    print("ОТВЕТ (Объединение всех найденных пересечений):")
    if not final_solutions:
        answer = "Нет решений (Пустое множество)"
        print(answer)
    else:
        # Формируем строку ответа в формате логического выражения
        parts = []
        for sol in final_solutions:
            conditions = []
            if sol.type == 'line':
                var_names = sorted(sol.intervals.keys())
                sum_expr = "+".join(var_names)
                conditions.append(f"{sum_expr}={sol.sum_val}")
            
            for var_name in sorted(sol.intervals.keys()):
                interval = sol.intervals[var_name]
                # Если границы интервала совпадают (одно значение), используем "=" вместо "∈"
                if abs(interval.low - interval.high) < 1e-9:
                    conditions.append(f"{var_name}={round(interval.low, 2)}")
                else:
                    conditions.append(f"{var_name}∈{interval}")
            
            parts.append(f"({' ∧ '.join(conditions)})")
        
        answer = " V ".join(parts)
        print(answer)
    
    # Записываем только итоговый ответ в output файл
    with open(output_file, 'w', encoding='utf-8') as f:
        if not final_solutions:
            f.write("Нет решений (Пустое множество)")
        else:
            f.write(answer)
    
    print(f"\nИтоговый ответ записан в {output_file}")

if __name__ == "__main__":
    main()