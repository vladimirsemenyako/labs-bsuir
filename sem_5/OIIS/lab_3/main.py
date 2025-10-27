import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image_and_histogram(image, title):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(image, cmap='gray')
    plt.title(f'{title} Изображение')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.hist(image.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    plt.title(f'{title} Гистограмма')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')

    plt.tight_layout()
    plt.show()

def histogram_equalization(image):
    return cv2.equalizeHist(image)

image1_path = 'image1.jpg'
image2_path = 'image2.jpg'

img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

if img1 is None:
    raise FileNotFoundError(f"Не удалось загрузить изображение: {image1_path}")
if img2 is None:
    raise FileNotFoundError(f"Не удалось загрузить изображение: {image2_path}")

equalized_img1 = histogram_equalization(img1)
equalized_img2 = histogram_equalization(img2)

show_image_and_histogram(img1, "Исходное 1")
show_image_and_histogram(equalized_img1, "Выровненное 1")

show_image_and_histogram(img2, "Исходное 2")
show_image_and_histogram(equalized_img2, "Выровненное 2")