import streamlit as st
import openai
import json
import sqlite3
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="ЕГЭ Генератор",
    page_icon="📚",
    layout="wide"
)

# Инициализация OpenAI
openai.api_key = st.secrets["openai_api_key"]

# Создание базы данных
def init_db():
    conn = sqlite3.connect('ege_tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  task_number INTEGER,
                  condition TEXT,
                  solution TEXT,
                  answer TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# Генерация задачи
def generate_task(task_number):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Вы - опытный преподаватель математики, специализирующийся на подготовке к ЕГЭ."},
                {"role": "user", "content": f"Сгенерируйте задачу №{task_number} ЕГЭ по математике. "
                                          f"Верните ответ в формате JSON с полями: condition (условие задачи), "
                                          f"solution (подробное решение), answer (ответ)."}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["condition"], result["solution"], result["answer"]
    except Exception as e:
        st.error(f"Произошла ошибка при генерации задачи: {str(e)}")
        return None, None, None

# Сохранение задачи в базу данных
def save_task(task_number, condition, solution, answer):
    conn = sqlite3.connect('ege_tasks.db')
    c = conn.cursor()
    c.execute('''INSERT INTO tasks (task_number, condition, solution, answer, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (task_number, condition, solution, answer, datetime.now()))
    conn.commit()
    conn.close()

# Получение истории задач
def get_task_history():
    conn = sqlite3.connect('ege_tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = c.fetchall()
    conn.close()
    return tasks

# Инициализация базы данных
init_db()

# Заголовок
st.title("🎯 Генератор задач ЕГЭ по математике")

# Выбор номера задания
task_number = st.selectbox(
    "Выберите номер задания:",
    range(1, 20),
    format_func=lambda x: f"Задание №{x}"
)

# Кнопка генерации
if st.button("Сгенерировать задачу"):
    with st.spinner("Генерируем задачу..."):
        condition, solution, answer = generate_task(task_number)
        
        if condition:
            # Сохраняем задачу
            save_task(task_number, condition, solution, answer)
            
            # Отображаем условие
            st.subheader("Условие задачи:")
            st.write(condition)
            
            # Кнопка для показа решения
            if st.button("Показать решение"):
                st.subheader("Решение:")
                st.write(solution)
                st.subheader("Ответ:")
                st.write(answer)

# История задач
st.subheader("История сгенерированных задач")
tasks = get_task_history()

for task in tasks:
    with st.expander(f"Задание №{task[1]} от {task[5]}"):
        st.write("**Условие:**")
        st.write(task[2])
        st.write("**Решение:**")
        st.write(task[3])
        st.write("**Ответ:**")
        st.write(task[4]) 
