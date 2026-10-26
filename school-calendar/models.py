from dataclasses import dataclass
from typing import Optional


@dataclass
class Schedule:
    id: Optional[int] = None
    title: str = ""
    date: str = ""
    time: str = "00:00"
    type: str = "기타"
    alert_time: str = "none"
    repeat_type: str = "none"
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

    @property
    def is_repeating(self):
        return self.repeat_type in {"weekly", "yearly"}

    @property
    def alert_display(self):
        if self.alert_time == "none":
            return "알림 없음"
        return f"{self.alert_time} 전"
