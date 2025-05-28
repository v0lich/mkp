import PyInstaller.__main__
import os

# Получаем текущую директорию
current_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к иконке (если есть)
# icon_path = os.path.join(current_dir, 'icon.ico')

PyInstaller.__main__.run([
    'main.py',  # основной файл приложения
    '--name=TheaterSystem',  # имя выходного файла
    '--onefile',  # создать один exe-файл
    '--windowed',  # не показывать консоль
    # f'--icon={icon_path}',  # путь к иконке (раскомментируйте, если есть иконка)
    '--add-data=theater.db;.',  # добавить базу данных
    '--clean',  # очистить кэш перед сборкой
    '--noconfirm',  # не спрашивать подтверждения
]) 