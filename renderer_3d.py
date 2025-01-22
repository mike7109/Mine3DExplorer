import math
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame

import config
import utils
from classes import Trolley  # если надо

quadric = gluNewQuadric()

text_texture_cache = {}
pygame.font.init()
font_obj = None

def draw_mine():
    """Главная функция рендера: рисуем выработки, оборудование, вагонетки и т.д."""
    global font_obj
    font_obj = pygame.font.SysFont("Arial", 20)
    draw_floor()
    draw_mine_axes()
    draw_equipment()
    # (если нужно) draw_work_places() - у вас может быть другое
    # Рисуем вагонетки
    for trolley in config.trolleys_list:
        draw_trolley(trolley)

def draw_floor():
    """Сеточная плоскость."""
    grid_size = 50
    grid_spacing = 1.0
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-grid_size, grid_size + 1):
        glVertex3f(-grid_size * grid_spacing, 0, i * grid_spacing)
        glVertex3f(grid_size * grid_spacing, 0, i * grid_spacing)
        glVertex3f(i * grid_spacing, 0, -grid_size * grid_spacing)
        glVertex3f(i * grid_spacing, 0, grid_size * grid_spacing)
    glEnd()

def draw_mine_axes():
    glLineWidth(3.0)
    glBegin(GL_LINES)
    for ax in config.axes_list:
        # Проверка, является ли эта ось выбранной
        if ax == config.selected_axis:
            # Подсвечиваем ось жёлтым
            glColor3f(1.0, 1.0, 0.0)
        else:
            # Иначе обычная логика по status
            if ax.status == 1:
                glColor3f(1, 0, 0)
            elif ax.status == 2:
                glColor3f(0, 1, 0)
            elif ax.status == 3:
                glColor3f(0, 0, 1)
            else:
                glColor3f(0.8, 0.8, 0.8)

        glVertex3f(ax.xs, ax.ys, ax.zs)
        glVertex3f(ax.xf, ax.yf, ax.zf)
    glEnd()
    glLineWidth(1.0)

    # Рисуем название работы на середине оси, если выбрано
    if config.selected_axis and config.selected_work:
        ax = config.selected_axis
        # Проверим, активна ли эта работа на оси
        if config.selected_work in ax.active_works:
            mx = (ax.xs + ax.xf) / 2.0
            my = (ax.ys + ax.yf) / 2.0
            mz = (ax.zs + ax.zf) / 2.0

            work_name = config.selected_work.work_name
            # Выводим текст (например, жёлтый)
            draw_text_3d(work_name, (mx, my, mz), scale=0.5, color=(255, 255, 0))

def draw_equipment():
    """Рисуем оборудование как пунктирные линии + сфера + подпись."""
    glLineWidth(2.0)
    for eq in config.equipment_list:
        if eq.eq_status == 1:
            glColor3f(1, 0.5, 0.5)
        elif eq.eq_status == 2:
            glColor3f(0.5, 1, 0.5)
        else:
            glColor3f(0.8, 0.8, 0.8)

        start = (eq.xs, eq.ys, eq.zs)
        end = (eq.xf, eq.yf, eq.zf)
        # Пунктир
        draw_dashed_line(start, end,
                         dash_length=config.EQUIPMENT_DASH_LENGTH,
                         gap_length=config.EQUIPMENT_GAP_LENGTH)

        # Сфера в начале
        glPushMatrix()
        glTranslatef(*start)
        gluSphere(quadric, 0.2, 16, 16)
        glPopMatrix()

        # Подпись
        draw_text_3d(eq.eq_name, start, scale=0.5, color=(255, 255, 0))
    glLineWidth(1.0)

def draw_dashed_line(start, end, dash_length=0.5, gap_length=0.5):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    if distance == 0:
        return
    dx /= distance
    dy /= distance
    dz /= distance

    current_dist = 0.0
    drawing = True
    while current_dist < distance:
        seg_len = dash_length if drawing else gap_length
        seg_len = min(seg_len, distance - current_dist)
        if drawing:
            glBegin(GL_LINES)
            glVertex3f(start[0] + dx*current_dist,
                       start[1] + dy*current_dist,
                       start[2] + dz*current_dist)
            glVertex3f(start[0] + dx*(current_dist+seg_len),
                       start[1] + dy*(current_dist+seg_len),
                       start[2] + dz*(current_dist+seg_len))
            glEnd()
        current_dist += seg_len
        drawing = not drawing

def draw_text_3d(text, position, scale=1.0, color=(255, 255, 0)):
    """Простейший биллборд-текст в 3D."""
    texture_id, w, h = get_text_texture(text, color)
    if not texture_id:
        return

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glPushMatrix()
    glTranslatef(*position)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    # Извлекаем right & up векторы
    right = (modelview[0][0], modelview[1][0], modelview[2][0])
    up    = (modelview[0][1], modelview[1][1], modelview[2][1])

    aspect = w / float(h)
    sr = [r * scale * aspect for r in right]
    su = [u * scale for u in up]

    glBegin(GL_QUADS)
    # левый нижний угол
    glTexCoord2f(0, 0)
    glVertex3f(0, 0, 0)
    # правый нижний угол
    glTexCoord2f(1, 0)
    glVertex3f(sr[0], sr[1], sr[2])
    # правый верхний
    glTexCoord2f(1, 1)
    glVertex3f(sr[0]+su[0], sr[1]+su[1], sr[2]+su[2])
    # левый верхний
    glTexCoord2f(0, 1)
    glVertex3f(su[0], su[1], su[2])
    glEnd()

    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

def get_text_texture(text, color):
    """Возвращает (texture_id, w, h)"""
    key = (text, color)
    if key in text_texture_cache:
        return text_texture_cache[key]

    surf = font_obj.render(text, True, color)
    text_data = pygame.image.tostring(surf, "RGBA", True)
    w, h = surf.get_size()

    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    text_texture_cache[key] = (tid, w, h)
    return text_texture_cache[key]

def compute_yaw_pitch(direction):
    dx, dy, dz = direction
    # yaw = arctan2(dx, dz) — но аккуратнее
    yaw_rad = math.atan2(dx, dz)
    yaw = math.degrees(yaw_rad)
    horiz_len = math.sqrt(dx*dx + dz*dz)
    pitch_rad = math.atan2(dy, horiz_len)
    pitch = math.degrees(pitch_rad)
    return (yaw, pitch)

def draw_trolley(trolley):
    """Рисуем примитивную вагонетку."""
    pos = trolley.get_position()
    dir_vec = trolley.get_direction_vector()
    yaw, pitch = compute_yaw_pitch(dir_vec)

    glPushMatrix()
    glTranslatef(*pos)
    # Сначала крутим по X (pitch), потом по Y (yaw)
    glRotatef(-pitch, 1, 0, 0)
    glRotatef(-yaw, 0, 1, 0)
    # Просто нарисуем прямоугольный параллелепипед
    glColor3f(0.2, 0.6, 0.8)

    rect_length = 0.3
    rect_height = 0.1
    rect_depth = 1.3

    glBegin(GL_QUADS)
    # Верх
    glVertex3f(-rect_length/2, rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, rect_depth/2)
    glVertex3f(-rect_length/2, rect_height/2, rect_depth/2)

    # Низ
    glVertex3f(-rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, -rect_height/2, rect_depth/2)
    glVertex3f(-rect_length/2, -rect_height/2, rect_depth/2)

    # Перед
    glVertex3f(-rect_length/2, -rect_height/2, rect_depth/2)
    glVertex3f(rect_length/2, -rect_height/2, rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, rect_depth/2)
    glVertex3f(-rect_length/2, rect_height/2, rect_depth/2)

    # Зад
    glVertex3f(-rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, -rect_depth/2)
    glVertex3f(-rect_length/2, rect_height/2, -rect_depth/2)

    # Левая грань
    glVertex3f(-rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(-rect_length/2, -rect_height/2, rect_depth/2)
    glVertex3f(-rect_length/2, rect_height/2, rect_depth/2)
    glVertex3f(-rect_length/2, rect_height/2, -rect_depth/2)

    # Правая грань
    glVertex3f(rect_length/2, -rect_height/2, -rect_depth/2)
    glVertex3f(rect_length/2, -rect_height/2, rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, rect_depth/2)
    glVertex3f(rect_length/2, rect_height/2, -rect_depth/2)
    glEnd()

    glPopMatrix()