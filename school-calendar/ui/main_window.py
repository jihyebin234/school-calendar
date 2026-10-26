from pathlib import Path

from datetime import date as date_util, timedelta

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QApplication, QCalendarWidget, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QMessageBox

from database import (
    init_db,
    create_schedule,
    get_schedules_by_date,
    get_schedules_by_range,
    update_schedule,
    delete_schedule,
    get_schedule,
    get_schedules_by_title,
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학사 일정 알림 캘린더")
        self.resize(900, 640)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QHBoxLayout()
        self.label = QLabel("학사 일정 알림 캘린더")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(self.label)

        self.select_date_label = QLabel("조회 날짜:")

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.select_calendar_date)

        self.search_label = QLabel("제목 검색:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("제목 검색")

        self.today_button = QPushButton("오늘")
        self.today_button.clicked.connect(self.select_today)

        self.this_week_button = QPushButton("이번 주")
        self.this_week_button.clicked.connect(self.select_this_week)

        self.add_button = QPushButton("등록")
        self.add_button.clicked.connect(self.open_add_window)

        self.refresh_button = QPushButton("확인")
        self.refresh_button.clicked.connect(self.refresh_list)

        header.addWidget(self.select_date_label)
        header.addWidget(self.date_input)
        header.addWidget(self.today_button)
        header.addWidget(self.this_week_button)
        header.addWidget(self.search_label)
        header.addWidget(self.search_input)
        header.addWidget(self.refresh_button)
        header.addWidget(self.add_button)

        list_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 14px;")

        list_layout.addWidget(self.list_widget)

        layout.addLayout(header)
        layout.addWidget(self.calendar)
        layout.addLayout(list_layout)

        self.models = _get_models()
        self.list_widget.itemDoubleClicked.connect(self.open_edit_window)
        self.date_input.setText(date_util.today().strftime("%Y-%m-%d"))
        self.refresh_list()

    def select_calendar_date(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.date_input.setText(selected_date)
        self.refresh_list()

    def select_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())

    def select_this_week(self):
        start = date_util.today() - timedelta(days=date_util.today().weekday())
        end = start + timedelta(days=6)
        self.date_input.setText(f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}")
        self.refresh_list()

    def refresh_list(self):
        try:
            date_query = self.date_input.text().strip()
            title = self.search_input.text().strip()

            if not date_query:
                self.show_message("날짜를 입력하거나 오늘/이번 주를 선택하세요.", "경고")
                return

            if " ~ " in date_query:
                start_text, end_text = date_query.split(" ~ ", 1)
                start_text = start_text.strip()
                end_text = end_text.strip()
                if start_text and end_text:
                    try:
                        self.models["validate_date"](start_text)
                        self.models["validate_date"](end_text)
                    except ValueError as exc:
                        self.show_message(str(exc), "경고")
                        return
                if start_text > end_text:
                    self.show_message("시작 날짜는 종료 날짜보다 늦을 수 없습니다.", "경고")
                    return
            else:
                self.models["validate_date"](date_query)

            if title:
                schedules = self.models["get_schedules_by_title"](title)
            else:
                if " ~ " in date_query:
                    schedules = self.models["get_schedules_by_range"](start_text, end_text)
                else:
                    schedules = self.models["get_schedules_by_range"](date_query, date_query)

            self.list_widget.clear()
            if not schedules:
                self.list_widget.addItem("일정이 없습니다.")
                return

            for schedule in schedules:
                title_text = schedule.get("title", "제목 없음")
                date_text = schedule.get("date", "")
                time_text = schedule.get("time", "")
                type_text = schedule.get("type", "기타")
                alert_text = schedule.get("alert_time", "none")
                repeat_text = schedule.get("repeat_type", "none")
                description_text = schedule.get("description", "")

                item_text = f"{date_text} {time_text} [{type_text}] {title_text}"
                if alert_text != "none":
                    item_text += f" | 알림: {alert_text}"
                if repeat_text != "none":
                    item_text += f" | 반복: {repeat_text}"
                if description_text:
                    item_text += f" | {description_text}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, schedule.get("id"))
                self.list_widget.addItem(item)

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

    def open_edit_window(self, item):
        schedule_id = item.data(Qt.ItemDataRole.UserRole)
        if schedule_id is None:
            return
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
