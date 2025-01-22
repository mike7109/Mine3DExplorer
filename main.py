# main.py

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import pygame_gui

import config
import data_loader
import renderer_3d
import input_handling
import renderer_2d
import utils


def init_pygame_window(width=1024, height=768):
    pygame.init()
    display_flags = DOUBLEBUF | OPENGL | RESIZABLE
    pygame.display.set_mode((width, height), display_flags)
    pygame.display.set_caption("Mine3DExplorer")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.3, 0.4, 1.0)
    utils.set_perspective(width, height)


def main():
    # Инициализация
    config.WINDOW_WIDTH, config.WINDOW_HEIGHT = 1024, 768
    init_pygame_window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    renderer_2d.init_font()

    # Менеджер GUI
    ui_manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

    clock = pygame.time.Clock()

    # Загрузка данных
    data_loader.load_mine_axes("mine_axes.csv")  # заполнит config.axes_list
    data_loader.load_equipment("equipment.csv")  # заполнит config.equipment_list и trolleys_list
    data_loader.load_works("works.csv")  # заполнит config.works_list
    data_loader.load_axis_works("axis_works.csv")  # свяжет выработки и работы

    # Подготовим список имён выработок (для DropDown)
    axis_names = [ax.name for ax in config.axes_list]
    if not axis_names:
        axis_names = ["No Axes"]

    # Создадим выпадающий список, но не отображаем его сразу
    drop_down = pygame_gui.elements.UIDropDownMenu(
        options_list=axis_names,
        starting_option=axis_names[0],
        relative_rect=pygame.Rect((20, 20), (200, 30)),
        manager=ui_manager,
        visible=0  # Меню скрыто по умолчанию
    )

    # Создадим SelectionList для работ, тоже скрыт
    work_list_ui = pygame_gui.elements.UISelectionList(
        relative_rect=pygame.Rect((20, 60), (250, 200)),
        item_list=[],
        manager=ui_manager,
        visible=0  # Скрыт по умолчанию
    )

    # По умолчанию выберем первую выработку (если есть)
    selected_axis = config.axes_list[0] if config.axes_list else None
    if selected_axis:
        # Заполним список работ
        items = [w.work_name for w in selected_axis.works]
        work_list_ui.set_item_list(items)

    # Флаг видимости меню
    menu_visible = False

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                config.WINDOW_WIDTH, config.WINDOW_HEIGHT = event.size
                glViewport(0, 0, event.w, event.h)
                utils.set_perspective(event.w, event.h)
                ui_manager.set_window_resolution((event.w, event.h))

            # Передаём событие в pygame_gui
            ui_manager.process_events(event)

            # Обработка нашей камеры, горячих клавиш
            input_handling.handle_event(event)

            # Обработка открытия/закрытия меню
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    menu_visible = not menu_visible
                    drop_down.visible = menu_visible
                    work_list_ui.visible = menu_visible

            # События UI
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == drop_down:
                        chosen_axis_name = drop_down.selected_option
                        # Найдём в списке
                        for ax in config.axes_list:
                            if ax.name == chosen_axis_name:
                                selected_axis = ax
                                break
                        # Обновим список работ
                        if selected_axis:
                            items = [w.work_name for w in selected_axis.works]
                            work_list_ui.set_item_list(items)

                elif event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    if event.ui_element == work_list_ui:
                        chosen_work_name = event.text
                        print("Выбрана работа:", chosen_work_name)

        ui_manager.update(time_delta)

        # Обновляем камеру
        input_handling.update_camera_state()

        # Обновляем вагонетки
        for trolley in config.trolleys_list:
            trolley.update()

        # 3D-отрисовка
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Позиция/ориентация камеры
        from math import radians, sin, cos
        yaw_rad = radians(config.camera_yaw)
        pitch_rad = radians(config.camera_pitch)
        fx = cos(yaw_rad) * cos(pitch_rad)
        fy = sin(pitch_rad)
        fz = sin(yaw_rad) * cos(pitch_rad)

        cx = config.camera_x
        cy = config.camera_y
        cz = config.camera_z

        gluLookAt(cx, cy, cz,
                  cx + fx, cy + fy, cz + fz,
                  0, 1, 0)

        renderer_3d.draw_mine()

        # (Optional) Рендерим 2D наложение (старый текст)
        renderer_2d.draw_2d_overlay()

        # Теперь отрисовываем GUI
        glFlush()
        screen = pygame.display.get_surface()
        ui_manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
