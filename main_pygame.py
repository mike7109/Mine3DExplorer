# main_pygame.py

import threading
import pygame
import config
import ui_settings
import data_loader
import renderer_3d
import renderer_2d
import input_handling
import utils
from pygame.locals import *

def init_pygame_window(width=1024, height=768):
    """Инициализация окна Pygame/OpenGL."""
    pygame.init()
    display_flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
    pygame.display.set_mode((width, height), display_flags)
    pygame.display.set_caption("Mine3DExplorer")

    from OpenGL.GL import (
        glEnable, GL_DEPTH_TEST, glClearColor, glDepthFunc, GL_LESS
    )
    from OpenGL.GLU import gluPerspective

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.2, 0.3, 0.4, 1.0)

    utils.set_perspective(width, height)

def main():
    """Главная функция запуска 3D-визуализации (Pygame)"""
    # 1. Загрузка данных
    data_loader.load_mine_axes("mine_axes.csv")
    data_loader.load_equipment("equipment.csv")
    data_loader.load_works("works.csv")
    data_loader.load_axis_works("axis_works.csv")

    # 2. Инициализируем Pygame
    config.WINDOW_WIDTH, config.WINDOW_HEIGHT = 1024, 768
    init_pygame_window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    renderer_2d.init_font()

    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                config.WINDOW_WIDTH, config.WINDOW_HEIGHT = event.w, event.h
                from OpenGL.GL import glViewport
                glViewport(0, 0, event.w, event.h)
                utils.set_perspective(event.w, event.h)

            # Обработка клавиш, мыши и т.д.
            input_handling.handle_event(event)

        # Обновляем камеру
        input_handling.update_camera_state()

        # Обновляем (например) вагонетки
        for trolley in config.trolleys_list:
            trolley.update()

        # Очищаем экран
        from OpenGL.GL import (
            glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
            glMatrixMode, GL_MODELVIEW, glLoadIdentity
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Ставим камеру
        from math import radians, sin, cos
        yaw_rad = radians(config.camera_yaw)
        pitch_rad = radians(config.camera_pitch)
        fx = cos(yaw_rad) * cos(pitch_rad)
        fy = sin(pitch_rad)
        fz = sin(yaw_rad) * cos(pitch_rad)

        cx, cy, cz = config.camera_x, config.camera_y, config.camera_z

        from OpenGL.GLU import gluLookAt
        gluLookAt(
            cx, cy, cz,
            cx + fx, cy + fy, cz + fz,
            0, 1, 0
        )

        # Рисуем 3D-сцену
        renderer_3d.draw_mine()

        # Наложение 2D (текст, HUD)
        renderer_2d.draw_2d_overlay()

        pygame.display.flip()

    pygame.quit()

# При желании можно оставить этот блок, чтобы при запуске файла напрямую из командной строки
# всё сразу работало. Но если вы импортируете это из другого модуля (pygame_runner.py),
# можете закомментировать.
if __name__ == "__main__":
    main()
