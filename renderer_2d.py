# renderer_2d.py

import pygame
from OpenGL.raw.GLU import gluOrtho2D
from pygame.locals import *
from OpenGL.GL import *

import config

font_obj = None

def init_font():
    pygame.font.init()
    global font_obj
    # Возьмём шрифт Arial (или любой системный)
    font_obj = pygame.font.SysFont("Arial", 20)

def draw_2d_overlay():
    """Рисуем текст в левом верхнем углу с правильной обработкой прозрачности."""
    global font_obj
    if not font_obj:
        return

    lines = [
        f"Camera pos: X={config.camera_x:.2f}, Y={config.camera_y:.2f}, Z={config.camera_z:.2f}",
        f"Camera yaw={config.camera_yaw:.2f}, pitch={config.camera_pitch:.2f}",
        "Controls: W/S/A/D - move, Q/E - up/down,",
        "Right Mouse - look around",
        "F - Toggle Fullscreen",
        f"Speed: {'Fast' if pygame.key.get_mods() & pygame.KMOD_SHIFT else 'Normal'}"
    ]

    # Сохраняем матрицы
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    width = config.WINDOW_WIDTH
    height = config.WINDOW_HEIGHT
    gluOrtho2D(0, width, height, 0)  # (0,0) - верхний левый угол

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    x_start = 10
    y_start = 10
    line_height = 22
    cur_y = y_start

    for text_line in lines:
        # Рендер текста в Surface (белый текст на прозрачном фоне)
        # surface = font_obj.render(text_line, True, (255, 255, 255, 255), (0, 0, 0, 0))
        surface = font_obj.render(text_line, True, (255, 255, 0))
        # Исправляем цвета, если нужно (RGBA)
        text_data = pygame.image.tostring(surface, "RGBA", True)

        w, h = surface.get_size()

        # Создаём текстуру OpenGL
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        # Включаем текстурирование
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Рисуем текстурный квад
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x_start, cur_y)
        glTexCoord2f(1, 1); glVertex2f(x_start + w, cur_y)
        glTexCoord2f(1, 0); glVertex2f(x_start + w, cur_y + h)
        glTexCoord2f(0, 0); glVertex2f(x_start, cur_y + h)
        glEnd()

        # Удаляем текстуру после использования
        glDeleteTextures([texture_id])

        glDisable(GL_TEXTURE_2D)

        cur_y += line_height

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    # Восстанавливаем матрицы
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
