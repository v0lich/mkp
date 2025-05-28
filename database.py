import sqlite3
from datetime import datetime

class TheaterDB:
    def __init__(self, db_name='theater.db'):
        self.db_name = db_name
        self.create_tables()
        self.insert_initial_data()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создание таблицы пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    fio TEXT,
                    achievements TEXT,
                    experience TEXT
                )
            ''')

            # Создание таблицы спектаклей с уникальным названием
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    date TEXT NOT NULL,
                    actors_count INTEGER,
                    budget DECIMAL(10,2)
                )
            ''')

            # Создание таблицы заявок актёров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actor_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fio TEXT NOT NULL,
                    birthdate TEXT NOT NULL,
                    achievements TEXT,
                    plays TEXT,
                    experience TEXT,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    login TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')

            # Создание таблицы заявок на спектакли
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS play_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_username TEXT NOT NULL,
                    play_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    application_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (actor_username) REFERENCES users(username),
                    FOREIGN KEY (play_id) REFERENCES plays(id)
                )
            ''')

            # Создание таблицы контрактов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_username TEXT NOT NULL,
                    play_id INTEGER NOT NULL,
                    salary DECIMAL(10,2) NOT NULL,
                    bonus DECIMAL(10,2),
                    status TEXT DEFAULT 'pending',
                    offer_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (actor_username) REFERENCES users(username),
                    FOREIGN KEY (play_id) REFERENCES plays(id)
                )
            ''')

            # Создание таблицы актёров в спектаклях
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actors_in_plays (
                    actor_username TEXT NOT NULL,
                    play_id INTEGER NOT NULL,
                    salary DECIMAL(10,2) NOT NULL,
                    bonus DECIMAL(10,2),
                    PRIMARY KEY (actor_username, play_id),
                    FOREIGN KEY (actor_username) REFERENCES users(username),
                    FOREIGN KEY (play_id) REFERENCES plays(id)
                )
            ''')

    def insert_initial_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Добавление начальных пользователей
            initial_users = [
                ('admin', 'password123', 'админ', 'admin@example.com', '123456789', None, None, None),
                ('director', 'directorpassword', 'генеральный директор', 'director@example.com', '112233445', None, None, None),
                ('actor1', 'actorpassword', 'актёр', 'actor1@example.com', '987654321', 'Иванов Иван Иванович', 'Народный артист', '10 лет')
            ]

            cursor.executemany('''
                INSERT OR IGNORE INTO users 
                (username, password, role, email, phone, fio, achievements, experience)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', initial_users)

            # Добавление трёх спектаклей
            initial_plays = [
                ('Чайка', '15.05.2024', 7, 150000),
                ('Ревизор', '20.06.2024', 8, 180000),
                ('Вишнёвый сад', '10.07.2024', 6, 130000)
            ]
            
            for play in initial_plays:
                try:
                    cursor.execute('''
                        INSERT INTO plays (name, date, actors_count, budget)
                        VALUES (?, ?, ?, ?)
                    ''', play)
                except sqlite3.IntegrityError:
                    pass

            # Восстанавливаем данные о контрактах и актерах в спектаклях
            self.restore_contracts(cursor)

    def restore_contracts(self, cursor):
        """Восстановление данных о контрактах и актерах в спектаклях"""
        try:
            # Получаем все принятые контракты
            cursor.execute('''
                SELECT * FROM contracts 
                WHERE status = "accepted"
            ''')
            accepted_contracts = cursor.fetchall()

            # Восстанавливаем актеров в спектаклях
            for contract in accepted_contracts:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO actors_in_plays 
                        (actor_username, play_id, salary, bonus)
                        VALUES (?, ?, ?, ?)
                    ''', (contract[1], contract[2], contract[3], contract[4]))
                except sqlite3.IntegrityError:
                    pass
        except:
            pass

    def authenticate_user(self, username, password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, role FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            return cursor.fetchone()

    def get_user_info(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            return cursor.fetchone()

    def add_actor_application(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actor_applications 
                (fio, birthdate, achievements, plays, experience, email, phone, login, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['ФИО'], data['Дата рождения'], data['Достижения'],
                data['Спектакли'], data['Стаж работы'], data['Почта'],
                data['Телефон'], data['Логин'], data['Пароль']
            ))
            return cursor.lastrowid

    def get_actor_applications(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM actor_applications WHERE status = "pending"')
            return cursor.fetchall()

    def get_all_plays(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM plays')
            return cursor.fetchall()

    def add_play(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO plays (name, date, actors_count, budget)
                    VALUES (?, ?, ?, ?)
                ''', (
                    data['Наименование'], data['Дата'],
                    data['Количество актеров'], data['Бюджет']
                ))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise Exception("Спектакль с таким названием уже существует")

    def approve_application(self, login):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Получаем данные заявки
            cursor.execute('''
                SELECT * FROM actor_applications 
                WHERE login = ? AND status = "pending"
            ''', (login,))
            application = cursor.fetchone()
            
            if application:
                # Добавляем пользователя
                cursor.execute('''
                    INSERT INTO users 
                    (username, password, role, email, phone, fio, achievements, experience)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    application[8],  # login
                    application[9],  # password
                    "актёр",
                    application[6],  # email
                    application[7],  # phone
                    application[1],  # fio
                    application[3],  # achievements
                    application[5]   # experience
                ))
                
                # Обновляем статус заявки
                cursor.execute('''
                    UPDATE actor_applications 
                    SET status = "approved" 
                    WHERE login = ?
                ''', (login,))
                
                return True
        return False

    def reject_application(self, login):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE actor_applications 
                SET status = "rejected" 
                WHERE login = ? AND status = "pending"
            ''', (login,))
            return cursor.rowcount > 0

    def check_login_exists(self, login):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Проверяем в таблице пользователей
            cursor.execute('SELECT 1 FROM users WHERE username = ?', (login,))
            if cursor.fetchone():
                return True
            # Проверяем в таблице заявок
            cursor.execute('SELECT 1 FROM actor_applications WHERE login = ?', (login,))
            if cursor.fetchone():
                return True
            return False

    def update_user_info(self, username, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Формируем SQL запрос динамически на основе предоставленных данных
            update_fields = []
            values = []
            
            if data.get("achievements") is not None:
                update_fields.append("achievements = ?")
                values.append(data["achievements"])
                
            if data.get("email") is not None:
                update_fields.append("email = ?")
                values.append(data["email"])
                
            if data.get("phone") is not None:
                update_fields.append("phone = ?")
                values.append(data["phone"])
                
            if data.get("password"):
                update_fields.append("password = ?")
                values.append(data["password"])
                
            if update_fields:
                sql = f"UPDATE users SET {', '.join(update_fields)} WHERE username = ?"
                values.append(username)
                cursor.execute(sql, values)
                return cursor.rowcount > 0
            return False

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()

    def delete_user(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Удаляем связанные данные
                cursor.execute('DELETE FROM actors_in_plays WHERE actor_username = ?', (username,))
                cursor.execute('DELETE FROM contracts WHERE actor_username = ?', (username,))
                cursor.execute('DELETE FROM play_applications WHERE actor_username = ?', (username,))
                # Удаляем пользователя
                cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                return True
            except:
                return False

    def add_play_application(self, actor_username, play_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO play_applications (actor_username, play_id)
                VALUES (?, ?)
            ''', (actor_username, play_id))
            return cursor.lastrowid

    def add_contract(self, actor_username, play_id, salary, bonus):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contracts (actor_username, play_id, salary, bonus)
                VALUES (?, ?, ?, ?)
            ''', (actor_username, play_id, salary, bonus))
            return cursor.lastrowid

    def get_contracts(self, actor_username=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if actor_username:
                cursor.execute('''
                    SELECT c.*, p.name as play_name 
                    FROM contracts c 
                    JOIN plays p ON c.play_id = p.id 
                    WHERE c.actor_username = ? AND c.status = "pending"
                ''', (actor_username,))
            else:
                cursor.execute('''
                    SELECT c.*, p.name as play_name 
                    FROM contracts c 
                    JOIN plays p ON c.play_id = p.id 
                    WHERE c.status = "pending"
                ''')
            return cursor.fetchall()

    def clear_plays(self):
        """Метод для очистки таблицы спектаклей"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM plays')

    def get_play_applications(self):
        """Получение всех заявок на спектакли со статусом 'pending'"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM play_applications 
                WHERE status = "pending"
            ''')
            return cursor.fetchall()

    def get_play_by_id(self, play_id):
        """Получение информации о спектакле по его ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM plays WHERE id = ?', (play_id,))
            return cursor.fetchone()

    def get_all_contracts(self):
        """Получение всех контрактов из базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, p.name as play_name 
                FROM contracts c 
                JOIN plays p ON c.play_id = p.id 
                WHERE c.status IN ("approved", "accepted")
            ''')
            return cursor.fetchall()

    def accept_contract(self, contract_id):
        """Подтверждение контракта актером"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Обновляем статус контракта
                cursor.execute('''
                    UPDATE contracts 
                    SET status = "accepted" 
                    WHERE id = ?
                ''', (contract_id,))
                
                # Получаем информацию о контракте
                cursor.execute('SELECT * FROM contracts WHERE id = ?', (contract_id,))
                contract = cursor.fetchone()
                
                if contract:
                    # Добавляем актера в спектакль
                    cursor.execute('''
                        INSERT INTO actors_in_plays 
                        (actor_username, play_id, salary, bonus)
                        VALUES (?, ?, ?, ?)
                    ''', (contract[1], contract[2], contract[3], contract[4]))
                
                return True
            except:
                return False

    def reject_contract(self, contract_id):
        """Отклонение контракта актером"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE contracts 
                    SET status = "rejected" 
                    WHERE id = ?
                ''', (contract_id,))
                return True
            except:
                return False

    def update_play_application_status(self, application_id, status):
        """Обновление статуса заявки на спектакль"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE play_applications 
                    SET status = ? 
                    WHERE id = ?
                ''', (status, application_id))
                return cursor.rowcount > 0
            except:
                return False

    def get_play_application_by_id(self, application_id):
        """Получение информации о заявке на спектакль по её ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM play_applications WHERE id = ?', (application_id,))
            return cursor.fetchone() 