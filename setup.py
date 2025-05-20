import subprocess
import sys
import os

def setup_environment():
    print("Начинаем установку зависимостей...")
    
    # Проверяем наличие виртуального окружения
    if not os.path.exists('.venv'):
        print("Создаем виртуальное окружение...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
    
    # Определяем путь к pip в зависимости от ОС
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('.venv', 'Scripts', 'pip')
    else:  # Linux/Mac
        pip_path = os.path.join('.venv', 'bin', 'pip')
    
    # Обновляем pip
    print("Обновляем pip...")
    subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
    
    # Устанавливаем зависимости
    print("Устанавливаем зависимости из requirements.txt...")
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    
    print("\nУстановка завершена успешно!")
    print("\nДля запуска приложения выполните:")
    if os.name == 'nt':  # Windows
        print(".venv\\Scripts\\streamlit run ege_generator.py")
    else:  # Linux/Mac
        print(".venv/bin/streamlit run ege_generator.py")

if __name__ == '__main__':
    try:
        setup_environment()
    except subprocess.CalledProcessError as e:
        print(f"Произошла ошибка при установке: {e}")
        sys.exit(1) 