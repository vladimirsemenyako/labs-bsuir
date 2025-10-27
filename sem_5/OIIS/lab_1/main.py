# import numpy as np
# import matplotlib.pyplot as plt
#
#
# def perform_fft_analysis(
#         signal_frequency: float = 5.0,
#         sampling_rate: int = 100,
#         duration: int = 2
# ):
#     num_samples = int(sampling_rate * duration)
#     time_vector = np.linspace(0, duration, num_samples, endpoint=False)
#
#     signal = np.sin(2 * np.pi * signal_frequency * time_vector)
#
#     fft_result = np.fft.fft(signal)
#
#     fft_amplitude = np.abs(fft_result) / num_samples
#
#     fft_frequencies = np.fft.fftfreq(num_samples, 1 / sampling_rate)
#
#     plt.figure(figsize=(12, 6))
#
#     plt.subplot(2, 1, 1)
#     plt.plot(time_vector, signal)
#     plt.title("Исходный сигнал: sin(x)")
#     plt.xlabel("Время (с)")
#     plt.ylabel("Амплитуда")
#     plt.grid(True)
#
#     plt.subplot(2, 1, 2)
#     positive_freq_indices = np.where(fft_frequencies >= 0)
#     plt.stem(fft_frequencies[positive_freq_indices], fft_amplitude[positive_freq_indices])
#     plt.title("Амплитудный спектр сигнала (БПФ)")
#     plt.xlabel("Частота (Гц)")
#     plt.ylabel("Амплитуда")
#     plt.grid(True)
#
#     plt.tight_layout()
#     plt.show()
#
# if __name__ == "__main__":
#     input_frequency = 5
#     perform_fft_analysis(signal_frequency=input_frequency)

import cmath
import math
import matplotlib.pyplot as plt


def fft(x: list[float]) -> list[complex]:
    N = len(x)
    if N <= 1:
        return [complex(val) for val in x]

    even = fft(x[0::2])
    odd = fft(x[1::2])

    result = [complex(0)] * N
    for k in range(N // 2):
        angle = -2j * cmath.pi * k / N
        t = cmath.exp(angle) * odd[k]

        result[k] = even[k] + t
        result[k + N // 2] = even[k] - t

    return result


def perform_fft_analysis(
        signal_frequency: float = 5.0,
        sampling_rate: int = 128,
        duration: int = 2
):
    num_samples = int(sampling_rate * duration)
    time_vector = [i / sampling_rate for i in range(num_samples)]

    signal = [
        math.sin(2 * math.pi * signal_frequency * t) for t in time_vector
    ]

    fft_result = fft(signal)

    fft_amplitude = [abs(c) / num_samples for c in fft_result]

    frequencies = [
        i * sampling_rate / num_samples for i in range(num_samples)
    ]

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(time_vector, signal)
    plt.title("Исходный сигнал: sin(x)")
    plt.xlabel("Время (с)")
    plt.ylabel("Амплитуда")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    half_N = num_samples // 2
    plt.stem(frequencies[:half_N], fft_amplitude[:half_N])
    plt.title("Амплитудный спектр сигнала (самописный БПФ)")
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    perform_fft_analysis(signal_frequency=5.0)