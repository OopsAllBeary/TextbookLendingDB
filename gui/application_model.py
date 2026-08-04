from PySide6.QtCore import Qt, QAbstractTableModel

from applications import get_all_applications


class ApplicationTableModel(QAbstractTableModel):

    COLUMNS = [
        ("Student ID", "student_id"),
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Requesting Book and/or Device", "requested_books_devices"),
        ("Status", "status"),
        ("Notes", "notes"),
        ("RSVP", "rsvp")
    ]

    def __init__(self):
        super().__init__()
        self._rows = []
        self.reload()

    def update_annotation(self, application_id, status, notes, rsvp):
        for index, row in enumerate(self._rows):
            if row["application_id"] == application_id:
                row["status"] = status
                row["notes"] = notes
                row["rsvp"] = rsvp

                self.dataChanged.emit(
                    self.index(index, 0),
                    self.index(index, len(self.COLUMNS)-1)
                )

                break

    def reload(self):
        self.beginResetModel()
        self._rows = get_all_applications()
        self.endResetModel()


    def rowCount(self, parent=None):
        return len(self._rows)
    

    def columnCount(self, parent=None):
        return len(self.COLUMNS)
    

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:

            row = self._rows[index.row()]
            column = self.COLUMNS[index.column()][1]

            value = row.get(column, "")

            if value is None:
                return ""

            return str(value)

        return None
    

    def headerData(self, section, orientation, role):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.COLUMNS[section][0]

        return str(section + 1)


    def application_id(self, row):
        return self._rows[row]["application_id"]


    def get_row(self, row):
        return self._rows[row]