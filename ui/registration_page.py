from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                           QTextEdit, QDateEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp
from .common import setup_button_style
from database import TheaterDB

class RegistrationPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = TheaterDB()

        # Основной layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Создаем форму
        form_layout = QFormLayout()
        
        # Создаем поля ввода
        self.input_fio = QLineEdit()
        self.input_fio.setPlaceholderText("Введите ФИО (только буквы) *")
        # Устанавливаем валидатор для ввода только букв и пробелов
        rx = QRegExp("[А-Яа-яA-Za-z\\s-]+")
        self.input_fio.setValidator(QRegExpValidator(rx))

        self.input_birthdate = QDateEdit()
        self.input_birthdate.setCalendarPopup(True)
        self.input_birthdate.setDisplayFormat("dd.MM.yyyy")
        
        self.input_achievements = QTextEdit()
        self.input_achievements.setPlaceholderText("Введите ваши звания и награды *")
        self.input_achievements.setMaximumHeight(100)
        self.input_achievements.setStyleSheet("QTextEdit { background-color: white; }")
        
        self.input_plays = QTextEdit()
        self.input_plays.setPlaceholderText("Перечислите отыгранные спектакли *")
        self.input_plays.setMaximumHeight(100)
        self.input_plays.setStyleSheet("QTextEdit { background-color: white; }")
        
        self.input_experience = QLineEdit()
        self.input_experience.setPlaceholderText("Укажите стаж работы (только цифры) *")
        # Устанавливаем валидатор для ввода только цифр
        self.input_experience.setValidator(QIntValidator())

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email *")

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Введите номер телефона (только цифры) *")
        # Устанавливаем валидатор для ввода только цифр
        self.input_phone.setValidator(QIntValidator())

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Придумайте логин *")

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Придумайте пароль *")

        # Добавляем поля в форму
        form_layout.addRow("ФИО:", self.input_fio)
        form_layout.addRow("Дата рождения:", self.input_birthdate)
        form_layout.addRow("Достижения:", self.input_achievements)
        form_layout.addRow("Спектакли:", self.input_plays)
        form_layout.addRow("Стаж работы:", self.input_experience)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Телефон:", self.input_phone)
        form_layout.addRow("Логин:", self.input_login)
        form_layout.addRow("Пароль:", self.input_password)

        # Кнопки
        button_layout = QVBoxLayout()
        
        self.submit_button = QPushButton("Отправить заявку")
        self.submit_button.clicked.connect(self.submit_application)
        setup_button_style(self.submit_button)
        
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        setup_button_style(self.back_button)
        
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.back_button)

        # Собираем все вместе
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def submit_application(self):
        # Получаем данные из полей
        application_data = {
            "ФИО": self.input_fio.text().strip(),
            "Дата рождения": self.input_birthdate.text(),
            "Достижения": self.input_achievements.toPlainText().strip(),
            "Спектакли": self.input_plays.toPlainText().strip(),
            "Стаж работы": self.input_experience.text().strip(),
            "Почта": self.input_email.text().strip(),
            "Телефон": self.input_phone.text().strip(),
            "Логин": self.input_login.text().strip(),
            "Пароль": self.input_password.text().strip()
        }

        # Проверяем заполнение всех полей
        empty_fields = [field for field, value in application_data.items() if not value]
        if empty_fields:
            QMessageBox.warning(self, "Ошибка", f"Пожалуйста, заполните следующие обязательные поля:\n{', '.join(empty_fields)}")
            return

        try:
            # Проверяем существование логина
            if self.db.check_login_exists(application_data["Логин"]):
                QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
                return

            # Добавляем заявку в базу данных
            self.db.add_actor_application(application_data)
            QMessageBox.information(self, "Успех", "Заявка отправлена администратору на рассмотрение.")
            
            # Очищаем поля формы
            self.input_fio.clear()
            self.input_achievements.clear()
            self.input_plays.clear()
            self.input_experience.clear()
            self.input_email.clear()
            self.input_phone.clear()
            self.input_login.clear()
            self.input_password.clear()
            
            # Возвращаемся на страницу логина
            self.main_window.show_login_page()
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при сохранении заявки: {str(e)}")

    def go_back(self):
        self.main_window.show_login_page() 