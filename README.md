# Ultimate Guitar Downloader

Скрипт для скачивания табулатур с сайта Ultimate Guitar.

⚠️ **ВАЖНО**: Для скачивания табулатур теперь требуется авторизация на сайте Ultimate Guitar.

## 🎉 Последнее обновление

✅ **Исправлено извлечение данных табулатур**: Скрипт теперь правильно работает с новой архитектурой Ultimate Guitar (SPA - Single Page Application). Данные извлекаются из встроенного JSON вместо поиска прямых ссылок в HTML.

## Установка зависимостей

### В nix-shell:
```bash
nix-shell  # Использует shell.nix для автоматической настройки окружения
```

### Или через pip:
```bash
pip install httpx
```

## Использование

### 1. Настройка авторизации (обязательно)

Создайте шаблон для cookies:
```bash
python main.py --create-cookies-template
```

Затем отредактируйте файл `cookies_sample.json` и переименуйте его в `cookies.json`. 

**Как получить cookies:**
1. Войдите в свой аккаунт на Ultimate Guitar
2. Откройте Developer Tools (F12)
3. Перейдите на вкладку Application/Storage → Cookies
4. Скопируйте значения cookies в файл

📖 **Подробная инструкция**: см. файл `COOKIES_GUIDE.md`

### 2. Запуск скачивания

```bash
python main.py input_file.txt --cookies cookies.json
```

где `input_file.txt` содержит URL-адреса табулатур (по одному на строку).

### Пример input_file.txt:
```
https://tabs.ultimate-guitar.com/tab/ghost/kaisarion-guitar-pro-4104691
https://tabs.ultimate-guitar.com/tab/violent-femmes/blister-in-the-sun-power-316513
```

## Параметры командной строки

- `input` - Файл со списком URL-адресов табулатур
- `--cookies`, `-c` - Путь к файлу с cookies (JSON формат)
- `--create-cookies-template` - Создать шаблон файла cookies
- `--help-cookies` - Подробная помощь по cookies
- `--test-cookies` - Проверить cookies файл
- `--help`, `-h` - Показать справку

## Особенности

- ✅ Поддержка авторизации через cookies
- ✅ **Новое**: Извлечение данных из JSON (работает с SPA архитектурой UG)
- ✅ Автоматическое извлечение токенов скачивания
- ✅ Поддержка Guitar Pro и Power Tab файлов
- ✅ Сохранение файлов с правильными именами
- ✅ Подробная информация об ошибках
- ✅ Прогресс-бар и статистика
- ✅ **Новое**: Развитое nix-shell окружение для разработки

## Отладка и разработка

```bash
# Войти в development окружение
nix-shell

# Отладка извлечения данных
python debug_example.py

# Анализ структуры страниц UG
python analyze_page.py

# Интерактивная отладка
pudb main.py
python -m ipdb main.py
```

## Возможные проблемы

### "Successfully constructed download URL" но "Got HTML response instead of file"
✅ **Это нормально!** Скрипт правильно извлекает данные, но для скачивания нужны cookies авторизации.

### "No download token found on page"
❌ Старая проблема - исправлена в новой версии.

### "Got HTML response instead of file"
Ваши cookies устарели или неправильные. Обновите файл cookies.

### Ошибки 403/401
Проверьте правильность cookies и что у вас есть права на скачивание.

## Безопасность

⚠️ Не делитесь файлом `cookies.json` - он содержит данные вашей сессии!

Добавьте в `.gitignore`:
```
cookies.json
cookies_*.json
output/
```

## Структура проекта

```
ultimate-guitar-downloader/
├── main.py                 # Основной скрипт
├── shell.nix              # Nix окружение для разработки
├── extract_cookies.py     # Helper для создания cookies
├── debug_example.py       # Отладочные функции
├── analyze_page.py        # Анализатор структуры страниц UG
├── requirements.txt       # Зависимости Python
├── COOKIES_GUIDE.md       # Подробная инструкция по cookies
├── QUICK_START.md         # Быстрый старт
├── in.txt                 # Пример входного файла
├── cookies_sample.json    # Шаблон файла cookies
└── output/                # Папка для скачанных файлов
```
