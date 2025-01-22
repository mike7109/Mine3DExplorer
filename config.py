import math

# Параметры окна и камеры
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

camera_x = 0.0
camera_y = 0.0
camera_z = 3.0

camera_yaw = 0.0
camera_pitch = 0.0

MOVE_SPEED = 0.2
MOUSE_SENSITIVITY = 0.1
PITCH_LIMIT = 89.0

right_mouse_held = False
fullscreen = False

# Хранилища данных
axes_list = []       # Список объектов MineAxis
equipment_list = []  # Список объектов Equipment
works_list = []      # Список объектов Work

# Троллей (вагонетки)
trolleys_list = []

# Для хранения текстур (если нужно)
floor_texture = None
wall_texture = None

# Параметры пунктирной линии для оборудования
EQUIPMENT_DASH_LENGTH = 0.5
EQUIPMENT_GAP_LENGTH = 0.5

settings_window = None
selected_axis = None   # Какая выработка сейчас выделена
selected_work = None   # Какая работа "активно" выбрана (последняя включенная)
pygame_running = False  # глобальный флаг
force_close_pygame = False
