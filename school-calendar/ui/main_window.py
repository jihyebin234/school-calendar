from pathlib import Path
from datetime import date as date_util, timedelta

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QApplication, QCalendarWidget, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)
from PyQt5.QtGui import QPalette, QColor

from database import (
    init_db, create_schedule, get_schedules_by_date, get_schedules_by_range,
    update_schedule, delete_schedule, get_schedule, get_schedules_by_title,
)
from utils.validator import validate_date

BASE_DIR = Path(__file__).resolve().parent.parent


def _get_models():
    return {
        "init_db": init_db,
        "create_schedule": create_schedule,
        "get_schedules_by_date": get_schedules_by_date,
        "get_schedules_by_range": get_schedules_by_range,
        "update_schedule": update_schedule,
        "delete_schedule": delete_schedule,
        "get_schedule": get_schedule,
        "get_schedules_by_title": get_schedules_by_title,
        "validate_date": validate_date,
    }


class ScheduleCard(QFrame):
    """A compact, double-clickable schedule card for the vertical agenda."""

    def __init__(self, schedule, on_open):
        super().__init__()
        self.schedule_id = schedule.get("id")
        self.on_open = on_open
        self.setObjectName("scheduleCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.NoFrame)
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(14)

        time_label = QLabel(schedule.get("time") or "하루 종일")
        time_label.setObjectName("scheduleTime")
        time_label.setFixedWidth(60)
        time_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        row.addWidget(time_label)

        accent = QFrame()
        accent.setObjectName("scheduleAccent")
        accent.setFixedWidth(3)
        row.addWidget(accent)

        content = QVBoxLayout()
        content.setSpacing(5)
        title = QLabel(schedule.get("title") or "제목 없음")
        title.setObjectName("scheduleTitle")
        title.setWordWrap(True)
        content.addWidget(title)

        details = [schedule.get("type") or "기타"]
        alert = schedule.get("alert_time", "none")
        repeat = schedule.get("repeat_type", "none")
        if alert != "none":
            details.append(f"알림 {alert}")
        if repeat != "none":
            details.append(f"반복 {repeat}")
        detail_label = QLabel("  ·  ".join(details))
        detail_label.setObjectName("scheduleDetails")
        content.addWidget(detail_label)

        description = (schedule.get("description") or "").strip()
        if description:
            description_label = QLabel(description)
            description_label.setObjectName("scheduleDescription")
            description_label.setWordWrap(True)
            content.addWidget(description_label)
        row.addLayout(content, 1)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.schedule_id is not None:
            self.on_open(self.schedule_id)
        super().mouseDoubleClickEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학사 일정 알림 캘린더")
        self.resize(1080, 720)
        self.setMinimumSize(820, 560)
        self.setStyleSheet("""
            QMainWindow, QWidget#central { background: #ffffff; color: #242424; }
            QWidget#sidebar { background: #f7f7f5; border-right: 1px solid #e8e8e5; }
            QLabel#brand { color: #202020; font-size: 17px; font-weight: 700; }
            QLabel#sideHeading { color: #696963; font-size: 11px; font-weight: 700; }
            QLabel#pageTitle { color: #202020; font-size: 25px; font-weight: 700; }
            QLabel#subtle { color: #85857e; font-size: 12px; }
            QLineEdit { color: #242424; background: #ffffff; border: 1px solid #e2e2de; border-radius: 6px; padding: 8px 9px; }
            QLineEdit:focus { border-color: #a7a79f; }
            QPushButton { color: #292929; background: #ffffff; border: 1px solid #e2e2de; border-radius: 6px; padding: 8px 11px; }
            QPushButton:hover { color: #202020; background: #f3f3f1; }
            QPushButton#primary { color: white; background: #2383e2; border-color: #2383e2; font-weight: 600; }
            QPushButton#primary:hover { background: #176fc4; }
            QCalendarWidget QWidget { color: #292929; background: #f7f7f5; }
            QCalendarWidget QToolButton { color: #292929; background: transparent; border: 0; padding: 5px; }
            QCalendarWidget QToolButton:hover { background: #eaeae7; }
            QCalendarWidget QAbstractItemView { color: #292929; background: #f7f7f5; selection-background-color: #2383e2; selection-color: #ffffff; }
            QCalendarWidget QTableView { color: #292929; background: #f7f7f5; }
            QScrollArea { background: #ffffff; }
            QWidget#agendaContent { background: #ffffff; }
            QFrame#scheduleCard { background: white; border: 1px solid #e9e9e6; border-radius: 9px; }
            QFrame#scheduleCard:hover { background: #fafaf9; border-color: #d8d8d3; }
            QLabel#scheduleTime { color: #777770; font-size: 12px; }
            QFrame#scheduleAccent { background: #72a7dc; border-radius: 1px; }
            QLabel#scheduleTitle { color: #252525; font-size: 14px; font-weight: 600; }
            QLabel#scheduleDetails, QLabel#scheduleDescription { color: #777770; font-size: 12px; }
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 20, 18, 18)
        side.setSpacing(13)
        brand = QLabel("학사 일정")
        brand.setObjectName("brand")
        side.addWidget(brand)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setMaximumHeight(245)
        calendar_palette = self.calendar.palette()
        for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
            calendar_palette.setColor(role, QColor("#292929"))
        calendar_palette.setColor(QPalette.Window, QColor("#f7f7f5"))
        calendar_palette.setColor(QPalette.Base, QColor("#f7f7f5"))
        calendar_palette.setColor(QPalette.Highlight, QColor("#2383e2"))
        calendar_palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.calendar.setPalette(calendar_palette)
        self.calendar.selectionChanged.connect(self.select_calendar_date)
        side.addWidget(self.calendar)

        quick_row = QHBoxLayout()
        self.today_button = QPushButton("오늘")
        self.today_button.clicked.connect(self.select_today)
        self.this_week_button = QPushButton("이번 주")
        self.this_week_button.clicked.connect(self.select_this_week)
        quick_row.addWidget(self.today_button)
        quick_row.addWidget(self.this_week_button)
        side.addLayout(quick_row)

        search_heading = QLabel("검색")
        search_heading.setObjectName("sideHeading")
        side.addWidget(search_heading)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("일정 제목 검색")
        self.search_input.returnPressed.connect(self.refresh_list)
        side.addWidget(self.search_input)

        date_heading = QLabel("날짜 범위")
        date_heading.setObjectName("sideHeading")
        side.addWidget(date_heading)
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD 또는 날짜 ~ 날짜")
        self.date_input.returnPressed.connect(self.refresh_list)
        side.addWidget(self.date_input)
        refresh_button = QPushButton("날짜 적용")
        refresh_button.clicked.connect(self.refresh_list)
        side.addWidget(refresh_button)
        side.addStretch(1)

        main = QWidget()
        content = QVBoxLayout(main)
        content.setContentsMargins(34, 27, 34, 24)
        content.setSpacing(16)
        header = QHBoxLayout()
        heading_box = QVBoxLayout()
        heading_box.setSpacing(5)
        self.page_title = QLabel("오늘의 일정")
        self.page_title.setObjectName("pageTitle")
        self.count_label = QLabel("")
        self.count_label.setObjectName("subtle")
        heading_box.addWidget(self.page_title)
        heading_box.addWidget(self.count_label)
        header.addLayout(heading_box)
        header.addStretch(1)
        self.add_button = QPushButton("+ 일정 등록")
        self.add_button.setObjectName("primary")
        self.add_button.clicked.connect(self.open_add_window)
        header.addWidget(self.add_button, alignment=Qt.AlignTop)
        content.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.list_container = QWidget()
        self.list_container.setObjectName("agendaContent")
        agenda_palette = self.list_container.palette()
        agenda_palette.setColor(QPalette.Window, QColor("#ffffff"))
        agenda_palette.setColor(QPalette.WindowText, QColor("#242424"))
        self.list_container.setPalette(agenda_palette)
        self.list_container.setAutoFillBackground(True)
        self.scroll.viewport().setPalette(agenda_palette)
        self.scroll.viewport().setAutoFillBackground(True)
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(1, 4, 8, 4)
        self.list_layout.setSpacing(9)
        self.scroll.setWidget(self.list_container)
        content.addWidget(self.scroll, 1)

        root.addWidget(sidebar)
        root.addWidget(main, 1)

        self.models = _get_models()
        self.date_input.setText(date_util.today().strftime("%Y-%m-%d"))
        self.refresh_list()

    def select_calendar_date(self):
        self.date_input.setText(self.calendar.selectedDate().toString("yyyy-MM-dd"))
        self.refresh_list()

    def select_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())

    def select_this_week(self):
        today = date_util.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        self.date_input.setText(f"{start:%Y-%m-%d} ~ {end:%Y-%m-%d}")
        self.refresh_list()

    def clear_schedule_cards(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_list(self):
        try:
            date_query = self.date_input.text().strip()
            title_query = self.search_input.text().strip()
            if not date_query:
                self.show_message("날짜를 입력하거나 오늘/이번 주를 선택하세요.", "경고")
                return

            is_range = " ~ " in date_query
            if is_range:
                start_text, end_text = (part.strip() for part in date_query.split(" ~ ", 1))
                self.models["validate_date"](start_text)
                self.models["validate_date"](end_text)
                if start_text > end_text:
                    self.show_message("시작 날짜는 종료 날짜보다 늦을 수 없습니다.", "경고")
                    return
            else:
                self.models["validate_date"](date_query)
                start_text = end_text = date_query

            if title_query:
                schedules = self.models["get_schedules_by_title"](title_query)
                schedules = [s for s in schedules if start_text <= s.get("date", "") <= end_text]
            else:
                schedules = self.models["get_schedules_by_range"](start_text, end_text)

            self.clear_schedule_cards()
            if is_range:
                self.page_title.setText(f"{start_text}  —  {end_text}")
            else:
                self.page_title.setText(date_query)
            self.count_label.setText(f"일정 {len(schedules)}개 · 시간을 기준으로 위에서 아래로 표시")

            if not schedules:
                empty = QLabel("이 날짜에는 일정이 없습니다.")
                empty.setObjectName("subtle")
                empty.setAlignment(Qt.AlignCenter)
                empty.setMinimumHeight(120)
                self.list_layout.addWidget(empty)
            else:
                previous_date = None
                for schedule in schedules:
                    schedule_date = schedule.get("date", "")
                    if is_range and schedule_date != previous_date:
                        day_heading = QLabel(schedule_date)
                        day_heading.setObjectName("sideHeading")
                        day_heading.setContentsMargins(2, 12 if previous_date else 4, 0, 0)
                        self.list_layout.addWidget(day_heading)
                        previous_date = schedule_date
                    card = ScheduleCard(schedule, self.open_edit_window)
                    self.list_layout.addWidget(card)
            self.list_layout.addStretch(1)
        except ValueError as exc:
            self.show_message(str(exc), "경고")

    def open_add_window(self):
        from ui.add_edit_window import AddEditWindow

        self.add_window = AddEditWindow()
        self.add_window.set_model(self.refresh_model)
        self.add_window.open_for_create()
        self.add_window.date_input.setText(self.calendar.selectedDate().toString("yyyy-MM-dd"))
        self.add_window.finished.connect(self.refresh_list)
        self.add_window.show()

    def refresh_model(self, model):
        self.refresh_list()

    def open_edit_window(self, schedule_id):
        from ui.add_edit_window import AddEditWindow

        self.add_window = AddEditWindow()
        self.add_window.set_model(self.refresh_model)
        if self.add_window.open_for_edit(schedule_id):
            self.add_window.finished.connect(self.refresh_list)
            self.add_window.show()

    def show_message(self, message, title="경고"):
        QMessageBox.warning(self, title, message)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
