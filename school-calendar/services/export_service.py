import csv
from datetime import datetime
from pathlib import Path

from database import get_connection


def export_to_csv(file_path, days=30):
    end_date = (datetime.now() + __import__("datetime").timedelta(days=days)).strftime("%Y-%m-%d")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT title, date, time, type, alert_time, repeat_type, description
            FROM schedules
            WHERE date >= ? AND date <= ?
            ORDER BY date, time, id
            """,
            (datetime.now().strftime("%Y-%m-%d"), end_date),
        ).fetchall()

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["제목", "날짜", "시간", "유형", "알림 시점", "반복", "설명"])
        for row in rows:
            writer.writerow(
                [
                    row["title"],
                    row["date"],
                    row["time"],
                    row["type"],
                    row["alert_time"],
                    row["repeat_type"],
                    row["description"],
                ]
            )

    return str(file_path)
