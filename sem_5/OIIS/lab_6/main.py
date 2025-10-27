from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt

SPORTS_BALL_CLASS = 32

print("Загружаем модель YOLOv8...")
model = YOLO('yolov8n.pt')

image_addr = 'guy_with_ball.png'
image = cv2.imread(image_addr)
if image is None:
    raise FileNotFoundError(f"Не найдено изображение {image_addr}")

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

print("Выполняем детекцию объектов...")
results = model(image_rgb)

boxes = results[0].boxes.xyxy.cpu().numpy()
class_ids = results[0].boxes.cls.cpu().numpy().astype(int)


def replace_ball_with_cube(img, boxes, class_ids, cube_path='basketball.png'):
    cube_bgra = cv2.imread(cube_path, cv2.IMREAD_UNCHANGED)
    if cube_bgra is None:
        raise FileNotFoundError(f"Не найден файл: {cube_path}")
    if cube_bgra.shape[2] == 4:
        cube_rgba = cv2.cvtColor(cube_bgra, cv2.COLOR_BGRA2RGBA)
    else:
        cube_rgba = cv2.cvtColor(cube_bgra, cv2.COLOR_BGR2RGB)

    output = img.copy()
    for box, cls in zip(boxes, class_ids):
        if cls == SPORTS_BALL_CLASS:
            x1, y1, x2, y2 = map(int, box)
            w, h = max(1, x2 - x1), max(1, y2 - y1)

            resized = cv2.resize(cube_rgba, (w, h), interpolation=cv2.INTER_AREA)

            if resized.shape[2] == 4:
                alpha = resized[:, :, 3:] / 255.0
                output[y1:y2, x1:x2] = (
                        alpha * resized[:, :, :3] + (1 - alpha) * output[y1:y2, x1:x2]
                ).astype(np.uint8)
            else:
                output[y1:y2, x1:x2] = resized

    return output

print("Замена объекта...")
result_img = replace_ball_with_cube(image_rgb, boxes, class_ids, 'basketball.png')

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.imshow(image_rgb)
plt.title("Исходное")
plt.axis("off")
plt.subplot(1, 2, 2)
plt.imshow(result_img)
plt.title("После замены")
plt.axis("off")
plt.tight_layout()
plt.show()