{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python и основные пакеты
    python311
    python311Packages.pip
    python311Packages.setuptools
    python311Packages.wheel
    
    # Основные зависимости проекта
    python311Packages.httpx
    
    # Инструменты для отладки и разработки
    python311Packages.ipdb      # улучшенный отладчик
    python311Packages.pudb      # полнофункциональный визуальный отладчик
    python311Packages.icecream  # удобная библиотека для отладочного вывода
    
    # Инструменты для тестирования
    python311Packages.pytest
    python311Packages.pytest-cov
    
    # Линтеры и форматеры кода
    python311Packages.black     # форматер кода
    python311Packages.flake8    # линтер
    python311Packages.mypy      # проверка типов
    python311Packages.isort     # сортировка импортов
    
    # Полезные инструменты для разработки
    python311Packages.requests  # может пригодиться как альтернатива httpx
    python311Packages.beautifulsoup4  # для парсинга HTML
    python311Packages.lxml      # быстрый XML/HTML парсер
    
    # Системные инструменты
    curl                        # для тестирования HTTP запросов
    jq                          # для работы с JSON
    tree                        # для просмотра структуры директорий
    
    # Git (если не установлен системно)
    git
  ];

  shellHook = ''
    echo "🎸 Ultimate Guitar Downloader Development Environment"
    echo "===================================================="
    echo "Python version: $(python --version)"
    echo "Available commands:"
    echo "  python main.py --help          # Показать справку"
    echo "  python extract_cookies.py      # Интерактивное создание cookies"
    echo "  python main.py --help-cookies  # Помощь с cookies"
    echo "  python main.py --test-cookies cookies.json  # Тест cookies"
    echo ""
    echo "Отладка:"
    echo "  pudb                           # Визуальный отладчик"
    echo "  python -m ipdb script.py       # ipdb отладчик"
    echo "  python -c 'import icecream; icecream.install()'  # ic() для отладки"
    echo ""
    echo "Качество кода:"
    echo "  black *.py                     # Форматирование кода"
    echo "  flake8 *.py                    # Проверка стиля"
    echo "  mypy *.py                      # Проверка типов"
    echo "  isort *.py                     # Сортировка импортов"
    echo ""
    echo "Тестирование:"
    echo "  pytest                         # Запуск тестов"
    echo "  curl -s 'https://www.ultimate-guitar.com' | head  # Тест подключения"
    echo ""
    
    # Настройка переменных окружения для отладки
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export PYTHONDONTWRITEBYTECODE=1  # Не создавать .pyc файлы
    export PYTHONUNBUFFERED=1         # Небуферизованный вывод
    
    # Создание необходимых директорий
    mkdir -p output
    
    # Информация о проекте
    if [ -f "README.md" ]; then
      echo "📖 Документация доступна в README.md и QUICK_START.md"
    fi
    
    if [ ! -f "cookies.json" ] && [ ! -f "cookies_sample.json" ]; then
      echo "⚠️  Не найден файл cookies. Создайте его командой:"
      echo "   python extract_cookies.py"
      echo "   или"
      echo "   python main.py --create-cookies-template"
    fi
    echo ""
  '';

  # Настройки для отладки в VS Code
  # Если используете VS Code, эти переменные помогут с интеграцией
  PYTHON_CONFIGURE_OPTS = "--enable-shared";
  
  # Для лучшей интеграции с debugger
  NIX_SHELL_PRESERVE_PROMPT = 1;
} 