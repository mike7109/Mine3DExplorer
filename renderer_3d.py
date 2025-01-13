# renderer_3d.py

import config
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import utils
import pygame

# Инициализируем Quadric объект для отрисовки сфер
quadric = gluNewQuadric()

# Инициализируем шрифт Pygame
pygame.font.init()
font_obj = pygame.font.SysFont("Arial", 20)

# Кэш текстур для названий
text_texture_cache = {}


def get_text_texture(text, color=(255, 255, 0)):
    key = (text, color)
    if key in text_texture_cache:
        return text_texture_cache[key]

    surface = font_obj.render(text, True, color)
    text_data = pygame.image.tostring(surface, "RGBA", True)
    w, h = surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    text_texture_cache[key] = (texture_id, w, h)
    return texture_id, w, h

def draw_text_3d(text, position, scale=1.0, color=(255, 255, 0)):
    """Рисует текст в 3D-пространстве с использованием билборда."""
    texture_info = get_text_texture(text, color)
    if not texture_info:
        return
    texture_id, w, h = texture_info

    # Настройка прозрачности
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Включаем текстурирование
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Сохранение текущего состояния матрицы
    glPushMatrix()
    glTranslatef(*position)

    # Получаем текущие матрицы модели и вида
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)

    # Извлекаем правый и верхний векторы из матрицы модели
    right = [modelview[0][0], modelview[1][0], modelview[2][0]]
    up = [modelview[0][1], modelview[1][1], modelview[2][1]]

    # Вычисляем соотношение сторон текстуры
    aspect_ratio = w / h
    scaled_right = [component * scale * aspect_ratio for component in right]
    scaled_up = [component * scale for component in up]

    # Рисуем текстурный квад
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)  # Нижний левый угол
    glVertex3f(0, 0, 0)
    glTexCoord2f(1, 0)  # Нижний правый угол
    glVertex3f(*scaled_right)
    glTexCoord2f(1, 1)  # Верхний правый угол
    glVertex3f(scaled_right[0] + scaled_up[0],
               scaled_right[1] + scaled_up[1],
               scaled_right[2] + scaled_up[2])
    glTexCoord2f(0, 1)  # Верхний левый угол
    glVertex3f(*scaled_up)
    glEnd()

    # Восстанавливаем матрицу
    glPopMatrix()

    # Отключаем текстурирование и блэндинг
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

def draw_trolley(trolley):
    """Рисуем упрощённую вагонетку параллельно линии оборудования с вращающимися колёсами."""
    position = trolley.get_position()
    x, y, z = position

    # Получаем направление движения для ориентации
    direction = trolley.get_direction_vector()

    # Вычисляем угол поворота на основе направления
    angle = math.degrees(math.atan2(direction[0], direction[2]))  # atan2(X, Z)

    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-angle, 0, 1, 0)  # Поворачиваем вагонетку вдоль линии

    # Устанавливаем цвет вагоночки
    glColor3f(0.7, 0.7, 0.7)  # Серый цвет

    # Рисуем основной прямоугольный блок
    glBegin(GL_QUADS)
    # Передняя грань
    glVertex3f(-0.5, 0.0, -0.2)
    glVertex3f(0.5, 0.0, -0.2)
    glVertex3f(0.5, 0.0, 0.2)
    glVertex3f(-0.5, 0.0, 0.2)
    # Задняя грань
    glVertex3f(-0.5, -0.2, -0.2)
    glVertex3f(0.5, -0.2, -0.2)
    glVertex3f(0.5, -0.2, 0.2)
    glVertex3f(-0.5, -0.2, 0.2)
    # Боковые грани
    glVertex3f(-0.5, 0.0, -0.2)
    glVertex3f(0.5, 0.0, -0.2)
    glVertex3f(0.5, -0.2, -0.2)
    glVertex3f(-0.5, -0.2, -0.2)

    glVertex3f(0.5, 0.0, -0.2)
    glVertex3f(0.5, 0.0, 0.2)
    glVertex3f(0.5, -0.2, 0.2)
    glVertex3f(0.5, -0.2, -0.2)

    glVertex3f(0.5, 0.0, 0.2)
    glVertex3f(-0.5, 0.0, 0.2)
    glVertex3f(-0.5, -0.2, 0.2)
    glVertex3f(0.5, -0.2, 0.2)

    glVertex3f(-0.5, 0.0, 0.2)
    glVertex3f(-0.5, 0.0, -0.2)
    glVertex3f(-0.5, -0.2, -0.2)
    glVertex3f(-0.5, -0.2, 0.2)
    glEnd()

    # Рисуем колёса как цилиндры
    wheel_radius = 0.05
    wheel_length = 0.1
    glColor3f(0, 0, 0)  # Черный цвет колёс

    # Позиции колёс относительно центра вагонетки
    wheel_offsets = [
        (-0.3, -0.2, -0.3),
        (0.3, -0.2, -0.3),
        (-0.3, -0.2, 0.3),
        (0.3, -0.2, 0.3)
    ]

    for offset in wheel_offsets:
        glPushMatrix()
        glTranslatef(*offset)
        glRotatef(90, 1, 0, 0)  # Вращаем цилиндр, чтобы ось была по X
        glRotatef(trolley.wheel_rotation, 0, 0, 1)  # Вращение колеса для анимации
        gluCylinder(quadric, wheel_radius, wheel_radius, wheel_length, 12, 1)
        glPopMatrix()

    glPopMatrix()

def draw_mine_axes():
    """Рисуем шахтные оси как линии."""
    glLineWidth(3.0)
    glBegin(GL_LINES)
    for ax in config.axes_list:
        status = ax['status']
        if status == 1:
            glColor3f(1, 0, 0)  # Красный
        elif status == 2:
            glColor3f(0, 1, 0)  # Зеленый
        elif status == 3:
            glColor3f(0, 0, 1)  # Синий
        else:
            glColor3f(0.8, 0.8, 0.8)  # Серый
        glVertex3f(ax['xs'], ax['ys'], ax['zs'])
        glVertex3f(ax['xf'], ax['yf'], ax['zf'])
    glEnd()
    glLineWidth(1.0)

def draw_dashed_line(start, end, dash_length=0.5, gap_length=0.5):
    """Рисует пунктирную линию между двумя точками."""
    # Расчёт расстояния между точками
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    # Нормализация вектора направления
    if distance == 0:
        return
    dx /= distance
    dy /= distance
    dz /= distance

    # Инициализация переменных
    current_distance = 0.0
    drawing = True  # Начинаем с рисования штриха

    while current_distance < distance:
        if drawing:
            # Определяем конец штриха
            segment_length = min(dash_length, distance - current_distance)
            glBegin(GL_LINES)
            glVertex3f(start[0] + dx * current_distance,
                       start[1] + dy * current_distance,
                       start[2] + dz * current_distance)
            glVertex3f(start[0] + dx * (current_distance + segment_length),
                       start[1] + dy * (current_distance + segment_length),
                       start[2] + dz * (current_distance + segment_length))
            glEnd()

        # Обновляем текущее расстояние
        current_distance += dash_length if drawing else gap_length
        # Переключаем режим рисования
        drawing = not drawing

# renderer_3d.py

def draw_equipment():
    """Рисуем оборудование как пунктирные линии с сферами и названиями."""
    glLineWidth(2.0)

    camera_pos = (config.camera_x, config.camera_y, config.camera_z)

    for eq in config.equipment_list:
        # Установка цвета в зависимости от статуса оборудования
        if eq['eq_status'] == 1:
            glColor3f(1, 0.5, 0.5)  # Светло-красный
        elif eq['eq_status'] == 2:
            glColor3f(0.5, 1, 0.5)  # Светло-зеленый
        else:
            glColor3f(0.8, 0.8, 0.8)  # Серый

        start = (eq['xs'], eq['ys'], eq['zs'])
        end = (eq['xf'], eq['yf'], eq['zf'])

        screen_pos = utils.project_3d_to_2d(start)
        text = eq['eq_name']
        if screen_pos:
            config.labels_to_draw.append((text, screen_pos[0], screen_pos[1]))

        # Отрисовка пунктирной линии
        draw_dashed_line(start, end, dash_length=config.EQUIPMENT_DASH_LENGTH, gap_length=config.EQUIPMENT_GAP_LENGTH)

        # Отрисовка сферы в начале линии
        glPushMatrix()
        glTranslatef(*start)
        gluSphere(quadric, 0.2, 16, 16)  # Сфера с радиусом 0.2
        glPopMatrix()

        # Вычисление расстояния до камеры
        distance = math.sqrt(
            (start[0] - camera_pos[0]) ** 2 +
            (start[1] - camera_pos[1]) ** 2 +
            (start[2] - camera_pos[2]) ** 2
        )

        # Определение масштаба текста на основе расстояния
        # Чем дальше, тем меньше масштаб, но не ниже min_scale
        min_scale = 0.5  # Минимальный масштаб
        max_scale = 1.0  # Максимальный масштаб
        max_distance = 50.0  # Расстояние, при котором текст будет минимального размера
        scale = max_scale - (distance / max_distance) * (max_scale - min_scale)
        scale = max(min_scale, min(scale, max_scale))  # Ограничиваем масштаб

        # Отрисовка названия оборудования
        draw_text_3d(eq['eq_name'], start, scale=0.5, color=(255, 255, 0))

    glLineWidth(1.0)


def draw_work_places():
    """Рисуем рабочие места."""
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for work in config.works_list:
        glColor3f(1, 1, 0)  # Желтый
        glVertex3f(work['xs'], work['ys'], work['zs'])
    glEnd()
    glPointSize(1.0)

def draw_floor():
    """Рисуем сеточную плоскость (пол)."""
    grid_size = 50  # Количество линий в каждой плоскости
    grid_spacing = 1.0  # Расстояние между линиями

    glColor3f(0.5, 0.5, 0.5)  # Серый цвет сетки
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(-grid_size, grid_size + 1):
        # Линии вдоль X
        glVertex3f(-grid_size * grid_spacing, 0, i * grid_spacing)
        glVertex3f(grid_size * grid_spacing, 0, i * grid_spacing)
        # Линии вдоль Z
        glVertex3f(i * grid_spacing, 0, -grid_size * grid_spacing)
        glVertex3f(i * grid_spacing, 0, grid_size * grid_spacing)
    glEnd()

def draw_mine():
    """Главная функция рендеринга шахты."""
    draw_floor()
    draw_mine_axes()
    draw_equipment()
    draw_work_places()

    # Рисуем все вагонетки
    for trolley in config.trolleys_list:
        draw_trolley(trolley)
