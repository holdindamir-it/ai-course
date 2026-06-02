import os
import re

# Название папки, где лежат твои HTML-уроки
# Если скрипт лежит в той же папке, что и уроки, оставь "."
# Если уроки лежат, например, в "course_lessons_styled", замени на нее
SOURCE_DIR = "." 

# Имя итогового файла
OUTPUT_FILE = "all_lessons_compiled.txt"

def extract_clean_content(html_content):
    """Вытаскивает заголовок h1 и очищает контент урока от HTML-тегов"""
    # 1. Ищем название урока в теге <h1>
    h1_match = re.search(r'<h1>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
    lesson_title = h1_match.group(1).strip() if h1_match else "Урок без названия"
    # Очищаем заголовок от возможных внутренних HTML тегов
    lesson_title = re.sub(r'<[^>]+>', '', lesson_title)

    # 2. Вырезаем основной контент из <div class="lesson-content">...</div>
    content_match = re.search(r'<div class="lesson-content">(.*?)</div>', html_content, re.IGNORECASE | re.DOTALL)
    if content_match:
        body_html = content_match.group(1)
    else:
        # Если такого дива нет, берем все между body
        body_match = re.search(r'<body>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
        body_html = body_match.group(1) if body_match else html_content

    # 3. Базовое форматирование HTML элементов в читаемый текст
    text = body_html
    text = re.sub(r'</p>', '\n\n', text) # Разделяем абзацы
    text = re.sub(r'<li>', '  * ', text) # Делаем маркеры списков аккуратными
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<h1>|<h2>|<h3>|<h4>', '\n\n=== ', text) # Выделяем подзаголовки
    text = re.sub(r'</h1>|</h2>|</h3>|</h4>', ' ===\n', text)
    
    # 4. Полностью удаляем все оставшиеся HTML-теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # 5. Декодируем HTML-сущности (если они есть) и убираем лишние пробелы/пустые строки
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'\n\s*\n+', '\n\n', text).strip()
    
    return lesson_title, text

def main():
    compiled_data = []
    
    # Сканируем папку на наличие HTML файлов
    if not os.path.exists(SOURCE_DIR):
        print(f"Ошибка: Папка {SOURCE_DIR} не найдена.")
        return

    # Сортируем файлы по имени, чтобы уроки шли по порядку (0.1, 1.1, 1.2 и т.д.)
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.html')])
    
    if not files:
        print("В указанной папке не найдено HTML-файлов.")
        return

    print(f"Найдено {len(files)} файлов. Начинаю сборку...")

    for file_name in files:
        # Пропускаем служебные файлы, если они вдруг есть
        if file_name in ['index.html', 'dashboard.html']:
            continue
            
        file_path = os.path.join(SOURCE_DIR, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            title, clean_text = extract_clean_content(html_content)
            
            # Формируем красивый блок для каждого урока
            lesson_block = f"==================================================\n"
            lesson_block += f"ФАЙЛ: {file_name}\n"
            lesson_block += f"НАЗВАНИЕ: {title}\n"
            lesson_block += f"==================================================\n\n"
            lesson_block += f"{clean_text}\n\n"
            lesson_block += f"{'='*50}\n\n\n"
            
            compiled_data.append(lesson_block)
            print(f"[Успешно] Обработан: {file_name}")
            
        except Exception as e:
            print(f"[Ошибка] Не удалось прочитать {file_name}: {e}")

    # Записываем всё в один файл
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        out_f.writelines(compiled_data)

    print(f"\nГотово! Все уроки объединены в файл: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()