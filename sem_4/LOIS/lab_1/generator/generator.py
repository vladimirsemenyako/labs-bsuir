import json
import random

def generate_dnf_formula(variables, max_terms=3, max_literals=3):
    terms = []
    used_vars = variables.copy()
    for _ in range(random.randint(1, max_terms)):
        literals = []
        random.shuffle(used_vars)
        for _ in range(random.randint(1, max_literals)):
            if not used_vars:
                used_vars = variables.copy()
                random.shuffle(used_vars)
            var = used_vars.pop()
            if random.choice([True, False]):
                literals.append(var)
            else:
                literals.append(f"(!{var})")
        if len(literals) == 1:
            terms.append(literals[0])
        else:
            terms.append(f"({'/\\'.join(literals)})")
    return '\\/'.join(terms)

def is_atomic(formula):
    if len(formula) == 1 and 'A' <= formula <= 'Z':
        return True

    if (len(formula) == 4 and
        formula[0] == '(' and
        formula[1] == '!' and
        'A' <= formula[2] <= 'Z' and
        formula[3] == ')' ):
        return True
    return False

def generate_test_set(out_file, gen_dnf=True):
    VARIABLES = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    formulas = set()
    attempts = 0
    max_attempts = 10000
    while len(formulas) < (50 if not gen_dnf else 5) and attempts < max_attempts:
        if gen_dnf:
            formula = generate_dnf_formula(VARIABLES)
        else:
            formula = generate_dnf_formula(VARIABLES)
            if is_atomic(formula):
                continue 
            if random.choice([True, False]):
                formula = formula.replace('/\\', '\\/')
            else:
                formula = formula.replace('\\/', '/\\')
        formulas.add(formula)
        attempts += 1
    with open(out_file, "w") as file:
        file.write(json.dumps(list(formulas), indent=4))
