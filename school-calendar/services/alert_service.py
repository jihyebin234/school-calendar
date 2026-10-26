from datetime import date as date_type
from datetime import datetime as datetime_type

from database import get_connection


ALERT_MESSAGE_TEMPLATES = {
    "1day": "내일 {title}이(가) 있어요.",
    "3day": "3일 후 {title}이(가) 있어요.",
    "1week": "일주일 후 {title}이(가) 있어요.",
}


def build_alert_text(schedule):
    title = schedule.get("title", "")
    alert_time = schedule.get("alert_time", "none")

    if alert_time == "none":
        return None

    if alert_time == "1day":
        return ALERT_MESSAGE_TEMPLATES["1day"].format(title=title)
    if alert_time == "3day":
        return ALERT_MESSAGE_TEMPLATES["3day"].format(title=title)
    if alert_time == "1week":
        return ALERT_MESSAGE_TEMPLATES["1week"].format(title=title)

    return None


def build_alert_texts(schedules):
    today = date_type.today().isoformat()
    texts = []

    for schedule in schedules:
        if schedule.get("alert_time") == "none":
            continue

        schedule_date = schedule.get("date", "")
        if isinstance(schedule_date, str) and schedule_date < today:
            continue

        message = build_alert_text(schedule)
        if message:
            texts.append(message)

    return texts
