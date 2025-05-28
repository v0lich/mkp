from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout,
                           QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt
from .common import CustomDialog, setup_button_style, adjust_table_size
from database import TheaterDB

class ActorDashboard(QMainWindow):
    def __init__(self, main_window, username):
        super().__init__()
        self.main_window = main_window
        self.username = username
        self.setWindowTitle(f"Кабинет актера: {username}")
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
            ("Редактировать информацию о себе", self.edit_info),
            ("Просмотр списка спектаклей", self.view_plays),
            ("Просмотр предложений", self.view_contract_offers),
            ("Выход", self.logout)
        ]
        
        for text, handler in buttons:
            button = QPushButton(text)
            setup_button_style(button)
            button.clicked.connect(handler)
            button_container.addWidget(button)

        main_layout.addLayout(button_container)

    def edit_info(self):
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Редактирование информации")

        form_layout = QFormLayout()

        # Получаем информацию о пользователе из базы данных
        user_info = self.db.get_user_info(self.username)
        if not user_info:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить информацию о пользователе")
            return

        # Многострочное поле для достижений
        self.achievements_input = QTextEdit()
        self.achievements_input.setText(user_info[6] or "")  # achievements - 7-й столбец
        self.achievements_input.setMaximumHeight(100)

        self.email_input = QLineEdit(user_info[3] or "")  # email - 4-й столбец
        self.phone_input = QLineEdit(user_info[4] or "")  # phone - 5-й столбец

        # Поля для смены пароля
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Текущий пароль")
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Новый пароль")

        form_layout.addRow("Достижения:", self.achievements_input)
        form_layout.addRow("Почта:", self.email_input)
        form_layout.addRow("Телефон:", self.phone_input)
        form_layout.addRow("Старый пароль:", self.old_password)
        form_layout.addRow("Новый пароль:", self.new_password)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_info(dialog))
        setup_button_style(save_button)

        dialog.main_layout.addLayout(form_layout)
        dialog.main_layout.addWidget(save_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def save_info(self, dialog):
        """ Сохранение измененной информации """
        try:
            # Проверяем, что все обязательные поля заполнены
            if not self.achievements_input.toPlainText().strip():
                QMessageBox.warning(self, "Ошибка", "Поле 'Достижения' не может быть пустым")
                return
                
            if not self.email_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Поле 'Почта' не может быть пустым")
                return
                
            if not self.phone_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Поле 'Телефон' не может быть пустым")
                return

            # Проверяем старый пароль, если введен новый
            if self.new_password.text():
                if not self.old_password.text():
                    QMessageBox.warning(self, "Ошибка", "Для смены пароля необходимо ввести текущий пароль")
                    return
                if not self.db.authenticate_user(self.username, self.old_password.text()):
                    QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль")
                    return

            # Обновляем информацию о пользователе
            self.db.update_user_info(
                self.username,
                {
                    "achievements": self.achievements_input.toPlainText().strip(),
                    "email": self.email_input.text().strip(),
                    "phone": self.phone_input.text().strip(),
                    "password": self.new_password.text() if self.new_password.text() else None
                }
            )
            QMessageBox.information(self, "Успех", "Информация успешно обновлена!")
            dialog.close()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить информацию: {str(e)}")

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

        # Кнопка подачи заявки
        apply_button = QPushButton("Подать заявку на спектакль")
        setup_button_style(apply_button)
        apply_button.clicked.connect(lambda: self.apply_for_play(table))

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(apply_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def apply_for_play(self, table):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите спектакль для подачи заявки.")
            return

        play_name = table.item(selected_row, 0).text()
        
        try:
            # Получаем ID спектакля из базы данных
            plays = self.db.get_all_plays()
            play_id = None
            for play in plays:
                if play[1] == play_name:  # play[1] - это название спектакля
                    play_id = play[0]  # play[0] - это ID спектакля
                    break
            
            if play_id is None:
                QMessageBox.warning(self, "Ошибка", "Спектакль не найден в базе данных.")
                return
            
            # Добавляем заявку в базу данных
            self.db.add_play_application(self.username, play_id)
            QMessageBox.information(self, "Успех", f"Заявка на спектакль '{play_name}' подана!")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось подать заявку: {str(e)}")

    def view_contract_offers(self):
        contracts = self.db.get_contracts(self.username)
        if not contracts:
            QMessageBox.information(self, "Информация", "Нет новых предложений")
            return
        
        dialog = CustomDialog(self)
        dialog.setWindowTitle("Предложения контрактов")

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Спектакль", "Зарплата", "Премия", "Дата предложения"
        ])
        
        table.setRowCount(len(contracts))
        
        for row, contract in enumerate(contracts):
            # Создаем элементы таблицы
            play_item = QTableWidgetItem(contract[-1])  # play_name
            play_item.setData(Qt.UserRole, contract[0])  # Сохраняем ID контракта
            
            table.setItem(row, 0, play_item)
            table.setItem(row, 1, QTableWidgetItem(f"{contract[3]} руб."))  # salary
            table.setItem(row, 2, QTableWidgetItem(f"{contract[4]} руб."))  # bonus
            table.setItem(row, 3, QTableWidgetItem(contract[6]))  # offer_date

        width, height = adjust_table_size(table)
        dialog.setMinimumSize(width + 40, height + 150)

        # Кнопки для обработки предложений
        accept_button = QPushButton("Принять предложение")
        reject_button = QPushButton("Отклонить предложение")
        setup_button_style(accept_button)
        setup_button_style(reject_button)
        
        accept_button.clicked.connect(lambda: self.process_contract(table, True))
        reject_button.clicked.connect(lambda: self.process_contract(table, False))

        dialog.main_layout.addWidget(table)
        dialog.main_layout.addWidget(accept_button)
        dialog.main_layout.addWidget(reject_button)
        dialog.main_layout.addWidget(dialog.back_button)
        dialog.exec_()

    def process_contract(self, table, is_accepted):
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предложение для обработки.")
            return

        contract_id = table.item(selected_row, 0).data(Qt.UserRole)
        try:
            if is_accepted:
                self.db.accept_contract(contract_id)
                QMessageBox.information(self, "Успех", "Вы приняли предложение!")
            else:
                self.db.reject_contract(contract_id)
                QMessageBox.information(self, "Информация", "Вы отклонили предложение")
            table.removeRow(selected_row)  # Удаляем обработанное предложение из таблицы
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обработать предложение: {str(e)}")

    def logout(self):
        self.main_window.show_login_page() 