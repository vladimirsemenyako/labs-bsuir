"////////////////////////////////////////////////////////"
"// Лабораторная работа 1 по дисциплине ЛОИС //"
"// Выполнена студентами группы 321701 БГУИР Астахов А.С, Духвалов П.Н., Семеняко В.Д.//"
"// Реализация прямого нечеткого логического вывода с использованием треугольной нормы и нечеткой импликации Хомахера//"
"// 17.10.2025 //"
"// Использованные источники: Голенков, В. В. Логические основы интеллектуальных систем. Практикум: учеб.-метод. пособие / В. В. Голенков. — БГУИР, 2011//"


import sys
class Fact:
    precision = 2

    def __init__(self, value_percision, name="", fuzzy_set=None, definition_set=None):
        self.name = name
        self.fuzzy_set = fuzzy_set if fuzzy_set is not None else []
        self.definition_set = definition_set if definition_set is not None else set()
        if(Fact.precision <= value_percision):
            Fact.precision = value_percision

    def get_element_value(self,element_name):
        for elem in self.fuzzy_set:
            elem_name = elem[0]
            elem_value = elem[1]
            if elem_name == element_name:
                return elem_value

class Rule:
    def __init__(self, fact1, fact2):
        self.fact1 = fact1
        self.fact2 = fact2

def is_valid_name(name):
    if not name:
        return False
    first_char = name[0]
    if not (('A' <= first_char <= 'Z') or ('a' <= first_char <= 'z')):
        return False
    
    for char in name[1:]:
        if not (('0' <= char <= '9') or (('A' <= char <= 'Z') or ('a' <= char <= 'z'))):
            return False
    
    return True

def is_valid_value(value_str):
    try:
        value = float(value_str)
        return 0.0 <= value <= 1.0
    except ValueError:
        return False

def check_fact_exists(fact, facts):
    if len(facts)==0:
        return False
    
    for f in facts:
        if fact.name == f.name:
            return True
    
    return False

def check_rule_exists(rule, rules):
    if len(rules)==0:
        return False
    
    for r in rules:
        if rule.fact1.name == r.fact1.name:
            if rule.fact2.name == r.fact2.name:
                return True
    
    return False

def read_facts_and_rules(filename):
    facts = []
    rules = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
        sys.exit(1)
    
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    # Ищем индекс первого правила (строка с "~>")
    rule_start_index = None
    for i, line in enumerate(lines):
        if '~>' in line:
            rule_start_index = i
            break

    if rule_start_index is None:
        print("Ошибка: Правила не найдены (отсутствует '~>')")
        sys.exit(1)

    # Разделяем на факты и правила
    fact_lines = lines[:rule_start_index]
    rule_lines = lines[rule_start_index:]
    
    if fact_lines==[]:
        print("Ошибка: Факты не найдены ")
        sys.exit(1)
        
    if rule_lines==[]:
        print("Ошибка: Правила не найдены (отсутствует '~>')")
        sys.exit(1)
        
    for line in fact_lines:
        fact = parse_fact(line)
        if fact:
            if not check_fact_exists(fact, facts):
                facts.append(fact)
            else:
                print(f"Ошибка: Факт с именем '{fact.name}' записан несколько раз")
                sys.exit(1)
    
    for line in rule_lines:
        rule = parse_rule(line, facts)
        if rule:
            if not check_rule_exists(rule, rules):
                rules.append(rule)
            else:
                print(f"Ошибка: Правило '{rule.fact1.name}~>{rule.fact2.name}' записано несколько раз")
                sys.exit(1)
    
    return facts, rules

def parse_elem(line, fact_name):
    if line[0] != '<':
        print(f"Ошибка: Нет открывающей угловой скобки в элементе факта '{fact_name}': '{line}'")
        sys.exit(1)
    
    if line[-1] != '>':
        print(f"Ошибка: Нет закрывающей угловой скобки в элементе факта '{fact_name}': '{line}'")
        sys.exit(1)
    
    element = line[1:-1]
    
    # Проверка на пустой кортеж
    if not element:
        print(f"Ошибка: Пустой кортеж в факте '{fact_name}'")
        sys.exit(1)
            
    # Разделяем на части по точке с запятой
    comma_pos = element.find(';')
    if comma_pos == -1:
        print(f"Ошибка: Кортеж должен содержать точку с запятой в факте '{fact_name}': '{line}'")
        sys.exit(1)
            
    elem_name = element[:comma_pos]
    value_str = element[comma_pos+1:]

    # Проверка имени элемента
    if not is_valid_name(elem_name):
        print(f"Ошибка: Некорректное имя элемента '{elem_name}' в факте '{fact_name}'. Допустимы только буквы латинского алфавита и цифры, начинаться должно с буквы")
        sys.exit(1)
    
    # Проверка значения принадлежности
    if not is_valid_value(value_str):
        print(f"Ошибка: Некорректное значение меры принадлежности '{value_str}' в факте '{fact_name}'. Должно быть действительным числом от 0 до 1")
        sys.exit(1)
    
    value_precision = len(value_str.split('.')[1])
    
    value = float(value_str)

    return elem_name, value, value_precision

def parse_fact(line):
    if '=' not in line:
        print(f"Ошибка: Отсутствует знак '=' в факте: '{line}'")
        sys.exit(1)
    
    if '{' not in line or '}' not in line:
        print(f"Ошибка: Отсутствуют фигурные скобки в факте: '{line}'")
        sys.exit(1)
    
    fact_name = line.split('=')[0].strip()
    
    # Проверка имени факта
    if not is_valid_name(fact_name):
        print(f"Ошибка: Некорректное имя факта '{fact_name}'. Допустимы только буквы латинского алфавита и цифры, начинаться должно с буквы")
        sys.exit(1)
    
    start = line.find('{') + 1
    end = line.find('}')
    
    if start >= end:
        print(f"Ошибка: Пустой или некорректный набор элементов в факте: '{line}'")
        sys.exit(1)
    
    # Выделяем нечеткое множество и разделяем его на элементы
    fuzzy_set_content = line[start:end].strip()
    lines_of_elements = [item.replace(" ", "") for item in fuzzy_set_content.split(',')]

    fuzzy_set = []
    definition_set = set()
    value_percision = 2

    for element_line in lines_of_elements:
        element, value, percision = parse_elem(element_line, fact_name)

        if(value_percision < percision):
            value_percision = percision
        fuzzy_set.append((element, value))
        definition_set.add(element)

    if not fuzzy_set:
        print(f"Ошибка: Факт '{fact_name}' не содержит корректных элементов")
        sys.exit(1)
    
    return Fact(value_percision, fact_name, fuzzy_set, definition_set)

def parse_rule(line, facts_list):
    if '~>' not in line:
        print(f"Ошибка: Правило записано некорректно, нечеткая импликация '~>' не найдена: '{line}'")
        sys.exit(1)
    
    parts = line.split('~>')
    if len(parts) != 2:
        print(f"Ошибка: Правило записано с несколькими нечеткими импликациями '~>': '{line}'")
        sys.exit(1)
    
    fact_name1 = parts[0].strip()
    fact_name2 = parts[1].strip()
    
    if not is_valid_name(fact_name1):
        print(f"Ошибка: Некорректное имя факта '{fact_name1}' в правиле. Допустимы только буквы латинского алфавита и цифры, начинаться должно с буквы")
        sys.exit(1)
    
    if not is_valid_name(fact_name2):
        print(f"Ошибка: Некорректное имя факта '{fact_name2}' в правиле. Допустимы только буквы латинского алфавита и цифры, начинаться должно с буквы")
        sys.exit(1)
    
    # Проверка существования фактов, упомянутых в правиле
    fact1_exists = False
    fact2_exists = False
    for fact in facts_list:
        if fact.name == fact_name1:
            fact1_exists = True
            fact1 = fact
        if fact.name == fact_name2:
            fact2_exists = True
            fact2 = fact
    
    if not fact1_exists:
        print(f"Ошибка: Факт '{fact_name1}', упомянутый в правиле, не определен: '{line}'")
        sys.exit(1)
    
    if not fact2_exists:
        print(f"Ошибка: Факт '{fact_name2}', упомянутый в правиле, не определен: '{line}'")
        sys.exit(1)
    
    return Rule(fact1, fact2)

def can_apply_fact_to_rule(fact, rule):
    if fact.definition_set == rule.fact1.definition_set:
        return True
    
    return False


class Implication:
    def __init__(self, rule_name, matrix, row_labels, col_labels):
        self.rule_name = rule_name
        self.matrix = matrix  
        self.row_labels = row_labels  
        self.col_labels = col_labels

    def get_implication_value(self, elem_row_name, elem_col_name):
         for i, elem_c in enumerate(self.col_labels):
             elem_c_name, elem_c_value = elem_c
             if elem_c_name == elem_col_name:
                 for j, elem_r in enumerate(self.row_labels):
                     elem_r_name, elem_r_value = elem_r
                     if elem_r_name == elem_row_name:
                         return self.matrix[j][i]                        

def calculate_implication(rule):
    #Вычисляет матрицу импликации для правила
    col_labels = [elem for elem in rule.fact1.fuzzy_set]
    row_labels = [elem for elem in rule.fact2.fuzzy_set]
    matrix = []
  
    for row_elem in rule.fact2.fuzzy_set:
        row_name, b_value = row_elem
        row = []
      
        for col_elem in rule.fact1.fuzzy_set:
            col_name, a_value = col_elem
        
            if a_value <= b_value:
                value = 1.0
            else:
                value = round((a_value*b_value) / (a_value - b_value + a_value*b_value),Fact.precision)
            
            if value>1.0:
                value=1.0
                
            row.append(value)
                 
        matrix.append(row)
    
    rule_name = f"{rule.fact1.name}~>{rule.fact2.name}"
    
    return Implication(rule_name, matrix, row_labels, col_labels)

def calculate_all_implications(rules):
   
    implications = []
    
    for rule in rules:
        implication = calculate_implication(rule)
        implications.append(implication)
    
    return implications

def print_implication(implication):
    print(f"\nИмпликация: {implication.rule_name}")

    # Вычисляем ширину для каждой колонки
    col_widths = []
    
    # Ширина для левой колонки с названиями строк
    left_col_width = max(len(f"<{name},{value}>:") for name, value in implication.row_labels)
    
    # Ширина для заголовков колонок
    for col_label in implication.col_labels:
        name, value = col_label
        header = f"<{name},{value}>"
        col_widths.append(max(len(header), 10))  # Минимум 10 символов для чисел
    
    # Вывод заголовков
    print(" " * left_col_width, end="")
    for i, col_label in enumerate(implication.col_labels):
        name, value = col_label
        header = f"<{name},{value}>"
        print(f"{header:^{col_widths[i]}}", end=" ")
    print()
    
    # Вывод данных
    for i, row_label in enumerate(implication.row_labels):
        name, value = row_label
        row_header = f"<{name},{value}>:"
        print(f"{row_header:<{left_col_width}}", end="")
        
        for j, num in enumerate(implication.matrix[i]):
            print(f"{num:^{col_widths[j]}.{Fact.precision}f}", end=" ")
        print()

'''
def print_implication(implication):
    print(f"\nИмпликация: {implication.rule_name}")

    print("     ", end="")
    for col_label in implication.col_labels:
        elem_name, value = col_label
        print(f"<{elem_name},{value}>".ljust(12), end="")
    print()
    
    for i, row_label in enumerate(implication.row_labels):
        elem_name, value = row_label
        print(f"<{elem_name},{value}>: ", end="")
        for value in implication.matrix[i]:
            print(f"{value:8.2f}", end="")
        print()
'''

def apply_t_norm(fact, implication):
    result = []
    
    for row_elem in implication.row_labels:
        row_values = []
        row_elem_name = row_elem[0]
        for col_elem in implication.col_labels:
            col_elem_name = col_elem[0]
            implication_value = implication.get_implication_value(row_elem_name,col_elem_name)
            fact_elem_value = fact.get_element_value(col_elem_name)
            t_norm_value = round((fact_elem_value * implication_value)/(fact_elem_value + implication_value - fact_elem_value*implication_value),Fact.precision)
            if t_norm_value < 0:
                t_norm_value = 0
            if t_norm_value > 1:
                t_norm_value = 1
            row_values.append(t_norm_value)
        max_value = max(row_values) if row_values else 0.0
        result.append((row_elem_name,max_value))
    
    return result

def fuzzy_set_equal_exact(res, facts_list):
    res_set = set((elem, float(val)) for elem, val in res)
    
    for  fact in facts_list:
        fact_set = set((elem, float(val)) for elem, val in fact.fuzzy_set)
        if res_set == fact_set:
            return True, fact.name
            
    return False, 0

def format_res(fuzzy_set):
    elements = []
    for elem_name, value in fuzzy_set:
        elements.append(f"<{elem_name}; {value}>")
    
    return "{" + ", ".join(elements) + "}"

if __name__ == "__main__":
    try:
        facts, rules = read_facts_and_rules(input("Введите имя файла: "))
        
        # Вычисляем все импликации
        implications = calculate_all_implications(rules)
      
        for implication in implications:
            print_implication(implication)
        
        print()

        new_facts_calc = 0
        
        for fact in facts:
            for j, rule in enumerate(rules):
                if can_apply_fact_to_rule(fact, rule):
                    res = apply_t_norm(fact, implications[j])
                    flag, index = fuzzy_set_equal_exact(res, facts)
                    new_facts_calc += 1
                    if flag:
                        print("{",fact.name,",",implications[j].rule_name,"}"," |~ ","I",new_facts_calc, "=",format_res(res), "=", index)
                    else:
                        facts.append(Fact(2,"I"+str(new_facts_calc), res, rule.fact2.definition_set))
                        print("{",fact.name,",",implications[j].rule_name,"}"," |~ ","I",new_facts_calc, "=",format_res(res))
                        
    except SystemExit:
        pass
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)