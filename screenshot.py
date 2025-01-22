from OpenGL.GL import *
from PIL import Image
import numpy as np

def save_screenshot(filename, width, height):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    arr = np.frombuffer(data, dtype=np.uint8)
    arr = arr.reshape((height, width, 4))
    arr = np.flip(arr, axis=0)

    img = Image.fromarray(arr, "RGBA")
    img.save(filename)
    print(f"Скриншот сохранён: {filename}")
