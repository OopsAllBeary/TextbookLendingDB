from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView
)


class BookstoreViewDialog(QDialog):

    def __init__(
        self,
        materials,
        student_id=None,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Saved Bookstore Materials"
        )

        self.resize(
            950,
            600
        )

        layout = QVBoxLayout(self)

        # -----------------------------------------
        # Header
        # -----------------------------------------

        title = QLabel(
            "Saved Bookstore Materials"
        )

        title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        layout.addWidget(title)


        if student_id:

            student_label = QLabel(
                f"Student ID: {student_id}"
            )

            layout.addWidget(
                student_label
            )


        # -----------------------------------------
        # Table
        # -----------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "Course",
            "Material",
            "Category",
            "ISBN",
            "Option",
            "Price",
            "Availability"
        ])

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setAlternatingRowColors(
            True
        )

        header = (
            self.table.horizontalHeader()
        )

        header.setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        header.setStretchLastSection(
            True
        )

        layout.addWidget(
            self.table
        )


        self.populate(
            materials
        )


        # -----------------------------------------
        # Close
        # -----------------------------------------

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            close_button
        )

        layout.addLayout(
            buttons
        )


    def populate(self, materials):

        self.table.setRowCount(
            len(materials)
        )

        for row, material in enumerate(
            materials
        ):

            values = [
                material.get(
                    "course",
                    ""
                ),

                material.get(
                    "title",
                    ""
                ),

                material.get(
                    "category",
                    ""
                ),

                material.get(
                    "isbn",
                    ""
                ),

                material.get(
                    "option_label",
                    ""
                ),

                material.get(
                    "price_display",
                    ""
                ),

                material.get(
                    "availability",
                    ""
                )
            ]


            for column, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(value or "")
                )

                self.table.setItem(
                    row,
                    column,
                    item
                )