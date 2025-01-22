import tkinter as tk
from tkinter import ttk
import config

class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        config.settings_window = self
        self.title("Управление выработками и работами")
        self.geometry("700x400")  # Пример фиксированного размера окна (можно убрать)

        # Выбираем тему
        style = ttk.Style(self)
        style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative' (зависит от ОС)

        # Можно немного подкрутить стили цветов:
        style.configure("TFrame", background="#F0F0F0")
        style.configure("TLabel", background="#F0F0F0", font=("Arial", 11))
        style.configure("TCheckbutton", background="#F0F0F0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))

        # Главный фрейм
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Разделим окно на две области: слева выработки, справа работы
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # -- Секция слева --
        left_frame = ttk.LabelFrame(main_frame, text="Список выработок", padding=5)
        left_frame.pack(side="left", fill="both", expand=True)

        self.axes_listbox = tk.Listbox(left_frame, font=("Arial", 10), height=15)
        self.axes_listbox.pack(fill="both", expand=True)
        self.axes_listbox.bind("<<ListboxSelect>>", self.on_axis_select)

        for axis in config.axes_list:
            self.axes_listbox.insert(tk.END, axis.name)

        # -- Секция справа --
        right_frame = ttk.LabelFrame(main_frame, text="Доступные работы", padding=5)
        right_frame.pack(side="right", fill="both", expand=True)

        # Скроллбар для фрейма с чекбоксами, если работ много
        self.canvas = tk.Canvas(right_frame, bg="#F8F8F8", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Внутренний фрейм для чекбоксов
        self.works_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.works_frame, anchor="nw")

        self.works_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.current_checkvars = []

    def on_axis_select(self, event):
        """Когда выбираем выработку, отображаем набор ее работ."""
        for child in self.works_frame.winfo_children():
            child.destroy()
        self.current_checkvars.clear()

        sel = self.axes_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        axis = config.axes_list[idx]

        config.selected_axis = axis

        # Подпись с названием текущей выработки (опционально)
        label_text = f"Выработки: {axis.name}"
        title_label = ttk.Label(self.works_frame, text=label_text, font=("Arial", 11, "bold"))
        title_label.pack(pady=(0,5), anchor="w")

        # Для каждой потенциальной работы (axis.works) — чекбокс
        for work_obj in axis.works:
            var = tk.BooleanVar(value=(work_obj in axis.active_works))
            chk = ttk.Checkbutton(
                self.works_frame,
                text=f"{work_obj.work_name} (код {work_obj.work_code})",
                variable=var,
                command=lambda w=work_obj, v=var: self.toggle_work(axis, w, v)
            )
            chk.pack(anchor="w", pady=2)
            self.current_checkvars.append(var)

        # Обновим canvas на случай, если чекбоксов много
        self.works_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def toggle_work(self, axis, work_obj, bool_var):
        """Включаем или отключаем работу у текущей выработки."""
        if bool_var.get():
            axis.enable_work(work_obj)
            config.selected_work = work_obj
        else:
            axis.disable_work(work_obj)
            if config.selected_work == work_obj:
                config.selected_work = None

    def select_axis_by_name(self, axis_name):
        """Программно выделить выработку в Listbox по имени."""
        # Снимем предыдущий выбор:
        self.axes_listbox.selection_clear(0, tk.END)
        # Найдём индекс
        items = self.axes_listbox.get(0, tk.END)
        for i, item in enumerate(items):
            if item == axis_name:
                self.axes_listbox.selection_set(i)
                self.axes_listbox.activate(i)
                self.axes_listbox.see(i)
                # Вручную вызовем on_axis_select, имитируя пользовательский клик
                self.on_axis_select(None)
                break


def run_settings_window():
    win = SettingsWindow()
    win.mainloop()
