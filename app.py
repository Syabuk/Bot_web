import os
import json
import hashlib
from datetime import datetime
from flask import Flask, render_template, send_file, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app)

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_FILE = os.path.join(BASE_DIR, 'articles', 'articles_data.json')
FILES_FOLDER = os.path.join(BASE_DIR, 'static', 'files')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'articles_images')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'png', 'zip', 'rar'}

# Создаем необходимые папки
os.makedirs(FILES_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(ARTICLES_FILE), exist_ok=True)

# Данные статей


def load_articles():
    """Загрузка статей из JSON файла"""
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_articles()


def save_articles(articles):
    """Сохранение статей в JSON файл"""
    with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def get_default_articles():
    """Получение демо-статей"""
    return [
        {
            'id': 1,
            'title': 'Добро пожаловать в наш блог!',
            'description': 'Здесь вы найдете полезные статьи и материалы',
            'content': '''
# Добро пожаловать!

Это первая статья в нашем блоге. Здесь мы будем делиться полезной информацией и файлами.

## Что вы найдете здесь?

- 📝 **Интересные статьи** на различные темы
- 📥 **Полезные файлы** для скачивания
- 🎯 **Актуальные новости** и обновления
- 💡 **Советы и рекомендации**

## Как пользоваться сайтом?

1. Читайте статьи на главной странице
2. Скачивайте файлы из материалов
3. Следите за обновлениями

Спасибо, что вы с нами! 🚀
            ''',
            'image': 'https://via.placeholder.com/800x400/0088cc/ffffff?text=Welcome',
            'date': '2024-01-15',
            'author': 'Admin',
            'category': 'Новости',
            'files': ['user_guide.txt', 'info.txt'],
            'views': 156
        },
        {
            'id': 2,
            'title': 'Как скачивать файлы в Telegram Mini App',
            'description': 'Подробная инструкция по скачиванию файлов',
            'content': '''
# Инструкция по скачиванию файлов

В этом руководстве мы расскажем, как правильно скачивать файлы через наше приложение.

## Пошаговая инструкция

### Шаг 1: Найдите нужный файл
Все файлы находятся в разделе "Файлы" или прикреплены к статьям.

### Шаг 2: Нажмите на кнопку скачивания
Нажмите на кнопку "📥 Скачать" рядом с файлом.

### Шаг 3: Подтвердите скачивание
В браузере появится запрос на сохранение файла.

### Шаг 4: Откройте файл
Файл сохранится в папку "Загрузки" на вашем устройстве.

## Поддерживаемые форматы

- 📄 Текстовые файлы (.txt)
- 📑 Документы (.pdf, .doc, .docx)
- 🖼️ Изображения (.jpg, .png)
- 🗜️ Архивы (.zip, .rar)

## Возможные проблемы

Если файл не скачивается:
1. Проверьте подключение к интернету
2. Обновите страницу
3. Попробуйте другой браузер

Успешного использования! 🎉
            ''',
            'image': 'https://via.placeholder.com/800x400/28a745/ffffff?text=Download+Guide',
            'date': '2024-01-20',
            'author': 'Support Team',
            'category': 'Инструкции',
            'files': ['guide.pdf', 'example.txt'],
            'views': 89
        },
        {
            'id': 3,
            'title': 'Полезные советы для начинающих',
            'description': 'Советы и рекомендации для новых пользователей',
            'content': '''
# Советы для начинающих

Мы подготовили несколько полезных советов, которые помогут вам эффективно использовать наше приложение.

## 💡 Совет 1: Используйте поиск

На главной странице есть поиск по статьям - это поможет быстро найти нужную информацию.

## 💡 Совет 2: Сохраняйте важные файлы

Все скачанные файлы сохраняются на вашем устройстве. Рекомендуем создавать отдельную папку для них.

## 💡 Совет 3: Следите за обновлениями

Мы регулярно добавляем новые статьи и файлы. Подпишитесь на уведомления, чтобы ничего не пропустить.

## 💡 Совет 4: Делитесь с друзьями

Понравилась статья? Поделитесь ссылкой с друзьями через Telegram!

## 💡 Совет 5: Оставляйте отзывы

Ваше мнение важно для нас. Пишите свои предложения в поддержку.

Следуйте этим советам и используйте приложение с удовольствием! 😊
            ''',
            'image': 'https://via.placeholder.com/800x400/ffc107/000000?text=Tips',
            'date': '2024-01-25',
            'author': 'Expert',
            'category': 'Советы',
            'files': ['tips.txt'],
            'views': 234
        }
    ]

# Создаем демо-файлы


def create_demo_files():
    """Создание демонстрационных файлов"""

    files_data = {
        'user_guide.txt': 'Руководство пользователя\n\n1. Откройте приложение\n2. Выберите статью\n3. Скачайте файлы',
        'info.txt': 'Информация о приложении\nВерсия 1.0.0\nДата создания: 2024',
        'guide.pdf': 'PDF руководство (демо версия)\n\nПодробная инструкция будет добавлена позже',
        'example.txt': 'Пример текстового файла\nЭто демонстрационный файл для скачивания',
        'tips.txt': 'Полезные советы:\n- Регулярно проверяйте обновления\n- Сохраняйте важные файлы\n- Делитесь с друзьями'
    }

    for filename, content in files_data.items():
        file_path = os.path.join(FILES_FOLDER, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)


# Инициализация данных
create_demo_files()
articles = load_articles()


@app.route('/')
def index():
    """Главная страница со списком статей"""
    return render_template('index.html', articles=articles)


@app.route('/article/<int:article_id>')
def article(article_id):
    """Страница статьи"""
    article_data = next((a for a in articles if a['id'] == article_id), None)
    if not article_data:
        abort(404)

    # Увеличиваем счетчик просмотров
    article_data['views'] += 1
    save_articles(articles)

    # Конвертируем Markdown в HTML
    article_data['content_html'] = markdown.markdown(article_data['content'])

    return render_template('article.html', article=article_data)


@app.route('/files')
def files_page():
    """Страница со всеми файлами"""
    all_files = []

    # Собираем все файлы из статей
    for article in articles:
        for filename in article.get('files', []):
            file_path = os.path.join(FILES_FOLDER, filename)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                all_files.append({
                    'name': filename,
                    'article_title': article['title'],
                    'article_id': article['id'],
                    'size': format_file_size(file_size),
                    'url': f'/download/{filename}'
                })

    return render_template('files.html', files=all_files)


@app.route('/api/articles')
def api_articles():
    """API для получения списка статей"""
    return jsonify(articles)


@app.route('/api/article/<int:article_id>')
def api_article(article_id):
    """API для получения конкретной статьи"""
    article_data = next((a for a in articles if a['id'] == article_id), None)
    if not article_data:
        return jsonify({'error': 'Article not found'}), 404
    return jsonify(article_data)


@app.route('/api/files')
def api_files():
    """API для получения списка файлов"""
    files_list = []

    for filename in os.listdir(FILES_FOLDER):
        file_path = os.path.join(FILES_FOLDER, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            files_list.append({
                'name': filename,
                'size': format_file_size(file_size),
                'url': f'/download/{filename}'
            })

    return jsonify(files_list)


@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание файла"""
    file_path = os.path.join(FILES_FOLDER, filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/search')
def search_articles():
    """Поиск статей"""
    query = request.args.get('q', '').lower()

    if not query:
        return jsonify(articles)

    results = []
    for article in articles:
        if (query in article['title'].lower() or
            query in article['description'].lower() or
                query in article['content'].lower()):
            results.append(article)

    return jsonify(results)


@app.route('/api/categories')
def get_categories():
    """Получение категорий"""
    categories = list(set(article['category'] for article in articles))
    return jsonify(categories)


def format_file_size(size):
    """Форматирование размера файла"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ═══════════════════════════════════════════════
    📱 Telegram MiniWeb Blog App запущен!
    🎨 Красивый блог со статьями и файлами
    🌐 http://localhost:{port}
    📝 Статей: {len(articles)}
    📁 Файлов: {len(os.listdir(FILES_FOLDER))}
    ═══════════════════════════════════════════════
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
