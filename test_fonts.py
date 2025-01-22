#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import imgui
from imgui.integrations.pygame import PygameRenderer


def main():
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("ImGui Integration Test - Настройки")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.3, 0.4, 1.0)
    gluPerspective(60, (width / float(height)), 0.1, 1000.0)

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = (width, height)
    print("ImGui display_size set to:", io.display_size)

    try:
        # Добавляем диапазон кириллицы
        cyrillic_ranges = io.fonts.get_glyph_ranges_cyrillic()

        # Загружаем шрифт с учётом кириллического диапазона
        io.fonts.add_font_from_file_ttf(
            "freesans.ttf",
            20.0,
            None,  # Вместо FontConfig()
            cyrillic_ranges
        )

        impl.refresh_font_texture()
        print("Шрифт DejaVuSans.ttf успешно загружен и поддерживает кириллицу.")
    except Exception as e:
        print("Ошибка при загрузке шрифта:", e)

    settings_visible = False

    clock = pygame.time.Clock()
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
                glViewport(0, 0, width, height)
                gluPerspective(60, (width / float(height)), 0.1, 1000.0)
                io.display_size = (width, height)
                print("Window resized. New display_size set to:", io.display_size)
            impl.process_event(event)

            if event.type == KEYDOWN:
                if event.key == K_m:
                    settings_visible = not settings_visible
                    print("Настройки открыты" if settings_visible else "Настройки закрыты")

        imgui.new_frame()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

        # Отрисовка куба (или чего угодно)
        # ...

        # Рендер окна настроек
        if settings_visible:
            try:
                imgui.set_next_window_position(0, 0)
                imgui.set_next_window_size(300, height)
                imgui.begin("Настройки", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)

                imgui.text("Настройки Выработки")
                imgui.separator()

                changed, checkbox = imgui.checkbox("Активировать выработку", False)
                if changed:
                    print("Активировать выработку:", checkbox)

                changed, slider = imgui.slider_float("Скорость выработки", 0.0, 0.0, 100.0)
                if changed:
                    print(f"Скорость выработки: {slider}")

                if imgui.button("Применить настройки"):
                    print("Настройки применены")

                imgui.end()
            except Exception as e:
                print("Exception in ImGui menu:", e)
                imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()

    impl.shutdown()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
