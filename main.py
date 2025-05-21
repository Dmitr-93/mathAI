import streamlit as st
import requests
import json
from datetime import datetime
import sqlite3
import hashlib
from PIL import Image
import traceback
import time
import openai
from openai import OpenAI

# Настройки API
API_KEY = "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"

# Подключение к базе данных (используем conn из глобальной области видимости)
conn = None # Инициализируем позже в main

# Конфигурация задач ЕГЭ (добавляем поле для теории)
TASKS_CONFIG = {
    "1": {"title": "Планиметрия", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по планиметрии (задание 1)..."},
    "2": {"title": "Векторы", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по векторам (задание 2)..."},
    "3": {"title": "Стереометрия", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по стереометрии (задание 3)..."},
    "4": {"title": "Простая теория вероятности", "difficulty": "Повышенная", "format": "Краткий", "points": 1, "theory": "Теория по простой теории вероятности (задание 4)..."},
    "5": {"title": "Сложная вероятность", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по сложной вероятности (задание 5)..."},
    "6": {"title": "Уравнения", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по уравнениям (задание 6)..."},
    "7": {"title": "Вычисления и преобразования", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по вычислениям и преобразованиям (задание 7)..."},
    "8": {"title": "Производная и первообразная", "difficulty": "Низкая", "format": "Краткий", "points": 1, "theory": "Теория по производной и первообразной (задание 8)..."},
    "9": {"title": "Прикладная задача", "difficulty": "Повышенная", "format": "Краткий", "points": 1, "theory": "Теория по прикладным задачам (задание 9)..."},
    "10": {"title": "Текстовая задача", "difficulty": "Повышенная", "format": "Краткий", "points": 1, "theory": "Теория по текстовым задачам (задание 10)..."},
    "11": {"title": "Графики функций", "difficulty": "Повышенная", "format": "Краткий", "points": 1, "theory": "Теория по графикам функций (задание 11)..."},
    "12": {"title": "Анализ функций", "difficulty": "Повышенная", "format": "Краткий", "points": 1, "theory": "Теория по анализу функций (задание 12)..."},
    "13": {"title": "Уравнения", "difficulty": "Повышенная", "format": "Развернутый", "points": 2, "theory": "Теория по уравнениям (задание 13)..."},
    "14": {"title": "Стереометрия", "difficulty": "Повышенная", "format": "Развернутый", "points": 3, "theory": "Теория по стереометрии (задание 14)..."},
    "15": {"title": "Неравенства", "difficulty": "Повышенная", "format": "Развернутый", "points": 2, "theory": "Теория по неравенствам (задание 15)..."},
    "16": {"title": "Экономическая задача", "difficulty": "Повышенная", "format": "Развернутый", "points": 2, "theory": "Теория по экономическим задачам (задание 16)..."},
    "17": {"title": "Планиметрия", "difficulty": "Повышенная", "format": "Развернутый", "points": 3, "theory": "Теория по планиметрии (задание 17)..."},
    "18": {"title": "Задача с параметром", "difficulty": "Высокая", "format": "Развернутый", "points": 4, "theory": "Теория по задачам с параметром (задание 18)..."},
    "19": {"title": "Числа и их свойства", "difficulty": "Высокая", "format": "Развернутый", "points": 4, "theory": "Теория по числам и их свойствам (задание 19)..."}
}

def init_database():
    """Инициализация базы данных и создание необходимых таблиц"""
    global conn
    try:
        conn = sqlite3.connect('ege_database.db', check_same_thread=False)
        c = conn.cursor()
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
                task_type TEXT NOT NULL,
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
    except sqlite3.Error as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")
        raise

def authenticate_user(username, password):
    """Аутентификация пользователя"""
    global conn
    c = conn.cursor()
    try:
        # Проверяем существование пользователя
        c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user:
            user_id, stored_hash = user
            if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                return user_id
            else:
                return None # Неверный пароль
        else:
            # Пользователь не найден, можно предложить регистрацию
            return None
    except sqlite3.Error as e:
        st.error(f"Ошибка базы данных при аутентификации: {str(e)}")
        st.code(traceback.format_exc())
        return None

def register_user(username, password):
    """Регистрация нового пользователя"""
    global conn
    c = conn.cursor()
    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_password))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        st.error("Пользователь с таким именем уже существует.")
        return None
    except sqlite3.Error as e:
        st.error(f"Ошибка базы данных при регистрации: {str(e)}")
        st.code(traceback.format_exc())
        return None

def save_task(task_type, task_text, answer):
    """Сохранение задачи в базу данных"""
    global conn
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO tasks (task_type, task_text, answer)
            VALUES (?, ?, ?)
        """, (task_type, task_text, answer))
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        st.error(f"Ошибка при сохранении задачи: {str(e)}")
        st.code(traceback.format_exc())
        return None

def save_solution(user_id, task_id, is_correct):
    """Сохранение решения задачи"""
    global conn
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO solved_tasks (user_id, task_id, is_correct, solve_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, task_id, is_correct, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Ошибка при сохранении решения: {str(e)}")
        st.code(traceback.format_exc())

def get_user_stats(user_id):
    """Получение статистики пользователя"""
    global conn
    c = conn.cursor()
    try:
        # Получаем общее количество решенных задач
        c.execute("""
            SELECT COUNT(*) FROM solved_tasks 
            WHERE user_id = ?
        """, (user_id,))
        total_solved = c.fetchone()[0]
        
        # Получаем количество правильно решенных задач
        c.execute("""
            SELECT COUNT(*) FROM solved_tasks 
            WHERE user_id = ? AND is_correct = 1
        """, (user_id,))
        correct_solved = c.fetchone()[0]
        
        # Получаем статистику по типам задач
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
        st.error(f"Ошибка при получении статистики: {str(e)}")
        st.code(traceback.format_exc())
        return None

def get_solution_history(user_id):
    """Получение истории решенных задач"""
    global conn
    c = conn.cursor()
    try:
        # Получаем последние 10 решенных задач
        c.execute("""
            SELECT t.task_type, t.task_text, t.answer, st.is_correct, st.solve_date
            FROM solved_tasks st
            JOIN tasks t ON st.task_id = t.id
            WHERE st.user_id = ?
            ORDER BY st.solve_date DESC
            LIMIT 10
        """, (user_id,))
        history = c.fetchall()
        return history
            
    except sqlite3.Error as e:
        st.error(f"Ошибка при получении истории решений: {str(e)}")
        st.code(traceback.format_exc())
        return None

def generate_task(task_type):
    """Генерация задачи ЕГЭ по математике через API"""
    task_info = TASKS_CONFIG[task_type]
    prompt = f"""Сгенерируй задачу ЕГЭ по математике (профильный уровень) номер {task_type} на тему "{task_info['title']}".
    Сложность: {task_info['difficulty']}
    Формат: {task_info['format']}
    Баллы: {task_info['points']}
    
    Задача должна быть в формате:
    
    Условие задачи:
    [текст условия]
    
    Решение:
    [подробное решение]
    
    Ответ: [числовой ответ]
    
    Убедись, что задача соответствует формату ЕГЭ и имеет четкое решение."""
    
    try:
        # Создаем клиент OpenAI с настройками OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY,
        )
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "EGE Generator",
            },
            model="qwen/qwen3-0.6b-04-28:free",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=16000
        )
        
        task_text = completion.choices[0].message.content
        
        # Извлекаем ответ из текста задачи
        answer = task_text.split("Ответ:")[-1].strip()
        
        # Сохраняем задачу в базу данных
        task_id = save_task(task_type, task_text, answer)
        
        return {
            "task_type": task_type,
            "task_condition": task_text.split("Условие задачи:", 1)[1].split("Решение:", 1)[0].strip() if "Условие задачи:" in task_text else task_text,
            "task_solution": task_text.split("Решение:", 1)[1].split("Ответ:", 1)[0].strip() if "Решение:" in task_text else "Решение не найдено.",
            "task_answer": answer,
            "task_id": task_id
        }
        
    except Exception as e:
        st.error(f"Ошибка при генерации задачи: {str(e)}")
        st.code(traceback.format_exc())
        return None

def show_login_form():
    """Отображение формы входа/регистрации"""
    st.warning("Пожалуйста, войдите или зарегистрируйтесь для доступа к генератору задач.")
    st.markdown("""
    ### О приложении
    Это приложение помогает готовиться к ЕГЭ по математике (профильный уровень), 
    генерируя задачи по всем темам экзамена. После регистрации вы сможете:
    
    - Генерировать задачи по конкретным темам
    - Получать подробные решения
    - Отслеживать свой прогресс
    - Сохранять историю решенных задач
    """)
    
    with st.form("login_form"):
        st.subheader("Вход / Регистрация")
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти / Зарегистрироваться")
        
        if submit:
            if not username or not password:
                st.error("Пожалуйста, заполните все поля")
            else:
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.success("Вход выполнен успешно!")
                    st.rerun()
                else:
                    # Попытка регистрации, если вход не удался
                    registered_user_id = register_user(username, password)
                    if registered_user_id:
                        st.session_state.user_id = registered_user_id
                        st.success("Регистрация успешна и выполнен вход!")
                        st.rerun()

def show_user_info():
    """Отображение информации о пользователе"""
    global conn
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (st.session_state.user_id,))
    username = c.fetchone()[0]
    st.success(f"Вы вошли как: {username}")
    
    if st.button("Выйти"):
        st.session_state.user_id = None
        st.session_state.generated_task = None
        st.session_state.user_answer = ""
        st.session_state.show_answer = False
        st.rerun()

def show_stats():
    """Отображение статистики пользователя"""
    stats = get_user_stats(st.session_state.user_id)
    
    if stats:
        st.subheader("📊 Ваша статистика")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего решено задач", stats["total_solved"])
        with col2:
            if stats["total_solved"] > 0:
                accuracy = (stats["correct_solved"] / stats["total_solved"]) * 100
                st.metric("Точность", f"{accuracy:.1f}%")
        
        if stats["task_stats"]:
            st.subheader("Статистика по типам задач")
            for task_type, total, correct in stats["task_stats"]:
                if total > 0:
                    accuracy = (correct / total) * 100
                    st.metric(
                        f"Задача №{task_type}",
                        f"Решено: {total}",
                        f"Точность: {accuracy:.1f}%"
                    )

def show_history():
    """Отображение истории решенных задач"""
    history = get_solution_history(st.session_state.user_id)
    
    if history:
        st.subheader("📜 История решений")
        for task_type, task_text, answer, is_correct, solve_date in history:
            with st.expander(f"Задача №{task_type} ({solve_date})"):
                st.markdown("### Условие задачи:")
                st.markdown(task_text.split("Условие задачи:", 1)[1].split("Решение:", 1)[0].strip() if "Условие задачи:" in task_text else task_text)
                st.markdown("### Ваш результат:")
                if is_correct:
                    st.success("✅ Правильно")
                else:
                    st.error("❌ Неправильно")
                st.markdown(f"**Правильный ответ:** {answer}")
    else:
        st.info("У вас пока нет решенных задач")

def show_task_content(task_type):
    """Отображение содержимого задачи в expander"""
    task_info = TASKS_CONFIG[task_type]

    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
        <h3 style='color: #1f77b4; margin-bottom: 5px;'>Задание {task_type}: {task_info['title']}</h3>
        <div style='display: flex; gap: 20px; font-size: 0.9em;'>
            <div><strong>Сложность:</strong> {task_info['difficulty']}</div>
            <div><strong>Формат:</strong> {task_info['format']}</div>
            <div><strong>Баллы:</strong> {task_info['points']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"Сгенерировать задачу {task_type}", key=f"gen_{task_type}"):
        with st.spinner("Генерируем задачу..."):
            try:
                task = generate_task(task_type)
                if task:
                    st.session_state.generated_task = task
                    st.session_state.user_answer = ""
                    st.session_state.show_answer = False
            except Exception as e:
                st.error(f"Произошла ошибка при генерации задачи: {str(e)}")
                st.code(traceback.format_exc())

    # Отображаем элементы задачи последовательно
    if st.session_state.generated_task and st.session_state.generated_task["task_type"] == task_type:
        st.markdown("#### Условие задачи:")
        st.markdown(st.session_state.generated_task["task_condition"])

        # Поле для ввода ответа
        if task_info["format"] == "Краткий":
            user_answer = st.text_input("Ваш ответ:", value=st.session_state.user_answer, key=f"ans_{task_type}", autocomplete="off")
            st.session_state.user_answer = user_answer

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Проверить ответ", key=f"check_{task_type}"):
                    if user_answer.strip().lower() == st.session_state.generated_task["task_answer"].strip().lower():
                        st.success("✅ Правильно!")
                        if st.session_state.user_id and st.session_state.generated_task["task_id"]:
                             save_solution(st.session_state.user_id, st.session_state.generated_task["task_id"], 1)
                    else:
                        st.error("❌ Неправильно")
                        if st.session_state.user_id and st.session_state.generated_task["task_id"]:
                            save_solution(st.session_state.user_id, st.session_state.generated_task["task_id"], 0)

            with col_btn2:
                 # Кнопка для показа решения и ответа
                 if st.button("Показать решение и ответ", key=f"show_{task_type}"):
                      st.session_state.show_answer = True
                      st.rerun()

        # Отображаем решение и ответ только если show_answer True
        if st.session_state.show_answer:
             st.markdown("#### Решение:")
             st.markdown(st.session_state.generated_task["task_solution"])

             st.markdown("#### Правильный ответ:")
             st.markdown(f"**{st.session_state.generated_task['task_answer']}**")

def main():
    st.set_page_config(page_title="Генератор задач ЕГЭ по математике", page_icon="📚", layout="wide")
    
    # Инициализация состояния сессии
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'generated_task' not in st.session_state:
        st.session_state.generated_task = None
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = ""
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    
    # Инициализация базы данных
    init_database()
    
    st.title("🎯 Генератор задач ЕГЭ по математике")
    
    if st.session_state.user_id is None:
        show_login_form()
    else:
        show_user_info()
        
        # Оставляем только вкладку с задачами
        st.subheader("Часть 1 (Задания 1-12)")
        for i in range(1, 13):
            with st.expander(f"Задание {i}"):
                show_task_content(str(i))

        st.subheader("Часть 2 (Задания 13-19)")
        for i in range(13, 20):
            with st.expander(f"Задание {i}"):
                show_task_content(str(i))

        show_stats()
        show_history()

if __name__ == "__main__":
    main() 
