from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QComboBox,
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
        self.resize(520, 560)

        self.schedule_id = None
        self.refresh_model = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("제목"))

        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("날짜"))

        self.date_input = QLineEdit()
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel("시간"))

        self.time_input = QLineEdit()
        layout.addWidget(self.time_input)

        layout.addWidget(QLabel("유형"))

        self.type_input = QComboBox()
        layout.addWidget(self.type_input)

        layout.addWidget(QLabel("알림 시점"))

        self.alert_input = QComboBox()
        layout.addWidget(self.alert_input)

        layout.addWidget(QLabel("반복 여부"))

        self.repeat_input = QComboBox()
        layout.addWidget(self.repeat_input)

        layout.addWidget(QLabel("설명"))

        self.description_input = QLineEdit()
        layout.addWidget(self.description_input)

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
        self.type_input.addItems(DEFAULT_TYPE)
        self.alert_input.addItems(DEFAULT_ALERT)
        self.repeat_input.addItems(DEFAULT_REPEAT)
        self.time_input.setPlaceholderText("HH:MM (비우면 00:00)")
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.description_input.setPlaceholderText("선택 사항")
        self.delete_button.clicked.connect(self.delete_schedule)
        self.delete_button.hide()

    def set_model(self, model):
        self.refresh_model = model

    def open_for_create(self):
        self.clear_inputs()
        self.schedule_id = None
        self.delete_button.hide()
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
        self.alert_input.setCurrentText(schedule.get("alert_time", "none"))
        self.repeat_input.setCurrentText(schedule.get("repeat_type", "none"))
        if schedule.get("type") not in DEFAULT_TYPE:
            self.type_input.addItem(schedule.get("type"))
        self.type_input.setCurrentText(schedule.get("type", "기타"))
        self.description_input.setText(schedule.get("description", ""))
        self.setWindowTitle("일정 수정")
        self.delete_button.show()

        return True

    def clear_inputs(self):
        self.title_input.clear()
        self.date_input.clear()
        self.time_input.clear()
        self.type_input.setCurrentIndex(DEFAULT_TYPE.index("기타"))
        self.alert_input.setCurrentIndex(DEFAULT_ALERT.index("none"))
        self.repeat_input.setCurrentIndex(DEFAULT_REPEAT.index("none"))
        self.description_input.clear()

    def save(self):
        try:
            validate_required_string(self.title_input.text().strip(), "제목")
            validate_date(self.date_input.text().strip())
            validate_time(self.time_input.text().strip())
            validate_required_string(self.type_input.currentText().strip(), "유형")
            validate_alert_value(self.alert_input.currentText().strip())
            validate_repeat_value(self.repeat_input.currentText().strip())

            data = {
                "title": self.title_input.text().strip(),
                "date": self.date_input.text().strip(),
                "time": self.time_input.text().strip() or "00:00",
                "type": self.type_input.currentText(),
                "alert_time": self.alert_input.currentText(),
                "repeat_type": self.repeat_input.currentText(),
                "description": self.description_input.text().strip(),
            }

            if self.schedule_id is None:
                schedule_id = create_schedule(data)
            else:
                update_schedule(self.schedule_id, data)
                schedule_id = self.schedule_id

            if self.refresh_model:
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
            if self.refresh_model:
                self.refresh_model({"id": self.schedule_id})
            self.reject()
