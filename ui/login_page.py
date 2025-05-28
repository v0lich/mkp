from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from .common import setup_button_style
from database import TheaterDB

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = TheaterDB()

        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Создаем контейнер для элементов
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setAlignment(Qt.AlignCenter)

        # Поля для ввода логина и пароля
        self.label_username = QLabel("Имя пользователя:")
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Введите имя пользователя")
        self.input_username.setMaximumWidth(300)

        self.label_password = QLabel("Пароль:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setMaximumWidth(300)

        # Кнопки
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate_user)
        setup_button_style(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.open_registration)
        setup_button_style(self.register_button)

        # Добавляем элементы в layout
        form_layout.addWidget(self.label_username)
        form_layout.addWidget(self.input_username)
        form_layout.addWidget(self.label_password)
        form_layout.addWidget(self.input_password)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.register_button)

        # Добавляем контейнер в основной layout
        layout.addWidget(form_container)
        self.setLayout(layout)

    def authenticate_user(self):
        username = self.input_username.text()
        password = self.input_password.text()

        # Используем метод authenticate_user из базы данных
        user = self.db.authenticate_user(username, password)
        if user:
            username, role = user  # Распаковываем результат
            QMessageBox.information(self, "Успешный вход", f"Добро пожаловать, {username}!")
            
            if role == "админ":
                self.main_window.show_admin_page()
            elif role == "актёр":
                self.main_window.show_actor_page(username)
            elif role == "генеральный директор":
                self.main_window.show_director_page(username)
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неправильное имя пользователя или пароль!")

    def open_registration(self):
        self.main_window.show_registration_page() 