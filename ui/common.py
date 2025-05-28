from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QTableWidget,
                           QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        self.back_button = QPushButton("Назад")
        setup_button_style(self.back_button)
        self.back_button.clicked.connect(self.close)

def setup_button_style(button):
    button.setMinimumWidth(200)
    button.setMinimumHeight(40)
    font = QFont()
    font.setPointSize(10)
    button.setFont(font)
    button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)

def adjust_table_size(table):
    # Устанавливаем ширину столбцов
    header = table.horizontalHeader()
    for i in range(table.columnCount()):
        header.setSectionResizeMode(i, header.Stretch)
    
    # Вычисляем размеры таблицы
    width = sum(table.columnWidth(i) for i in range(table.columnCount()))
    height = table.rowHeight(0) * table.rowCount() + table.horizontalHeader().height()
    
    return width, height

def show_error_message(parent, message):
    QMessageBox.warning(parent, "Ошибка", message)

def show_success_message(parent, message):
    QMessageBox.information(parent, "Успех", message) 