import itertools


def vigenere_cipher(text: str, key: str, decrypt: bool = False) -> str:
    key = key.lower()
    if not key.isalpha():
        raise ValueError("Ключ должен состоять только из букв!")

    result_chars = []
    key_index = 0
    for char in text:
        if 'a' <= char.lower() <= 'z':
            shift = ord(key[key_index % len(key)]) - ord('a')
            if decrypt:
                shift = -shift

            start_char_code = ord('A') if char.isupper() else ord('a')
            processed_char_code = (ord(char) - start_char_code + shift) % 26
            result_chars.append(chr(start_char_code + processed_char_code))
            key_index += 1
        else:
            result_chars.append(char)
    return "".join(result_chars)


def brute_force_attack(ciphertext: str, max_key_length: int) -> dict:
    common_words = ["the", "and", "for", "are", "but", "not", "you", "all", "was", "her"]
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    for length in range(1, max_key_length + 1):
        for key_tuple in itertools.product(alphabet, repeat=length):
            key = "".join(key_tuple)
            decrypted_text = vigenere_cipher(ciphertext, key, decrypt=True)
            if any(f" {word} " in decrypted_text.lower() for word in common_words):
                return {"key": key, "decrypted_text": decrypted_text}
    return {"key": None, "decrypted_text": "Не удалось найти ключ"}


if __name__ == '__main__':
    original_message = "The Vigenere cipher is a polyalphabetic substitution cipher."
    encryption_key = "secret"

    encrypted_message = vigenere_cipher(original_message, encryption_key)
    print(f"Оригинальный текст:  {original_message}")
    print(f"Ключ:            {encryption_key}")
    print(f"Зашифрованный тектс: {encrypted_message}")

    decrypted_message = vigenere_cipher(encrypted_message, encryption_key, decrypt=True)
    print(f"Расшифрованный текст: {decrypted_message}\n")

    attack_key = "key"
    message_for_attack = "This is a secret message that we will try to break."
    ciphertext_for_attack = vigenere_cipher(message_for_attack, attack_key)

    print("--- Brute-Force Атака ---")
    print(f"Текст подверженный атаке: {ciphertext_for_attack}")

    attack_result = brute_force_attack(ciphertext_for_attack, max_key_length=3)

    if attack_result["key"]:
        print(f"Успех! Найден ключ: '{attack_result['key']}'")
        print(f"Расшифрованное сообщение:  '{attack_result['decrypted_text']}'")
    else:
        print("В ходе Brute-force атаки не удалось найти ключ.")