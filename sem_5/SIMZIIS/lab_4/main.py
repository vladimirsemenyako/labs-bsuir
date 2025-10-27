import random

def mod_exp(base, exp, mod):
    result = 1
    base = base % mod

    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod

    return result

def is_primitive_root(g, p):
    if g <= 1 or g >= p:
        return False

    generated_set = set()
    for i in range(1, p):
        val = mod_exp(g, i, p)
        if val in generated_set:
            return False
        generated_set.add(val)

    return len(generated_set) == p - 1

if __name__ == "__main__":
    P = 2957
    print(f"Заданное простое число P: {P}")

    print("Поиск первообразного корня g...")
    g = None
    for candidate in range(2, P):
        if is_primitive_root(candidate, P):
            g = candidate
            break

    if g is None:
        print("Первообразный корень не найден. (Это маловероятно для простого P)")
    else:
        print(f"Найден первообразный корень g: {g}")

    alice_secret_num = random.randint(2, P - 2)
    bob_secret_num = random.randint(2, P - 2)

    print(f"\n--- Начало протокола Диффи-Хеллмана ---")
    print(f"Алиса выбирает секретное число a: {alice_secret_num}")
    print(f"Боб выбирает секретное число b: {bob_secret_num}")

    A = mod_exp(g, alice_secret_num, P)
    print(f"Алиса вычисляет A = g^a mod P = {g}^{alice_secret_num} mod {P} = {A} и отправляет его Бобу.")

    B = mod_exp(g, bob_secret_num, P)
    print(f"Боб вычисляет B = g^b mod P = {g}^{bob_secret_num} mod {P} = {B} и отправляет его Алисе.")

    K_alice = mod_exp(B, alice_secret_num, P)
    print(f"Алиса вычисляет общий секрет K = B^a mod P = {B}^{alice_secret_num} mod {P} = {K_alice}")

    K_bob = mod_exp(A, bob_secret_num, P)
    print(f"Боб вычисляет общий секрет K = A^b mod P = {A}^{bob_secret_num} mod {P} = {K_bob}")

    if K_alice == K_bob:
        print(f"\nУСПЕХ! Алиса и Боб получили одинаковый общий секретный ключ: K = {K_alice}")
    else:
        print("\nОШИБКА! Ключи не совпадают.")