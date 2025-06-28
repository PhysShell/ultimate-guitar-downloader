# Как получить cookies для скачивания с Ultimate Guitar

Поскольку Ultimate Guitar теперь требует авторизации для скачивания табулатур, вам нужно предоставить скрипту ваши cookies сессии.

## Пошаговая инструкция:

### 1. Войдите в свой аккаунт на Ultimate Guitar
- Откройте https://www.ultimate-guitar.com/
- Войдите через Google или любым другим способом

### 2. Откройте Developer Tools в браузере
- Chrome/Edge: F12 или Ctrl+Shift+I
- Firefox: F12 или Ctrl+Shift+I

### 3. Найдите cookies
- Перейдите на вкладку **Application** (Chrome) или **Storage** (Firefox)
- В левой панели найдите **Cookies** и разверните
- Выберите `https://www.ultimate-guitar.com`

### 4. Скопируйте важные cookies
Из ваших скриншотов нам нужны следующие cookies:
- `UGSESSION` или `SESSIONUG` (основная сессия - очень важно!)
- `_ug_session_id` (ID сессии UG)
- `bbsessionhash` (session hash форума)
- `_pro_buySession` (Pro подписка - если есть)
- `ug_auth_provider` (провайдер авторизации, например Google)
- `ug_unified_id` (унифицированный ID пользователя)
- `bbuserid` и `bbpassword` (ID и хеш пароля форума)
- `_ga` (Google Analytics)

### 5. Создайте файл cookies.json

Сначала создайте шаблон:
```bash
python main.py --create-cookies-template
```

Затем отредактируйте файл `cookies_sample.json` и переименуйте его в `cookies.json`:

```json
{
  "session_id": "ваш_реальный_session_id_здесь",
  "user_token": "ваш_реальный_токен_здесь",
  "_ga": "GA1.2.ваш_google_analytics_id",
  "_gid": "GA1.2.ваш_google_analytics_session_id"
}
```

### 6. Используйте скрипт с cookies

```bash
python main.py in.txt --cookies cookies.json
```

## Альтернативный способ через Network Inspector

1. На странице Ultimate Guitar откройте Developer Tools
2. Перейдите на вкладку **Network**
3. Попробуйте скачать любую табулатуру
4. В списке запросов найдите запрос к `tab/download`
5. Щелкните по нему правой кнопкой
6. Выберите **Copy** → **Copy as cURL**
7. Из скопированной команды извлеките значения cookies

## Возможные проблемы

### Cookies устарели
Если скачивание не работает, возможно cookies устарели. Повторите процедуру получения cookies.

### Неправильные cookies
Убедитесь, что вы скопировали cookies именно с домена `ultimate-guitar.com`, а не с других сайтов.

### 403/401 ошибки
Это означает, что сервер не принимает вашу авторизацию. Проверьте:
- Правильность cookies
- Что вы авторизованы на сайте
- Что у вас есть подписка (если требуется)

## Пример правильного файла cookies.json

```json
{
  "UGSESSION": "ваше_значение_ugsession",
  "SESSIONUG": "ваше_значение_sessionug",
  "_ug_session_id": "ваш_ug_session_id",
  "bbsessionhash": "ваш_bbsessionhash",
  "_pro_buySession": "ваша_pro_подписка",
  "ug_auth_provider": "google",
  "ug_unified_id": "ваш_unified_id",
  "bbuserid": "12345",
  "bbpassword": "хеш_пароля_форума",
  "_ga": "GA1.2.1234567890.1234567890"
}
```

## Простые способы создания cookies.json

### Способ 1: Интерактивный helper
```bash
python extract_cookies.py
```
Этот скрипт поможет вам пошагово создать файл cookies.

### Способ 2: Автоматический шаблон
```bash
python main.py --create-cookies-template
```
Создаст шаблон `cookies_sample.json`, который нужно заполнить и переименовать.

### Способ 3: Подробная помощь
```bash
python main.py --help-cookies
```
Покажет детальные инструкции по извлечению cookies.

### Способ 4: Тестирование cookies
```bash
python main.py --test-cookies cookies.json
```
Проверит, работают ли ваши cookies.

## Безопасность

⚠️ **ВАЖНО**: Не делитесь файлом cookies.json с другими людьми! Он содержит данные вашей сессии, которые дают доступ к вашему аккаунту. 