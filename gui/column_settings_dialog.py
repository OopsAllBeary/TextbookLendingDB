from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QLabel,
    QDialogButtonBox,
    QWidget,
)


class ColumnSettingsDialog(QDialog):

    def __init__(
        self,
        columns,
        visible_columns,
        export_columns,
        column_order,
        default_visible,
        default_export,
        parent=None
    ):
        super().__init__(parent)

        self.columns = columns
        self.default_visible = default_visible
        self.default_export = default_export

        self.setWindowTitle("Column Settings")
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        column_label = QLabel("Column")
        display_label = QLabel("Display")
        export_label = QLabel("Export")

        header_layout.addWidget(column_label)
        header_layout.addStretch()
        header_layout.addWidget(display_label)
        header_layout.addWidget(export_label)

        layout.addLayout(header_layout)

        # -------------------------------------------------
        # Column list
        # -------------------------------------------------

        self.list_widget = QListWidget()

        layout.addWidget(self.list_widget)

        self.populate_list(
            column_order,
            visible_columns,
            export_columns
        )

        # -------------------------------------------------
        # Move buttons
        # -------------------------------------------------

        move_layout = QHBoxLayout()

        self.up_button = QPushButton("↑ Move Up")
        self.down_button = QPushButton("↓ Move Down")

        self.up_button.clicked.connect(
            self.move_up
        )

        self.down_button.clicked.connect(
            self.move_down
        )

        move_layout.addStretch()
        move_layout.addWidget(self.up_button)
        move_layout.addWidget(self.down_button)
        move_layout.addStretch()

        layout.addLayout(move_layout)

        # -------------------------------------------------
        # Bottom buttons
        # -------------------------------------------------

        bottom_layout = QHBoxLayout()

        self.reset_button = QPushButton(
            "Reset to Defaults"
        )

        self.reset_button.clicked.connect(
            self.reset_defaults
        )

        bottom_layout.addWidget(
            self.reset_button
        )

        bottom_layout.addStretch()

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

        bottom_layout.addWidget(
            dialog_buttons
        )

        layout.addLayout(bottom_layout)

    # -----------------------------------------------------
    # Build the list
    # -----------------------------------------------------

    def populate_list(
        self,
        column_order,
        visible_columns,
        export_columns
    ):

        self.list_widget.clear()

        for column_index in column_order:

            title, field_name = self.columns[
                column_index
            ]

            item = QListWidgetItem()

            item.setData(
                Qt.UserRole,
                column_index
            )

            widget = QWidget()

            row_layout = QHBoxLayout(widget)

            row_layout.setContentsMargins(
                4,
                2,
                4,
                2
            )

            label = QLabel(title)

            display_checkbox = QCheckBox()
            export_checkbox = QCheckBox()

            display_checkbox.setChecked(
                column_index in visible_columns
            )

            export_checkbox.setChecked(
                column_index in export_columns
            )

            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(display_checkbox)
            row_layout.addWidget(export_checkbox)

            item.setSizeHint(
                widget.sizeHint()
            )

            self.list_widget.addItem(item)

            self.list_widget.setItemWidget(
                item,
                widget
            )

    # -----------------------------------------------------
    # Read current state
    # -----------------------------------------------------

    def get_current_settings(self):

        column_order = []
        visible_columns = set()
        export_columns = set()

        for row in range(
            self.list_widget.count()
        ):

            item = self.list_widget.item(row)

            column_index = item.data(
                Qt.UserRole
            )

            column_order.append(
                column_index
            )

            widget = self.list_widget.itemWidget(
                item
            )

            if widget is None:
                continue

            checkboxes = widget.findChildren(
                QCheckBox
            )

            if len(checkboxes) >= 2:

                display_checkbox = checkboxes[0]
                export_checkbox = checkboxes[1]

                if display_checkbox.isChecked():
                    visible_columns.add(
                        column_index
                    )

                if export_checkbox.isChecked():
                    export_columns.add(
                        column_index
                    )

        return (
            column_order,
            visible_columns,
            export_columns
        )

    # -----------------------------------------------------
    # Move up
    # -----------------------------------------------------

    def move_up(self):

        row = self.list_widget.currentRow()

        if row <= 0:
            return

        (
            column_order,
            visible_columns,
            export_columns
        ) = self.get_current_settings()

        # Swap the two columns
        column_order[row], column_order[row - 1] = (
            column_order[row - 1],
            column_order[row]
        )

        self.populate_list(
            column_order,
            visible_columns,
            export_columns
        )

        self.list_widget.setCurrentRow(
            row - 1
        )

    # -----------------------------------------------------
    # Move down
    # -----------------------------------------------------

    def move_down(self):

        row = self.list_widget.currentRow()

        if row < 0:
            return

        if row >= self.list_widget.count() - 1:
            return

        (
            column_order,
            visible_columns,
            export_columns
        ) = self.get_current_settings()

        # Swap the two columns
        column_order[row], column_order[row + 1] = (
            column_order[row + 1],
            column_order[row]
        )

        self.populate_list(
            column_order,
            visible_columns,
            export_columns
        )

        self.list_widget.setCurrentRow(
            row + 1
        )

    # -----------------------------------------------------
    # Reset defaults
    # -----------------------------------------------------

    def reset_defaults(self):

        column_order = list(
            range(len(self.columns))
        )

        visible_columns = set()

        export_columns = set()

        for column_index, (
            title,
            field_name
        ) in enumerate(self.columns):

            if field_name in self.default_visible:
                visible_columns.add(
                    column_index
                )

            if field_name in self.default_export:
                export_columns.add(
                    column_index
                )

        self.populate_list(
            column_order,
            visible_columns,
            export_columns
        )

        self.list_widget.setCurrentRow(0)

    # -----------------------------------------------------
    # Return settings to MainWindow
    # -----------------------------------------------------

    def get_settings(self):

        return self.get_current_settings()