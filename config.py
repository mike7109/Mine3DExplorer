# config.py
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Позиция камеры
camera_x = 0.0
camera_y = 0.0
camera_z = 3.0

# Углы поворота (в градусах)
camera_yaw = 0.0
camera_pitch = 0.0

MOVE_SPEED = 0.05
MOUSE_SENSITIVITY = 0.1

# Лимиты pitch
PITCH_LIMIT = 89.0

# Флаг: зажата ли правая кнопка мыши (для вращения)
right_mouse_held = False

# Линии для сцены
lines_data = []


# Списки, куда загрузим
axes_list = []       # для mine_axes
equipment_list = []  # для equipment
works_list = []      # для works