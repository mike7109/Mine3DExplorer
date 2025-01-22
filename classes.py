import math

class MineAxis:
    """Класс для выработки (шахтной оси)."""
    def __init__(self, short_name, full_name, status, xs, ys, zs, xf, yf, zf):
        self.short_name = short_name
        self.full_name = full_name
        self.status = status
        self.xs = xs
        self.ys = ys
        self.zs = zs
        self.xf = xf
        self.yf = yf
        self.zf = zf

        self.works = []         # все потенциальные работы
        self.active_works = set()  # включённые пользователем

    def enable_work(self, work_obj):
        self.active_works.add(work_obj)

    def disable_work(self, work_obj):
        if work_obj in self.active_works:
            self.active_works.remove(work_obj)

    def __repr__(self):
        return f"MineAxis(name={self.name}, status={self.status})"


class Equipment:
    """Класс для оборудования."""
    def __init__(self, short_name, full_name, status, line_eq, xs, ys, zs, xf, yf, zf):
        self.short_name = short_name
        self.full_name = full_name
        self.status = status
        self.line_eq = line_eq
        self.xs = xs
        self.ys = ys
        self.zs = zs
        self.xf = xf
        self.yf = yf
        self.zf = zf

    def __repr__(self):
        return f"Equipment(eq_name={self.short_name}, eq_status={self.status})"


class Work:
    """Класс для описания работы."""
    def __init__(self, work_name, work_code, col_work, str_work, ud_risk):
        self.work_name = work_name
        self.work_code = work_code
        self.col_work = col_work
        self.str_work = str_work
        self.ud_risk = ud_risk

    def __repr__(self):
        return f"Work(code={self.work_code}, name={self.work_name})"


class Trolley:
    """Вагонетка, перемещающаяся между двумя точками (xs, ys, zs) и (xf, yf, zf)."""
    def __init__(self, equipment, speed=0.02):
        """
        equipment: объект класса Equipment (или словарь),
                   где лежат поля xs, ys, zs, xf, yf, zf
        speed: скорость движения вагонетки
        """
        self.equipment = equipment
        self.speed = speed
        self.direction = 1  # 1: вперёд, -1: назад
        self.progress = 0.0  # Прогресс от 0.0 до 1.0
        self.wheel_rotation = 0.0

    def update(self):
        """Обновление позиции и вращения колёс."""
        self.progress += self.direction * self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.direction = -1
        elif self.progress <= 0.0:
            self.progress = 0.0
            self.direction = 1

        # Вращение колеса (условно)
        wheel_radius = 0.05
        wheel_circumference = 2 * math.pi * wheel_radius
        self.wheel_rotation += (self.speed / wheel_circumference) * 360
        self.wheel_rotation %= 360

    def get_position(self):
        """Текущая позиция (x, y, z) на линии."""
        start = (self.equipment.xs, self.equipment.ys, self.equipment.zs)
        end = (self.equipment.xf, self.equipment.yf, self.equipment.zf)
        x = start[0] + (end[0] - start[0]) * self.progress
        y = start[1] + (end[1] - start[1]) * self.progress
        z = start[2] + (end[2] - start[2]) * self.progress
        return (x, y, z)

    def get_direction_vector(self):
        """Нормализованный вектор направления движения."""
        start = (self.equipment.xs, self.equipment.ys, self.equipment.zs)
        end = (self.equipment.xf, self.equipment.yf, self.equipment.zf)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length == 0:
            return (0, 0, 1)
        return (dx / length, dy / length, dz / length)

    def set_speed(self, new_speed):
        self.speed = new_speed

    def accelerate(self, delta):
        self.speed += delta
