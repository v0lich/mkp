from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from .login_page import LoginPage
from .admin_dashboard import AdminDashboard
from .registration_page import RegistrationPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Театр")
        
        # Устанавливаем цвет фона через палитру
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#e6f3ff"))  # Светло-голубой цвет
        palette.setColor(QPalette.Base, QColor("#e6f3ff"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем главный layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        # Создаем стек для переключения между окнами
        self.stack = QStackedWidget()
        
        # Создаем все окна
        self.login_page = LoginPage(self)
        self.admin_page = AdminDashboard(self)
        self.actor_page = None  # Будет создаваться при входе конкретного актера
        self.director_page = None  # Будет создаваться при входе директора
        self.registration_page = RegistrationPage(self)
        
        # Добавляем страницы в стек
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.admin_page)
        self.stack.addWidget(self.registration_page)
        
        # Добавляем стек в главный layout
        self.main_layout.addWidget(self.stack)
        
        # Показываем страницу логина
        self.show_login_page()

    def show_login_page(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_admin_page(self):
        self.stack.setCurrentWidget(self.admin_page)

    def show_actor_page(self, username):
        if self.actor_page:
            self.stack.removeWidget(self.actor_page)
        from .actor_dashboard import ActorDashboard
        self.actor_page = ActorDashboard(self, username)
        self.stack.addWidget(self.actor_page)
        self.stack.setCurrentWidget(self.actor_page)

    def show_director_page(self, username):
        if self.director_page:
            self.stack.removeWidget(self.director_page)
        from .director_dashboard import DirectorDashboard
        self.director_page = DirectorDashboard(self, username)
        self.stack.addWidget(self.director_page)
        self.stack.setCurrentWidget(self.director_page)

    def show_registration_page(self):
        self.stack.setCurrentWidget(self.registration_page) 