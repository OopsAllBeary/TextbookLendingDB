from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QColor

from applications import get_all_applications


class ApplicationTableModel(QAbstractTableModel):

    COLUMNS = [
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

    DEFAULT_COLUMNS = [
        "student_id",
        "first_name",
        "last_name",
        "status",
        "requested_books_devices",
        "notes",
        "rsvp"
    ]

    def __init__(self):
        super().__init__()

        self._all_rows = []

        self._rows = []

        self._filter_text = ""

        self._sort_column = next(
            i for i, (_, field) in enumerate(self.COLUMNS)
            if field == "status"
        )

        self._sort_order = Qt.AscendingOrder

        self.reload()

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    def reload(self):
        self.beginResetModel()

        self._all_rows = get_all_applications()

        self._apply_filter()
        self._apply_sort()

        self.endResetModel()

    def update_annotation(self, application_id, status, notes, rsvp):

        old_status = None

        for row in self._all_rows:

            if row["application_id"] == application_id:

                old_status = row.get("status") or "New"

                row["status"] = status
                row["notes"] = notes
                row["rsvp"] = rsvp

                break

        self.beginResetModel()

        self._apply_filter()
        self._apply_sort()

        self.endResetModel()

        return old_status

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def set_filter(self, text):

        self._filter_text = text.strip().lower()

        self.beginResetModel()

        self._apply_filter()
        self._apply_sort()

        self.endResetModel()

    def _apply_filter(self):

        if not self._filter_text:
            self._rows = list(self._all_rows)
            return

        self._rows = []

        for row in self._all_rows:

            for value in row.values():

                if self._filter_text in str(value).lower():

                    self._rows.append(row)
                    break

    # ---------------------------------------------------------
    # SORTING
    # ---------------------------------------------------------

    def sort(self, column, order=Qt.AscendingOrder):

        self._sort_column = column
        self._sort_order = order

        self.layoutAboutToBeChanged.emit()

        self._apply_sort()

        self.layoutChanged.emit()

    def _apply_sort(self):

        if self._sort_column is None:
            return

        column_name = self.COLUMNS[self._sort_column][1]

        if column_name == "status":

            status_order = {
                "New": 0,
                "WaitList": 1,
                "Approved": 2,
                "Denied": 3
            }

            self._rows.sort(
                key=lambda row: status_order.get(
                    row.get("status") or "New",
                    99
                ),
                reverse=(self._sort_order == Qt.DescendingOrder)
            )

        else:

            self._rows.sort(
                key=lambda row: str(
                    row.get(column_name) or ""
                ).lower(),
                reverse=(self._sort_order == Qt.DescendingOrder)
            )

    # ---------------------------------------------------------
    # TABLE MODEL
    # ---------------------------------------------------------

    def rowCount(self, parent=None):
        return len(self._rows)

    def columnCount(self, parent=None):
        return len(self.COLUMNS)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        row = self._rows[index.row()]
        column = self.COLUMNS[index.column()][1]

        if role == Qt.DisplayRole:

            value = row.get(column, "")

            if value is None:
                return ""

            return str(value)

        status = (row.get("status") or "New").strip().lower()

        if role == Qt.BackgroundRole:

            if status == "new":
                return QColor("#FFF59D")

        if role == Qt.ForegroundRole:

            if status == "new":
                return QColor("#000000")

        return None

    def headerData(self, section, orientation, role):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COLUMNS[section][0]

        return str(section + 1)

    # ---------------------------------------------------------
    # APPLICATION ACCESS
    # ---------------------------------------------------------

    def application_id(self, row):
        return self._rows[row]["application_id"]

    def get_row(self, row):
        return self._rows[row]

    def get_all_rows(self):
        return self._all_rows

    def get_status(self, application_id):

        for row in self._all_rows:

            if row["application_id"] == application_id:
                return row.get("status") or "New"

        return "New"