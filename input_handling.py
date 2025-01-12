# input_handling.py

import pygame
from pygame.locals import *
import math

import config
import screenshot
import utils  # Вместо import main

DOUBLE_CLICK_TIME = 500  # Максимальное время между кликами в миллисекундах
last_click_time = 0
click_count = 0

def handle_event(event):
    """Обработка событий Pygame (клики и т.д.)"""
    global last_click_time, click_count

    if event.type == pygame.KEYDOWN:
        # Нажали "p" для скриншота
        if event.key == pygame.K_p:
            filename = make_screenshot_filename()
            width = config.WINDOW_WIDTH
            height = config.WINDOW_HEIGHT
            screenshot.save_screenshot(filename, width, height)

        # Нажали ESC (добавляем событие выхода)
        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))

        # Нажатие 'F' для переключения полноэкранного режима
        if event.key == pygame.K_f:
            config.fullscreen = not config.fullscreen
            toggle_fullscreen()

    # ====== Обработка нажатий мыши =======
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Правая кнопка мыши (button=3)
        if event.button == 3:
            config.right_mouse_held = True

        # Обработка двойного щелчка левой кнопки для полноэкранного режима
        if event.button == 1:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time < DOUBLE_CLICK_TIME:
                click_count += 1
                if click_count == 2:
                    config.fullscreen = not config.fullscreen
                    toggle_fullscreen()
                    click_count = 0
            else:
                click_count = 1
            last_click_time = current_time

    if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 3:
            config.right_mouse_held = False

    # ====== Перемещение мыши =======
    if event.type == pygame.MOUSEMOTION:
        # event.rel = (dx, dy) - сдвиг мыши за один кадр
        if config.right_mouse_held:
            rel_x, rel_y = event.rel

            # При зажатой правой кнопке вращаем камеру
            config.camera_yaw   += rel_x * config.MOUSE_SENSITIVITY
            config.camera_pitch -= rel_y * config.MOUSE_SENSITIVITY

            # Ограничим pitch
            if config.camera_pitch > config.PITCH_LIMIT:
                config.camera_pitch = config.PITCH_LIMIT
            if config.camera_pitch < -config.PITCH_LIMIT:
                config.camera_pitch = -config.PITCH_LIMIT

def update_camera_state():
    """Движение камеры при нажатии W/S/A/D/Q/E и ускорение при Shift."""
    pressed = pygame.key.get_pressed()

    # Проверяем, удерживается ли Shift (левый или правый)
    mods = pygame.key.get_mods()
    shift_held = mods & pygame.KMOD_SHIFT

    # Устанавливаем скорость перемещения
    move_speed = config.MOVE_SPEED * 4 if shift_held else config.MOVE_SPEED

    # Перевод углов в радианы
    yaw_rad   = math.radians(config.camera_yaw)
    pitch_rad = math.radians(config.camera_pitch)

    # Вектор взгляда (forward)
    forward_x = math.cos(yaw_rad) * math.cos(pitch_rad)
    forward_y = math.sin(pitch_rad)
    forward_z = math.sin(yaw_rad) * math.cos(pitch_rad)

    # Вектор up
    up_x, up_y, up_z = 0.0, 1.0, 0.0

    # Вектор right = forward × up
    right_x = forward_y * up_z - forward_z * up_y
    right_y = forward_z * up_x - forward_x * up_z
    right_z = forward_x * up_y - forward_y * up_x

    # Нормализуем right
    rlen = math.sqrt(right_x**2 + right_y**2 + right_z**2)
    if rlen > 1e-9:
        right_x /= rlen
        right_y /= rlen
        right_z /= rlen

    # W - вперёд
    if pressed[pygame.K_w]:
        config.camera_x += forward_x * move_speed
        config.camera_y += forward_y * move_speed
        config.camera_z += forward_z * move_speed

    # S - назад
    if pressed[pygame.K_s]:
        config.camera_x -= forward_x * move_speed
        config.camera_y -= forward_y * move_speed
        config.camera_z -= forward_z * move_speed

    # A - влево (против right)
    if pressed[pygame.K_a]:
        config.camera_x -= right_x * move_speed
        config.camera_y -= right_y * move_speed
        config.camera_z -= right_z * move_speed

    # D - вправо (по right)
    if pressed[pygame.K_d]:
        config.camera_x += right_x * move_speed
        config.camera_y += right_y * move_speed
        config.camera_z += right_z * move_speed

    # Q - вверх
    if pressed[pygame.K_q]:
        config.camera_y += move_speed
    # E - вниз
    if pressed[pygame.K_e]:
        config.camera_y -= move_speed

def make_screenshot_filename():
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    return f"screenshot_{timestr}.png"

def toggle_fullscreen():
    """Переключение между оконным и полноэкранным режимом."""
    width, height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    if config.fullscreen:
        display_flags = DOUBLEBUF | OPENGL | FULLSCREEN
        screen = pygame.display.set_mode((0, 0), display_flags)
        # Обновляем ширину и высоту до разрешения экрана
        info = pygame.display.Info()
        config.WINDOW_WIDTH, config.WINDOW_HEIGHT = info.current_w, info.current_h
    else:
        display_flags = DOUBLEBUF | OPENGL | RESIZABLE
        pygame.display.set_mode((800, 600), display_flags)  # Возвращаем стандартное разрешение
        config.WINDOW_WIDTH, config.WINDOW_HEIGHT = 800, 600

    # Обновляем перспективу
    utils.set_perspective(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
