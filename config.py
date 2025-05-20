# Настройки API
API_URL = "https://openrouter.ai/api/v1"
API_KEY = "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"

# Описание заданий ЕГЭ
TASKS = {
    1: {
        "title": "Планиметрия",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на планиметрию: площади, периметры, углы, теоремы"
    },
    2: {
        "title": "Векторы",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на векторы: сложение, вычитание, скалярное произведение"
    },
    3: {
        "title": "Стереометрия",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на стереометрию: объемы, площади поверхностей, сечения"
    },
    4: {
        "title": "Простая теория вероятности",
        "difficulty": "повышенная",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на простые вероятности: броски монет, кубиков, выбор карт"
    },
    5: {
        "title": "Сложная вероятность",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на сложные вероятности: условные вероятности, независимые события"
    },
    6: {
        "title": "Уравнения",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на решение уравнений: линейных, квадратных, рациональных"
    },
    7: {
        "title": "Вычисления и преобразования",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на вычисления и преобразования выражений"
    },
    8: {
        "title": "Производная и первообразная",
        "difficulty": "низкая",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на производные и первообразные функций"
    },
    9: {
        "title": "Прикладная задача",
        "difficulty": "повышенная",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на применение математики в реальных ситуациях"
    },
    10: {
        "title": "Текстовая задача",
        "difficulty": "повышенная",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на составление и решение уравнений по условию"
    },
    11: {
        "title": "Графики функций",
        "difficulty": "повышенная",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на анализ графиков функций"
    },
    12: {
        "title": "Анализ функций",
        "difficulty": "повышенная",
        "format": "Краткий",
        "points": 1,
        "description": "Задачи на исследование функций"
    },
    13: {
        "title": "Уравнения",
        "difficulty": "повышенная",
        "format": "Развернутый",
        "points": 2,
        "description": "Задачи на решение сложных уравнений с развернутым ответом"
    },
    14: {
        "title": "Стереометрия",
        "difficulty": "повышенная",
        "format": "Развернутый",
        "points": 3,
        "description": "Задачи на стереометрию с развернутым решением"
    },
    15: {
        "title": "Неравенства",
        "difficulty": "повышенная",
        "format": "Развернутый",
        "points": 2,
        "description": "Задачи на решение неравенств с развернутым ответом"
    },
    16: {
        "title": "Экономическая задача",
        "difficulty": "повышенная",
        "format": "Развернутый",
        "points": 2,
        "description": "Задачи на экономические расчеты с развернутым решением"
    },
    17: {
        "title": "Планиметрия",
        "difficulty": "повышенная",
        "format": "Развернутый",
        "points": 3,
        "description": "Задачи на планиметрию с развернутым решением"
    },
    18: {
        "title": "Задача с параметром",
        "difficulty": "высокая",
        "format": "Развернутый",
        "points": 4,
        "description": "Задачи с параметром и развернутым решением"
    },
    19: {
        "title": "Числа и их свойства",
        "difficulty": "высокая",
        "format": "Развернутый",
        "points": 4,
        "description": "Задачи на числа и их свойства с развернутым решением"
    }
}

# Стили для Streamlit
STYLES = """
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .task-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .task-header {
        color: #2c3e50;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .task-description {
        color: #7f8c8d;
        font-size: 16px;
        margin-bottom: 20px;
    }
    .task-info {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    .task-info-item {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        flex: 1;
    }
</style>
""" 