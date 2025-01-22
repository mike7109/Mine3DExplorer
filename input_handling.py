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

        if event.button == 1:  # левая кнопка
            mx, my = event.pos
            pick_axis(mx, my)

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

def pick_axis(mouse_x, mouse_y):
    """Упрощённый поиск выработки, близкой к лучу, с помощью midpoint + distance до луча."""
    ray_origin, ray_dir = get_ray_from_mouse(mouse_x, mouse_y)
    best_axis = None
    best_dist = 1e9
    threshold = 1.0  # Насколько "далеко" можно быть от центра оси

    for ax in config.axes_list:
        mid_x = (ax.xs + ax.xf) / 2
        mid_y = (ax.ys + ax.yf) / 2
        mid_z = (ax.zs + ax.zf) / 2
        dist = distance_point_to_ray((mid_x, mid_y, mid_z), ray_origin, ray_dir)
        if dist < threshold and dist < best_dist:
            best_dist = dist
            best_axis = ax

    if best_axis:
        config.selected_axis = best_axis
        # Если наш "главный" фрейм 'ManageAxesFrame' виден,
        # мы хотим отразить выбор в Listbox. Но теперь у нас фрейм, а не окно.
        # Допустим, мы сделаем config.manage_axes_frame, если хотим напрямую
        # Или найдём способ через tkinter variables.
        # Проще сделать:
        if hasattr(config, "manage_axes_frame") and config.manage_axes_frame is not None:
            config.manage_axes_frame.select_axis_by_name(best_axis.name)
        print("Выбрана ось:", best_axis.name)

def get_ray_from_mouse(mouse_x, mouse_y):
    """Преобразуем 2D-координаты мыши в 3D-луч (origin, direction)."""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    real_y = viewport[3] - mouse_y

    x0, y0, z0 = gluUnProject(mouse_x, real_y, 0.0, modelview, projection, viewport)
    x1, y1, z1 = gluUnProject(mouse_x, real_y, 1.0, modelview, projection, viewport)

    origin = (x0, y0, z0)
    dirx = x1 - x0
    diry = y1 - y0
    dirz = z1 - z0
    length = math.sqrt(dirx*dirx + diry*diry + dirz*dirz)
    if length > 1e-9:
        dirx /= length
        diry /= length
        dirz /= length

    return origin, (dirx, diry, dirz)

def distance_point_to_ray(point, ray_origin, ray_dir):
    px, py, pz = point
    ox, oy, oz = ray_origin
    vx, vy, vz = ray_dir
    # Вектор O->P
    dx = px - ox
    dy = py - oy
    dz = pz - oz
    # Проекция на луч (скалярное произведение)
    proj = dx*vx + dy*vy + dz*vz
    # Точка на луче
    rx = ox + proj*vx
    ry = oy + proj*vy
    rz = oz + proj*vz
    # Расстояние от P до R
    ex = rx - px
    ey = ry - py
    ez = rz - pz
    return math.sqrt(ex*ex + ey*ey + ez*ez)