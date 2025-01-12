# utils.py

from OpenGL.GL import *
from OpenGL.GLU import *

import config

def set_perspective(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height), 0.1, 1000.0)  # Увеличено значение far до 1000.0
    glMatrixMode(GL_MODELVIEW)
