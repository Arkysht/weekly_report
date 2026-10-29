# Weekly Report Bot

Telegram-бот, який щопонеділка збирає статистику з рекламних кабінетів **Meta Ads** і надсилає готові текстові звіти для клієнтів. Замінює ручну вибірку даних з Ads Manager та складання звітів.

## Можливості

- Збирає метрики за попередній тиждень (понеділок — неділя) по кожному рекламному кабінету через Meta Marketing API.
- Автоматично визначає тип кампанії (покупки, повідомлення, ліди) за ціллю кампанії, ціллю оптимізації або ключовими словами в назві.
- Рахує витрати, кількість результатів і ціну за результат.
- Додає витрати з початку місяця та поточну заборгованість кабінету.
- Підтримує індивідуальні шаблони звітів для окремих кабінетів: власні заголовки, секції, фільтри кампаній за ключовими словами та порожні поля для ручного заповнення.
- Якщо звіт по одному кабінету не вдався, надсилає повідомлення про помилку в чат і продовжує з наступним.

## Стек

- Python 3
- [aiogram 3](https://docs.aiogram.dev/): Telegram-бот
- [facebook_business](https://github.com/facebook/facebook-python-business-sdk): Meta Marketing API SDK
- asyncio

## Структура проєкту

```
weekly_report/
├── weekly_report.py               # основний скрипт
├── config_example.py              # приклад налаштувань (токени)
├── accounts_config_example.py     # приклад списку рекламних кабінетів
└── requirements.txt
```

Файли `config.py` та `accounts_config.py` містять секрети й дані клієнтів, тому вони додані в `.gitignore` і в репозиторії відсутні.

## Встановлення

Потрібен Python 3.10 або новіший.

```bash
git clone https://github.com/Arkysht/weekly_report.git
cd weekly_report
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Налаштування

### 1. Токени: `config.py`

Скопіюйте `config_example.py` у `config.py` і заповніть:

```python
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"   # токен від @BotFather
CHAT_ID = 123456789                          # чат, куди надсилати звіти
FB_APP_ID = "YOUR_FB_APP_ID"
FB_APP_SECRET = "YOUR_FB_APP_SECRET"
FB_ACCESS_TOKEN = "YOUR_FB_ACCESS_TOKEN"     # потрібен доступ до кабінетів (ads_read)
```

Не знаєте свій Chat ID? Його можна дізнатися, наприклад, через бота `@userinfobot`.

### 2. Рекламні кабінети: `accounts_config.py`

Скопіюйте `accounts_config_example.py` у `accounts_config.py`:

```python
ACCOUNTS = [
    {"name": "Example Shop", "fb_account_id": "act_1234567890"},
    {
        "name": "Example Studio",
        "fb_account_id": "act_0987654321",
        # необов'язково: рахувати лише одну конкретну подію як результат
        "custom_requests_action_type": "onsite_conversion.messaging_conversation_started_7d",
    },
]
```

### 3. Індивідуальні звіти (необов'язково)

Для кабінетів, яким потрібен власний формат, у `weekly_report.py` є словник `EXTENDED_REPORTS`. Ключ — ID кабінету, значення — декларативний опис звіту, без дублювання коду:

```python
EXTENDED_REPORTS = {
    "act_1234567890": {
        "greeting": "Відправляю короткий звіт за {period} ({account_name})\n",
        "total_spend_line": True,
        "sections": [
            {
                "header": "📩 Повідомлення",
                "blocks": [
                    {
                        "label": "Директ",
                        "keywords": ["директ", "direct"],       # фільтр кампаній за назвою
                        "auto_count": None,
                        "manual_fields": ["Переписки", "Покупки"],  # залишаються порожніми: ____
                    },
                ],
            },
        ],
        "currency_override": "$",
    },
}
```

Основні параметри:

| Параметр | Призначення |
|---|---|
| `greeting` | Вітальний рядок; доступні `{period}` і `{account_name}` |
| `sections` | Секції звіту із заголовком і блоками |
| `keywords` / `exclude_keywords` | Які кампанії потрапляють у блок (за назвою, без урахування регістру) |
| `auto_count` | Що рахувати автоматично: `"lead_priority"` або тип події Meta, наприклад `"purchase"` |
| `manual_fields` | Поля, які менеджер дописує вручну (`Назва: ____`) |
| `total_spend_line` | Додати рядок із загальними витратами за тиждень |
| `month_line_template`, `debt_line_template` | Свої рядки для місячних витрат і заборгованості |
| `currency_override` | Валюта у звіті замість тієї, що повертає API |

Кабінети без запису в `EXTENDED_REPORTS` отримують стандартний звіт.

## Запуск

```bash
python weekly_report.py
```

Приклад стандартного звіту (вигадані дані):

```
Надсилаю короткий звіт за 20.10-26.10 (Example Shop)

Використаний бюджет за тиждень: 120.50 USD

📉 Конверсія/трафік (повідомлень)
Використаний бюджет: 120.50 USD
Кількість повідомлень: 25
Ціна за результат: 4.82 USD

Витрачений бюджет за весь період (October) - 410.00 USD
Поточна заборгованість: 35.20 USD.
```

### Запуск за розкладом

Бот розрахований на запуск раз на тиждень, у понеділок. Найпростіше це зробити через systemd timer або cron на сервері.

Приклад для cron (щопонеділка о 09:00):

```
0 9 * * 1 cd /path/to/weekly_report && ./venv/bin/python weekly_report.py
```

## Безпека

- Токени та секрети зберігаються лише в `config.py`, який не потрапляє в git.
- Не публікуйте скріншоти звітів із реальними даними клієнтів.

## Плани

- [ ] Запуск у Docker (`docker compose`)
- [ ] Змінні середовища замість `config.py`
- [ ] Планувальник усередині бота
