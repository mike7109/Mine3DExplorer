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
    """Проверяем, попали ли мы в какую-то выработку."""
    ray_origin, ray_dir = get_ray_from_mouse(mouse_x, mouse_y)

    best_axis = None
    min_dist = 999999.0
    threshold = 0.2  # Насколько близко луч должен идти, чтобы считалось "попаданием"

    for ax in config.axes_list:
        seg_start = (ax.xs, ax.ys, ax.zs)
        seg_end   = (ax.xf, ax.yf, ax.zf)

        dist = distance_ray_to_segment(ray_origin, ray_dir, seg_start, seg_end)
        if dist < threshold and dist < min_dist:
            min_dist = dist
            best_axis = ax

    if best_axis:
        config.selected_axis = best_axis
        print(f"Выбрана ось: {best_axis.name}")
        # Если окно настроек (SettingsWindow) открыто, попросим его выделить эту ось в Listbox:
        if config.settings_window is not None:
            config.settings_window.select_axis_by_name(best_axis.name)

def get_ray_from_mouse(mouse_x, mouse_y):
    """Преобразуем 2D-координаты мыши в 3D-луч (origin, direction)."""
    # Читаем матрицы OpenGL
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    # OpenGL имеет начало в левом нижнем углу, а Pygame — в левом верхнем, значит:
    real_y = viewport[3] - mouse_y

    # gluUnProject для z=0 -> получить точку на "передней плоскости"
    x0, y0, z0 = gluUnProject(mouse_x, real_y, 0.0, modelview, projection, viewport)
    # gluUnProject для z=1 -> получить точку на "задней плоскости"
    x1, y1, z1 = gluUnProject(mouse_x, real_y, 1.0, modelview, projection, viewport)

    ray_origin = (x0, y0, z0)
    ray_dir = (x1 - x0, y1 - y0, z1 - z0)
    # Нормализуем ray_dir
    length = math.sqrt(ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2)
    if length > 1e-9:
        ray_dir = (ray_dir[0]/length, ray_dir[1]/length, ray_dir[2]/length)

    return ray_origin, ray_dir

def distance_ray_to_segment(ray_origin, ray_dir, seg_start, seg_end):
    """Расстояние от бесконечного луча (ray_origin + t*ray_dir) до отрезка seg_start->seg_end."""
    # Для упрощения — можем проверить расстояние до бесконечной прямой,
    # потом убедиться, что проекция точки лежит в пределах отрезка, иначе взять конец ближе к лучу.
    # Существуют готовые формулы, ниже "по шагам":

    px, py, pz = ray_origin
    vx, vy, vz = ray_dir
    # Отрезок:
    ax, ay, az = seg_start
    bx, by, bz = seg_end

    # Вектор AB:
    abx = bx - ax
    aby = by - ay
    abz = bz - az

    # Вектор PA:
    pax = ax - px
    pay = ay - py
    paz = az - pz

    # Скалярно-векторная магия:
    # Ищем параметр t на луче, s на отрезке (0<=s<=1), где расстояние минимально.
    # Формулы можно посмотреть в интернете ("Ray-Segment distance").

    # Для краткости можно взять упрощённый способ: сэмплировать несколько точек.
    # Но здесь дадим более точный, хоть и объёмный вариант:

    # Переменные для системы уравнений
    # (P + t*V) - (A + s*AB) = 0
    # => px + t*vx - (ax + s*abx) = 0  (1)
    #    py + t*vy - (ay + s*aby) = 0  (2)
    #    pz + t*vz - (az + s*abz) = 0  (3)
    #
    # Можно решить через метод наименьших квадратов.
    # Или используем готовый рецепт:

    EPS = 1e-9
    cross_v_ab = cross(vx, vy, vz, abx, aby, abz)
    denom = dot(cross_v_ab, cross_v_ab)
    if denom < EPS:
        # Луч и отрезок параллельны (или AB нулевой)
        # Возьмём расстояние до любой точки, например, seg_start
        return distance_point_to_ray((ax, ay, az), (px, py, pz), (vx, vy, vz))

    # Иначе найдем t и s
    cross_p_ab = cross(pax, pay, paz, abx, aby, abz)
    t = dot(cross_p_ab, cross_v_ab) / denom

    cross_p_v = cross(pax, pay, paz, vx, vy, vz)
    s = dot(cross_p_v, cross_v_ab) / denom

    # Если s < 0 -> ближайшая точка на отрезке за пределами [0,1], берем s=0
    # Если s > 1 -> тоже выходим за пределы отрезка, берем s=1
    if s < 0:
        s = 0
    elif s > 1:
        s = 1

    # Теперь точка на луче: R(t) = P + t*V
    # Но t мы нашли так, будто отрезок бесконечный. В реальности
    # нужно пересчитать t, учитывая скорректированное s.

    # К точке на сегменте: S(s) = A + s*AB
    sx = ax + s*abx
    sy = ay + s*aby
    sz = az + s*abz

    # Теперь расстояние от луча до этой точки - это расстояние от S(s) до прямой P+ t*V
    # Проще всего найти t_min, спроецировав вектор PS на V:
    psx = sx - px
    psy = sy - py
    psz = sz - pz
    t_min = dot(psx, psy, psz, vx, vy, vz)
    # Если t_min < 0, значит ближайшая точка на луче позади начала луча => берем 0
    if t_min < 0:
        t_min = 0
    # Точка на луче: R(t_min)
    rx = px + t_min*vx
    ry = py + t_min*vy
    rz = pz + t_min*vz

    # Расстояние между R(t_min) и S(s)
    dx = rx - sx
    dy = ry - sy
    dz = rz - sz
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def cross(ax, ay, az, bx, by, bz):
    return (ay*bz - az*by,
            az*bx - ax*bz,
            ax*by - ay*bx)

def dot(ax, ay, az, bx, by, bz):
    return ax*bx + ay*by + az*bz

def distance_point_to_ray(point, ray_origin, ray_dir):
    # Расстояние от точки до бесконечной прямой.
    px, py, pz = point
    ox, oy, oz = ray_origin
    vx, vy, vz = ray_dir
    # Вектор OP
    oxp = px - ox
    oyp = py - oy
    ozp = pz - oz
    # Проекция на V
    proj = dot(oxp, oyp, ozp, vx, vy, vz)
    # Точка на луче: R(proj)
    # Но если proj < 0 => луч в другую сторону, всё равно считаем для прямой
    rx = ox + proj*vx
    ry = oy + proj*vy
    rz = oz + proj*vz

    dx = px - rx
    dy = py - ry
    dz = pz - rz
    return math.sqrt(dx*dx + dy*dy + dz*dz)