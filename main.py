# main.py
import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import config
import data_loader
import renderer_3d
import input_handling

def init_pygame_window(width=800, height=600):
    pygame.init()
    display_flags = DOUBLEBUF | OPENGL
    pygame.display.set_mode((width, height), display_flags)
    pygame.display.set_caption("Mine3DExplorer — Only Mine Axes")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.3, 0.4, 1.0)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, width / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    # Инициализация окна
    width, height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    init_pygame_window(width, height)

    # Загрузка данных шахтных осей
    data_loader.load_mine_axes("mine_axes.csv")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            input_handling.handle_event(event)

        input_handling.update_camera_state()

        # Очищаем экран
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Рассчитываем направление камеры
        from math import radians, sin, cos
        yaw_rad = radians(config.camera_yaw)
        pitch_rad = radians(config.camera_pitch)
        fx = cos(yaw_rad) * cos(pitch_rad)
        fy = sin(pitch_rad)
        fz = sin(yaw_rad) * cos(pitch_rad)

        cx = config.camera_x
        cy = config.camera_y
        cz = config.camera_z

        # Устанавливаем камеру
        gluLookAt(cx, cy, cz,
                  cx + fx, cy + fy, cz + fz,
                  0, 1, 0)

        # Рендерим шахту
        renderer_3d.draw_mine()

        # Обновляем экран
        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()