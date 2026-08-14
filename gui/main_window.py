import csv

from PySide6.QtCore import Qt, QTimer, QSettings
from datetime import datetime
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QTextEdit,
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
    QScrollArea,
    QSizePolicy,
    QTabWidget
)

from gui.deleted_applications_dialog import DeletedApplicationsDialog

from gui.column_settings_dialog import ColumnSettingsDialog

from import_csv import import_applications

from email_handler import open_status_email

from annotations import (
    set_status,
    set_notes,
    set_rsvp
)

from applications import delete_application

from bookstore.server import (
    BookstoreServer
)

from bookstore.parser import (
    parse_bookstore_response
)

from bookstore.database import (
    clear_bookstore_selections_for_lookup,
    create_bookstore_lookup,
    save_bookstore_lookup,
    save_bookstore_results,
    save_bookstore_selection,
    get_bookstore_lookup_summary,
    get_bookstore_total_current_price,
    get_latest_bookstore_lookup,
    get_bookstore_materials,
    get_all_bookstore_selections,
    delete_bookstore_selection,
    get_bookstore_selections_total
)

from bookstore.dialog import (
    BookstoreDialog
)

from bookstore.view_dialog import (
    BookstoreViewDialog
)


from gui.bookstore_selections_model import (
    BookstoreSelectionsModel
)

from bookstore.config import (
    PRIMARY_PROGRAM_ID,
    FALLBACK_PROGRAM_ID,
    BOOKSTORE_PROGRAMS,
    BOOKSTORE_TERM_ID
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

from db import clear_database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_application_id = None

        self.bookstore_application_id = None
        self.bookstore_student_id = None
        self.bookstore_lookup_id = None

        self.bookstore_server = BookstoreServer()

        self.bookstore_server.results_received.connect(
            self.on_bookstore_results
        )

        self.bookstore_server.error_occurred.connect(
            self.on_bookstore_error
        )

        self.bookstore_server.start()

        self.setWindowTitle("Textbook Lending Tracker")

        screen = self.screen().availableGeometry()

        window_width = min(
            1200,
            int(screen.width() * 0.90)
        )

        window_height = min(
            800,
            int(screen.height() * 0.90)
        )

        self.resize(
            window_width,
            window_height
        )

        self.settings = QSettings(
            "TextbookLendingTracker",
            "TextbookLendingTracker"
        )

        self.setup_menu()

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout = QVBoxLayout(
            central
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )


        # ---------------------------------------------------------
        # TABS
        # ---------------------------------------------------------

        self.tabs = QTabWidget()

        layout.addWidget(
            self.tabs
        )


        # ---------------------------------------------------------
        # APPLICATIONS TAB
        # ---------------------------------------------------------

        self.applications_tab = QWidget()

        self.tabs.addTab(
            self.applications_tab,
            "Applications"
        )

        applications_layout = QVBoxLayout(
            self.applications_tab
        )

        # ---------------------------------------------------------
        # TOP CONTROLS
        # ---------------------------------------------------------

        top_widget = QWidget()

        top_widget.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed
        )

        top_layout = QVBoxLayout(top_widget)

        top_layout.setContentsMargins(
            0,
            0,
            0,
            4
        )

        top_layout.setSpacing(4)


        # Import / Export / Refresh buttons

        button_layout = QHBoxLayout()

        self.import_button = QPushButton(
            "Import CSV"
        )

        self.export_button = QPushButton(
            "Export CSV"
        )

        self.refresh_button = QPushButton(
            "Refresh"
        )

        button_layout.addWidget(
            self.import_button
        )

        button_layout.addWidget(
            self.export_button
        )

        button_layout.addWidget(
            self.refresh_button
        )

        button_layout.addStretch()

        top_layout.addLayout(
            button_layout
        )


        # Search

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search applications..."
        )

        self.search_box.setFixedHeight(
            28
        )

        top_layout.addWidget(
            self.search_box
        )


        # Filtered bookstore total

        self.bookstore_filtered_total_label = QLabel(
            "Filtered Book Cost: $0.00"
        )

        self.bookstore_filtered_total_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 2px;
            }
            """
        )

        self.bookstore_filtered_total_label.setFixedHeight(
            28
        )

        top_layout.addWidget(
            self.bookstore_filtered_total_label
        )


        applications_layout.addWidget(
            top_widget
        )


        # ---------------------------------------------------------
        # MAIN CONTENT
        # ---------------------------------------------------------

        splitter = QSplitter(
            Qt.Horizontal
        )

        splitter.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        applications_layout.addWidget(
            splitter
        )

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
        self.load_column_settings()

        self.table.sortByColumn(
            4,
            Qt.AscendingOrder
        )
        
        splitter.addWidget(self.table)

        self.refresh_button.clicked.connect(self.load_data)
        self.import_button.clicked.connect(self.import_csv)
        self.export_button.clicked.connect(self.export_csv)

        self.search_box.textChanged.connect(
            self.on_search_changed
        )

        self.load_data()

        details_widget = QWidget()

        details_layout = QFormLayout(details_widget)

        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setWidget(details_widget)
        details_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        splitter.addWidget(details_scroll)

        splitter.setSizes([750, 250])

        self.detail_labels = {}
        self.edit_widgets = {}

        self.bookstore_total_label = QLabel(
            "Not yet looked up"
        )

        self.bookstore_lookup_label = QLabel(
            ""
        )

        self.bookstore_total_label.setWordWrap(
            True
        )

        self.bookstore_lookup_label.setWordWrap(
            True
        )

        details_layout.addRow(
            "Bookstore:",
            self.bookstore_total_label
        )

        details_layout.addRow(
            "Last Lookup:",
            self.bookstore_lookup_label
        )

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
                widget.setFixedHeight(60)

                self.edit_widgets[field_name] = widget

                details_layout.addRow(
                    label_text + ":",
                    widget
                )

            elif field_name == "notes":
                widget = QTextEdit()
                widget.setFixedHeight(100)

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

        self.bookstore_button = QPushButton(
            "Look Up Bookstore Materials"
        )

        self.bookstore_button.clicked.connect(
            self.lookup_bookstore
        )

        details_layout.addRow(
            self.bookstore_button
        )

        self.view_bookstore_button = QPushButton(
            "View Saved Materials"
        )

        self.view_bookstore_button.clicked.connect(
            self.view_bookstore_materials
        )

        self.view_bookstore_button.setEnabled(
            False
        )

        details_layout.addWidget(
            self.view_bookstore_button
        )


        self.save_button = QPushButton(
            "Save"
        )

        details_layout.addRow(
            self.save_button
        )

        self.save_button.clicked.connect(
            self.save_changes
        )


        self.delete_button = QPushButton("Delete Application")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                font-weight: bold;
                border: none;
                padding: 5px 10px;}
        """)

        details_layout.addRow(QLabel(""))
        details_layout.addRow(self.delete_button)

        self.delete_button.clicked.connect(
            self.delete_selected_application
        )

        # ---------------------------------------------------------
        # SELECTED MATERIALS TAB
        # ---------------------------------------------------------

        self.selected_materials_tab = QWidget()

        self.tabs.addTab(
            self.selected_materials_tab,
            "Selected Materials"
        )


        selected_layout = QVBoxLayout(
            self.selected_materials_tab
        )


        # ---------------------------------------------------------
        # MATERIALS TABLE
        # ---------------------------------------------------------

        self.selected_materials_model = (
            BookstoreSelectionsModel()
        )


        self.selected_materials_table = (
            QTableView()
        )

        self.selected_materials_table.setModel(
            self.selected_materials_model
        )

        self.selected_materials_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.selected_materials_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.selected_materials_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.selected_materials_table.setAlternatingRowColors(
            True
        )

        self.selected_materials_table.setSortingEnabled(
            True
        )

        self.selected_materials_table.horizontalHeader().setStretchLastSection(
            True
        )

        self.selected_materials_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )


        selected_layout.addWidget(
            self.selected_materials_table
        )


        # ---------------------------------------------------------
        # BOTTOM CONTROLS
        # ---------------------------------------------------------

        bottom_layout = QHBoxLayout()


        self.selected_materials_total_label = QLabel(
            "Total: $0.00"
        )

        self.selected_materials_total_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 16px;
                padding: 6px;
            }
            """
        )


        self.refresh_selected_materials_button = (
            QPushButton(
                "Refresh"
            )
        )


        self.remove_selected_material_button = (
            QPushButton(
                "Remove Selected Material"
            )
        )


        bottom_layout.addWidget(
            self.selected_materials_total_label
        )

        bottom_layout.addStretch()


        bottom_layout.addWidget(
            self.refresh_selected_materials_button
        )

        bottom_layout.addWidget(
            self.remove_selected_material_button
        )


        selected_layout.addLayout(
            bottom_layout
        )


        # ---------------------------------------------------------
        # CONNECTIONS
        # ---------------------------------------------------------

        self.refresh_selected_materials_button.clicked.connect(
            self.load_selected_materials
        )

        self.remove_selected_material_button.clicked.connect(
            self.remove_selected_material
        )


        # ---------------------------------------------------------
        # INITIAL LOAD
        # ---------------------------------------------------------

        self.load_selected_materials()

    def load_selected_materials(self):
        """
        Load all currently selected bookstore materials
        into the Selected Materials tab.
        """

        try:

            materials = get_all_bookstore_selections()

            self.selected_materials_model.set_materials(
                materials
            )


            total = 0.0

            for material in materials:

                try:

                    total += float(
                        material.get("price") or 0
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    pass


            self.selected_materials_total_label.setText(
                f"Total: ${total:,.2f}"
            )


        except Exception as e:

            print(
                "Error loading selected materials:",
                e
            )

            self.selected_materials_model.set_materials(
                []
            )

            self.selected_materials_total_label.setText(
                "Total: $0.00"
            )

    def remove_selected_material(self):

        index = (
            self.selected_materials_table
            .currentIndex()
        )

        if not index.isValid():
            return

        material = (
            self.selected_materials_model
            .get_material(index.row())
        )

        if not material:
            return

        selection_id = material.get(
            "selection_id"
        )

        if not selection_id:
            return

        try:

            delete_bookstore_selection(
                selection_id
            )

            self.load_selected_materials()

        except Exception as e:

            print(
                "Error removing selected material:",
                e
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

        deleted_applications_action = (
            settings_menu.addAction(
                "Deleted Applications"
            )
        )

        deleted_applications_action.triggered.connect(
            self.open_deleted_applications
        )

        clear_database_action = settings_menu.addAction(
            "Clear Database..."
        )

        clear_database_action.triggered.connect(
            self.clear_database
        )

    def open_deleted_applications(self):

        dialog = DeletedApplicationsDialog(
            self
        )

        dialog.exec()

        self.model.reload()

    def open_column_settings(self):

        header = self.table.horizontalHeader()

        column_order = []

        for visual_index in range(
            header.count()
        ):

            logical_index = header.logicalIndex(
                visual_index
            )

            column_order.append(
                logical_index
            )

        visible_columns = set()

        for column_index in range(
            header.count()
        ):

            if not self.table.isColumnHidden(
                column_index
            ):
                visible_columns.add(
                    column_index
                )

        export_columns = self.get_export_columns()

        dialog = ColumnSettingsDialog(
            self.model.COLUMNS,
            visible_columns,
            export_columns,
            column_order,
            set(self.model.DEFAULT_COLUMNS),
            set(self.model.DEFAULT_EXPORT_COLUMNS),
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        (
            new_order,
            new_visible,
            new_export
        ) = dialog.get_settings()

        self.apply_column_settings(
            new_order,
            new_visible
        )

        self.save_column_settings(
            new_order,
            new_visible,
            new_export
        )

    def get_export_columns(self):

        saved_export = self.settings.value(
            "export_columns",
            None
        )

        if saved_export is None:

            return {
                index
                for index, (_, field_name)
                in enumerate(self.model.COLUMNS)
                if field_name in self.model.DEFAULT_EXPORT_COLUMNS
            }

        return {
            int(value)
            for value in saved_export
        }

    def apply_column_settings(
        self,
        column_order,
        visible_columns
    ):

        header = self.table.horizontalHeader()

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
        visible_columns,
        export_columns
    ):

        self.settings.setValue(
            "column_order",
            column_order
        )

        self.settings.setValue(
            "visible_columns",
            list(visible_columns)
        )

        self.settings.setValue(
            "export_columns",
            list(export_columns)
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

            saved_visible = {
                index
                for index, (_, field_name)
                in enumerate(self.model.COLUMNS)
                if field_name in self.model.DEFAULT_COLUMNS
            }

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

        self.update_filtered_bookstore_total()

    def on_selection_changed(self):

        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            self.current_application_id = None
            return

        new_application = self.model.get_row(
            indexes[0].row()
        )

        self.save_current_application()

        self.current_application_id = new_application.get(
            "application_id"
        )

        self.bookstore_total_label.setText(
            "Not yet looked up"
        )

        self.display_application(
            new_application
        )

    def display_application(self, application):
        self.current_application_id = application["application_id"]

        summary = get_bookstore_lookup_summary(
            self.current_application_id
        )

        total_current_price = (
            get_bookstore_total_current_price(
                self.current_application_id
            )
        )

        materials = get_bookstore_materials(
            self.current_application_id
        )

        self.view_bookstore_button.setEnabled(
            bool(materials)
        )

        if summary.get("lookup_id") is None:

            self.bookstore_total_label.setText(
                "Not yet looked up"
            )

            self.bookstore_lookup_label.setText(
                "Never"
            )

        else:

            self.bookstore_total_label.setText(
                f"${total_current_price:,.2f}"
            )

            self.bookstore_lookup_label.setText(
                summary["lookup_date"]
            )

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

        lookup_summary = get_bookstore_lookup_summary(
            self.current_application_id
        )

        total_current_price = (
            get_bookstore_total_current_price(
                self.current_application_id
            )
        )

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

    def delete_selected_application(self):

        indexes = self.table.selectionModel().selectedRows()

        if not indexes:
            QMessageBox.information(
                self,
                "Delete Application",
                "Please select an application first."
            )
            return

        application = self.model.get_row(
            indexes[0].row()
        )

        student_name = (
            f"{application.get('first_name', '')} "
            f"{application.get('last_name', '')}"
        ).strip()

        reply = QMessageBox.warning(
            self,
            "Delete Application",
            (
                f"Are you sure you want to delete "
                f"the application for {student_name}?\n\n"
                "This can be undone later."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.save_current_application()

        application_id = application["application_id"]

        delete_application(application_id)

        self.current_application_id = None

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

    def lookup_bookstore(self):

        if self.current_application_id is None:

            QMessageBox.warning(
                self,
                "No Application Selected",
                "Please select an application first."
            )

            return


        # -----------------------------------------
        # Find current application
        # -----------------------------------------

        application = None

        for row in self.model.get_all_rows():

            if row.get("application_id") == self.current_application_id:

                application = row

                break


        if application is None:

            QMessageBox.warning(
                self,
                "Application Not Found",
                "The selected application could not be found."
            )

            return


        # -----------------------------------------
        # Check for existing lookup
        # -----------------------------------------

        existing_lookup = get_latest_bookstore_lookup(
            self.current_application_id
        )

        if existing_lookup:

            reply = QMessageBox.question(
                self,
                "Bookstore Results Already Exist",
                "This application already has bookstore "
                "results.\n\n"
                "Would you like to perform a new lookup?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return


        # -----------------------------------------
        # Student ID
        # -----------------------------------------

        student_id = application.get(
            "student_id"
        )

        if not student_id:

            QMessageBox.warning(
                self,
                "Missing Student ID",
                "This application does not have a Student ID."
            )

            return


        # -----------------------------------------
        # Prepare lookup state
        # -----------------------------------------

        self.bookstore_application_id = (
            self.current_application_id
        )

        self.bookstore_student_id = str(
            student_id
        )

        self.bookstore_program_id = (
            PRIMARY_PROGRAM_ID
        )


        self.bookstore_button.setEnabled(
            False
        )

        self.bookstore_button.setText(
            "Waiting for Bookstore Results..."
        )


        # -----------------------------------------
        # Create lookup record
        # -----------------------------------------

        self.bookstore_lookup_id = (
            create_bookstore_lookup(
                application_id=(
                    self.bookstore_application_id
                ),
                student_id=(
                    self.bookstore_student_id
                ),
                program_id=(
                    self.bookstore_program_id
                ),
                term_id=BOOKSTORE_TERM_ID
            )
        )


        # -----------------------------------------
        # Request bookstore lookup
        # -----------------------------------------

        success = (
            self.bookstore_server.request_lookup(
                student_id=self.bookstore_student_id,
                term_id=BOOKSTORE_TERM_ID,
                program_id=self.bookstore_program_id
            )
        )


        if not success:

            self.reset_bookstore_lookup()

            return


    def on_bookstore_results(
        self,
        data
    ):

        if (
            self.bookstore_application_id
            != self.current_application_id
        ):

            QMessageBox.warning(
                self,
                "Bookstore Result Ignored",
                "The bookstore results belong to "
                "a different application."
            )

            return


        self.bookstore_button.setEnabled(
            True
        )

        self.bookstore_button.setText(
            "Look Up Bookstore Materials"
        )


        try:

            response = data.get(
                "response",
                data
            )


            result = parse_bookstore_response(
                response
            )

            materials = result["materials"]

            total_current_price = result[
                "total_current_price"
            ]


            # -----------------------------------------
            # Make sure we have the lookup ID
            # -----------------------------------------

            if self.bookstore_lookup_id is None:

                raise RuntimeError(
                    "No bookstore lookup ID is available."
                )


            lookup_id = (
                self.bookstore_lookup_id
            )


            # -----------------------------------------
            # Save total
            # -----------------------------------------

            save_bookstore_lookup(
                self.bookstore_application_id,
                total_current_price
            )


            # -----------------------------------------
            # Save materials
            # -----------------------------------------

            save_bookstore_results(
                self.bookstore_application_id,
                lookup_id,
                materials
            )


            # -----------------------------------------
            # Update UI
            # -----------------------------------------

            self.bookstore_total_label.setText(
                f"${total_current_price:,.2f}"
            )

            self.bookstore_lookup_label.setText(
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

            self.view_bookstore_button.setEnabled(
                bool(materials)
            )


        except Exception as e:

            QMessageBox.critical(
                self,
                "Bookstore Error",
                "Could not process bookstore "
                "results.\n\n"
                f"{e}"
            )

            return


        # -----------------------------------------
        # No materials
        # -----------------------------------------

        if not materials:

            QMessageBox.information(
                self,
                "No Materials Found",
                "No course materials were found."
            )

            self.bookstore_application_id = None
            self.bookstore_student_id = None
            self.bookstore_lookup_id = None

            return


        # -----------------------------------------
        # Show selection dialog
        # -----------------------------------------

        dialog = BookstoreDialog(
            materials,
            student_id=self.bookstore_student_id,
            parent=self
        )


        if dialog.exec() == QDialog.Accepted:

            selected = (
                dialog.selected_materials()
            )


            print(
                "Selected bookstore materials:",
                len(selected)
            )


            self.handle_selected_materials(
                selected
            )


        # -----------------------------------------
        # Clear lookup state
        # -----------------------------------------

        self.bookstore_application_id = None
        self.bookstore_student_id = None
        self.bookstore_lookup_id = None

  
    def on_bookstore_error(
        self,
        message
    ):

        self.reset_bookstore_lookup()


        QMessageBox.warning(
            self,
            "Bookstore Connection Error",
            message
        )

    def handle_selected_materials(
        self,
        selected
    ):

        if self.current_application_id is None:
            return

        if self.bookstore_lookup_id is None:
            return

        lookup_id = (
            self.bookstore_lookup_id
        )

        try:

            # -----------------------------------------
            # Remove previous selections for this lookup
            # -----------------------------------------

            clear_bookstore_selections_for_lookup(
                lookup_id
            )


            # -----------------------------------------
            # Save selected options
            # -----------------------------------------

            saved_count = 0

            for item in selected:

                material = item["material"]

                option = item["option"]

                if option is None:
                    continue

                material_id = material.get(
                    "id"
                )

                if material_id is None:
                    print(
                        "Selected material has no ID:",
                        material
                    )
                    continue

                save_bookstore_selection(
                    material_id,
                    option
                )

                saved_count += 1


            # -----------------------------------------
            # Refresh Selected Materials tab
            # -----------------------------------------

            self.load_selected_materials()


            # -----------------------------------------
            # Keep the selection confirmation
            # -----------------------------------------

            QMessageBox.information(
                self,
                "Bookstore Materials",
                f"{saved_count} material(s) selected."
            )


        except Exception as e:

            QMessageBox.critical(
                self,
                "Save Failed",
                "The bookstore selections "
                "could not be saved.\n\n"
                f"{e}"
            )

            print(
                "Error saving bookstore selections:",
                e
            )

    def view_bookstore_materials(self):

        if self.current_application_id is None:
            return


        materials = get_bookstore_materials(
            self.current_application_id
        )


        if not materials:

            QMessageBox.information(
                self,
                "No Bookstore Materials",
                "There are no saved bookstore "
                "materials for this application."
            )

            return


        student_id = None

        indexes = (
            self.table
            .selectionModel()
            .selectedRows()
        )


        if indexes:

            application = self.model.get_row(
                indexes[0].row()
            )

            student_id = application.get(
                "student_id"
            )


        dialog = BookstoreViewDialog(
            materials,
            student_id=student_id,
            parent=self
        )

        dialog.exec()

    def reset_bookstore_lookup(self):
        self.bookstore_application_id = None
        self.bookstore_student_id = None

        self.bookstore_button.setEnabled(True)
        self.bookstore_button.setText(
            "Look Up Bookstore Materials"
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

            export_columns = self.get_export_columns()

            fieldnames = [
                field_name
                for index, (_, field_name) 
                in enumerate(self.model.COLUMNS)
                if index in export_columns
            ]

            if not fieldnames:

                QMessageBox.warning(
                    self,
                    "Export",
                    "Nocolumns are selected for export."
                )

                return

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

    def update_filtered_bookstore_total(self):

        rows = self.model.get_filtered_rows()

        total = 0.0

        for application in rows:

            application_id = application.get(
                "application_id"
            )

            if not application_id:
                continue

            total += get_bookstore_total_current_price(
                application_id
            )

        self.bookstore_filtered_total_label.setText(
            f"Filtered Book Cost: ${total:,.2f}"
        )

    def on_search_changed(self, text):

        self.model.set_filter(
            text
        )

        self.update_filtered_bookstore_total()

    def clear_database(self):

        reply = QMessageBox.warning(
            self,
            "Clear Database",
            (
                "This will permanently delete ALL data "
                "from the database.\n\n"
                "This includes:\n"
                "• Applications\n"
                "• Annotations\n"
                "• Bookstore materials\n"
                "• Bookstore selections\n"
                "• Bookstore lookups\n"
                "• Import history\n\n"
                "This cannot be undone.\n\n"
                "Are you sure you want to continue?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:

            clear_database()

            self.current_application_id = None
            self.bookstore_application_id = None
            self.bookstore_student_id = None
            self.bookstore_lookup_id = None

            self.model.reload()

            for label in self.detail_labels.values():
                label.setText("")

            self.bookstore_total_label.setText(
                "Not yet looked up"
            )

            self.bookstore_lookup_label.setText(
                ""
            )

            self.view_bookstore_button.setEnabled(
                False
            )

            QMessageBox.information(
                self,
                "Database Cleared",
                "The database has been completely cleared."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Clear Database Failed",
                f"The database could not be cleared.\n\n{e}"
            )

    def save_selected_bookstore_materials(
        self,
        selected_materials
    ):

        try:

            # Remove any previous selections
            # for this lookup first.
            clear_bookstore_selections_for_lookup(
                self.bookstore_lookup_id
            )

            for item in selected_materials:

                material = item["material"]
                option = item["option"]

                material_id = material.get(
                    "id"
                )

                if not material_id:
                    print(
                        "Skipping material without ID:",
                        material
                    )
                    continue

                if option is None:
                    print(
                        "Skipping material without selected option:",
                        material
                    )
                    continue

                save_bookstore_selection(
                    material_id,
                    option
                )

            self.load_selected_materials()

            print(
                "Saved bookstore selections:",
                len(selected_materials)
            )

        except Exception as e:

            print(
                "Error saving bookstore selections:",
                e
            )
            raise