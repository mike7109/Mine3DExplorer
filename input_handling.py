import pygame
from pygame.locals import *
import math
import config
import screenshot
import utils

DOUBLE_CLICK_TIME = 500  # мс
last_click_time = 0
click_count = 0

def handle_event(event):
    global last_click_time, click_count

    if event.type == pygame.KEYDOWN:
        # p -> скриншот
        if event.key == pygame.K_p:
            filename = utils.make_screenshot_filename()
            width = config.WINDOW_WIDTH
            height = config.WINDOW_HEIGHT
            screenshot.save_screenshot(filename, width, height)

        # ESC -> выход
        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))

        # F -> переключение полноэкранного режима
        if event.key == pygame.K_f:
            config.fullscreen = not config.fullscreen
            toggle_fullscreen()

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 3:  # правая кнопка мыши
            config.right_mouse_held = True

        # Двойной клик левой кнопкой для фуллскрина
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

    if event.type == pygame.MOUSEMOTION:
        if config.right_mouse_held:
            rel_x, rel_y = event.rel
            config.camera_yaw   += rel_x * config.MOUSE_SENSITIVITY
            config.camera_pitch -= rel_y * config.MOUSE_SENSITIVITY

            # Ограничиваем pitch
            if config.camera_pitch > config.PITCH_LIMIT:
                config.camera_pitch = config.PITCH_LIMIT
            if config.camera_pitch < -config.PITCH_LIMIT:
                config.camera_pitch = -config.PITCH_LIMIT


def update_camera_state():
    pressed = pygame.key.get_pressed()

    # Удерживается ли Shift
    mods = pygame.key.get_mods()
    shift_held = mods & pygame.KMOD_SHIFT
    move_speed = config.MOVE_SPEED * 4 if shift_held else config.MOVE_SPEED

    yaw_rad = math.radians(config.camera_yaw)
    pitch_rad = math.radians(config.camera_pitch)

    # Вектор взгляда
    forward_x = math.cos(yaw_rad) * math.cos(pitch_rad)
    forward_y = math.sin(pitch_rad)
    forward_z = math.sin(yaw_rad) * math.cos(pitch_rad)

    # Вектор up
    up_x, up_y, up_z = 0.0, 1.0, 0.0

    # Вектор right = forward x up
    right_x = forward_y * up_z - forward_z * up_y
    right_y = forward_z * up_x - forward_x * up_z
    right_z = forward_x * up_y - forward_y * up_x

    # нормализуем right
    rlen = math.sqrt(right_x**2 + right_y**2 + right_z**2)
    if rlen > 1e-9:
        right_x /= rlen
        right_y /= rlen
        right_z /= rlen

    # W / S
    if pressed[pygame.K_w]:
        config.camera_x += forward_x * move_speed
        config.camera_y += forward_y * move_speed
        config.camera_z += forward_z * move_speed

    if pressed[pygame.K_s]:
        config.camera_x -= forward_x * move_speed
        config.camera_y -= forward_y * move_speed
        config.camera_z -= forward_z * move_speed

    # A / D
    if pressed[pygame.K_a]:
        config.camera_x -= right_x * move_speed
        config.camera_y -= right_y * move_speed
        config.camera_z -= right_z * move_speed

    if pressed[pygame.K_d]:
        config.camera_x += right_x * move_speed
        config.camera_y += right_y * move_speed
        config.camera_z += right_z * move_speed

    # Q / E
    if pressed[pygame.K_q]:
        config.camera_y += move_speed
    if pressed[pygame.K_e]:
        config.camera_y -= move_speed


def toggle_fullscreen():
    width, height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    if config.fullscreen:
        display_flags = DOUBLEBUF | OPENGL | FULLSCREEN
        screen = pygame.display.set_mode((0, 0), display_flags)
        info = pygame.display.Info()
        config.WINDOW_WIDTH, config.WINDOW_HEIGHT = info.current_w, info.current_h
    else:
        display_flags = DOUBLEBUF | OPENGL | RESIZABLE
        pygame.display.set_mode((800, 600), display_flags)
        config.WINDOW_WIDTH, config.WINDOW_HEIGHT = 800, 600
