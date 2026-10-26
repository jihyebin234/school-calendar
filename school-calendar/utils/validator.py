from datetime import datetime


def validate_date(value):
    if not value:
        raise ValueError("날짜는 필수 입력값입니다.")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("날짜 형식은 YYYY-MM-DD 이어야 합니다.") from exc


def validate_time(value):
    if not value:
        return

    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValueError("시간 형식은 HH:MM 이어야 합니다.") from exc


def validate_required_string(value, field_name):
    if not value:
        raise ValueError(f"{field_name}은(는) 필수 입력값입니다.")
    if not value.strip():
        raise ValueError(f"{field_name}은(는) 공백일 수 없습니다.")


def validate_repeat_value(value):
    valid = {"none", "weekly", "yearly"}
    if value not in valid:
        raise ValueError("반복 방식은 none, weekly, yearly 중 하나여야 합니다.")


def validate_alert_value(value):
    valid = {"none", "1day", "3day", "1week"}
    if value not in valid:
        raise ValueError("알림 시점은 none, 1day, 3day, 1week 중 하나여야 합니다.")
