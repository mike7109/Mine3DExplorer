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

def combined_risk_for_entire_mine():
    """
    Считает суммарный риск по ВСЕЙ шахте, учитывая каждое
    активное включение работы (даже если одна и та же работа
    включена на нескольких выработках, это считается несколько раз).
    Формула: P = 1 - П(1 - p_i).
    """
    import config

    # Собираем все включённые работы в общий список (не set!)
    all_works_list = []
    for ax in config.axes_list:
        # Добавляем все работы, которые активны на этой оси
        all_works_list.extend(ax.active_works)

    if not all_works_list:
        return 0.0  # если нет работ, риск 0

    product = 1.0
    for w in all_works_list:
        product *= (1.0 - w.ud_risk)

    return 1.0 - product

def combined_risk(work_set):
    # Формула: P = 1 - Π(1 - p_i)
    product = 1.0
    for w in work_set:
        product *= (1.0 - w.ud_risk)
    return 1.0 - product
