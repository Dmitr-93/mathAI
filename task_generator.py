from openai import OpenAI
from src.config import API_URL, API_KEY, TASKS
import traceback

def generate_task(task_type):
    """Генерация задачи ЕГЭ по математике через API"""
    client = OpenAI(
        base_url=API_URL,
        api_key=API_KEY
    )
    
    task_info = TASKS[task_type]
    
    prompt = f"""Сгенерируй задачу ЕГЭ по математике (профильный уровень) номер {task_type}.
    Тема: {task_info['title']}
    Сложность: {task_info['difficulty']}
    Формат: {task_info['format']}
    Баллы: {task_info['points']}
    
    Задача должна быть СТРОГО в формате:
    
    Условие задачи:
    [текст условия]
    
    Решение:
    [подробное решение]
    
    Ответ: [числовой ответ]
    
    Убедись, что:
    1. Задача соответствует формату ЕГЭ
    2. Задача имеет четкое решение
    3. Задача соответствует указанной теме и сложности
    4. Для задач с развернутым ответом решение должно быть подробным
    5. Для задач с кратким ответом решение может быть более компактным
    6. Ответ должен быть числовым и соответствовать формату ЕГЭ.
    7. Текст должен строго соответствовать указанному формату с заголовками "Условие задачи:", "Решение:", "Ответ:".
    """
    
    try:
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "EGE Generator",
            },
            model="nousresearch/deephermes-3-mistral-24b-preview:free",
            messages=[
                {"role": "system", "content": "Ты - эксперт по математике и подготовке к ЕГЭ."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        full_text = response.choices[0].message.content
        
        # Разделяем текст на условие, решение и ответ
        condition = ""
        solution = ""
        answer = ""
        
        condition_marker = "Условие задачи:"
        solution_marker = "Решение:"
        answer_marker = "Ответ:"
        
        # Находим индексы маркеров
        cond_idx = full_text.find(condition_marker)
        sol_idx = full_text.find(solution_marker)
        ans_idx = full_text.find(answer_marker)
        
        if cond_idx != -1:
            if sol_idx != -1:
                condition = full_text[cond_idx + len(condition_marker):sol_idx].strip()
            elif ans_idx != -1:
                 condition = full_text[cond_idx + len(condition_marker):ans_idx].strip()
            else:
                condition = full_text[cond_idx + len(condition_marker):].strip()
                
        if sol_idx != -1:
            if ans_idx != -1:
                solution = full_text[sol_idx + len(solution_marker):ans_idx].strip()
            else:
                solution = full_text[sol_idx + len(solution_marker):].strip()
                
        if ans_idx != -1:
            answer = full_text[ans_idx + len(answer_marker):].strip()

        # Если не удалось распарсить, сохраняем весь текст в условии
        if not condition and not solution and not answer:
             condition = full_text
             solution = "Не удалось извлечь решение."
             answer = "Не удалось извлечь ответ."
        
        return {
            "task_type": task_type,
            "full_text": full_text, # Сохраняем полный текст для базы данных
            "task_condition": condition,
            "task_solution": solution,
            "task_answer": answer,
            "task_info": task_info
        }
        
    except Exception as e:
        print(f"Ошибка при генерации задачи: {str(e)}")
        raise 