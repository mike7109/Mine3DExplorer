from OpenGL.GL import *
from OpenGL.GLU import *
import time
import config

def set_perspective(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width/float(height), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

def project_3d_to_2d(position):
    """Проецируем 3D -> 2D (экрана). Возвращаем (x, y)."""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    winX, winY, winZ = gluProject(position[0], position[1], position[2],
                                  modelview, projection, viewport)
    screen_x = winX
    screen_y = viewport[3] - winY
    return (screen_x, screen_y)

def make_screenshot_filename():
    return f"screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"