# config.py
import math

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

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

# Флаг полноэкранного режима
fullscreen = False

# Линии для сцены
lines_data = []

# Списки, куда загрузим
axes_list = []       # для mine_axes
equipment_list = []  # для equipment
works_list = []      # для works
labels_to_draw = []

# Добавим переменные для текстур, например:
floor_texture = None  # Текстура для пола (пример)
wall_texture = None   # Если понадобится
