# main_tkinter.py
import tkinter as tk
from tkinter import ttk
import threading
import config
import ui_settings
import pygame_runner  # условно: файл, где "main()" Пygame
import sys


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Главное окно приложения")
        self.geometry("1024x768")

        # Создаём меню
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Выход", command=self.on_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Инструменты"
        tools_menu = tk.Menu(menubar, tearoff=False)
        tools_menu.add_command(label="Запустить 3D-модель", command=self.start_3d)
        tools_menu.add_command(label="Управление выработками", command=self.open_axes_settings)
        tools_menu.add_command(label="Создание и настройка работ", command=self.open_work_creation)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        # Можно какой-то виджет в центральной части
        label = ttk.Label(self, text="Добро пожаловать в приложение шахты!", font=("Arial", 14))
        label.pack(pady=50)

    def on_exit(self):
        self.destroy()
        sys.exit(0)

    def start_3d(self):
        """Запуск Pygame-окна в отдельном потоке."""
        # Если хотим, чтобы при нажатии повторно окно не открывалось заново, надо проверять флаг
        t = threading.Thread(target=pygame_runner.run_3d_app, daemon=True)
        t.start()

    def open_axes_settings(self):
        """Открыть окно настроек (если не открыто)."""
        if config.settings_window is not None:
            # Уже открыто, можно .lift() чтобы перенести на передний план
            config.settings_window.lift()
        else:
            ui_settings.run_settings_window()

    def open_work_creation(self):
        """Пример окна для создания/редактирования работ."""
        win = tk.Toplevel(self)
        win.title("Создание и настройка работы")
        win.geometry("600x300")

        lbl = ttk.Label(win, text="Здесь будет функционал создания/редактирования Work")
        lbl.pack(pady=20)

    def show_about(self):
        tk.messagebox.showinfo("О программе", "Версия 1.0. Создал Михаил!")


def main():
    # Предположим, что data_loader мы вызываем здесь, прежде чем всё остальное
    import data_loader
    data_loader.load_mine_axes("mine_axes.csv")
    data_loader.load_equipment("equipment.csv")
    data_loader.load_works("works.csv")
    data_loader.load_axis_works("axis_works.csv")

    # Запускаем главное окно
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
