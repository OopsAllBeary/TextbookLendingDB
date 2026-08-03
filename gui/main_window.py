from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTableWidgetItem,
    QTableView,
    QHeaderView,
    QFormLayout,
    QComboBox,
    QAbstractItemView,
    QLabel
)

from applications import (
    get_all_applications,
    DISPLAY_COLUMNS
)

from annotations import (
    set_status,
    set_notes,
    set_rsvp
)

DETAIL_FIELDS = [
    ("Student ID", "student_id"),
    ("First Name", "first_name"),
    ("Last Name", "last_name"),
    ("Population Type", "pop_type"),
    ("Semester", "semester"),
    ("Campus", "campus"),
    ("Program", "program"),
    ("Books and/or Devices", "requested_books_devices"),
    ("Requested Device", "requested_device"),
    ("Course Names", "course_names"),
    ("Status", "status"),
    ("Notes", "notes"),
    ("RSVP", "rsvp")
]

from gui.application_model import ApplicationTableModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Textbook Lending Tracker")
        self.resize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        self.refresh_button = QPushButton("Refresh")
        layout.addWidget(self.refresh_button)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        self.model = ApplicationTableModel()

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.table.setSortingEnabled(True)
        splitter.addWidget(self.table)

        self.refresh_button.clicked.connect(self.load_data)

        self.load_data()

        details_widget = QWidget()

        splitter.addWidget(details_widget)

        details_layout = QFormLayout(details_widget)

        self.detail_labels = {}
        self.edit_widgets = {}

        for label_text, field_name in DETAIL_FIELDS:
            if field_name == "status":
                widget = QComboBox()
                widget.addItems([
                    "New",
                    "Approved",
                    "Denied",
                    "Pending"
                ])

                self.edit_widgets[field_name] = widget

                details_layout.addRow(
                    label_text + ":",
                    widget
                )

            elif field_name == "rsvp":
                widget = QTextEdit()
                self.edit_widgets[field_name] = widget

                details_layout.addRow(
                    label_text + ":",
                    widget
                )

            elif field_name == "notes":
                widget = QTextEdit()
                widget.setMinimumHeight(100)

                self.edit_widgets[field_name] = widget

                details_layout.addRow(
                    label_text + ":",
                    widget
                )
            else:
                label = QLabel()

                label.setWordWrap(True)
                label.setAlignment(Qt.AlignTop)

                self.detail_labels[field_name] = label

                details_layout.addRow(
                    label_text + ":",
                    label
                )

        self.save_button = QPushButton("Save")
        details_layout.addRow(self.save_button)

        self.save_button.clicked.connect(
            self.save_changes
        )



    def load_data(self):
        self.model.reload()


    def on_selection_changed(self):
        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        row = indexes[0].row()

        application = self.model.get_row(row)

        self.display_application(application)


    def display_application(self, application):
        for _, field_name in DETAIL_FIELDS:
            value = application.get(field_name) or ""

            if field_name == "course_names":
                value = value.replace(";", "\n")
                value = value.replace(",", "\n")

            if field_name in self.edit_widgets:
                widget = self.edit_widgets[field_name]

                if isinstance(widget, QComboBox):
                    widget.setCurrentText(str(value))

                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value))

            else:
                self.detail_labels[field_name].setText(str(value))


    def save_changes(self):
        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        application = self.model.get_row(indexes[0].row())

        application_id = application["application_id"]

        set_status(
            application_id,
            self.edit_widgets["status"].currentText()
        )

        set_notes(
            application_id,
            self.edit_widgets["notes"].toPlainText()
        )

        set_rsvp(
            application_id,
            self.edit_widgets["rsvp"].toPlainText()
        )

        self.model.reload()



