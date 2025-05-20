import sqlite3
import hashlib
from datetime import datetime

def init_database():
    """Инициализация базы данных и создание необходимых таблиц"""
    conn = sqlite3.connect('ege_database.db', check_same_thread=False)
    c = conn.cursor()
    
    try:
        # Создаем таблицу пользователей
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу задач
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type INTEGER NOT NULL,
                task_text TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу решенных задач
        c.execute('''
            CREATE TABLE IF NOT EXISTS solved_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                solve_date TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        conn.commit()
        print("База данных успешно инициализирована")
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")
        raise

def get_user_stats(conn, user_id):
    """Получение статистики пользователя"""
    c = conn.cursor()
    try:
        # Общее количество решенных задач
        c.execute("""
            SELECT COUNT(*) FROM solved_tasks 
            WHERE user_id = ?
        """, (user_id,))
        total_solved = c.fetchone()[0]
        
        # Количество правильно решенных задач
        c.execute("""
            SELECT COUNT(*) FROM solved_tasks 
            WHERE user_id = ? AND is_correct = 1
        """, (user_id,))
        correct_solved = c.fetchone()[0]
        
        # Статистика по типам задач
        c.execute("""
            SELECT t.task_type, 
                   COUNT(*) as total,
                   SUM(CASE WHEN st.is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM solved_tasks st
            JOIN tasks t ON st.task_id = t.id
            WHERE st.user_id = ?
            GROUP BY t.task_type
            ORDER BY t.task_type
        """, (user_id,))
        task_stats = c.fetchall()
        
        return {
            "total_solved": total_solved,
            "correct_solved": correct_solved,
            "task_stats": task_stats
        }
    except sqlite3.Error as e:
        print(f"Ошибка при получении статистики: {str(e)}")
        raise

def get_solution_history(conn, user_id, limit=10):
    """Получение истории решенных задач"""
    c = conn.cursor()
    try:
        c.execute("""
            SELECT t.task_type, t.task_text, t.answer, st.is_correct, st.solve_date
            FROM solved_tasks st
            JOIN tasks t ON st.task_id = t.id
            WHERE st.user_id = ?
            ORDER BY st.solve_date DESC
            LIMIT ?
        """, (user_id, limit))
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка при получении истории решений: {str(e)}")
        raise

def save_task(conn, task_type, task_text, answer):
    """Сохранение новой задачи в базу данных"""
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO tasks (task_type, task_text, answer)
            VALUES (?, ?, ?)
        """, (task_type, task_text, answer))
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении задачи: {str(e)}")
        raise

def save_solution(conn, user_id, task_id, is_correct):
    """Сохранение результата решения задачи"""
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO solved_tasks (user_id, task_id, is_correct, solve_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, task_id, is_correct, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении решения: {str(e)}")
        raise

def authenticate_user(conn, username, password):
    """Аутентификация пользователя"""
    c = conn.cursor()
    try:
        # Проверяем существование пользователя
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user is None:
            # Регистрируем нового пользователя
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed_password))
            conn.commit()
            return c.lastrowid
        else:
            # Проверяем пароль
            c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user_id, stored_hash = c.fetchone()
            if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                return user_id
            return None
    except sqlite3.Error as e:
        print(f"Ошибка при аутентификации: {str(e)}")
        raise 