# main_tkinter.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import threading

import config
import data_loader
import main_pygame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Главное окно приложения")
        self.geometry("1024x768")

        style = ttk.Style(self)
        style.theme_use("clam")  # попробуйте 'vista' или другое, зависит от ОС
        style.configure("Treeview", font=("Arial", 10), rowheight=22)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("TLabelFrame", background="#F0F0F0")

        # Загрузка данных
        data_loader.load_mine_axes("mine_axes.csv")
        data_loader.load_equipment("equipment.csv")
        data_loader.load_works("works.csv")
        data_loader.load_axis_works("axis_works.csv")

        # Флаг, запущена ли 3D-сцена
        self.pygame_running = False

        # Создаём меню
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Выход", command=self.on_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Инструменты"
        tools_menu = tk.Menu(menubar, tearoff=False)
        tools_menu.add_command(label="Отобразить 3D модель", command=self.toggle_pygame_3d)
        tools_menu.add_command(label="Назначение нарядов", command=self.show_manage_axes)
        tools_menu.add_command(label="Создание нарядов", command=self.show_create_work)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        # =========== Область контента (куда будем добавлять фреймы) ===========
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)

        # Создаём два фрейма (может быть больше), пока скрыты
        self.manage_axes_frame = ManageAxesFrame(self.content_frame)
        self.create_work_frame = CreateWorkFrame(self.content_frame)

        # По умолчанию покажем "Управление выработками"
        self.show_manage_axes()

    def on_exit(self):
        """Обработчик пункта меню 'Выход'."""
        self.destroy()
        sys.exit(0)

    def toggle_pygame_3d(self):
        if not config.pygame_running:
            # Запускаем
            t = threading.Thread(target=main_pygame.main, daemon=True)
            t.start()
        else:
            messagebox.showinfo("Информация", "3D модель уже запущена!")

    def show_manage_axes(self):
        """Показать фрейм управления выработками."""
        self.hide_all_frames()
        self.manage_axes_frame.pack(fill="both", expand=True)

    def show_create_work(self):
        """Показать фрейм создания/редактирования работ."""
        self.hide_all_frames()
        self.create_work_frame.pack(fill="both", expand=True)

    def hide_all_frames(self):
        """Скрыть все фреймы."""
        self.manage_axes_frame.pack_forget()
        self.create_work_frame.pack_forget()

    def show_about(self):
        messagebox.showinfo("О программе", "Версия 1.0\nСоздал Михаил!")

class ManageAxesFrame(ttk.Frame):
    """Фрейм со списком выработок и чекбоксами доступных работ."""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Две колонки: слева список выработок, справа - работы
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)  # Основная область
        self.rowconfigure(1, weight=0)  # Нижняя часть не растягивается

        # ЛЕВАЯ ЧАСТЬ - список выработок
        left_frame = ttk.LabelFrame(self, text="Список выработок", padding=5)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.axes_listbox = tk.Listbox(left_frame, font=("Arial", 10))
        self.axes_listbox.pack(fill="both", expand=True)
        self.axes_listbox.bind("<<ListboxSelect>>", self.on_axis_select)

        # Заполняем Listbox
        for axis in config.axes_list:
            self.axes_listbox.insert(tk.END, axis.full_name)

        # ПРАВАЯ ЧАСТЬ - чекбоксы для работ
        right_frame = ttk.LabelFrame(self, text="Работы на выработке", padding=5)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Прокручиваемая область для чекбоксов
        self.canvas = tk.Canvas(right_frame, bg="#F8F8F8", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.works_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.works_frame, anchor="nw")

        self.works_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.current_checkvars = []

        # Нижняя часть: bottom_frame
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)  # Изменён sticky и добавлены отступы

        # Ограничим максимальную ширину нижней части (опционально)
        bottom_frame.columnconfigure(0, weight=1)

        # Разделим bottom_frame на 2 строки
        bottom_frame.rowconfigure(0, weight=0)  # строка для лейбла
        bottom_frame.rowconfigure(1, weight=1)  # строка для таблицы
        bottom_frame.columnconfigure(0, weight=1)

        # 1) Лейбл "Общий риск" в row=0
        self.lbl_total_risk = ttk.Label(
            bottom_frame,
            text="Общий риск по шахте: 0.00%",
            font=("Arial", 11, "bold")
        )
        self.lbl_total_risk.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # 2) Фрейм для таблицы со скроллбаром (row=1)
        table_frame = ttk.Frame(bottom_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")

        # Настроим, чтобы table_frame растягивался
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Горизонтальный/вертикальный скроллбар (если нужно, хотя в примере только вертикальный)
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky="ns")

        # TreeView в column=0
        self.tree = ttk.Treeview(
            table_frame,
            columns=("axis", "works", "risk"),
            show="headings",
            yscrollcommand=vsb.set
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb.config(command=self.tree.yview)

        # Настраиваем заголовки и ширину столбцов
        self.tree.heading("axis", text="Выработка")
        self.tree.heading("works", text="Активные работы")
        self.tree.heading("risk", text="Сумм. риск (%)")
        self.tree.column("axis", width=120, anchor="w")
        self.tree.column("works", width=300, anchor="w")
        self.tree.column("risk", width=100, anchor="e")

        # Вызовем обновление, чтобы таблица и лейбл сразу заполнились
        self.update_summary_table()

    def on_axis_select(self, event):
        # При выборе выработки в списке, показать её работы
        for child in self.works_frame.winfo_children():
            child.destroy()
        self.current_checkvars.clear()

        sel = self.axes_listbox.curselection()
        if not sel:
            return
        idx = sel[0]

        axis = config.axes_list[idx]
        config.selected_axis = axis

        # Заголовок
        title_label = ttk.Label(self.works_frame, text=f"Выработка: {axis.full_name}", font=("Arial", 11, "bold"))
        title_label.pack(pady=(0,5), anchor="w")

        # Чекбоксы по работам
        for work_obj in axis.works:
            import tkinter as tki
            var = tki.BooleanVar(value=(work_obj in axis.active_works))
            chk = ttk.Checkbutton(
                self.works_frame,
                text=f"{work_obj.work_name} (код {work_obj.work_code})",
                variable=var,
                command=lambda w=work_obj, v=var: self.toggle_work(axis, w, v)
            )
            chk.pack(anchor="w", pady=2)
            self.current_checkvars.append(var)

        self.works_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.update_summary_table()

    def toggle_work(self, axis, work_obj, bool_var):
        if bool_var.get():
            axis.enable_work(work_obj)
            config.selected_work = work_obj
        else:
            axis.disable_work(work_obj)
            if config.selected_work == work_obj:
                config.selected_work = None

        # Обновляем таблицу статистики
        self.update_summary_table()

    def update_summary_table(self):
        """Обновить таблицу (TreeView) и общий риск."""
        # Очистка предыдущих строк
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        # Заполняем заново
        from utils import combined_risk_for_entire_mine, combined_risk
        import config

        for ax in config.axes_list:
            if ax.active_works:
                works_str = ", ".join(w.work_name for w in ax.active_works)
                risk_val = combined_risk(ax.active_works)
                risk_percent = f"{risk_val * 100:.2f}"
            else:
                works_str = "-"
                risk_percent = "0.00"
            self.tree.insert("", "end", values=(ax.full_name, works_str, risk_percent))

        # Считаем общий риск
        total_risk = combined_risk_for_entire_mine()
        self.lbl_total_risk.config(text=f"Общий риск по всей шахте: {total_risk * 100:.2f}%")


class CreateWorkFrame(ttk.Frame):
    """Фрейм для создания/редактирования новой работы."""
    def __init__(self, parent):
        super().__init__(parent)
        lbl = ttk.Label(self, text="Здесь можно создать или настроить работу", font=("Arial", 11))
        lbl.pack(pady=20)

        # Тут вы добавите свои поля ввода:
        # entry для имени работы, кода, риска и т.д.

def main():
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
