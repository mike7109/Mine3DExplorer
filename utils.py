# utils.py

from OpenGL.GL import *
from OpenGL.GLU import *
import config

def set_perspective(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height), 0.1, 1000.0)  # Увеличено значение far до 1000.0
    glMatrixMode(GL_MODELVIEW)

def project_3d_to_2d(position):
    """Преобразует 3D координаты в 2D экранные."""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    winX, winY, winZ = gluProject(position[0], position[1], position[2],
                                 modelview, projection, viewport)
    # Инвертируем Y, так как Pygame использует (0,0) в верхнем левом углу
    screen_x = winX
    screen_y = viewport[3] - winY
    return screen_x, screen_y
