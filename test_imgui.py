import dearpygui.dearpygui as dpg
import os
import ctypes


def apply_settings(sender, app_data):
    print("Настройки применены")


def toggle_menus(sender, app_data):
    # Получение текущего состояния видимости левого меню
    left_visible = dpg.get_item_configuration("left_menu")["show"]
    # Переключение видимости левого меню
    dpg.configure_item("left_menu", show=not left_visible)

    # Получение текущего состояния видимости правого меню
    right_visible = dpg.get_item_configuration("right_menu")["show"]
    # Переключение видимости правого меню
    dpg.configure_item("right_menu", show=not right_visible)

    if not left_visible:
        # Получение размеров viewport для правильного позиционирования
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()

        # Установка позиции левого меню (слева)
        dpg.configure_item("left_menu", pos=(0, 0))

        # Установка позиции правого меню (справа)
        menu_width = 300  # Ширина меню
        pos_x = viewport_width - menu_width
        pos_y = 0
        dpg.configure_item("right_menu", pos=(pos_x, pos_y))
    else:
        # При закрытии меню можно оставить их позиции по умолчанию
        pass


def main():
    dpg.create_context()

    # Получение абсолютного пути к шрифту
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, "freesans.ttf")  # Убедитесь, что этот файл существует

    if not os.path.exists(font_path):
        print(f"Файл шрифта не найден: {font_path}")
        print("Убедитесь, что файл freesans.ttf находится в той же директории, что и скрипт.")
        return

    # Регистрация шрифта с поддержкой кириллицы
    with dpg.font_registry():
        with dpg.font(font_path, 20) as default_font:
            # Используем предопределённые диапазоны глифов для кириллицы
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.bind_font(default_font)

    # Основное окно
    with dpg.window(label="Тестовое окно", width=400, height=300):
        dpg.add_text("Привет, мир!")
        dpg.add_text("Это тест кириллического текста: Привет, как дела?")
        dpg.add_input_text(label="Введите текст", default_value="", width=300)
        dpg.add_button(label="Нажми меня", callback=apply_settings)

    # Левое меню, изначально скрытое
    with dpg.window(tag="left_menu", label="Левое меню", width=300, height=600, pos=(0, 0), show=False,
                    no_title_bar=True):
        dpg.add_text("Это левое меню")
        dpg.add_separator()
        dpg.add_button(label="Закрыть", callback=lambda: dpg.configure_item("left_menu", show=False))
        # Добавьте здесь дополнительные элементы управления по необходимости

    # Правое меню, изначально скрытое
    with dpg.window(tag="right_menu", label="Правое меню", width=300, height=600, pos=(900, 0), show=False,
                    no_title_bar=True):
        dpg.add_text("Это правое меню")
        dpg.add_separator()
        dpg.add_button(label="Закрыть", callback=lambda: dpg.configure_item("right_menu", show=False))
        # Добавьте здесь дополнительные элементы управления по необходимости

    # Обработчик нажатия клавиши 'M'
    with dpg.handler_registry():
        dpg.add_key_down_handler(key=dpg.mvKey_M, callback=toggle_menus)

    # Создание и настройка viewport
    dpg.create_viewport(title='Dear PyGui - Тест кириллицы и меню', width=1200, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
