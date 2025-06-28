#!/usr/bin/env python3
"""
Пример скрипта для демонстрации отладки Ultimate Guitar Downloader
"""

# Для использования icecream отладочной библиотеки
try:
    from icecream import ic
    ic.configureOutput(prefix='🐞 DEBUG: ')
except ImportError:
    # Fallback если icecream не установлен
    def ic(*args):
        print("DEBUG:", *args)

import json
from main import UGDownloader

def debug_cookies_parsing():
    """
    Отладка парсинга cookies
    """
    ic("Начинаем отладку парсинга cookies")
    
    # Пример cookies для тестирования
    test_cookies = {
        "UGSESSION": "test_session_123",
        "_ug_session_id": "test_id_456",
        "bbsessionhash": "test_hash_789"
    }
    
    ic(test_cookies)
    
    # Сохраняем тестовые cookies
    with open('debug_cookies.json', 'w') as f:
        json.dump(test_cookies, f, indent=2)
    
    ic("Тестовые cookies сохранены в debug_cookies.json")
    
    # Создаем downloader для тестирования
    downloader = UGDownloader('debug_cookies.json')
    ic(f"Cookies загружены: {len(downloader.cookies)} штук")
    
    return downloader

def debug_headers():
    """
    Отладка HTTP заголовков
    """
    ic("Отладка HTTP заголовков")
    
    downloader = UGDownloader()
    headers = downloader.headers
    
    ic("Используемые заголовки:")
    for key, value in headers.items():
        ic(f"{key}: {value}")

def debug_url_extraction():
    """
    Отладка извлечения токенов из URL
    """
    ic("Отладка извлечения токенов с новой логикой JSON")
    
    test_url = "https://tabs.ultimate-guitar.com/tab/ghost/kaisarion-guitar-pro-4104691"
    ic(f"Тестовый URL: {test_url}")
    
    # Здесь можно добавить breakpoint для пошаговой отладки
    # import ipdb; ipdb.set_trace()
    
    downloader = UGDownloader()
    
    print("\n" + "="*50)
    print("ОТЛАДОЧНАЯ ИНФОРМАЦИЯ - Новая JSON логика")
    print("="*50)
    print(f"URL для тестирования: {test_url}")
    print(f"Headers: {len(downloader.headers)} заголовков")
    print(f"Cookies: {len(downloader.cookies)} cookies")
    
    # Тестируем новую функцию извлечения
    print("\nТестируем get_download_token_from_page...")
    try:
        download_url = downloader.get_download_token_from_page(test_url)
        if download_url:
            ic(f"✅ Успешно извлечен URL: {download_url}")
        else:
            ic("❌ Не удалось извлечь URL")
    except Exception as e:
        ic(f"❌ Ошибка при извлечении: {e}")
    
    print("="*50)

if __name__ == "__main__":
    print("🐞 ОТЛАДОЧНЫЙ СКРИПТ Ultimate Guitar Downloader")
    print("=" * 60)
    
    # Выберите, что отлаживать:
    print("Доступные отладочные функции:")
    print("1. debug_cookies_parsing() - отладка cookies")
    print("2. debug_headers() - отладка HTTP заголовков") 
    print("3. debug_url_extraction() - отладка извлечения токенов")
    print()
    
    print("Запуск всех отладочных функций...")
    
    try:
        debug_cookies_parsing()
        print("\n" + "-"*40)
        
        debug_headers()
        print("\n" + "-"*40)
        
        debug_url_extraction()
        
    except Exception as e:
        ic(f"Ошибка в отладке: {e}")
        # Для детальной отладки можно включить:
        # import traceback
        # traceback.print_exc()
    
    print("\n🎉 Отладка завершена!")
    print("\nДля интерактивной отладки используйте:")
    print("  pudb debug_example.py")
    print("  python -m ipdb debug_example.py")
    print("\nИли установите breakpoint в коде:")
    print("  import ipdb; ipdb.set_trace()") 