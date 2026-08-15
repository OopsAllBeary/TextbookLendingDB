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


class BookstoreViewDialog(QDialog):

    def __init__(
        self,
        materials,
        selected_materials=None,
        student_id=None,
        parent=None
    ):
        super().__init__(parent)

        self.materials = materials
        self.student_id = student_id

        self.selected_materials = (
            selected_materials or []
        )

        self.option_groups = []

        self.setWindowTitle(
            "Saved Bookstore Materials"
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
        # Instructions
        # -----------------------------------------

        instructions = QLabel(
            "Change the materials you want to include, "
            "then click Save Selections."
        )

        instructions.setStyleSheet(
            "color: #555;"
        )

        layout.addWidget(
            instructions
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

        save_button = QPushButton(
            "Save Selections"
        )

        save_button.clicked.connect(
            self.accept
        )

        button_layout.addWidget(
            cancel_button
        )

        button_layout.addWidget(
            save_button
        )

        layout.addLayout(
            button_layout
        )


    def build_materials(self):

        for material in self.materials:

            self.add_material(
                material
            )


    def is_material_selected(
        self,
        material
    ):

        material_id = material.get(
            "id"
        )

        for selected in (
            self.selected_materials
        ):

            if (
                selected.get("material_id")
                == material_id
            ):
                return selected

        return None


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
        # ISBN
        # -----------------------------------------

        isbn = material.get(
            "isbn",
            ""
        )

        if isbn:

            isbn_label = QLabel(
                f"ISBN: {isbn}"
            )

            group_layout.addWidget(
                isbn_label
            )

        # -----------------------------------------
        # Include checkbox
        # -----------------------------------------

        include_checkbox = QCheckBox(
            "Include this material"
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

        # -----------------------------------------
        # Restore existing selection
        # -----------------------------------------

        existing_selection = (
            self.is_material_selected(
                material
            )
        )

        if existing_selection:

            include_checkbox.setChecked(
                True
            )

            existing_type = (
                existing_selection.get(
                    "option_type"
                )
            )

            existing_sku = (
                existing_selection.get(
                    "sku"
                )
            )

            matched = False

            for radio in option_widgets:

                option = radio.property(
                    "option_data"
                )

                if not option:
                    continue

                option_type = option.get(
                    "type"
                )

                option_sku = option.get(
                    "sku"
                )

                if (
                    option_type
                    == existing_type
                    or (
                        existing_sku
                        and option_sku
                        == existing_sku
                    )
                ):

                    radio.setChecked(
                        True
                    )

                    matched = True

                    break

            if not matched and option_widgets:

                option_widgets[0].setChecked(
                    True
                )

        else:

            # New/unselected material.
            include_checkbox.setChecked(
                False
            )

            if option_widgets:

                option_widgets[0].setChecked(
                    True
                )

        # -----------------------------------------
        # Included material handling
        # -----------------------------------------

        if material.get(
            "included_material",
            False
        ):

            if not existing_selection:

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

            include = item[
                "include"
            ]

            if not include.isChecked():
                continue

            button = item[
                "group"
            ].checkedButton()

            option = None

            if button:

                option = button.property(
                    "option_data"
                )

            selected.append(
                {
                    "material":
                        item["material"],

                    "option":
                        option
                }
            )

        return selected