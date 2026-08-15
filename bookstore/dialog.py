
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
        selected_materials=None,
        student_id=None,
        parent=None
    ):

        super().__init__(parent)

        self.materials = materials

        self.student_id = student_id

        # None means this is the initial
        # selection dialog.
        #
        # A list means this is editing
        # previously saved selections.

        self.edit_mode = (
            selected_materials is not None
        )

        self.saved_selections = (
            selected_materials or []
        )

        self.option_groups = []


        # -----------------------------------------
        # Window
        # -----------------------------------------

        if self.edit_mode:

            self.setWindowTitle(
                "Edit Saved Bookstore Materials"
            )

        else:

            self.setWindowTitle(
                "Bookstore Materials"
            )


        self.resize(
            900,
            700
        )


        layout = QVBoxLayout(
            self
        )


        # -----------------------------------------
        # Header
        # -----------------------------------------

        if self.edit_mode:

            title_text = (
                "Edit Saved Bookstore Materials"
            )

        else:

            title_text = (
                "Bookstore Materials"
            )


        title = QLabel(
            title_text
        )

        title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )


        # -----------------------------------------
        # Student ID
        # -----------------------------------------

        if student_id:

            student_label = QLabel(
                f"Student ID: {student_id}"
            )

            layout.addWidget(
                student_label
            )


        # -----------------------------------------
        # Edit instructions
        # -----------------------------------------

        if self.edit_mode:

            instructions = QLabel(
                "Change the materials you want "
                "to include, then click "
                "Save Selections."
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

        self.material_layout = (
            QVBoxLayout(
                content
            )
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


        # -----------------------------------------
        # Build materials
        # -----------------------------------------

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


        if self.edit_mode:

            action_text = (
                "Save Selections"
            )

        else:

            action_text = (
                "Use Selected Materials"
            )


        action_button = QPushButton(
            action_text
        )

        action_button.clicked.connect(
            self.accept
        )


        button_layout.addWidget(
            cancel_button
        )

        button_layout.addWidget(
            action_button
        )


        layout.addLayout(
            button_layout
        )


    # =========================================
    # BUILD MATERIALS
    # =========================================

    def build_materials(self):

        for material in self.materials:

            self.add_material(
                material
            )


    # =========================================
    # CHECK EXISTING SELECTION
    # =========================================

    def get_existing_selection(
        self,
        material
    ):

        material_id = material.get(
            "id"
        )


        for selected in (
            self.saved_selections
        ):

            if (
                selected.get(
                    "material_id"
                )
                == material_id
            ):

                return selected


        return None


    # =========================================
    # ADD MATERIAL
    # =========================================

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
                "\n".join(
                    details
                )
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


        # =========================================
        # RESTORE / DEFAULT SELECTION
        # =========================================

        existing_selection = (
            self.get_existing_selection(
                material
            )
        )


        # -----------------------------------------
        # EDIT MODE
        # -----------------------------------------

        if self.edit_mode:

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

                        or

                        (
                            existing_sku
                            and
                            option_sku
                            == existing_sku
                        )

                    ):

                        radio.setChecked(
                            True
                        )

                        matched = True

                        break


                if (
                    not matched
                    and option_widgets
                ):

                    option_widgets[
                        0
                    ].setChecked(
                        True
                    )


            else:

                include_checkbox.setChecked(
                    False
                )


                if option_widgets:

                    option_widgets[
                        0
                    ].setChecked(
                        True
                    )


        # -----------------------------------------
        # INITIAL SELECTION MODE
        # -----------------------------------------

        else:

            include_checkbox.setChecked(
                True
            )


            if option_widgets:

                option_widgets[
                    0
                ].setChecked(
                    True
                )


        # =========================================
        # INCLUDED MATERIAL HANDLING
        # =========================================

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


        # -----------------------------------------
        # Store widgets
        # -----------------------------------------

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


    # =========================================
    # GET SELECTED MATERIALS
    # =========================================

    def selected_materials(self):

        selected = []


        for item in self.option_groups:

            include = item[
                "include"
            ]


            # -------------------------------------
            # Material unchecked
            # -------------------------------------

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
