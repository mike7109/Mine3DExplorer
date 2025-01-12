# textures.py

import pygame
from OpenGL.GL import *

def load_texture(filepath) -> int:
    """Загружает текстуру из файла (PNG, JPG, BMP и т.д.)
       и возвращает идентификатор texture_id."""
    # Загружаем изображение через pygame
    surface = pygame.image.load(filepath)
    # Преобразуем пиксели в строку байт (RGBA)
    image_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_rect().size

    # Генерируем 1 текстуру в OpenGL
    texture_id = glGenTextures(1)
    # Делаем эту текстуру "текущей"
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Загружаем пиксели в OpenGL
    glTexImage2D(
        GL_TEXTURE_2D,
        0,             # уровень детализации
        GL_RGBA,       # Внутренний формат
        width,
        height,
        0,             # границы (border = 0)
        GL_RGBA,       # формат пикселей
        GL_UNSIGNED_BYTE,
        image_data
    )

    # Настраиваем параметры текстуры (увеличение/уменьшение)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # По желанию настройка Wrap (повтор/зажим)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Отвязываем
    glBindTexture(GL_TEXTURE_2D, 0)

    print(f"[load_texture] Текстура '{filepath}' загружена (ID={texture_id}, {width}x{height})")
    return texture_id
