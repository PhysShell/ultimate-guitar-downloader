# Устранение проблем / Troubleshooting

## Проблема: "Got HTML response instead of file - likely need to be logged in"

Эта ошибка означает, что Ultimate Guitar возвращает HTML страницу вместо файла. Это происходит из-за проблем с авторизацией.

### Диагностика

1. **Запустите диагностику авторизации:**
   ```bash
   python debug_auth.py cookies.json
   ```

2. **Проверьте файлы отладки:**
   - `headers.txt` - заголовки ответа сервера
   - `text.txt` - содержимое HTML ответа

### Основные индикаторы проблем

В файле `headers.txt` ищите:
- `x-ug-unified-id: 0` - означает анонимного пользователя ❌
- `x-ug-unified-id: [число > 0]` - означает авторизованного пользователя ✅

### Решения

#### 1. Обновите cookies

Ваши cookies могли устареть. Ultimate Guitar cookies имеют короткое время жизни (часто 5 минут).

**Шаги:**
1. Откройте браузер и зайдите на https://www.ultimate-guitar.com/
2. Авторизуйтесь в вашем аккаунте
3. Перейдите на любую Pro табулатуру
4. Экспортируйте cookies заново

#### 2. Проверьте критичные cookies

Убедитесь, что в `cookies.json` есть:
- `UGSESSION`
- `SESSIONUG` 
- `_ug_session_id`
- `ug_unified_id` (должен быть НЕ 0)
- `bbuserid`
- `bbpassword`

#### 3. Экспорт cookies через DevTools

**Chrome/Firefox:**
1. Откройте DevTools (F12)
2. Перейдите на вкладку Application/Storage
3. Выберите Cookies → https://www.ultimate-guitar.com
4. Скопируйте ВСЕ cookies для этого домена

**Или используйте встроенный инструмент:**
```bash
python extract_cookies.py
```

#### 4. Проверьте формат cookies

Убедитесь, что `cookies.json` имеет правильный формат:
```json
{
    "UGSESSION": "abc123...",
    "SESSIONUG": "def456...",
    "_ug_session_id": "ghi789...",
    "ug_unified_id": "12345",
    "bbuserid": "67890",
    "bbpassword": "xyz..."
}
```

#### 5. Используйте свежую браузерную сессию

1. Закройте все вкладки Ultimate Guitar
2. Очистите cookies браузера для UG
3. Зайдите на сайт заново
4. Авторизуйтесь
5. Экспортируйте cookies

### Команды для диагностики

```bash
# Полная диагностика авторизации
python debug_auth.py cookies.json

# Тест конкретного URL
python main.py --test-cookies cookies.json

# Анализ структуры страницы
python analyze_page.py "https://tabs.ultimate-guitar.com/tab/artist/song-123456"

# Базовый тест загрузки
python main.py "https://tabs.ultimate-guitar.com/tab/artist/song-123456"
```

### Дополнительные проверки

#### Проверка сетевого подключения
```bash
curl -I https://www.ultimate-guitar.com/
```

#### Проверка cookies в браузере
1. Зайдите на https://www.ultimate-guitar.com/ 
2. Откройте DevTools → Application → Cookies
3. Убедитесь, что cookies установлены

#### Проверка Pro статуса
Убедитесь, что ваш аккаунт имеет Pro подписку, необходимую для скачивания табулатур.

### Часто задаваемые вопросы

**Q: Cookies быстро устаревают**
A: Ultimate Guitar использует короткоживущие session cookies. Экспортируйте их непосредственно перед использованием скрипта.

**Q: Получаю 403 Forbidden**
A: Это может означать, что UG детектирует автоматизированные запросы. Попробуйте изменить User-Agent или добавить задержки между запросами.

**Q: Получаю капчу**
A: Ultimate Guitar может показывать капчу при подозрительной активности. Используйте браузер для её решения, затем экспортируйте новые cookies.

**Q: Нет Pro подписки**
A: Для скачивания Guitar Pro и Power Tab файлов нужна Pro подписка на Ultimate Guitar.

### Логи отладки

Скрипт автоматически создает отладочные файлы:
- `headers.txt` - HTTP заголовки ответа
- `text.txt` - HTML содержимое (если получен HTML вместо файла)

Эти файлы помогают диагностировать проблемы с авторизацией. 