import random
import string
import time
import matplotlib.pyplot as plt

def generate_passwords(num_passwords: int, length: int) -> list[str]:
    alphabet = string.ascii_letters
    random.seed(time.time())
    return [
        ''.join(random.choice(alphabet) for _ in range(length))
        for _ in range(num_passwords)
    ]

def plot_frequency_distribution(passwords: list[str]):
    alphabet = string.ascii_letters
    freq = {ch: 0 for ch in alphabet}

    for pwd in passwords:
        for ch in pwd:
            freq[ch] += 1

    plt.figure(figsize=(12, 6))
    plt.bar(freq.keys(), freq.values())
    plt.title("Частотное распределение символов (по множеству паролей)")
    plt.xlabel("Символ")
    plt.ylabel("Частота")
    plt.show()

def average_bruteforce_time(length: int, rate: float = 1e9) -> float:
    N = len(string.ascii_letters)
    total = N ** length
    avg_time = total / (2 * rate)
    return avg_time

def plot_bruteforce_times(max_length: int, rate: float = 1e9):
    lengths = list(range(1, max_length + 1))
    times = [average_bruteforce_time(L, rate) for L in lengths]

    plt.figure(figsize=(10, 5))
    plt.plot(lengths, times, marker='o')
    plt.yscale("log")
    plt.title("Среднее время подбора пароля от его длины")
    plt.xlabel("Длина пароля")
    plt.ylabel("Среднее время (сек)")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.show()

if __name__ == "__main__":
    num_passwords = 10000
    length = 8

    passwords = generate_passwords(num_passwords, length)
    print(f"Сгенерировано {num_passwords} паролей длиной {length} символов")

    plot_frequency_distribution(passwords)

    plot_bruteforce_times(12, rate=1e9)
