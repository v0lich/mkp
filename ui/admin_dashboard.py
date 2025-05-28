from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout,
                           QLineEdit, QDateEdit, QSpinBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QDate
from .common import CustomDialog, setup_button_style, adjust_table_size
from database import TheaterDB

class AdminDashboard(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Кабинет администратора")
        self.db = TheaterDB()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # Контейнер для кнопок
        button_container = QVBoxLayout()
        button_container.setAlignment(Qt.AlignCenter)
        
        # Создаем и стилизуем кнопки
        buttons = [
            ("Открыть заявки актеров", self.view_applications),
            ("Просмотр пользователей", self.view_users),
            ("Создать спектакль", self.create_play),
            ("Список спектаклей", self.view_plays),
            ("Выход", self.logout)
        ]
        
        for text, handler in buttons:
            button = QPushButton(text)
            setup_button_style(button)
            button.clicked.connect(handler)
            button_container.addWidget(button)

        main_layout.addLayout(button_container)

    def view_users(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Все пользователи")

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Логин", "Статус", "Почта", "Телефон", "ФИО"])
        
        # Получаем пользователей из базы данных
        users = self.db.get_all_users()
        table.setRowCount(len(users))

        for row, user in enumerate(users):
            table.setItem(row, 0, QTableWidgetItem(user[0]))  # username
            table.setItem(row, 1, QTableWidgetItem(user[2]))  # role
            table.setItem(row, 2, QTableWidgetItem(user[3]))  # email
            table.setItem(row, 3, QTableWidgetItem(user[4]))  # phone
            table.setItem(row, 4, QTableWidgetItem(user[5] or ""))  # fio

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 150)

        # Добавляем кнопку удаления
        delete_button = QPushButton("Удалить пользователя")
        setup_button_style(delete_button)
        delete_button.clicked.connect(lambda: self.delete_user(table))

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(delete_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def delete_user(self, table):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return

        username = table.item(selected_row, 0).text()
        
        # Проверяем, не пытается ли админ удалить сам себя
        if username == "admin":
            QMessageBox.warning(self, "Ошибка", "Невозможно удалить администратора")
            return

        reply = QMessageBox.question(self, "Подтверждение", 
                                   f"Вы уверены, что хотите удалить пользователя {username}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.db.delete_user(username):
                table.removeRow(selected_row)
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить пользователя")

    def view_applications(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Заявки актеров")

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ФИО", "Дата рождения", "Достижения", "Спектакли", 
            "Стаж работы", "Почта", "Телефон", "Логин"
        ])

        # Получаем заявки из базы данных
        applications = self.db.get_actor_applications()
        table.setRowCount(len(applications))

        for row, actor in enumerate(applications):
            table.setItem(row, 0, QTableWidgetItem(actor[1]))  # ФИО
            table.setItem(row, 1, QTableWidgetItem(actor[2]))  # Дата рождения
            table.setItem(row, 2, QTableWidgetItem(actor[3]))  # Достижения
            table.setItem(row, 3, QTableWidgetItem(actor[4]))  # Спектакли
            table.setItem(row, 4, QTableWidgetItem(actor[5]))  # Стаж работы
            table.setItem(row, 5, QTableWidgetItem(actor[6]))  # Почта
            table.setItem(row, 6, QTableWidgetItem(actor[7]))  # Телефон
            table.setItem(row, 7, QTableWidgetItem(actor[8]))  # Логин

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 150)

        button_layout = QHBoxLayout()
        confirm_button = QPushButton("Подтвердить заявку")
        reject_button = QPushButton("Отклонить заявку")
        
        confirm_button.clicked.connect(lambda: self.process_application(table, True))
        reject_button.clicked.connect(lambda: self.process_application(table, False))
        
        setup_button_style(confirm_button)
        setup_button_style(reject_button)
        
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(reject_button)

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addLayout(button_layout)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def process_application(self, table, is_approved):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку для обработки.")
            return

        login = table.item(selected_row, 7).text()  # Получаем логин из таблицы
        
        if is_approved:
            if self.db.approve_application(login):
                QMessageBox.information(self, "Успех", "Заявка подтверждена.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось подтвердить заявку.")
        else:
            if self.db.reject_application(login):
                QMessageBox.information(self, "Отклонено", "Заявка отклонена.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось отклонить заявку.")

        table.removeRow(selected_row)

    def create_play(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Создание спектакля")

        form_layout = QFormLayout()

        self.play_name_input = QLineEdit()
        
        # Используем QDateEdit для даты
        self.play_date_input = QDateEdit()
        self.play_date_input.setCalendarPopup(True)
        self.play_date_input.setDisplayFormat("dd.MM.yyyy")
        
        self.play_actors_input = QSpinBox()
        self.play_budget_input = QSpinBox()  # Числовое поле для бюджета
        self.play_budget_input.setMaximum(1000000000)
        self.play_budget_input.setSuffix(" руб.")

        form_layout.addRow("Наименование спектакля:", self.play_name_input)
        form_layout.addRow("Дата спектакля:", self.play_date_input)
        form_layout.addRow("Количество актеров:", self.play_actors_input)
        form_layout.addRow("Бюджет:", self.play_budget_input)

        create_button = QPushButton("Создать спектакль")
        create_button.clicked.connect(self.save_play)
        setup_button_style(create_button)

        dialog.main_layout.addLayout(form_layout)
        dialog.main_layout.addWidget(create_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def save_play(self):
        play_data = {
            "Наименование": self.play_name_input.text(),
            "Дата": self.play_date_input.text(),
            "Количество актеров": self.play_actors_input.value(),
            "Бюджет": self.play_budget_input.value()
        }
        
        try:
            # Добавляем спектакль в базу данных
            self.db.add_play(play_data)
            QMessageBox.information(self, "Успех", "Спектакль успешно создан!")
            
            # Очищаем поля
            self.play_name_input.clear()
            self.play_date_input.setDate(QDate.currentDate())
            self.play_actors_input.setValue(0)
            self.play_budget_input.setValue(0)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать спектакль: {str(e)}")

    def view_plays(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Список спектаклей")

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Наименование", "Дата", "Количество актеров", "Бюджет"
        ])
        
        # Получаем спектакли из базы данных
        plays = self.db.get_all_plays()
        table.setRowCount(len(plays))

        for row, play in enumerate(plays):
            table.setItem(row, 0, QTableWidgetItem(play[1]))  # name
            table.setItem(row, 1, QTableWidgetItem(play[2]))  # date
            table.setItem(row, 2, QTableWidgetItem(str(play[3])))  # actors_count
            table.setItem(row, 3, QTableWidgetItem(str(play[4])))  # budget

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 150)

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def logout(self):
        self.main_window.show_login_page() 