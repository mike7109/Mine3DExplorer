# main_tkinter.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import threading

import config
import data_loader

# (Если нужно запускать/останавливать Pygame)
import main_pygame

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Главное окно приложения")
        self.geometry("1024x768")  # Устанавливаем фиксированный размер

        # Загружаем данные (единожды здесь)
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
        tools_menu.add_command(label="Управление выработками", command=self.show_manage_axes)
        tools_menu.add_command(label="Создание работы", command=self.show_create_work)
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
        """Запуск или остановка Pygame-окна."""
        if not self.pygame_running:
            # Запустим в отдельном потоке
            self.pygame_running = True
            t = threading.Thread(target=main_pygame.main, daemon=True)
            t.start()
        else:
            # Тут зависит от реализации: вы можете отсылать сигнал в Pygame, чтобы он закрывался
            # Например, можно поставить config.running = False, проверять в цикле Pygame
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

        # ЛЕВАЯ ЧАСТЬ - список выработок
        left_frame = ttk.LabelFrame(self, text="Список выработок", padding=5)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.axes_listbox = tk.Listbox(left_frame, font=("Arial", 10))
        self.axes_listbox.pack(fill="both", expand=True)
        self.axes_listbox.bind("<<ListboxSelect>>", self.on_axis_select)

        # Заполняем Listbox
        for axis in config.axes_list:
            self.axes_listbox.insert(tk.END, axis.name)

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
        title_label = ttk.Label(self.works_frame, text=f"Выработка: {axis.name}", font=("Arial", 11, "bold"))
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

    def toggle_work(self, axis, work_obj, bool_var):
        if bool_var.get():
            axis.enable_work(work_obj)
            config.selected_work = work_obj
        else:
            axis.disable_work(work_obj)
            if config.selected_work == work_obj:
                config.selected_work = None

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
