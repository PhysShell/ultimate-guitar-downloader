# Быстрый старт

## 1. Получите cookies
Зайдите на Ultimate Guitar и войдите в аккаунт, затем:

### Самый простой способ:
```bash
python extract_cookies.py
```
Скрипт поможет пошагово создать файл cookies.

### Альтернатива:
1. `python main.py --create-cookies-template` - создать шаблон
2. F12 → Application → Cookies → https://www.ultimate-guitar.com
3. Скопировать значения из браузера в `cookies_sample.json`
4. Переименовать в `cookies.json`

## 2. Найдите эти cookies в браузере:
- **UGSESSION** (самый важный!)
- **_ug_session_id** 
- **bbsessionhash**
- **ug_auth_provider** (если вход через Google)
- **ug_unified_id**

## 3. Проверьте cookies
```bash
python main.py --test-cookies cookies.json
```

## 4. Скачайте табулатуры
```bash
python main.py in.txt --cookies cookies.json
```

## Помощь
- `python main.py --help-cookies` - подробная помощь
- `python main.py --help` - все опции 