import cv2
import numpy as np
from PIL import Image
import os
import sys


def create_wiggle_gif(left_path, right_path, output_path='stereo_wiggle.gif', duration=300, n_cycles=5):
    """
    Создаёт wiggle-анимацию (GIF) из стереопары.

    Параметры:
        left_path   : путь к левому изображению
        right_path  : путь к правому изображению
        output_path : имя выходного GIF-файла
        duration    : задержка между кадрами в миллисекундах (рекомендуется 200–500 мс)
        n_cycles    : сколько раз повторить цикл [лево → право → лево]
    """
    # Загрузка изображений
    left_img = cv2.imread(left_path)
    right_img = cv2.imread(right_path)

    if left_img is None:
        raise FileNotFoundError(f"Не найдено левое изображение: {left_path}")
    if right_img is None:
        raise FileNotFoundError(f"Не найдено правое изображение: {right_path}")

    # Преобразование в RGB и приведение к одинаковому размеру
    h = min(left_img.shape[0], right_img.shape[0])
    w = min(left_img.shape[1], right_img.shape[1])

    left_resized = cv2.resize(left_img, (w, h))
    right_resized = cv2.resize(right_img, (w, h))

    # Конвертация из BGR (OpenCV) в RGB (PIL)
    left_rgb = cv2.cvtColor(left_resized, cv2.COLOR_BGR2RGB)
    right_rgb = cv2.cvtColor(right_resized, cv2.COLOR_BGR2RGB)

    # Создание кадров: [лево, право, лево, право, ...]
    frames = []
    for _ in range(n_cycles):
        frames.append(Image.fromarray(left_rgb))
        frames.append(Image.fromarray(right_rgb))

    # Сохранение как GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0  # бесконечный цикл
    )
    print(f"Wiggle-анимация сохранена: {os.path.abspath(output_path)}")


def main():
    if len(sys.argv) == 3:
        left_path = sys.argv[1]
        right_path = sys.argv[2]
    else:
        left_path = 'left.jpg'
        right_path = 'right.jpg'

    try:
        create_wiggle_gif(left_path, right_path)
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()