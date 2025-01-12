# input_handling.py
import pygame
from pygame.locals import *
import math

import config
import screenshot

def handle_event(event):
    """Обработка событий Pygame (клики и т.д.)"""
    if event.type == pygame.KEYDOWN:
        # Например, нажали "p"
        if event.key == pygame.K_p:
            # делаем скриншот
            filename = make_screenshot_filename()  # какую-то функцию придумываем
            width = config.WINDOW_WIDTH
            height = config.WINDOW_HEIGHT
            screenshot.save_screenshot(filename, width, height)
            # Или: screenshot.save_screenshot("my_screen.png", width, height)

        if event.key == pygame.K_ESCAPE:
            # По ESC можно, например, завершать программу
            pass

    # ====== Обработка нажатий мыши =======
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Правая кнопка в Pygame обычно button=3
        if event.button == 3:
            config.right_mouse_held = True

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
    """Движение камеры при нажатии W/S/A/D/Q/E."""
    pressed = pygame.key.get_pressed()

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
    right_x = forward_y*up_z - forward_z*up_y
    right_y = forward_z*up_x - forward_x*up_z
    right_z = forward_x*up_y - forward_y*up_x

    # Нормируем right
    rlen = math.sqrt(right_x**2 + right_y**2 + right_z**2)
    if rlen > 1e-9:
        right_x /= rlen
        right_y /= rlen
        right_z /= rlen

    move_speed = config.MOVE_SPEED

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