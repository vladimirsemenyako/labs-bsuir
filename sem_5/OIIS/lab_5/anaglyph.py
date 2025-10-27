import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def create_anaglyph(left_img, right_img):

    if len(left_img.shape) == 3:
        left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
    else:
        left_gray = left_img

    if len(right_img.shape) == 3:
        right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)
    else:
        right_gray = right_img

    h = min(left_gray.shape[0], right_gray.shape[0])
    w = min(left_gray.shape[1], right_gray.shape[1])
    left_gray = cv2.resize(left_gray, (w, h))
    right_gray = cv2.resize(right_gray, (w, h))

    anaglyph = np.zeros((h, w, 3), dtype=np.uint8)
    anaglyph[:, :, 0] = right_gray
    anaglyph[:, :, 1] = right_gray
    anaglyph[:, :, 2] = left_gray

    return anaglyph


def show_images(left, right, anaglyph):
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(left, cv2.COLOR_BGR2RGB) if len(left.shape) == 3 else left, cmap='gray')
    plt.title('Левое изображение')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(cv2.cvtColor(right, cv2.COLOR_BGR2RGB) if len(right.shape) == 3 else right, cmap='gray')
    plt.title('Правое изображение')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(anaglyph, cv2.COLOR_BGR2RGB))
    plt.title('Анаглиф (стерео)')
    plt.axis('off')

    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) == 3:
        left_path = sys.argv[1]
        right_path = sys.argv[2]
    else:
        left_path = 'left.jpg'
        right_path = 'right.jpg'

    if not os.path.exists(left_path):
        print(f"Ошибка: файл '{left_path}' не найден.")
        return
    if not os.path.exists(right_path):
        print(f"Ошибка: файл '{right_path}' не найден.")
        return

    left_img = cv2.imread(left_path)
    right_img = cv2.imread(right_path)

    if left_img is None:
        print("Не удалось загрузить левое изображение.")
        return
    if right_img is None:
        print("Не удалось загрузить правое изображение.")
        return

    anaglyph = create_anaglyph(left_img, right_img)

    show_images(left_img, right_img, anaglyph)

    cv2.imwrite('stereo_anaglyph.jpg', anaglyph)
    print("Стереоскопическое изображение сохранено как 'stereo_anaglyph.jpg'.")


if __name__ == '__main__':
    main()