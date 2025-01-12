# renderer_3d.py

import config
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

def draw_equipment():
    """Рисуем оборудование как пунктирные линии."""
    glLineWidth(2.0)
    glEnable(GL_LINE_STIPPLE)  # Включаем штриховку линий

    # Настраиваем паттерн штриховки: 0x00FF - 8 бит штрих, 8 бит пробел
    glLineStipple(1, 0x00FF)  # Плотность и паттерн

    glBegin(GL_LINES)
    for eq in config.equipment_list:
        if eq['eq_status'] == 1:
            glColor3f(1, 0.5, 0.5)  # Светло-красный
        elif eq['eq_status'] == 2:
            glColor3f(0.5, 1, 0.5)  # Светло-зеленый
        else:
            glColor3f(0.8, 0.8, 0.8)  # Серый
        glVertex3f(eq['xs'], eq['ys'], eq['zs'])
        glVertex3f(eq['xf'], eq['yf'], eq['zf'])
    glEnd()

    glDisable(GL_LINE_STIPPLE)  # Выключаем штриховку линий
    glLineWidth(3.0)

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
