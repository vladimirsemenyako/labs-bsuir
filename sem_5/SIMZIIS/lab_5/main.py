import random
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes


def mod_exp(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y


def mod_inverse(a, m):
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Обратный элемент не существует")
    else:
        return x % m


def generate_prime(bits):
    return getPrime(bits)


def generate_keys(bits=1024):

    print(f"Генерация простых чисел длиной {bits} бит...")
    p = generate_prime(bits)
    q = generate_prime(bits)
    print("Простые числа p и q успешно сгенерированы.")

    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    if extended_gcd(e, phi_n)[0] != 1:
        e = 65539
        if extended_gcd(e, phi_n)[0] != 1:
            raise ValueError("Не удалось найти подходящую экспоненту e.")

    d = mod_inverse(e, phi_n)
    with open('public_key.txt', 'w') as f:
        f.write(f"{e}\n{n}")
    print("Открытый ключ (e, n) сохранен в 'public_key.txt'.")
    with open('private_key.txt', 'w') as f:
        f.write(f"{d}\n{n}")
    print("Секретный ключ (d, n) сохранен в 'private_key.txt'.")

    return (e, n), (d, n)


def encrypt(message, e, n):
    message_bytes = message.encode('utf-8')
    message_int = bytes_to_long(message_bytes)

    if message_int >= n:
        raise ValueError(
            "Сообщение слишком длинное для данного ключа. Увеличьте длину ключа или разбейте сообщение на части.")
    ciphertext = mod_exp(message_int, e, n)
    return ciphertext


def decrypt(ciphertext, d, n):
    message_int = mod_exp(ciphertext, d, n)
    try:
        message_bytes = long_to_bytes(message_int)
        message = message_bytes.decode('utf-8')
    except:
        raise ValueError("Ошибка при расшифровке. Возможно, используется неверный ключ.")

    return message


def sign(message, d, n):
    message_bytes = message.encode('utf-8')
    message_int = bytes_to_long(message_bytes)
    signature = mod_exp(message_int, d, n)
    return signature


def verify(message, signature, e, n):
    message_bytes = message.encode('utf-8')
    message_int = bytes_to_long(message_bytes)
    recovered_message_int = mod_exp(signature, e, n)

    return message_int == recovered_message_int


def load_public_key(filename='public_key.txt'):
    with open(filename, 'r') as f:
        e = int(f.readline().strip())
        n = int(f.readline().strip())
    return e, n


def load_private_key(filename='private_key.txt'):
    with open(filename, 'r') as f:
        d = int(f.readline().strip())
        n = int(f.readline().strip())
    return d, n


if __name__ == "__main__":
    print("--- Шаг 1: Генерация ключей ---")
    public_key, private_key = generate_keys(bits=1024)
    e, n = public_key
    d, _ = private_key
    print(f"Открытый ключ (e, n): ({e}, ...{str(n)[-10:]}...)")
    print(f"Секретный ключ (d, n): (...{str(d)[-10:]}..., ...{str(n)[-10:]}...)\n")
    print("--- Шаг 2: Шифрование и расшифрование ---")
    original_message = "Секретное сообщение для Боба: Встреча в 18:00."
    with open('message.txt', 'w', encoding='utf-8') as f:
        f.write(original_message)
    print(f"Исходное сообщение записано в 'message.txt': \"{original_message}\"")
    encrypted_msg = encrypt(original_message, e, n)
    with open('encrypted_message.txt', 'w') as f:
        f.write(str(encrypted_msg))
    print(f"Зашифрованное сообщение (целое число): {encrypted_msg}")
    print("Зашифрованное сообщение сохранено в 'encrypted_message.txt'.\n")
    decrypted_msg = decrypt(encrypted_msg, d, n)
    print(f"Расшифрованное сообщение: \"{decrypted_msg}\"")
    print(f"Успешно? {original_message == decrypted_msg}\n")
    print("--- Шаг 3: Создание и проверка цифровой подписи ---")
    signature = sign(original_message, d, n)
    print(f"Цифровая подпись (s): {signature}")
    is_valid = verify(original_message, signature, e, n)
    print(f"Подпись верна: {is_valid}")
    fake_message = "Поддельное сообщение: Встреча в 12:00."
    is_fake_valid = verify(fake_message, signature, e, n)
    print(f"Подпись для поддельного сообщения верна: {is_fake_valid}\n")
    print("--- Шаг 4: Тестирование на 10 наборах данных ---")
    test_messages = [
        "Тест 1", "Hello, World!", "12345", "Привет, Мир!",
        "The quick brown fox jumps over the lazy dog.",
        "Это сообщение номер шесть.", "7", "VIII", "九", "10/10"
    ]

    all_tests_passed = True
    for i, msg in enumerate(test_messages, 1):
        try:
            enc = encrypt(msg, e, n)
            dec = decrypt(enc, d, n)
            if dec != msg:
                print(f"ТЕСТ {i} НЕ ПРОЙДЕН (Шифрование/Расшифрование)")
                all_tests_passed = False
            sig = sign(msg, d, n)
            if not verify(msg, sig, e, n):
                print(f"ТЕСТ {i} НЕ ПРОЙДЕН (Подпись/Проверка)")
                all_tests_passed = False

        except Exception as ex:
            print(f"ТЕСТ {i} НЕ ПРОЙДЕН (Ошибка: {ex})")
            all_tests_passed = False

    if all_tests_passed:
        print("ВСЕ 10 ТЕСТОВ УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Проверьте код.")

    print("\n=== РАБОТА ЗАВЕРШЕНА ===")