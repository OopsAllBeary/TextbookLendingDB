from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTableWidgetItem,
    QTableView,
    QHeaderView,
    QFormLayout,
    QComboBox,
    QAbstractItemView,
    QLabel,
    QFileDialog,
    QMessageBox
)

from import_csv import import_applications

from email_handler import open_status_email

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
    ("Email", "email"),
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

        self.current_application_id = None

        self.setWindowTitle("Textbook Lending Tracker")
        self.resize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        button_layout = QHBoxLayout()

        self.import_button = QPushButton("Import CSV")
        self.refresh_button = QPushButton("Refresh")

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

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
        self.import_button.clicked.connect(self.import_csv)

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
                    "WaitList"
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

        new_application = self.model.get_row(indexes[0].row())

        self.save_current_application()

        self.display_application(new_application)


    def display_application(self, application):
        self.current_application_id = application["application_id"]

        for _, field_name in DETAIL_FIELDS:
            value = application.get(field_name) or ""

            if field_name == "course_names":
                value = value.replace(";", "\n")
                value = value.replace(",", "\n")

            if field_name in self.edit_widgets:
                widget = self.edit_widgets[field_name]

                if isinstance(widget, QComboBox):

                    if field_name == "status" and not value:
                        value = "New"

                    widget.setCurrentText(str(value))

                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value))

            else:
                self.detail_labels[field_name].setText(str(value))


    def save_annotation_changes(self, application_id, application):

        old_status = application.get("status")

        status = self.edit_widgets["status"].currentText()
        notes = self.edit_widgets["notes"].toPlainText()
        rsvp = self.edit_widgets["rsvp"].toPlainText()

        set_status(
            application_id,
            status
        )

        set_notes(
            application_id,
            notes
        )

        set_rsvp(
            application_id,
            rsvp
        )

        if status != old_status:
            open_status_email(
                application["email"],
                application["first_name"],
                status
            )

        self.model.update_annotation(
            application_id,
            status,
            notes,
            rsvp
        )

    def save_changes(self):
        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        application = self.model.get_row(indexes[0].row())

        self.save_annotation_changes(
            application["application_id"],
            application
        )

        self.model.reload()


    def save_current_application(self):

        print("Saving", self.current_application_id)

        if self.current_application_id is None:
            return

        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            return

        application = self.model.get_row(indexes[0].row())

        self.save_annotation_changes(
            self.current_application_id,
            application
        )
        


    def import_csv(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Applications",
            "",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            stats = import_applications(filename)
            self.load_data()

            QMessageBox.information(
                self,
                "Import Complete",
                f"""
Processed: {stats['processed']}
New: {stats["new"]}
Updated: {stats["updated"]}
"""
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                str(e)
            )

        


