from PySide6.QtCore import (
    Qt,
    QAbstractTableModel
)


class BookstoreSelectionsModel(
    QAbstractTableModel
):

    COLUMNS = [
        ("ISBN", "isbn"),
        ("Student ID", "student_id"),
        ("Student Name", "student_name"),
        ("Title", "title"),
        ("Course", "course"),
        ("Price", "price_display")
    ]

    def __init__(self):

        super().__init__()

        self._materials = []


    def set_materials(self, materials):

        self.beginResetModel()

        self._materials = list(
            materials
        )

        self.endResetModel()


    def get_material(self, row):

        if (
            row < 0
            or row >= len(self._materials)
        ):
            return None

        return self._materials[row]


    def rowCount(self, parent=None):

        return len(
            self._materials
        )


    def columnCount(self, parent=None):

        return len(
            self.COLUMNS
        )


    def data(
        self,
        index,
        role=Qt.DisplayRole
    ):

        if not index.isValid():
            return None

        material = self._materials[
            index.row()
        ]

        field = self.COLUMNS[
            index.column()
        ][1]

        if role == Qt.DisplayRole:

            value = material.get(
                field,
                ""
            )

            if value is None:
                return ""

            if field == "price":

                try:

                    return f"${float(value):,.2f}"

                except (
                    TypeError,
                    ValueError
                ):

                    return ""

            return str(value)

        return None


    def headerData(
        self,
        section,
        orientation,
        role=Qt.DisplayRole
    ):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            return self.COLUMNS[
                section
            ][0]

        return str(
            section + 1
        )