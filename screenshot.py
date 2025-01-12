# screenshot.py
from OpenGL.GL import *
from PIL import Image
import numpy as np
import time

def save_screenshot(filename, width, height):
    """Сохраняем текущий кадр OpenGL в файл (png или другой).
       width, height — размер текущего окна.
    """
    # Читаем пиксели из нижнего левого угла (0,0) до (width,height)
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)

    # data — это буфер типа bytes (или c_char_Array).
    # Преобразуем в numpy-массив для удобства
    # (width, height, 4) — RGBA
    arr = np.frombuffer(data, dtype=np.uint8)
    arr = arr.reshape((height, width, 4))

    # В OpenGL (0,0) — снизу, а Pillow ожидает (0,0) — сверху.
    # Нужно "перевернуть" arr по оси Y
    arr = np.flip(arr, axis=0)

    # Создаём Image из массива
    img = Image.fromarray(arr, "RGBA")

    # Сохраняем
    img.save(filename)
    print(f"Скриншот сохранён в {filename}")
