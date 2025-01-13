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

EQUIPMENT_DASH_LENGTH = 0.5
EQUIPMENT_GAP_LENGTH = 0.5

class Trolley:
    def __init__(self, equipment, speed=0.02):
        """
        equipment: словарь оборудования из equipment_list
        speed: скорость движения вагонетки
        """
        self.equipment = equipment
        self.speed = speed
        self.direction = 1  # 1: вперед, -1: назад
        self.progress = 0.0  # Прогресс по линии от 0.0 до 1.0
        self.wheel_rotation = 0.0  # Угол вращения колёс

    def update(self):
        """Обновление позиции вагонетки и вращения колёс."""
        self.progress += self.direction * self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.direction = -1
        elif self.progress <= 0.0:
            self.progress = 0.0
            self.direction = 1

        # Обновляем вращение колёс
        # Предполагаем, что полный оборот колеса соответствует перемещению на его окружность
        wheel_radius = 0.05  # Радиус колеса
        wheel_circumference = 2 * math.pi * wheel_radius
        self.wheel_rotation += (self.speed / wheel_circumference) * 360
        self.wheel_rotation = self.wheel_rotation % 360

    def get_position(self):
        """Вычисление текущей позиции вагонетки."""
        start = (self.equipment['xs'], self.equipment['ys'], self.equipment['zs'])
        end = (self.equipment['xf'], self.equipment['yf'], self.equipment['zf'])
        x = start[0] + (end[0] - start[0]) * self.progress
        y = start[1] + (end[1] - start[1]) * self.progress
        z = start[2] + (end[2] - start[2]) * self.progress
        return (x, y, z)

    def get_direction_vector(self):
        """Вычисление нормализованного вектора направления движения."""
        start = (self.equipment['xs'], self.equipment['ys'], self.equipment['zs'])
        end = (self.equipment['xf'], self.equipment['yf'], self.equipment['zf'])
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length == 0:
            return (0, 0, 1)  # По умолчанию вперед по оси Z
        return (dx / length, dy / length, dz / length)

    def set_speed(self, new_speed):
        self.speed = new_speed

    def accelerate(self, delta):
        self.speed += delta

# Список всех вагонеток
trolleys_list = []