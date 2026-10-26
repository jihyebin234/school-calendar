from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
)

from database import create_schedule, update_schedule, get_schedule, delete_schedule
from utils.validator import (
    validate_date,
    validate_time,
    validate_required_string,
    validate_repeat_value,
    validate_alert_value,
)
from services.export_service import export_to_csv

DEFAULT_TYPE = ["시험", "과제", "행사", "기타"]
DEFAULT_ALERT = ["none", "1day", "3day", "1week"]
DEFAULT_REPEAT = ["none", "weekly", "yearly"]


class AddEditWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("새 일정 등록")
        self.resize(520, 460)

        self.schedule_id = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("제목"))

        self.title_input = QLineEdit()

        layout.addWidget(QLabel("날짜"))

        self.date_input = QLineEdit()

        layout.addWidget(QLabel("시간"))

        self.time_input = QLineEdit()

        layout.addWidget(QLabel("유형"))

        self.type_input = QLineEdit()

        layout.addWidget(QLabel("알림 시점"))

        self.alert_input = QLineEdit()

        layout.addWidget(QLabel("반복 여부"))

        self.repeat_input = QLineEdit()

        layout.addWidget(QLabel("설명"))

        self.description_input = QLineEdit()

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("저장")
        self.cancel_button = QPushButton("취소")
        self.delete_button = QPushButton("삭제")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)

        self.setup_fields()

    def setup_fields(self):
        pass

    def set_model(self, model):
        self.refresh_model = model

    def open_for_create(self):
        self.clear_inputs()
        self.title_input.setFocus()
        self.setWindowTitle("새 일정 등록")

    def open_for_edit(self, schedule_id):
        self.clear_inputs()
        schedule = get_schedule(schedule_id)
        if schedule is None:
            return False

        self.schedule_id = schedule_id

        self.title_input.setText(schedule.get("title", ""))
        self.date_input.setText(schedule.get("date", ""))
        self.time_input.setText(schedule.get("time", ""))
        self.type_input.setText(schedule.get("type", ""))
        self.alert_input.setText(schedule.get("alert_time", ""))
        self.repeat_input.setText(schedule.get("repeat_type", ""))
        self.description_input.setText(schedule.get("description", ""))
        self.setWindowTitle("일정 수정")

        return True

    def clear_inputs(self):
        self.title_input.clear()
        self.date_input.clear()
        self.time_input.clear()
        self.type_input.clear()
        self.alert_input.clear()
        self.repeat_input.clear()
        self.description_input.clear()

    def save(self):
        try:
            validate_required_string(self.title_input.text().strip(), "제목")
            validate_date(self.date_input.text().strip())
            validate_time(self.time_input.text().strip())
            validate_required_string(self.type_input.text().strip(), "유형")
            validate_alert_value(self.alert_input.text().strip())
            validate_repeat_value(self.repeat_input.text().strip())

            data = {
                "title": self.title_input.text().strip(),
                "date": self.date_input.text().strip(),
                "time": self.time_input.text().strip(),
                "type": self.type_input.text().strip(),
                "alert_time": self.alert_input.text().strip(),
                "repeat_type": self.repeat_input.text().strip(),
                "description": self.description_input.text().strip(),
            }

            if self.schedule_id is None:
                schedule_id = create_schedule(data)
            else:
                update_schedule(self.schedule_id, data)
                schedule_id = self.schedule_id

            self.refresh_model({"id": schedule_id})
            self.accept()

        except ValueError as exc:
            self.show_message(str(exc), "경고")

    def show_message(self, message, title="경고"):
        QMessageBox.warning(self, title, message)

    def delete_schedule(self):
        if self.schedule_id is None:
            return

        reply = QMessageBox.question(
            self,
            "삭제 확인",
            "이 일정을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            from database import delete_schedule

            delete_schedule(self.schedule_id)
            self.refresh_model({"id": self.schedule_id})
            self.reject()
