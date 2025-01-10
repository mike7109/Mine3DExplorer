# data_loader.py
import csv
import config

def load_mine_axes(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Преобразуем поля
            name = row['name']
            status = int(row['status'])
            act_work_str = row['act_work']   # строка из 27 символов
            xs = float(row['xs'])
            ys = float(row['ys'])
            zs = float(row['zs'])
            xf = float(row['xf'])
            yf = float(row['yf'])
            zf = float(row['zf'])

            entry = {
                'name': name,
                'status': status,
                'act_work': act_work_str,
                'xs': xs, 'ys': ys, 'zs': zs,
                'xf': xf, 'yf': yf, 'zf': zf
            }
            config.axes_list.append(entry)
    print(f"Loaded {len(config.axes_list)} mine axes from {csv_file}")


def load_equipment(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eq_name   = row['eq_name']
            eq_status = int(row['eq_status'])
            line_eq   = int(row['line_eq'])
            xs = float(row['xs'])
            ys = float(row['ys'])
            zs = float(row['zs'])
            xf = float(row['xf'])
            yf = float(row['yf'])
            zf = float(row['zf'])

            entry = {
                'eq_name':   eq_name,
                'eq_status': eq_status,
                'line_eq':   line_eq,
                'xs': xs, 'ys': ys, 'zs': zs,
                'xf': xf, 'yf': yf, 'zf': zf
            }
            config.equipment_list.append(entry)
    print(f"Loaded {len(config.equipment_list)} equipment from {csv_file}")


def load_works(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wname    = row['work_name']
            wcode    = int(row['work_code'])
            cw       = int(row['col_work'])
            stw      = int(row['str_work'])
            risk     = float(row['ud_risk'])

            entry = {
                'work_name':  wname,
                'work_code':  wcode,
                'col_work':   cw,
                'str_work':   stw,
                'ud_risk':    risk
            }
            config.works_list.append(entry)
    print(f"Loaded {len(config.works_list)} works from {csv_file}")
