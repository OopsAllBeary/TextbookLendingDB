from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QCheckBox
)


class BookstoreDialog(QDialog):

    def __init__(
        self,
        materials,
        student_id=None,
        parent=None
    ):
        super().__init__(parent)

        self.materials = materials
        self.student_id = student_id

        self.option_groups = []

        self.setWindowTitle(
            "Bookstore Materials"
        )

        self.resize(
            900,
            700
        )

        layout = QVBoxLayout(self)

        # -----------------------------------------
        # Header
        # -----------------------------------------

        title = QLabel(
            "Bookstore Materials"
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
        # Scroll area
        # -----------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        content = QWidget()

        self.material_layout = QVBoxLayout(
            content
        )

        self.material_layout.setAlignment(
            Qt.AlignTop
        )

        scroll.setWidget(
            content
        )

        layout.addWidget(
            scroll
        )


        self.build_materials()


        # -----------------------------------------
        # Buttons
        # -----------------------------------------

        button_layout = QHBoxLayout()

        button_layout.addStretch()


        cancel_button = QPushButton(
            "Cancel"
        )

        cancel_button.clicked.connect(
            self.reject
        )


        use_button = QPushButton(
            "Use Selected Materials"
        )

        use_button.clicked.connect(
            self.accept
        )


        button_layout.addWidget(
            cancel_button
        )

        button_layout.addWidget(
            use_button
        )

        layout.addLayout(
            button_layout
        )


    def build_materials(self):

        for material in self.materials:

            self.add_material(
                material
            )


    def add_material(
        self,
        material
    ):

        title = material.get(
            "title",
            "Unknown Material"
        )

        group = QGroupBox(
            title
        )

        group_layout = QVBoxLayout(
            group
        )


        # -----------------------------------------
        # Category
        # -----------------------------------------

        category = material.get(
            "category",
            "Other"
        )

        category_label = QLabel(
            category
        )

        category_label.setStyleSheet(
            """
            font-weight: bold;
            """
        )

        group_layout.addWidget(
            category_label
        )


        # -----------------------------------------
        # Course
        # -----------------------------------------

        course = material.get(
            "course",
            ""
        )

        if course:

            course_label = QLabel(
                f"Course: {course}"
            )

            group_layout.addWidget(
                course_label
            )


        # -----------------------------------------
        # Requirement
        # -----------------------------------------

        requirement = material.get(
            "requirement_label",
            ""
        )

        if requirement:

            requirement_label = QLabel(
                f"Requirement: {requirement}"
            )

            group_layout.addWidget(
                requirement_label
            )


        # -----------------------------------------
        # Details
        # -----------------------------------------

        details = []


        isbn = material.get(
            "isbn"
        )

        if isbn:

            details.append(
                f"ISBN: {isbn}"
            )


        author = material.get(
            "author"
        )

        if author:

            details.append(
                f"Author: {author}"
            )


        edition = material.get(
            "edition"
        )

        if edition:

            details.append(
                f"Edition: {edition}"
            )


        publisher = material.get(
            "publisher"
        )

        if publisher:

            details.append(
                f"Publisher: {publisher}"
            )


        if details:

            details_label = QLabel(
                "\n".join(details)
            )

            details_label.setStyleSheet(
                "color: #555;"
            )

            group_layout.addWidget(
                details_label
            )


        # -----------------------------------------
        # Include checkbox
        # -----------------------------------------

        include_checkbox = QCheckBox(
            "Include this material"
        )

        include_checkbox.setChecked(
            True
        )

        group_layout.addWidget(
            include_checkbox
        )


        # -----------------------------------------
        # Options
        # -----------------------------------------

        options = material.get(
            "options",
            []
        )

        button_group = QButtonGroup(
            self
        )

        option_widgets = []


        for option in options:

            label = option.get(
                "label",
                "Unknown"
            )

            price = option.get(
                "price_display",
                ""
            )

            availability = option.get(
                "availability",
                ""
            )


            text = label


            if price:

                text += (
                    f" — {price}"
                )


            if availability:

                text += (
                    f" — {availability}"
                )


            radio = QRadioButton(
                text
            )

            radio.setProperty(
                "option_data",
                option
            )


            button_group.addButton(
                radio
            )

            group_layout.addWidget(
                radio
            )

            option_widgets.append(
                radio
            )


        # Default to first option.
        if option_widgets:

            option_widgets[0].setChecked(
                True
            )


        # Included materials don't necessarily
        # need a purchase option.
        if material.get(
            "included_material",
            False
        ):

            include_checkbox.setChecked(
                False
            )

            include_checkbox.setText(
                "Include this material "
                "(included with course)"
            )


        self.option_groups.append(
            {
                "material": material,
                "group": button_group,
                "include": include_checkbox
            }
        )


        self.material_layout.addWidget(
            group
        )

    def selected_materials(self):

        selected = []

        for item in self.option_groups:

            include = item["include"]

            if not include.isChecked():
                continue

            button = item["group"].checkedButton()

            option = None

            if button:
                option = button.property(
                    "option_data"
                )

            selected.append(
                {
                    "material": item["material"],
                    "option": option
                }
            )

        return selected