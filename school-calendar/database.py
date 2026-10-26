import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "school_calendar.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL DEFAULT '00:00',
                type TEXT NOT NULL DEFAULT '기타',
                alert_time TEXT NOT NULL DEFAULT 'none',
                repeat_type TEXT NOT NULL DEFAULT 'none',
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def create_schedule(data):
    required_fields = ["title", "date"]
    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        raise ValueError(f"필수 입력값이 비어 있습니다: {', '.join(missing)}")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO schedules
            (title, date, time, type, alert_time, repeat_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["date"],
                data.get("time", "00:00"),
                data.get("type", "기타"),
                data.get("alert_time", "none"),
                data.get("repeat_type", "none"),
                data.get("description", ""),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_schedule(schedule_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM schedules WHERE id = ?",
            (schedule_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def get_schedules_by_date(date):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM schedules WHERE date = ? ORDER BY time, id",
            (date,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_schedules_by_range(start_date, end_date):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM schedules
            WHERE date >= ? AND date <= ?
            ORDER BY date, time, id
            """,
            (start_date, end_date),
        ).fetchall()

    return [dict(row) for row in rows]


def get_schedules_by_type(schedule_type):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM schedules WHERE type = ? ORDER BY date, time, id",
            (schedule_type,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_schedules_by_title(title):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM schedules WHERE title LIKE ? ORDER BY date, time, id",
            (f"%{title}%",),
        ).fetchall()

    return [dict(row) for row in rows]


def update_schedule(schedule_id, data):
    allowed_fields = {
        "title",
        "date",
        "time",
        "type",
        "alert_time",
        "repeat_type",
        "description",
    }

    update_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if not update_data:
        return False

    if "date" in update_data and not update_data["date"]:
        raise ValueError("날짜는 비울 수 없습니다.")

    set_clause = ", ".join(f"{field} = ?" for field in update_data.keys())
    values = list(update_data.values()) + [schedule_id]

    with get_connection() as conn:
        conn.execute(
            f"""
            UPDATE schedules
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values,
        )
        conn.commit()
        return conn.total_changes > 0


def delete_schedule(schedule_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        conn.commit()
        return cursor.rowcount > 0
