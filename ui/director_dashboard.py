from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout,
                           QLineEdit, QTextEdit, QSpinBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from .common import CustomDialog, setup_button_style, adjust_table_size
from database import TheaterDB

class DirectorDashboard(QMainWindow):
    def __init__(self, main_window, username):
        super().__init__()
        self.main_window = main_window
        self.username = username
        self.setWindowTitle(f"Кабинет режиссера: {username}")
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
            ("База Актёров", self.view_actors_in_plays),
            ("Просмотр заявок", self.view_applications),
            ("Создать спектакль", self.create_play),
            ("Выход", self.logout)
        ]
        
        for text, handler in buttons:
            button = QPushButton(text)
            setup_button_style(button)
            button.clicked.connect(handler)
            button_container.addWidget(button)

        main_layout.addLayout(button_container)

    def view_actors_in_plays(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("База Актёров")

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Актер", "ФИО", "Спектакль", "Зарплата", "Премия", "Достижения"
        ])
        
        # Получаем контракты из базы данных
        contracts = self.db.get_all_contracts()
        table.setRowCount(len(contracts))

        for row, contract in enumerate(contracts):
            # Получаем информацию об актере
            actor_info = self.db.get_user_info(contract[1])  # contract[1] - username
            actor_name = f"{actor_info[1]} {actor_info[2]}"  # first_name + last_name
            actor_fio = actor_info[5] if actor_info[5] else "Не указано"  # ФИО
            actor_achievements = actor_info[6] if actor_info[6] else "Нет"  # Достижения
            
            table.setItem(row, 0, QTableWidgetItem(actor_name))
            table.setItem(row, 1, QTableWidgetItem(actor_fio))
            table.setItem(row, 2, QTableWidgetItem(contract[7]))  # play_name
            table.setItem(row, 3, QTableWidgetItem(f"{contract[3]} руб."))  # salary
            table.setItem(row, 4, QTableWidgetItem(f"{contract[4]} руб."))  # bonus
            table.setItem(row, 5, QTableWidgetItem(actor_achievements))

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 100)

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def view_applications(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Заявки актеров")

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Актер", "Спектакль", "Дата заявки", "Статус"
        ])
        
        # Получаем заявки из базы данных
        applications = self.db.get_play_applications()
        table.setRowCount(len(applications))

        for row, app in enumerate(applications):
            # Получаем информацию об актере
            actor_info = self.db.get_user_info(app[1])  # app[1] - username
            actor_name = actor_info[5] if actor_info else app[1]  # Используем ФИО из базы данных
            
            # Получаем информацию о спектакле
            play_info = self.db.get_play_by_id(app[2])  # app[2] - play_id
            
            # Создаем элементы таблицы
            actor_item = QTableWidgetItem(actor_name)
            actor_item.setData(Qt.UserRole, app[0])  # Сохраняем ID заявки
            
            table.setItem(row, 0, actor_item)
            table.setItem(row, 1, QTableWidgetItem(play_info[1]))  # play_name
            table.setItem(row, 2, QTableWidgetItem(app[3]))  # application_date
            table.setItem(row, 3, QTableWidgetItem(app[4]))  # status

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 150)

        # Кнопки для обработки заявок
        approve_button = QPushButton("Одобрить заявку")
        reject_button = QPushButton("Отклонить заявку")
        setup_button_style(approve_button)
        setup_button_style(reject_button)
        
        approve_button.clicked.connect(lambda: self.process_application(table, "approved"))
        reject_button.clicked.connect(lambda: self.process_application(table, "rejected"))

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(approve_button)
        dialog.main_layout.addWidget(reject_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def process_application(self, table, action):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку для обработки.")
            return

        application_id = table.item(selected_row, 0).data(Qt.UserRole)  # Получаем ID заявки
        try:
            if action == "approved":
                # Создаем диалог для ввода зарплаты и премии
                salary_dialog = CustomDialog(self)
                salary_dialog.setWindowTitle("Установка зарплаты и премии")
                
                form_layout = QFormLayout()
                
                salary_input = QSpinBox()
                salary_input.setRange(0, 1000000)
                salary_input.setValue(50000)  # Базовая зарплата
                salary_input.setSingleStep(1000)
                
                bonus_input = QSpinBox()
                bonus_input.setRange(0, 1000000)
                bonus_input.setValue(10000)  # Базовая премия
                bonus_input.setSingleStep(1000)
                
                form_layout.addRow("Зарплата (руб.):", salary_input)
                form_layout.addRow("Премия (руб.):", bonus_input)
                
                confirm_button = QPushButton("Подтвердить")
                setup_button_style(confirm_button)
                
                # Добавляем обработчик нажатия кнопки
                confirm_button.clicked.connect(salary_dialog.accept)
                
                salary_dialog.main_layout.addLayout(form_layout)
                salary_dialog.main_layout.addWidget(confirm_button)
                salary_dialog.main_layout.addWidget(salary_dialog.back_button)
                
                # Показываем диалог
                if salary_dialog.exec_() == CustomDialog.Accepted:
                    # Получаем информацию о заявке
                    application = self.db.get_play_application_by_id(application_id)
                    if application:
                        # Создаем контракт с указанной зарплатой и премией
                        self.db.add_contract(
                            application[1],  # actor_username
                            application[2],  # play_id
                            salary_input.value(),  # зарплата
                            bonus_input.value()   # премия
                        )
                else:
                    return  # Если диалог был отменен, не создаем контракт
            
            self.db.update_play_application_status(application_id, action)
            QMessageBox.information(self, "Успех", f"Заявка успешно {action}!")
            table.removeRow(selected_row)  # Удаляем обработанную заявку из таблицы
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обработать заявку: {str(e)}")

    def create_play(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Создание спектакля")

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.actors_count_input = QSpinBox()
        self.actors_count_input.setRange(1, 100)
        self.budget_input = QSpinBox()
        self.budget_input.setRange(0, 1000000)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)

        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow("Дата:", self.date_input)
        form_layout.addRow("Количество актеров:", self.actors_count_input)
        form_layout.addRow("Бюджет:", self.budget_input)
        form_layout.addRow("Описание:", self.description_input)

        save_button = QPushButton("Создать")
        save_button.clicked.connect(lambda: self.save_play(dialog))
        setup_button_style(save_button)

        dialog.main_layout.addLayout(form_layout)
        dialog.main_layout.addWidget(save_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def save_play(self, dialog):
        try:
            self.db.add_play(
                self.name_input.text(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.actors_count_input.value(),
                self.budget_input.value(),
                self.description_input.toPlainText()
            )
            QMessageBox.information(self, "Успех", "Спектакль успешно создан!")
            dialog.close()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать спектакль: {str(e)}")

    def logout(self):
        self.main_window.show_login_page() 