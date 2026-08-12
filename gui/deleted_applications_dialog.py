from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox
)

from applications import (
    get_deleted_applications,
    restore_application
)


class DeletedApplicationsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Deleted Applications"
        )

        self.resize(900, 500)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "Student ID",
            "First Name",
            "Last Name",
            "Status",
            "Deleted Date",
            "Application ID"
        ])

        # Application ID is only used internally.
        self.table.setColumnHidden(5, True)

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.restore_button = QPushButton(
            "Restore Selected"
        )

        self.close_button = QPushButton(
            "Close"
        )

        button_layout.addWidget(
            self.restore_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.close_button
        )

        layout.addLayout(button_layout)

        self.restore_button.clicked.connect(
            self.restore_selected
        )

        self.close_button.clicked.connect(
            self.close
        )

        self.load_data()


    def load_data(self):

        applications = get_deleted_applications()

        self.table.setRowCount(
            len(applications)
        )

        for row_index, application in enumerate(
            applications
        ):

            values = [
                application.get("student_id", ""),
                application.get("first_name", ""),
                application.get("last_name", ""),
                application.get("status", ""),
                application.get("deleted_date", ""),
                application.get("application_id", "")
            ]

            for column_index, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(value or "")
                )

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )


    def restore_selected(self):

        selected_rows = (
            self.table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:

            QMessageBox.information(
                self,
                "Restore Application",
                "Please select an application to restore."
            )

            return

        row = selected_rows[0].row()

        application_id_item = self.table.item(
            row,
            5
        )

        if application_id_item is None:

            return

        application_id = (
            application_id_item.text()
        )

        first_name = self.table.item(
            row,
            1
        ).text()

        last_name = self.table.item(
            row,
            2
        ).text()

        student_name = (
            f"{first_name} {last_name}"
        ).strip()

        reply = QMessageBox.question(
            self,
            "Restore Application",
            (
                f"Restore the application for "
                f"{student_name}?\n\n"
                "It will return to the active "
                "applications list."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:

            return

        try:

            restore_application(
                application_id
            )

            self.load_data()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Restore Failed",
                str(e)
            )