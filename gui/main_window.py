import csv

from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QAction
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
    QLineEdit,
    QLabel,
    QFileDialog,
    QMessageBox,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QDialogButtonBox,
    QCheckBox
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

class ColumnSettingsDialog(QDialog):

    def __init__(self, columns, visible_columns, column_order, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Column Settings")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()

        for column_index in column_order:

            title, field_name = columns[column_index]

            item = QListWidgetItem(title)

            item.setData(
                Qt.UserRole,
                column_index
            )

            item.setFlags(
                item.flags() |
                Qt.ItemIsUserCheckable
            )

            if column_index in visible_columns:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()

        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")

        self.up_button.clicked.connect(
            self.move_up
        )

        self.down_button.clicked.connect(
            self.move_down
        )

        button_layout.addStretch()
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        dialog_buttons.accepted.connect(
            self.accept
        )

        dialog_buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(dialog_buttons)

    def move_up(self):

        row = self.list_widget.currentRow()

        if row <= 0:
            return

        item = self.list_widget.takeItem(row)

        self.list_widget.insertItem(
            row - 1,
            item
        )

        self.list_widget.setCurrentRow(
            row - 1
        )

    def move_down(self):

        row = self.list_widget.currentRow()

        if row < 0 or row >= self.list_widget.count() - 1:
            return

        item = self.list_widget.takeItem(row)

        self.list_widget.insertItem(
            row + 1,
            item
        )

        self.list_widget.setCurrentRow(
            row + 1
        )

    def get_settings(self):

        column_order = []
        visible_columns = set()

        for row in range(self.list_widget.count()):

            item = self.list_widget.item(row)

            column_index = item.data(
                Qt.UserRole
            )

            column_order.append(
                column_index
            )

            if item.checkState() == Qt.Checked:
                visible_columns.add(
                    column_index
                )

        return column_order, visible_columns


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_application_id = None

        self.setWindowTitle("Textbook Lending Tracker")
        self.resize(1000, 600)

        self.settings = QSettings(
            "TextbookLendingTracker",
            "TextbookLendingTracker"
        )

        self.setup_menu()

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        button_layout = QHBoxLayout()

        self.import_button = QPushButton("Import CSV")
        self.export_button = QPushButton("Export CSV")
        self.refresh_button = QPushButton("Refresh")

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        

        self.model = ApplicationTableModel()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search applications...")

        layout.addWidget(self.search_box)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

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
        self.load_column_settings()

        self.table.sortByColumn(
            4,
            Qt.AscendingOrder
        )
        
        splitter.addWidget(self.table)

        self.refresh_button.clicked.connect(self.load_data)
        self.import_button.clicked.connect(self.import_csv)
        self.export_button.clicked.connect(self.export_csv)

        self.search_box.textChanged.connect(self.model.set_filter)

        self.load_data()

        details_widget = QWidget()

        splitter.addWidget(details_widget)

        splitter.setSizes([750, 250])

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


    def setup_menu(self):

        menu_bar = self.menuBar()

        settings_menu = menu_bar.addMenu("Settings")

        # Auto Email
        self.auto_email_action = QAction(
            "Automatically Send Status Emails",
            self
        )

        self.auto_email_action.setCheckable(True)

        self.auto_email_action.setChecked(
            self.settings.value(
                "auto_email",
                False,
                type=bool
            )
        )

        self.auto_email_action.toggled.connect(
            self.set_auto_email
        )

        settings_menu.addAction(
            self.auto_email_action
        )

        # Columns
        columns_action = QAction(
            "Columns...",
            self
        )

        columns_action.triggered.connect(
            self.open_column_settings
        )

        settings_menu.addAction(
            columns_action
        )

    def open_column_settings(self):

        header = self.table.horizontalHeader()

        column_order = []

        for visual_index in range(header.count()):

            logical_index = header.logicalIndex(
                visual_index
            )

            column_order.append(
                logical_index
            )

        visible_columns = set()

        for column_index in range(header.count()):

            if not self.table.isColumnHidden(
                column_index
            ):
                visible_columns.add(
                    column_index
                )

        dialog = ColumnSettingsDialog(
            self.model.COLUMNS,
            visible_columns,
            column_order,
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        new_order, new_visible = dialog.get_settings()

        self.apply_column_settings(
            new_order,
            new_visible
        )

        self.save_column_settings(
            new_order,
            new_visible
        )

    def apply_column_settings(
        self,
        column_order,
        visible_columns
    ):

        header = self.table.horizontalHeader()

        # Restore order
        for visual_index, logical_index in enumerate(
            column_order
        ):

            current_visual_index = header.visualIndex(
                logical_index
            )

            if current_visual_index != visual_index:

                header.moveSection(
                    current_visual_index,
                    visual_index
                )

        # Apply visibility
        for column_index in range(
            self.model.columnCount()
        ):

            self.table.setColumnHidden(
                column_index,
                column_index not in visible_columns
            )

    def save_column_settings(
        self,
        column_order,
        visible_columns
    ):

        self.settings.setValue(
            "column_order",
            column_order
        )

        self.settings.setValue(
            "visible_columns",
            list(visible_columns)
        )

    def load_column_settings(self):

        column_count = self.model.columnCount()

        saved_order = self.settings.value(
            "column_order",
            None
        )

        saved_visible = self.settings.value(
            "visible_columns",
            None
        )

        if saved_order is None:
            saved_order = list(
                range(column_count)
            )

        else:
            saved_order = [
                int(value)
                for value in saved_order
                if int(value) < column_count
            ]

            for column_index in range(column_count):
                if column_index not in saved_order:
                    saved_order.append(column_index)

        if saved_visible is None:
            saved_visible = set()

            for column_index, (_, field_name) in enumerate(
                self.model.COLUMNS
            ):
                if field_name in self.model.DEFAULT_COLUMNS:
                    saved_visible.add(column_index)

        else:
            saved_visible = {
                int(value)
                for value in saved_visible
                if int(value) < column_count
            }

        self.apply_column_settings(
            saved_order,
            saved_visible
        )

    def set_auto_email(self, enabled):

        self.settings.setValue(
            "auto_email",
            enabled
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

        old_status = self.model.get_status(application_id)

        status = self.edit_widgets["status"].currentText().strip()
        notes = self.edit_widgets["notes"].toPlainText()
        rsvp = self.edit_widgets["rsvp"].toPlainText()

        status_changed = old_status != status

        print(
            f"STATUS CHECK: {old_status!r} -> {status!r}"
        )

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

        if (
            status_changed
            and self.auto_email_action.isChecked()
            and status in ["Approved", "WaitList", "Denied"]
        ):
            print("SENDING STATUS EMAIL")

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

    def export_csv(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Applications",
            "all_applications_export.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            rows = self.model.get_all_rows()

            if not rows:
                QMessageBox.information(
                    self,
                    "Export",
                    "There are no applications to export."
                )
                return

            excluded_fields = {
                "current_data",
                "last_seen_import",
                "created_date",
                "updated_date"
            }

            fieldnames = [
                field_name
                for _, field_name in self.model.COLUMNS
                if field_name not in excluded_fields
            ]

            for row in rows:
                for field in row.keys():
                    if field not in fieldnames and field not in excluded_fields:
                        fieldnames.append(field)

            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                    extrasaction="ignore"
                )

                writer.writeheader()

                for row in rows:
                    writer.writerow(row)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Exported {len(rows)} applications."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Export Failed",
                str(e)
            )


