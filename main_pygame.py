# main_pygame.py
import pygame
import config
import data_loader
import renderer_3d
import renderer_2d
import input_handling
import utils
from pygame.locals import *
import math

def main():
    """Запускает окно Pygame/OpenGL"""
    pygame.init()
    display_flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
    screen = pygame.display.set_mode((1024, 768), display_flags)
    pygame.display.set_caption("Mine3DExplorer")

    from OpenGL.GL import (
        glEnable, GL_DEPTH_TEST, glClearColor, glDepthFunc, GL_LESS,
        glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
        glMatrixMode, GL_MODELVIEW, glLoadIdentity
    )
    from OpenGL.GLU import gluPerspective, gluLookAt

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.2, 0.3, 0.4, 1.0)

    utils.set_perspective(1024, 768)

    renderer_2d.init_font()

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                config.WINDOW_WIDTH, config.WINDOW_HEIGHT = event.w, event.h
                from OpenGL.GL import glViewport
                glViewport(0, 0, event.w, event.h)
                utils.set_perspective(event.w, event.h)

            input_handling.handle_event(event)  # Тут вызываем pick_axis упрощённо

        # Обновление камеры
        input_handling.update_camera_state()

        # Обновление вагонеток
        for trolley in config.trolleys_list:
            trolley.update()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        yaw_rad = math.radians(config.camera_yaw)
        pitch_rad = math.radians(config.camera_pitch)
        fx = math.cos(yaw_rad) * math.cos(pitch_rad)
        fy = math.sin(pitch_rad)
        fz = math.sin(yaw_rad) * math.cos(pitch_rad)

        cx, cy, cz = config.camera_x, config.camera_y, config.camera_z
        gluLookAt(cx, cy, cz,
                  cx + fx, cy + fy, cz + fz,
                  0, 1, 0)

        # Рисуем шахту
        renderer_3d.draw_mine()
        renderer_2d.draw_2d_overlay()

        pygame.display.flip()


    pygame.quit()
    config.running = False