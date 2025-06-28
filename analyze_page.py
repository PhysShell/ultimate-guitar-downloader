#!/usr/bin/env python3
"""
Анализатор страниц Ultimate Guitar для поиска JSON данных
"""

import httpx
import re
import json
import html
from main import UGDownloader

def analyze_ug_page(url: str):
    """
    Анализирует страницу UG и ищет различные паттерны данных
    """
    print(f"🔍 Анализ страницы: {url}")
    print("=" * 60)
    
    downloader = UGDownloader()
    
    with httpx.Client(cookies=downloader.cookies, timeout=30.0) as client:
        headers = downloader.headers.copy()
        headers['Referer'] = 'https://www.ultimate-guitar.com/'
        
        try:
            response = client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            page_content = response.text
            print(f"📄 Размер страницы: {len(page_content)} символов")
            print(f"📊 Статус ответа: {response.status_code}")
            
            # Ищем различные JSON паттерны
            patterns_to_check = [
                ("data-content", r'data-content="({[^"]*})"'),
                ("data-content with quotes", r'data-content="({&quot;[^"]*})"'),
                ("window.UGAPP.store.page", r'window\.UGAPP\.store\.page\s*=\s*({.+?});'),
                ("window.UGAPP.store", r'window\.UGAPP\.store\s*=\s*({.+?});'),
                ("js-store class", r'<div[^>]*class="[^"]*js-store[^"]*"[^>]*>([^<]+)</div>'),
                ("data-js attr", r'data-js="([^"]*)"'),
                ("JSON in script tag", r'<script[^>]*>.*?(\{[^}]*store[^}]*\})[^<]*</script>'),
                ("Store object", r'store\s*[:=]\s*(\{[^}]+\})'),
                ("Page data", r'pageData\s*[:=]\s*(\{[^}]+\})'),
                ("Tab data", r'tabData\s*[:=]\s*(\{[^}]+\})'),
            ]
            
            print("\n🎯 Поиск JSON паттернов:")
            print("-" * 40)
            
            found_patterns = []
            
            for pattern_name, pattern in patterns_to_check:
                matches = re.findall(pattern, page_content, re.DOTALL | re.IGNORECASE)
                if matches:
                    print(f"✅ {pattern_name}: найдено {len(matches)} совпадений")
                    found_patterns.append((pattern_name, matches))
                    
                    # Показываем первые несколько символов найденного JSON
                    for i, match in enumerate(matches[:2]):  # Только первые 2
                        preview = match[:200] + "..." if len(match) > 200 else match
                        print(f"   Совпадение {i+1}: {preview}")
                else:
                    print(f"❌ {pattern_name}: не найдено")
            
            # Дополнительный анализ: ищем любые объекты с "id" 
            print(f"\n🔑 Поиск объектов с 'id':")
            print("-" * 40)
            
            id_patterns = [
                r'"id"\s*:\s*"([^"]+)"',
                r'"id"\s*:\s*(\d+)',
                r'id["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            all_ids = set()
            for pattern in id_patterns:
                ids = re.findall(pattern, page_content)
                all_ids.update(str(id_val) for id_val in ids)
            
            if all_ids:
                print(f"Найдено {len(all_ids)} уникальных ID:")
                for i, id_val in enumerate(sorted(all_ids)[:10]):  # Первые 10
                    print(f"  {i+1}. {id_val}")
                if len(all_ids) > 10:
                    print(f"  ... и еще {len(all_ids) - 10}")
            else:
                print("ID не найдены")
            
            # Ищем тип табулатуры
            print(f"\n🎵 Поиск информации о типе табулатуры:")
            print("-" * 40)
            
            tab_types = [
                "Guitar Pro", "Power Tab", "guitar pro", "power tab",
                "guitarpro", "powertab", ".gp", ".ptb"
            ]
            
            for tab_type in tab_types:
                if tab_type.lower() in page_content.lower():
                    print(f"✅ Найден тип: {tab_type}")
                    
                    # Ищем контекст вокруг этого типа
                    pattern = rf'.{{0,100}}{re.escape(tab_type)}.{{0,100}}'
                    context_matches = re.findall(pattern, page_content, re.IGNORECASE)
                    if context_matches:
                        print(f"   Контекст: {context_matches[0][:200]}...")
            
            # Анализ заголовков ответа
            print(f"\n📋 Заголовки ответа:")
            print("-" * 40)
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'set-cookie', 'location']:
                    print(f"{key}: {value}")
            
            return found_patterns
            
        except Exception as e:
            print(f"❌ Ошибка при анализе: {e}")
            return []

def test_json_parsing(json_data, pattern_name):
    """
    Тестирует парсинг найденного JSON
    """
    print(f"\n🧪 Тестирование JSON из {pattern_name}")
    print("-" * 40)
    
    try:
        # Пробуем декодировать HTML entities
        if '&quot;' in json_data:
            json_data = html.unescape(json_data)
            print("✅ HTML entities декодированы")
        
        # Пробуем парсить JSON
        parsed = json.loads(json_data)
        print(f"✅ JSON успешно распарсен")
        print(f"📊 Корневые ключи: {list(parsed.keys())[:10]}")
        
        # Ищем табулатурные данные
        def find_in_dict(d, target_keys, path=""):
            results = []
            if isinstance(d, dict):
                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key
                    if key.lower() in [t.lower() for t in target_keys]:
                        results.append((current_path, value))
                    if isinstance(value, (dict, list)):
                        results.extend(find_in_dict(value, target_keys, current_path))
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    current_path = f"{path}[{i}]"
                    results.extend(find_in_dict(item, target_keys, current_path))
            return results
        
        # Ищем ключевые поля
        search_keys = ['id', 'tab_id', 'wiki_tab', 'type', 'download', 'file']
        found_keys = find_in_dict(parsed, search_keys)
        
        if found_keys:
            print(f"🎯 Найдены ключевые поля:")
            for path, value in found_keys[:10]:  # Первые 10
                print(f"  {path}: {str(value)[:100]}")
        
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return None

if __name__ == "__main__":
    test_url = "https://tabs.ultimate-guitar.com/tab/ghost/kaisarion-guitar-pro-4104691"
    
    print("🔍 АНАЛИЗАТОР СТРАНИЦ ULTIMATE GUITAR")
    print("=" * 60)
    
    patterns = analyze_ug_page(test_url)
    
    # Тестируем найденные JSON данные
    for pattern_name, matches in patterns:
        for i, match in enumerate(matches[:1]):  # Только первое совпадение
            test_json_parsing(match, f"{pattern_name}[{i}]") 