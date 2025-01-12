# renderer_3d.py

import config
import math
from OpenGL.GL import *
from OpenGL.GLU import *

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


def draw_dashed_line(start, end, dash_length=config.EQUIPMENT_DASH_LENGTH, gap_length=config.EQUIPMENT_GAP_LENGTH):
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

def draw_equipment():
    """Рисуем оборудование как пунктирные линии."""
    glLineWidth(2.0)

    for eq in config.equipment_list:
        if eq['eq_status'] == 1:
            glColor3f(1, 0.5, 0.5)  # Светло-красный
        elif eq['eq_status'] == 2:
            glColor3f(0.5, 1, 0.5)  # Светло-зеленый
        else:
            glColor3f(0.8, 0.8, 0.8)  # Серый

        start = (eq['xs'], eq['ys'], eq['zs'])
        end = (eq['xf'], eq['yf'], eq['zf'])

        # Отрисовка пунктирной линии между start и end
        draw_dashed_line(start, end, dash_length=0.5, gap_length=0.5)

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
