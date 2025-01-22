import csv
import config
from classes import MineAxis, Equipment, Work, Trolley

def load_mine_axes(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            status = int(row['status'])
            xs = float(row['xs'])
            ys = float(row['ys'])
            zs = float(row['zs'])
            xf = float(row['xf'])
            yf = float(row['yf'])
            zf = float(row['zf'])

            axis_obj = MineAxis(name, status, xs, ys, zs, xf, yf, zf)
            config.axes_list.append(axis_obj)

    print(f"Loaded {len(config.axes_list)} mine axes from {csv_file}")


def load_equipment(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eq_name = row['eq_name']
            eq_status = int(row['eq_status'])
            line_eq = int(row['line_eq'])
            xs = float(row['xs'])
            ys = float(row['ys'])
            zs = float(row['zs'])
            xf = float(row['xf'])
            yf = float(row['yf'])
            zf = float(row['zf'])

            eq_obj = Equipment(eq_name, eq_status, line_eq, xs, ys, zs, xf, yf, zf)
            config.equipment_list.append(eq_obj)

    print(f"Loaded {len(config.equipment_list)} equipment from {csv_file}")

    # Создание вагонеток на основе equipment
    config.trolleys_list.clear()
    for eq in config.equipment_list:
        # Пример: всем вагонеткам даём одинаковую скорость
        trolley = Trolley(eq, speed=0.005)
        config.trolleys_list.append(trolley)
    print(f"Initialized {len(config.trolleys_list)} trolleys.")


def load_works(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wname = row['work_name']
            wcode = int(row['work_code'])
            cw    = int(row['col_work'])
            stw   = int(row['str_work'])
            risk  = float(row['ud_risk'])

            w_obj = Work(wname, wcode, cw, stw, risk)
            config.works_list.append(w_obj)
    print(f"Loaded {len(config.works_list)} works from {csv_file}")


def load_axis_works(csv_file):
    """
    axis_works.csv:
        axis_name, work_code
    Связывает выработку (по имени) и работу (по коду).
    """
    axis_by_name = {ax.name: ax for ax in config.axes_list}
    work_by_code = {w.work_code: w for w in config.works_list}

    linked_count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            axis_name = row['axis_name'].strip()
            wcode = int(row['work_code'])
            if axis_name in axis_by_name and wcode in work_by_code:
                axis_by_name[axis_name].works.append(work_by_code[wcode])
                linked_count += 1
            else:
                print(f"[WARN] Not found axis={axis_name} or work_code={wcode}")

    print(f"Linked {linked_count} (axis-work) pairs from {csv_file}")
