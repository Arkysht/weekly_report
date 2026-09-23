import asyncio
import datetime
from typing import Dict, Any, List, Optional

import config
from accounts_config import ACCOUNTS

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

bot = Bot(token=config.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

tg_id = config.CHAT_ID


# ============================ КЛАССИФИКАЦИЯ КАМПАНИЙ ============================

PURCHASE_KEYWORDS = ["purchase"]
MESSAGE_KEYWORDS = ["direct", "директ", "смс", "sms"]
LEAD_KEYWORDS = ["lead", "лид"]

PURCHASE_OBJECTIVES = {"OUTCOME_SALES"}
MESSAGE_OBJECTIVES = {"OUTCOME_ENGAGEMENT"}
MESSAGE_OPTIMIZATION_GOALS = {"REPLIES", "CONVERSATIONS"}
LEAD_OBJECTIVES = {"OUTCOME_LEADS"}

PURCHASE_ACTION_TYPE = "purchase"
MESSAGE_ACTION_TYPE = "onsite_conversion.messaging_conversation_started_7d"
LEAD_ACTION_TYPE_PRIORITY = [
    "lead",
    "onsite_conversion.lead_grouped",
    "offsite_conversion.fb_pixel_lead",
]


def classify_campaign(
    campaign_name: str,
    objective: Optional[str] = None,
    optimization_goal: Optional[str] = None,
) -> Optional[str]:
    """Определяет категорию кампании (purchase, message, leads) по объективу, цели или ключевым словам."""
    if objective in PURCHASE_OBJECTIVES:
        return "purchase"
    if objective in MESSAGE_OBJECTIVES and optimization_goal in MESSAGE_OPTIMIZATION_GOALS:
        return "message"
    if objective in LEAD_OBJECTIVES:
        return "leads"

    name_lower = (campaign_name or "").lower()
    if any(kw in name_lower for kw in PURCHASE_KEYWORDS):
        return "purchase"
    if any(kw in name_lower for kw in MESSAGE_KEYWORDS):
        return "message"
    if any(kw in name_lower for kw in LEAD_KEYWORDS):
        return "leads"
    return None


def get_action_value(actions: Optional[List[Dict[str, Any]]], action_type: str) -> float:
    """Извлекает количество целевых действий заданного типа из ответа Meta API."""
    if not actions:
        return 0.0
    for a in actions:
        if a.get("action_type") == action_type:
            return float(a.get("value", 0) or 0)
    return 0.0


def get_action_value_priority(actions: Optional[List[Dict[str, Any]]], priority_types: List[str]) -> float:
    """Извлекает количество действий с учетом приоритета названий типов событий."""
    if not actions:
        return 0.0
    for action_type in priority_types:
        for a in actions:
            if a.get("action_type") == action_type:
                return float(a.get("value", 0) or 0)
    return 0.0


# ============================ ДАТЫ ============================

def get_last_week_range() -> tuple[datetime.date, datetime.date]:
    """Возвращает диапазон дат предыдущей недели (с понедельника по воскресенье)."""
    today = datetime.date.today()
    this_monday = today - datetime.timedelta(days=today.weekday())
    last_monday = this_monday - datetime.timedelta(days=7)
    last_sunday = this_monday - datetime.timedelta(days=1)
    return last_monday, last_sunday


def get_month_to_yesterday_range() -> tuple[datetime.date, datetime.date]:
    """Возвращает диапазон дат с первого числа текущего месяца по вчерашний день."""
    today = datetime.date.today()
    month_start = today.replace(day=1)
    yesterday = today - datetime.timedelta(days=1)
    return month_start, yesterday


# ============================ ЗАПРОСЫ К META API ============================

def fetch_campaign_rows_range(fb_account_id: str, since: str, until: str) -> List[Dict[str, Any]]:
    """Получает метрики по кампаниям аккаунта Meta Ads за указанный период."""
    account = AdAccount(fb_account_id)
    fields = [
        "campaign_name", "objective", "optimization_goal",
        "spend", "impressions", "clicks", "reach", "actions",
    ]
    params = {
        "level": "campaign",
        "time_range": {"since": since, "until": until},
    }
    insights = account.get_insights(fields=fields, params=params)
    return [dict(row) for row in insights]


def get_account_currency(fb_account_id: str) -> str:
    """Запрашивает валюту рекламного аккаунта."""
    account = AdAccount(fb_account_id)
    data = account.api_get(fields=["currency"])
    return data.get("currency", "")


def get_account_balance(fb_account_id: str) -> Optional[float]:
    """Запрашивает текущую задолженность по аккаунту и конвертирует центы в основные единицы."""
    account = AdAccount(fb_account_id)
    data = account.api_get(fields=["balance"])
    raw = data.get("balance")
    if raw is None:
        return None
    return round(float(raw) / 100, 2)


def sum_spend_for_period(fb_account_id: str, start: datetime.date, end: datetime.date) -> float:
    """Рассчитывает суммарные затраты по аккаунту за произвольный период."""
    rows = fetch_campaign_rows_range(fb_account_id, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    return round(sum(float(row.get("spend", 0) or 0) for row in rows), 2)


def sum_spend_from_rows(rows: List[Dict[str, Any]]) -> float:
    """Суммирует расходы по всем строкам полученной выгрузки."""
    return round(sum(float(row.get("spend", 0) or 0) for row in rows), 2)


# ============================ АГРЕГАЦИЯ ПО ТИПАМ ============================

def aggregate_by_category(
    rows: List[Dict[str, Any]],
    custom_requests_action_type: Optional[str] = None,
) -> Dict[str, Dict[str, float]]:
    """Группирует расходы и целевые действия по категориям кампаний."""
    if custom_requests_action_type:
        categories = {"custom": {"spend": 0.0, "count": 0.0}}
        for row in rows:
            spend = float(row.get("spend", 0) or 0)
            actions = row.get("actions")
            categories["custom"]["spend"] += spend
            categories["custom"]["count"] += get_action_value(actions, custom_requests_action_type)
        return categories

    categories = {
        "purchase": {"spend": 0.0, "count": 0.0},
        "message": {"spend": 0.0, "count": 0.0},
        "leads": {"spend": 0.0, "count": 0.0},
    }
    for row in rows:
        campaign_name = row.get("campaign_name", "")
        objective = row.get("objective")
        optimization_goal = row.get("optimization_goal")
        spend = float(row.get("spend", 0) or 0)
        actions = row.get("actions")

        category = classify_campaign(campaign_name, objective, optimization_goal)
        if category not in categories:
            continue

        categories[category]["spend"] += spend
        if category == "purchase":
            categories[category]["count"] += get_action_value(actions, PURCHASE_ACTION_TYPE)
        elif category == "message":
            categories[category]["count"] += get_action_value(actions, MESSAGE_ACTION_TYPE)
        elif category == "leads":
            categories[category]["count"] += get_action_value_priority(actions, LEAD_ACTION_TYPE_PRIORITY)

    return categories


# ============================ СБОРКА ТЕКСТА ОТЧЁТА ============================

def format_category_block(name_ua: str, spend: float, count: float, currency: str) -> str:
    """Форматирует текстовый блок результатов для отдельной категории."""
    if count <= 0:
        return ""
    cost_per_result = spend / count if count else 0
    return (
        f"Використаний бюджет: {spend:,.2f} {currency}\n"
        f"Кількість {name_ua}: {int(count)}\n"
        f"Ціна за результат: {cost_per_result:,.2f} {currency}\n"
    )


def build_report_text(
    account_name: str,
    week_start: datetime.date,
    week_end: datetime.date,
    week_total_spend: float,
    week_categories: Dict[str, Dict[str, float]],
    month_spend: float,
    currency: str,
    current_debt: Optional[float] = None,
) -> str:
    """Формирует итоговый текст отчета для Telegram."""
    period_str = f"{week_start.strftime('%d.%m')}-{week_end.strftime('%d.%m')}"
    month_name = week_end.strftime("%B")

    lines = [f"Надсилаю короткий звіт за {period_str} ({account_name})\n"]
    lines.append(f"Використаний бюджет за тиждень: {week_total_spend:,.2f} {currency}\n")

    labels = {"purchase": "покупок", "message": "повідомлень", "leads": "лідів", "custom": "результатів"}
    for cat, label in labels.items():
        if cat not in week_categories:
            continue
        block = format_category_block(label, week_categories[cat]["spend"], week_categories[cat]["count"], currency)
        if block:
            lines.append(f"📉 Конверсія/трафік ({label})")
            lines.append(block)

    lines.append(f"Витрачений бюджет за весь період ({month_name}) - {month_spend:,.2f} {currency}")
    if current_debt is not None:
        lines.append(f"Поточна заборгованість: {current_debt:,.2f} {currency}.")

    return "\n".join(lines)


# ============================ ОТПРАВКА ============================

async def send_weekly_report_for_account(acc: Dict[str, Any]) -> None:
    """Собирает метрики и отправляет отчет по одному рекламному аккаунту."""
    fb_account_id = acc["fb_account_id"]
    week_start, week_end = get_last_week_range()
    month_start, _ = get_month_to_yesterday_range()
    custom_type = acc.get("custom_requests_action_type")

    currency = get_account_currency(fb_account_id)

    week_rows = fetch_campaign_rows_range(
        fb_account_id, week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")
    )
    week_total_spend = sum_spend_from_rows(week_rows)
    week_categories = aggregate_by_category(week_rows, custom_type)

    month_spend = sum_spend_for_period(fb_account_id, month_start, week_end)
    current_debt = get_account_balance(fb_account_id)

    text = build_report_text(
        acc["name"], week_start, week_end, week_total_spend, week_categories,
        month_spend, currency, current_debt,
    )
    await bot.send_message(chat_id=tg_id, text=text, disable_web_page_preview=True)


async def send_all_reports() -> None:
    """Инициализирует SDK Meta API и запускает отправку отчетов для всех аккаунтов."""
    FacebookAdsApi.init(config.FB_APP_ID, config.FB_APP_SECRET, config.FB_ACCESS_TOKEN)
    for acc in ACCOUNTS:
        try:
            await send_weekly_report_for_account(acc)
        except Exception as e:
            await bot.send_message(chat_id=tg_id, text=f"Ошибка при формировании отчёта для {acc['name']}: {e}")


# ============================ ХЕНДЛЕРЫ ============================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Возвращает Chat ID пользователя при отправке команды /start."""
    await message.answer(f"Привет! Вот твой Chat ID: {message.chat.id}")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await send_all_reports()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())