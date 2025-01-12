# renderer_3d.py

import config
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_mine_axes():
    """Рисуем все выработки как линии."""
    glLineWidth(3.0)
    glBegin(GL_LINES)
    for ax in config.axes_list:
        st = ax['status']
        # грубое правило для цвета:
        if st == 1:
            glColor3f(1,0,0)
        elif st == 2:
            glColor3f(0,1,0)
        elif st == 3:
            glColor3f(0,0,1)
        elif st == 4:
            glColor3f(1,1,0)
        else:
            glColor3f(0.8, 0.8, 0.8)
        glVertex3f(ax['xs'], ax['ys'], ax['zs'])
        glVertex3f(ax['xf'], ax['yf'], ax['zf'])
    glEnd()
    glLineWidth(1.0)

def draw_equipment():
    """По аналогии рисуем equipment (линии, кубики, ...)."""
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for eq in config.equipment_list:
        # Цвет по eq_status
        if eq['eq_status'] == 1:
            glColor3f(1, 0.5, 0.5)
        elif eq['eq_status'] == 2:
            glColor3f(0.5, 1, 0.5)
        else:
            glColor3f(0.8, 0.8, 0.8)

        glVertex3f(eq['xs'], eq['ys'], eq['zs'])
        glVertex3f(eq['xf'], eq['yf'], eq['zf'])
    glEnd()
    glLineWidth(1.0)
