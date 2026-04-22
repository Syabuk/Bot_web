import os
import mimetypes
from flask import Flask, render_template, send_file, jsonify, request, send_from_directory
from flask_cors import CORS
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'files')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Настройка MIME типов для правильного скачивания на мобильных
mimetypes.add_type('application/octet-stream', '.txt')
mimetypes.add_type('application/pdf', '.pdf')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('application/zip', '.zip')

# Список файлов для скачивания (можно добавлять свои)
AVAILABLE_FILES = {
    'user_guide.txt': {
        'name': '📖 Руководство пользователя',
        'description': 'Подробная инструкция по использованию приложения',
        'category': 'Документация'
    },
    'example.pdf': {
        'name': '📄 Пример PDF файла',
        'description': 'Демонстрационный PDF документ',
        'category': 'Документы'
    },
    'info.txt': {
        'name': 'ℹ️ Информационный файл',
        'description': 'Основная информация о приложении',
        'category': 'Информация'
    }
}

def create_demo_files():
    """Создание демонстрационных файлов"""
    
    # Создаем user_guide.txt
    guide_path = os.path.join(UPLOAD_FOLDER, 'user_guide.txt')
    if not os.path.exists(guide_path):
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write("""РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ
================================

Добро пожаловать в Telegram MiniWeb App!

Основные функции:
1. Просмотр информации о приложении
2. Скачивание файлов различных форматов
3. Адаптивный интерфейс для мобильных устройств

Как скачать файл:
- Нажмите на кнопку "Скачать" рядом с нужным файлом
- Файл автоматически сохранится на ваше устройство
- Откройте файл в соответствующем приложении

Поддержка: @your_support_bot
Версия: 1.0.0
""")
    
    # Создаем info.txt
    info_path = os.path.join(UPLOAD_FOLDER, 'info.txt')
    if not os.path.exists(info_path):
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write("""ИНФОРМАЦИЯ О ПРИЛОЖЕНИИ
================================

Название: Telegram MiniWeb App
Версия: 1.0.0
Разработчик: Telegram MiniApps Team

Возможности:
✓ Просмотр информации
✓ Скачивание файлов
✓ Мобильная оптимизация
✓ Поддержка темной темы
✓ Интеграция с Telegram

Технологии:
- Python Flask
- HTML5/CSS3
- Telegram WebApp API

Контакты для связи:
Email: support@example.com
Telegram: @support_bot
""")
    
    # Создаем простой PDF (как текст для демо)
    pdf_path = os.path.join(UPLOAD_FOLDER, 'example.pdf')
    if not os.path.exists(pdf_path):
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write("""ДЕМОНСТРАЦИОННЫЙ PDF ДОКУМЕНТ
================================

Это пример документа в формате PDF.
В реальном приложении здесь может быть любой PDF файл.

Содержание:
1. Введение
2. Основные возможности
3. Инструкция по использованию
4. Техническая поддержка

Для создания реального PDF используйте библиотеки типа reportlab.
""")

# Создаем демо файлы при запуске
create_demo_files()

def get_file_size(filepath):
    """Получение размера файла в человекочитаемом формате"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    """API для получения списка файлов"""
    files_list = []
    
    for file_id, file_info in AVAILABLE_FILES.items():
        file_path = os.path.join(UPLOAD_FOLDER, file_id)
        if os.path.exists(file_path):
            file_size = get_file_size(file_path)
        else:
            file_size = "0 B"
        
        files_list.append({
            'id': file_id,
            'name': file_info['name'],
            'description': file_info['description'],
            'category': file_info['category'],
            'size': file_size,
            'url': f'/download/{file_id}'
        })
    
    return jsonify(files_list)

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание файла с правильными заголовками для мобильных"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Определяем MIME тип
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Отправляем файл с заголовками для мобильных устройств
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )
        
        # Добавляем заголовки для корректной работы на мобильных
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/info')
def app_info():
    """API с информацией о приложении"""
    # Подсчитываем реальное количество файлов
    files_count = len([f for f in os.listdir(UPLOAD_FOLDER) 
                      if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])
    
    return jsonify({
        'name': 'Telegram MiniWeb App',
        'version': '1.0.0',
        'description': 'Мобильное приложение для Telegram с возможностью скачивания файлов',
        'files_available': files_count,
        'platform': 'Mobile Optimized',
        'features': [
            'Просмотр информации',
            'Скачивание файлов',
            'Адаптивный дизайн',
            'Темная тема'
        ]
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Отдача статических файлов"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ═══════════════════════════════════════
    🚀 Telegram MiniWeb App запущен!
    📱 Оптимизировано для мобильных устройств
    🌐 http://localhost:{port}
    📁 Папка с файлами: {UPLOAD_FOLDER}
    ═══════════════════════════════════════
    """)
    app.run(host='0.0.0.0', port=port, debug=True)